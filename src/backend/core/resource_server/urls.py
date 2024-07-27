"""Resource Server URL Configuration"""

from django.urls import path

from .views import JWKSView

urlpatterns = [
    path("jwks", JWKSView.as_view(), name="resource_server_jwks"),
]
