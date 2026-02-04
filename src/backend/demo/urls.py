"""URL configuration for the demo helpers."""

from django.urls import path

from .views import TokenExchangeDemoView

app_name = "demo"

urlpatterns = [
    path(
        "token-exchange/",
        TokenExchangeDemoView.as_view(),
        name="token-exchange-demo",
    ),
]
