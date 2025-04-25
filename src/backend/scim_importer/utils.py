from django.apps import apps as django_apps
from django.contrib.auth import get_user_model


def get_scim_importer_user_model():
    """
    Return the user model that is used for SCIM import.
    """
    return django_apps.get_model("scim_importer.ScimImportedUser", require_ready=False)


def default_get_extra_model_filter_kwargs_getter(model):
    """
    Return a **method** that will return extra model filter kwargs for the passed in model.

    :param model:
    """

    if model is get_user_model():

        def get_extra_filter_kwargs(request, *args, **kwargs):
            """
            Return extra filter kwargs for the given model.
            :param request:
            :param args:
            :param kwargs:
            :rtype: dict
            """
            return {
                "scim_id__isnull": False,
            }

        return get_extra_filter_kwargs

    def get_extra_filter_kwargs(request, *args, **kwargs):
        """
        Return extra filter kwargs for the given model.
        :param request:
        :param args:
        :param kwargs:
        :rtype: dict
        """
        return {}

    return get_extra_filter_kwargs
