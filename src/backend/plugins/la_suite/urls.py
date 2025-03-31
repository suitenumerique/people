"""API URL Configuration for La Suite plugin"""

from rest_framework.routers import DefaultRouter

from .api.viewsets import ActiveOrganizationsSiret

router = DefaultRouter()
router.register(
    "la-suite/v1.0/siret",
    ActiveOrganizationsSiret,
    basename="active-organization-sirets",
)

urlpatterns = router.urls
