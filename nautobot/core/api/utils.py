import platform
import sys

from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status
from rest_framework.utils import formatting

from nautobot.core.api import exceptions
from nautobot.core.api.serializers import BaseModelSerializer
from nautobot.core.utils import utils


def get_serializer_for_model(model, prefix=""):
    """
    Dynamically resolve and return the appropriate serializer for a model.
    """
    app_name, model_name = model._meta.label.split(".")
    # Serializers for Django's auth models are in the users app
    if app_name == "auth":
        app_name = "users"
    serializer_name = f"{app_name}.api.serializers.{prefix}{model_name}Serializer"
    if app_name not in settings.PLUGINS:
        serializer_name = f"nautobot.{serializer_name}"
    try:
        return utils.dynamic_import(serializer_name)
    except AttributeError:
        raise exceptions.SerializerNotFound(
            f"Could not determine serializer for {app_name}.{model_name} with prefix '{prefix}'"
        )


def is_api_request(request):
    """
    Return True of the request is being made via the REST API.
    """
    api_path = reverse("api-root")
    return request.path_info.startswith(api_path)


def get_view_name(view, suffix=None):
    """
    Derive the view name from its associated model, if it has one. Fall back to DRF's built-in `get_view_name`.
    """
    if hasattr(view, "queryset"):
        # Determine the model name from the queryset.
        name = view.queryset.model._meta.verbose_name
        name = " ".join([w[0].upper() + w[1:] for w in name.split()])  # Capitalize each word

    else:
        # Replicate DRF's built-in behavior.
        name = view.__class__.__name__
        name = formatting.remove_trailing_string(name, "View")
        name = formatting.remove_trailing_string(name, "ViewSet")
        name = formatting.camelcase_to_spaces(name)

    if suffix:
        name += " " + suffix

    return name


def rest_api_server_error(request, *args, **kwargs):
    """
    Handle exceptions and return a useful error message for REST API requests.
    """
    type_, error, _traceback = sys.exc_info()
    data = {
        "error": str(error),
        "exception": type_.__name__,
        "nautobot_version": settings.VERSION,
        "python_version": platform.python_version(),
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TreeModelSerializerMixin(BaseModelSerializer):
    """Add a `tree_depth` field to model serializers based on django-tree-queries."""

    tree_depth = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_tree_depth(self, obj):
        """The `tree_depth` is not a database field, but an annotation automatically added by django-tree-queries."""
        return getattr(obj, "tree_depth", None)