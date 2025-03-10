"""Debug Views to check the layout of emails"""

from django.views.generic.base import TemplateView


class DebugBaseView(TemplateView):
    """Debug View to check the layout of emails"""

    def get_context_data(self, **kwargs):
        """Generates sample datas to have a valid debug email"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Development email preview"
        return context


# TEAM INVITATION
class DebugViewTeamInvitationBase(DebugBaseView):
    """Debug view for team invitation base email layout"""

    def get_context_data(self, **kwargs):
        """Add some fake context data for team invitation email layout"""
        context = super().get_context_data(**kwargs)
        context["team"] = "example team"
        context["role"] = "owner"
        return context


class DebugViewTeamInvitationHtml(DebugViewTeamInvitationBase):
    """Debug view for team invitation html email layout"""

    template_name = "mail/html/team_invitation.html"


class DebugViewTeamInvitationTxt(DebugViewTeamInvitationBase):
    """Debug view for team invitation text email layout"""

    template_name = "mail/text/team_invitation.txt"


# MAIL DOMAIN INVITATION
class DebugViewMaildomainInvitationBase(DebugBaseView):
    """Debug view for mail domain invitation base email layout"""

    def get_context_data(self, **kwargs):
        """Add some fake context data for mail domain invitation email layout"""
        context = super().get_context_data(**kwargs)
        context["domain"] = "example.com"
        context["role"] = "owner"
        return context


class DebugViewMaildomainInvitationHtml(DebugViewMaildomainInvitationBase):
    """Debug view for mail domain invitation html email layout"""

    template_name = "mail/html/maildomain_invitation.html"


class DebugViewMaildomainInvitationTxt(DebugViewMaildomainInvitationBase):
    """Debug view for mail domain invitation text email layout"""

    template_name = "mail/text/maildomain_invitation.txt"


# NEW MAILBOX
class DebugViewNewMailboxHtml(DebugBaseView):
    """Debug view for new mailbox email layout"""

    template_name = "mail/html/new_mailbox.html"

    def get_context_data(self, **kwargs):
        """Hardcode user credentials for debug setting."""
        context = super().get_context_data(**kwargs)
        context["mailbox_data"] = {
            "email": "john.doe@example.com",
            "password": "6HGVAsjoog_v",
        }
        return context
