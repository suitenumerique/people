"""API URL Configuration"""

from django.conf import settings
from django.urls import include, path, re_path

from lasuite.oidc_login.urls import urlpatterns as oidc_urls
from lasuite.oidc_resource_server.urls import urlpatterns as resource_server_urls
from rest_framework.routers import DefaultRouter

from core.api.client import viewsets

from mailbox_oauth2.urls import urlpatterns as mailbox_oauth2_urls

# - Main endpoints
router = DefaultRouter()
router.register("contacts", viewsets.ContactViewSet, basename="contacts")
router.register("organizations", viewsets.OrganizationViewSet, basename="organizations")
router.register("teams", viewsets.TeamViewSet, basename="teams")
router.register("users", viewsets.UserViewSet, basename="users")
router.register(
    "service-providers", viewsets.ServiceProviderViewSet, basename="service-providers"
)

# - Routes nested under a team
team_related_router = DefaultRouter()
team_related_router.register(
    "accesses",
    viewsets.TeamAccessViewSet,
    basename="team_accesses",
)

team_related_router.register(
    "invitations",
    viewsets.InvitationViewset,
    basename="invitations",
)


urlpatterns = [
    path(
        f"api/{settings.API_VERSION}/",
        include(
            [
                *router.urls,
                *mailbox_oauth2_urls,
                *oidc_urls,
                *resource_server_urls,
                re_path(
                    r"^teams/(?P<team_id>[0-9a-z-]*)/",
                    include(team_related_router.urls),
                ),
            ]
        ),
    ),
    path(f"api/{settings.API_VERSION}/", include("mailbox_manager.urls")),
    path(f"api/{settings.API_VERSION}/config/", viewsets.ConfigView.as_view()),
    path(f"api/{settings.API_VERSION}/stats/", viewsets.StatView.as_view()),
]
