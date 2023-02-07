# Generated by Django 3.2.16 on 2023-01-23 22:45

import logging

from django.db import migrations
from django.db.utils import IntegrityError
from nautobot.extras.utils import FeatureQuery

logger = logging.getLogger(__name__)


def create_region_location_type_locations(region_class, location_class, region_lt):
    """
    Create location objects for each region instance in the region_class model.

    Args:
        region_class: The model class for legacy regions
        location_class: The model class for locations
        region_lt: The newly created region location type
    """
    # Breadth First Query to create parents on the top levels first and children second.
    regions = (
        region_class.objects.with_tree_fields()
        .extra(order_by=["__tree.tree_depth", "__tree.tree_ordering"])
        .select_related("parent")
    )
    for region in regions:
        try:
            location_class.objects.create(
                location_type=region_lt,
                name=region.name,
                description=region.description,
                parent=location_class.objects.get(name=region.parent.name, location_type=region_lt)
                if region.parent
                else None,
            )
        except IntegrityError as e:
            logger.error(
                f"{e.args[0]} \nPlease consider changing the slug attribute of this Region instance to resolve this conflict."
            )


def create_site_location_type_locations(
    site_class,
    location_type_class,
    location_class,
    site_lt,
    exclude_lt,
    region_lt=None,
):
    """
    Create location objects for each site instance in the site_class model.

    Args:
        site_class: The model class for Legacy sites
        location_type_class: The model class for location types
        location_class: The model class for locations
        site_lt: The newly created site location type
        exclude_lt: The name of the top level location_type_class to exclude from the update query
        e.g.
            At the end of the function, we update all existing top level LocationTypes to have `Site` LocationType as their parent:
            `location_type_class.objects.filter(parent__isnull=True).exclude(name=exclude_lt).update(parent=site_lt)`
            If `Region` and `Site` instances both exist in the database, exclude_lt is set to "Region" (a top level lt) to prevent the above line from setting
            "Region" LocationType to have Site "LocationType" as its parent.
            If only `Site` instances exist in the database, exclude_lt is set to "Site" to prevent the above line from setting
            "Site" LocationType (a top level lt) to have itself as a parent.
        region_lt: The newly created region location type
    """
    count = 0
    location_instances = []

    # Django Documentation on .iterator():
    # "For a QuerySet which returns a large number of objects that you only need to access once
    # this can result in better performance and a significant reduction in memory."
    for site in site_class.objects.all().iterator():
        extra_kwargs = {}
        if region_lt:
            extra_kwargs["parent"] = location_class.objects.get(
                location_type=region_lt, name=site.region.name if site.region else "Global Region"
            )
        location_instances.append(
            location_class(
                name=site.name,
                slug=site.slug,
                location_type=site_lt,
                tenant=site.tenant,
                facility=site.facility,
                asn=site.asn,
                time_zone=site.time_zone,
                description=site.description,
                physical_address=site.physical_address,
                shipping_address=site.shipping_address,
                latitude=site.latitude,
                longitude=site.longitude,
                contact_name=site.contact_name,
                contact_phone=site.contact_phone,
                contact_email=site.contact_email,
                comments=site.comments,
                status=site.status,
                tags=site.tags,
                **extra_kwargs,
            )
        )
        count += 1

        # A simple pagination check:
        # If there are 1000 locations loaded into list `location_instances`, we create the locations in batch of 1000
        # This check is in place to optimize memeroy usage with the creation of large number of location objects
        if count == 1000:
            # Handle IntegrityError when Region, Site, Location instances with the same slug.
            try:
                location_class.objects.bulk_create(location_instances, batch_size=1000)
            except IntegrityError as e:
                logger.error(
                    f"{e.args[0]} \nPlease consider changing the slug attribute of this Site instance to resolve this conflict."
                )
            count = 0
            location_instances = []

    # Create the remaining locations
    if count < 1000:
        # Handle IntegrityError when Region, Site, Location instances with the same slug.
        try:
            location_class.objects.bulk_create(location_instances, batch_size=1000)
        except IntegrityError as e:
            logger.error(
                f"{e.args[0]} \nPlease consider changing the slug attribute of this Site instance to resolve this conflict."
            )

    # Set existing top level locations to have site locations as their parents
    site_lt_locations = location_class.objects.filter(location_type=site_lt)
    top_level_locations = location_class.objects.filter(site__isnull=False).select_related("site")
    for location in top_level_locations:
        location.parent = site_lt_locations.get(name=location.site.name)
    location_class.objects.bulk_update(top_level_locations, ["parent"], 1000)
    location_type_class.objects.filter(parent__isnull=True).exclude(name=exclude_lt).update(parent=site_lt)


