"""URLs for the mailbox_oauth2 app."""

from django.urls import path

from .views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="api_login"),
]
