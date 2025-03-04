"""Resource server API URL Configuration"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from core.api.resource_server import viewsets
from core.resource_server.urls import urlpatterns as resource_server_urls

# - Main endpoints
# Contacts will be added later
# Users will be added later
router = DefaultRouter()
router.register("teams", viewsets.TeamViewSet, basename="teams")

# - Routes nested under a team
team_related_router = DefaultRouter()
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
            ]
        ),
    ),
]