def migrate_site_and_region_data_to_locations(apps, schema_editor):
    """
    Create Location objects based on existing data and move Site related objects to be associated with new Location objects.
    """
    Region = apps.get_model("dcim", "region")
    Site = apps.get_model("dcim", "site")
    LocationType = apps.get_model("dcim", "locationtype")
    Location = apps.get_model("dcim", "location")

    # Region instances exist
    if Region.objects.exists():
        region_lt = LocationType.objects.create(name="Region", nestable=True)
        create_region_location_type_locations(region_class=Region, location_class=Location, region_lt=region_lt)
        if Site.objects.exists():  # Both Site and Region instances exist
            site_lt = LocationType.objects.create(name="Site", parent=LocationType.objects.get(name="Region"))
            if Site.objects.filter(region__isnull=True).exists():
                Location.objects.create(
                    location_type=region_lt,
                    name="Global Region",
                    description="Parent Location of Region LocationType for all sites that "
                    "did not have a region attribute set before the migration",
                )
            create_site_location_type_locations(
                site_class=Site,
                location_type_class=LocationType,
                location_class=Location,
                site_lt=site_lt,
                exclude_lt="Region",
                region_lt=region_lt,
            )
    elif Site.objects.exists():  # Only Site instances exist, we make Site the top level LocationType
        site_lt = LocationType.objects.create(name="Site")
        create_site_location_type_locations(
            site_class=Site,
            location_type_class=LocationType,
            location_class=Location,
            site_lt=site_lt,
            exclude_lt="Site",
        )

    # Reassign Region Models to Locations of Region LocationType
    if Region.objects.exists():
        ContentType = apps.get_model("contenttypes", "ContentType")
        region_ct = ContentType.objects.get_for_model(Region)
        # Config Context
        ConfigContext = apps.get_model("extras", "configcontext")
        ccs = ConfigContext.objects.filter(regions__isnull=False).prefetch_related("locations", "regions")
        for cc in ccs:
            region_name_list = list(cc.regions.all().values_list("name", flat=True))
            region_locs = list(Location.objects.filter(name__in=region_name_list, location_type=region_lt))
            if len(region_locs) < len(region_name_list):
                logger.warning(
                    f'There is a mismatch between the number of Regions ({len(region_name_list)}) and the number of "Region" LocationType locations ({len(region_locs)})'
                    f" found in this ConfigContext {cc.name}"
                )
            cc.locations.add(*region_locs)
            cc.save()

        # Custom Field
        CustomField = apps.get_model("extras", "customfield")
        custom_fields = CustomField.objects.filter(content_types__in=[region_ct])
        for cf in custom_fields:
            cf.content_types.add(ContentType.objects.get_for_model(Location))
            cf.save()

        region_locs = Location.objects.filter(location_type=region_lt).exclude(name="Global Region")
        for location in region_locs:
            region = Region.objects.get(name=location.name)
            location._custom_field_data = region._custom_field_data
        Location.objects.bulk_update(region_locs, ["_custom_field_data"], 1000)

        # Relationship
        Relationship = apps.get_model("extras", "relationship")
        RelationshipAssociation = apps.get_model("extras", "relationshipassociation")
        src_relationships = Relationship.objects.filter(source_type=region_ct)
        for relationship in src_relationships:
            relationship.source_type = ContentType.objects.get_for_model(Location)
            relationship.save()
            relationship_associations = RelationshipAssociation.objects.filter(relationship=relationship)
            relationship_associations.update(source_type=ContentType.objects.get_for_model(Location))
            for relationship_association in relationship_associations:
                src_region = Region.objects.get(id=relationship_association.source_id)
                src_loc = Location.objects.get(name=src_region.name, location_type=region_lt)
                relationship_association.source = src_loc
                relationship_association.source_id = src_loc.pk
                relationship_association.save()

        dst_relationships = Relationship.objects.filter(destination_type=region_ct)
        for relationship in dst_relationships:
            relationship.destination_type = ContentType.objects.get_for_model(Location)
            relationship.save()
            relationship_associations = RelationshipAssociation.objects.filter(relationship=relationship)
            relationship_associations.update(destination_type=ContentType.objects.get_for_model(Location))
            for relationship_association in relationship_associations:
                dst_region = Region.objects.get(id=relationship_association.destination_id)
                dst_loc = Location.objects.get(name=dst_region.name, location_type=region_lt)
                relationship_association.destination = dst_loc
                relationship_association.destination_id = dst_loc.pk
                relationship_association.save()

    # Reassign Site Models to Locations of Site LocationType
    if Site.objects.exists():  # Iff Site instances exist
        CircuitTermination = apps.get_model("circuits", "circuittermination")
        Device = apps.get_model("dcim", "device")
        PowerPanel = apps.get_model("dcim", "powerpanel")
        RackGroup = apps.get_model("dcim", "rackgroup")
        Rack = apps.get_model("dcim", "rack")
        ConfigContext = apps.get_model("extras", "configcontext")
        CustomField = apps.get_model("extras", "customfield")
        Relationship = apps.get_model("extras", "relationship")
        RelationshipAssociation = apps.get_model("extras", "relationshipassociation")
        Prefix = apps.get_model("ipam", "prefix")
        VLANGroup = apps.get_model("ipam", "vlangroup")
        VLAN = apps.get_model("ipam", "vlan")
        Cluster = apps.get_model("virtualization", "cluster")

        ContentType = apps.get_model("contenttypes", "ContentType")
        site_ct = ContentType.objects.get_for_model(Site)
        site_lt.content_types.set(ContentType.objects.filter(FeatureQuery("locations").get_query()))

        cts = CircuitTermination.objects.filter(location__isnull=True).select_related("site")
        for ct in cts:
            ct.location = Location.objects.get(name=ct.site.name, location_type=site_lt)
        CircuitTermination.objects.bulk_update(cts, ["location"], 1000)

        ccs = ConfigContext.objects.filter(sites__isnull=False).prefetch_related("locations", "sites")
        for cc in ccs:
            site_name_list = list(cc.sites.all().values_list("name", flat=True))
            site_locs = list(Location.objects.filter(name__in=site_name_list, location_type=site_lt))
            if len(site_locs) < len(site_name_list):
                logger.warning(
                    f'There is a mismatch between the number of Sites ({len(site_name_list)}) and the number of "Site" LocationType locations ({len(site_locs)})'
                    f" found in this ConfigContext {cc.name}"
                )
            cc.locations.add(*site_locs)
            cc.save()

        # Custom Field
        CustomField = apps.get_model("extras", "customfield")
        custom_fields = CustomField.objects.filter(content_types__in=[ContentType.objects.get_for_model(Site)])
        for cf in custom_fields:
            cf.content_types.add(ContentType.objects.get_for_model(Location))
            cf.save()

        site_locs = Location.objects.filter(location_type=site_lt)
        for location in site_locs:
            site = Site.objects.get(name=location.name)
            location._custom_field_data = site._custom_field_data
        Location.objects.bulk_update(site_locs, ["_custom_field_data"], 1000)

        # Relationship
        src_relationships = Relationship.objects.filter(source_type=site_ct)
        for relationship in src_relationships:
            relationship.source_type = ContentType.objects.get_for_model(Location)
            relationship.save()
            relationship_associations = RelationshipAssociation.objects.filter(relationship=relationship)
            relationship_associations.update(source_type=ContentType.objects.get_for_model(Location))
            for relationship_association in relationship_associations:
                src_site = Site.objects.get(id=relationship_association.source_id)
                src_loc = Location.objects.get(name=src_site.name, location_type=site_lt)
                relationship_association.source = src_loc
                relationship_association.source_id = src_loc.id
                relationship_association.save()

        dst_relationships = Relationship.objects.filter(destination_type=site_ct)
        for relationship in dst_relationships:
            relationship.destination_type = ContentType.objects.get_for_model(Location)
            relationship.save()
            relationship_associations = RelationshipAssociation.objects.filter(relationship=relationship)
            relationship_associations.update(destination_type=ContentType.objects.get_for_model(Location))
            for relationship_association in relationship_associations:
                dst_site = Site.objects.get(id=relationship_association.destination_id)
                dst_loc = Location.objects.get(name=dst_site.name, location_type=site_lt)
                relationship_association.destination = dst_loc
                relationship_association.destination_id = dst_loc.pk
                relationship_association.save()

        devices = Device.objects.filter(location__isnull=True).select_related("site")
        for device in devices:
            device.location = Location.objects.get(name=device.site.name, location_type=site_lt)
        Device.objects.bulk_update(devices, ["location"], 1000)

        powerpanels = PowerPanel.objects.filter(location__isnull=True).select_related("site")
        for powerpanel in powerpanels:
            powerpanel.location = Location.objects.get(name=powerpanel.site.name, location_type=site_lt)
        PowerPanel.objects.bulk_update(powerpanels, ["location"], 1000)

        rackgroups = RackGroup.objects.filter(location__isnull=True).select_related("site")
        for rackgroup in rackgroups:
            rackgroup.location = Location.objects.get(name=rackgroup.site.name, location_type=site_lt)
        RackGroup.objects.bulk_update(rackgroups, ["location"], 1000)

        racks = Rack.objects.filter(location__isnull=True).select_related("site")
        for rack in racks:
            rack.location = Location.objects.get(name=rack.site.name, location_type=site_lt)
        Rack.objects.bulk_update(racks, ["location"], 1000)

        # Below models' site attribute is not required, so we need to check each instance if the site field is not null
        # if so we reassign it to Site Location and if not we leave it alone

        prefixes = Prefix.objects.filter(location__isnull=True, site__isnull=False).select_related("site")
        for prefix in prefixes:
            prefix.location = Location.objects.get(name=prefix.site.name, location_type=site_lt)
        Prefix.objects.bulk_update(prefixes, ["location"], 1000)

        vlangroups = VLANGroup.objects.filter(location__isnull=True, site__isnull=False).select_related("site")
        for vlangroup in vlangroups:
            vlangroup.location = Location.objects.get(name=vlangroup.site.name, location_type=site_lt)
        VLANGroup.objects.bulk_update(vlangroups, ["location"], 1000)

        vlans = VLAN.objects.filter(location__isnull=True, site__isnull=False).select_related("site")
        for vlan in vlans:
            vlan.location = Location.objects.get(name=vlan.site.name, location_type=site_lt)
        VLAN.objects.bulk_update(vlans, ["location"], 1000)

        clusters = Cluster.objects.filter(location__isnull=True, site__isnull=False).select_related("site")
        for cluster in clusters:
            cluster.location = Location.objects.get(name=cluster.site.name, location_type=site_lt)
        Cluster.objects.bulk_update(clusters, ["location"], 1000)


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0029_change_tree_manager_on_tree_models"),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_site_and_region_data_to_locations,
            reverse_code=migrations.operations.special.RunPython.noop,
        ),
    ]
