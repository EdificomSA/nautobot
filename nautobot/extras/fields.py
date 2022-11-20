from functools import partialmethod

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable

from nautobot.utilities.forms import DynamicModelChoiceField


class LimitedChoiceField(models.ForeignKey):
    """
    Abstract model database field that automatically limits custom choices.

    The limit_choices_to for the field are automatically derived from:

        - the content-type to which the field is attached (e.g. `dcim.device`)
    """

    def __init__(self, **kwargs):
        kwargs.update(self.set_defaults(**kwargs))
        super().__init__(**kwargs)

    def set_defaults(self, **kwargs):
        """Set defaults of kwargs in class __init__ method.

        Override this method to set __init__ kwargs
        """
        kwargs.setdefault("null", True)

        return kwargs

    def get_limit_choices_to(self):
        return {"content_types": ContentType.objects.get_for_model(self.model)}

    def contribute_to_class(self, cls, name, *args, private_only=False, **kwargs):
        """
        Overload default so that we can assert that `.get_FOO_display` is
        attached to any model that is using a `LimitedChoiceField`.

        Using `.contribute_to_class()` is how field objects get added to the model
        at during the instance preparation. This is also where any custom model
        methods are hooked in. So in short this method asserts that any time a
        `LimitedChoiceField` is added to a model, that model also gets a
        `.get_`self.name`_display()` and a `.get_`self.name`_color()` method without
        having to define it on the model yourself.
        """
        super().contribute_to_class(cls, name, *args, private_only=private_only, **kwargs)

        def _get_FIELD_display(self, field):
            """
            Closure to replace default model method of the same name.

            Cargo-culted from `django.db.models.base.Model._get_FIELD_display`
            """
            choices = field.get_choices()
            value = getattr(self, field.attname)
            choices_dict = dict(make_hashable(choices))
            # force_str() to coerce lazy strings.
            return force_str(choices_dict.get(make_hashable(value), value), strings_only=True)

        # Install `.get_FOO_display()` onto the model using our own version.
        if f"get_{self.name}_display" not in cls.__dict__:
            setattr(
                cls,
                f"get_{self.name}_display",
                partialmethod(_get_FIELD_display, field=self),
            )

        def _get_FIELD_color(self, field):
            """
            Return `self.FOO.color` (where FOO is field name).

            I am added to the model via `LimitedChoiceField.contribute_to_class()`.
            """
            field_method = getattr(self, field.name)
            return getattr(field_method, "color")

        # Install `.get_FOO_color()` onto the model using our own version.
        if f"get_{self.name}_color" not in cls.__dict__:
            setattr(
                cls,
                f"get_{self.name}_color",
                partialmethod(_get_FIELD_color, field=self),
            )

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": self.model._meta.label_lower},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)