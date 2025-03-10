"""Debug Urls to check the layout of emails"""

from django.urls import path

from .views import (
    DebugViewMaildomainInvitationHtml,
    DebugViewMaildomainInvitationTxt,
    DebugViewNewMailboxHtml,
    DebugViewTeamInvitationHtml,
    DebugViewTeamInvitationTxt,
)

urlpatterns = [
    path(
        "__debug__/mail/team_invitation_html",
        DebugViewTeamInvitationHtml.as_view(),
        name="debug.mail.team_invitation_html",
    ),
    path(
        "__debug__/mail/team_invitation_txt",
        DebugViewTeamInvitationTxt.as_view(),
        name="debug.mail.team_invitation_txt",
    ),
    path(
        "__debug__/mail/new_mailbox_html",
        DebugViewNewMailboxHtml.as_view(),
        name="debug.mail.new_mailbox_html",
    ),
    path(
        "__debug__/mail/maildomain_invitation_txt",
        DebugViewMaildomainInvitationTxt.as_view(),
        name="debug.mail.maildomain_invitation_txt",
    ),
    path(
        "__debug__/mail/maildomain_invitation_html",
        DebugViewMaildomainInvitationHtml.as_view(),
        name="debug.mail.maildomain_invitation_html",
    ),
]
