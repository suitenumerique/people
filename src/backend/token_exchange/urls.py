"""URL configuration for the token_exchange application."""

from django.urls import path

from .views import TokenExchangeView, TokenIntrospectionView, TokenRevocationView

urlpatterns = [
    path("token/exchange/", TokenExchangeView.as_view(), name="token-exchange"),
    path(
        "token/introspect/", TokenIntrospectionView.as_view(), name="token-introspect"
    ),
    path("token/revoke/", TokenRevocationView.as_view(), name="token-revoke"),
]
