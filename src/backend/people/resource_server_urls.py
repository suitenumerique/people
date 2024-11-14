"""Resource server API URL Configuration"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from core.resource_server.urls import urlpatterns as resource_server_urls
from core.resource_server_api import viewsets

# - Main endpoints
# Contacts will be added later
# Users will be added later
router = DefaultRouter()
router.register("teams", viewsets.TeamViewSet, basename="teams")


# - Routes nested under a team
# Invitations will be added later

urlpatterns = [
    path(
        "resource-server/v1.0/",
        include(
            [
                *router.urls,
                *resource_server_urls,
            ]
        ),
    ),
]
