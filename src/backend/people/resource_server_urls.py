"""Resource server API URL Configuration"""

from django.urls import include, path

from lasuite.oidc_resource_server.urls import urlpatterns as resource_server_urls
from rest_framework.routers import SimpleRouter

from core.api.resource_server import viewsets
from core.api.resource_server.scim import viewsets as scim_viewsets

# - Main endpoints
# Contacts will be added later
# Users will be added later
router = SimpleRouter()
router.register("teams", viewsets.TeamViewSet, basename="teams")

# - SCIM endpoints
scim_router = SimpleRouter()
scim_router.register("Me", scim_viewsets.MeViewSet, basename="scim-me")

# - Routes nested under a team
team_related_router = SimpleRouter()
team_related_router.register(
    "invitations",
    viewsets.InvitationViewset,
    basename="invitations",
)


# - Routes nested under a team
# Invitations will be added later

urlpatterns = [
    path(
        "resource-server/v1.0/",
        include(
            [
                *router.urls,
                *resource_server_urls,
                path("teams/<uuid:team_id>/", include(team_related_router.urls)),
                path("scim/", include(scim_router.urls)),
            ]
        ),
    ),
]
