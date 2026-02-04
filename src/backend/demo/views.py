"""Views for demo application."""

from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import TokenExchangeDemoForm


class TokenExchangeDemoView(TemplateView):
    """Demo view to help test token exchange flows."""

    template_name = "demo/token_exchange_form.html"
    form_class = TokenExchangeDemoForm
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        """Add form and token exchange URL to the context."""
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(
            initial={
                "client_id": "client_id",
                "client_secret": "client_secret",
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "subject_token": self.request.session.get("oidc_access_token"),
                "requested_token_type": "urn:ietf:params:oauth:token-type:jwt",
            }
        )
        context["token_exchange_url"] = reverse_lazy("token-exchange")
        return context
