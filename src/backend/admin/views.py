"""Custom admin views for the People app."""

from smtplib import SMTPException

from django.views.generic import TemplateView


class BaseSelftestAdminPageView(TemplateView):
    """Base class for selftest admin pages."""

    is_index = False
    template_name = "selftest/base.html"
    title = "Selftest Admin Page"  # should be overridden in subclasses
    path = None

    def get_context_data(self, **kwargs):
        """Add the title to the context."""
        context = super().get_context_data(**kwargs)

        context["title"] = self.title
        return context


class IndexSelftestAdminPageView(BaseSelftestAdminPageView):
    """View for the selftest index page."""

    template_name = "selftest/index.html"
    is_index = True
    title = "Selftest Admin Index Page"
    path = ""

    def get_context_data(self, **kwargs):
        """Add all registered views to the context."""
        from .registry import view_registry  # pylint: disable=import-outside-toplevel

        context = super().get_context_data(**kwargs)
        context["pages"] = [
            {
                "title": view["title"],
                "url_name": view["name"],
            }
            for view in sorted(
                [
                    view
                    for view in view_registry.get_views()
                    if not view["view_class"].is_index
                ],
                key=lambda x: x["name"],
            )
        ]
        return context


class EmailSelftestAdminPageView(BaseSelftestAdminPageView):
    """View for testing email functionality."""

    title = "Send test email"
    template_name = "selftest/email.html"
    path = "email/"

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        context = self.get_context_data(**kwargs)
        context["form"] = {"email": ""}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Handle POST request to send test email."""
        from django.contrib import messages
        from django.core.mail import send_mail

        context = self.get_context_data(**kwargs)
        email = request.POST.get("email", "")

        if email:
            try:
                send_mail(
                    subject="Test Email from People Admin",
                    message="This is a test email from the People Admin site.",
                    from_email=None,  # Use DEFAULT_FROM_EMAIL
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f"Test email sent successfully to {email}")
            except SMTPException as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        else:
            messages.error(request, "Please provide an email address")

        context["form"] = {"email": email}
        return self.render_to_response(context)
