"""Debug Urls to check the layout of emails"""

from django.urls import path

from .views import (
    DebugViewHtml,
    DebugViewNewMailboxHtml,
    DebugViewTxt,
)

urlpatterns = [
    path(
        "__debug__/mail/invitation_html",
        DebugViewHtml.as_view(),
        name="debug.mail.invitation_html",
    ),
    path(
        "__debug__/mail/invitation_txt",
        DebugViewTxt.as_view(),
        name="debug.mail.invitation_txt",
    ),
    path(
        "__debug__/mail/new_mailbox_html",
        DebugViewNewMailboxHtml.as_view(),
        name="debug.mail.new_mailbox_html",
    ),
]
