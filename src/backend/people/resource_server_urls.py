"""Resource server API URL Configuration"""

from django.urls import include, path

from lasuite.oidc_resource_server.urls import urlpatterns as resource_server_urls
from rest_framework.routers import SimpleRouter

from core.api.resource_server.scim import viewsets as scim_viewsets

# - SCIM endpoints
scim_router = SimpleRouter()
scim_router.register("Me", scim_viewsets.MeViewSet, basename="scim-me")


urlpatterns = [
    path(
        "resource-server/v1.0/",
        include(
            [
                *resource_server_urls,
                path("scim/", include(scim_router.urls)),
            ]
        ),
    ),
]
