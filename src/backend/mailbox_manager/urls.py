"""API URL Configuration"""

from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from mailbox_manager.api.client import viewsets

maildomain_router = DefaultRouter()
maildomain_router.register(
    "mail-domains", viewsets.MailDomainViewSet, basename="mail-domains"
)

# - Routes nested under a mail domain
maildomain_related_router = DefaultRouter()
maildomain_related_router.register(
    "accesses",
    viewsets.MailDomainAccessViewSet,
    basename="accesses",
)
maildomain_related_router.register(
    "mailboxes",
    viewsets.MailBoxViewSet,
    basename="mailboxes",
)

maildomain_related_router.register(
    "invitations",
    viewsets.MailDomainInvitationViewset,
    basename="invitations",
)


urlpatterns = [
    path(
        "",
        include(
            [
                *maildomain_router.urls,
                re_path(
                    r"^mail-domains/(?P<domain_slug>[\w-]+)/",
                    include(maildomain_related_router.urls),
                ),
            ]
        ),
    ),
]
