import logging

from django.contrib.auth.backends import BaseBackend

from scim_importer.models import ScimClient

logger = logging.getLogger(__name__)


class ScimClientBackend(BaseBackend):
    """
    Authenticates against ScimClient.
    """

    def authenticate(self, request, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        logger.info("auth_header: %s", auth_header)
        if not auth_header:
            return None

        try:
            auth_mode, token = auth_header.split(" ")
        except (IndexError, ValueError) as err:
            logger.error("Invalid auth header: %s", err)
            return None

        if auth_mode.lower() != "bearer" or not token:
            logger.error("Invalid auth header: %s", auth_header)
            return None

        try:
            scim_client = ScimClient.objects.get(token=token)
        except ScimClient.DoesNotExist:
            logger.warning("Invalid token: %s", token)
            return None

        logger.info("scim_client: %s", scim_client)
        return scim_client

    async def aauthenticate(self, request, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        logger.info("auth_header: %s", auth_header)
        if not auth_header:
            return None

        try:
            auth_mode, token = auth_header.split(" ")
        except (IndexError, ValueError) as err:
            logger.error("Invalid auth header: %s", err)
            return None

        if auth_mode.lower() != "bearer" or not token:
            logger.error("Invalid auth header: %s", auth_header)
            return None

        try:
            scim_client = await ScimClient.objects.aget(token=token)
        except ScimClient.DoesNotExist:
            logger.warning("Invalid token: %s", token)
            return None

        logger.info("scim_client: %s", scim_client)
        return scim_client

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return user.is_active

    def get_user(self, user_id):
        try:
            user = ScimClient.objects.get(pk=user_id)
        except ScimClient.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

    async def aget_user(self, user_id):
        try:
            user = await ScimClient.objects.aget(pk=user_id)
        except ScimClient.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
