"""API URL Configuration for La Suite plugin"""

from rest_framework.routers import DefaultRouter

from .api.viewsets import ActiveOrganizationsSiret, OrganizationActivation

app_name = "la-suite"

router = DefaultRouter()
router.register(
    "la-suite/v1.0/siret",
    ActiveOrganizationsSiret,
    basename="active-organization-sirets",
)
router.register(
    "la-suite/v1.0",
    OrganizationActivation,
    basename="organizations",
)

urlpatterns = router.urls
