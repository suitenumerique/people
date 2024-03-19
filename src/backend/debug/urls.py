"""Debug Urls to check the layout of emails"""

from django.urls import path

from .views import (
    DebugViewHtml,
    DebugViewTxt,
)

urlpatterns = [
    path(
        "__debug__/mail/hello_html",
        DebugViewHtml.as_view(),
        name="debug.mail.hello_html",
    ),
    path(
        "__debug__/mail/hello_txt",
        DebugViewTxt.as_view(),
        name="debug.mail.hello_txt",
    ),
]
