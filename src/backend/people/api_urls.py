"""API URL Configuration"""

from django.conf import settings
from django.urls import include, path

from lasuite.oidc_login.urls import urlpatterns as oidc_urls
from lasuite.oidc_resource_server.urls import urlpatterns as resource_server_urls
from rest_framework.routers import DefaultRouter

from core.api.client import viewsets

# - Main endpoints
router = DefaultRouter()
router.register("organizations", viewsets.OrganizationViewSet, basename="organizations")
router.register("users", viewsets.UserViewSet, basename="users")
router.register(
    "service-providers", viewsets.ServiceProviderViewSet, basename="service-providers"
)


urlpatterns = [
    path(
        f"api/{settings.API_VERSION}/",
        include(
            [
                *router.urls,
                *oidc_urls,
                *resource_server_urls,
            ]
        ),
    ),
    path(f"api/{settings.API_VERSION}/", include("mailbox_manager.urls")),
    path(f"api/{settings.API_VERSION}/config/", viewsets.ConfigView.as_view()),
    path(f"api/{settings.API_VERSION}/stats/", viewsets.StatView.as_view()),
]
