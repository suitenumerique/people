"""
Tests for aliases API endpoint in People's app mailbox_manager.
Focus on "bulk delete" action.
"""
# pylint: disable=W0613

import re

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from core import factories as core_factories

from mailbox_manager import enums, factories, models

pytestmark = pytest.mark.django_db


def test_api_aliases_bulk_delete__anonymous_get_401():
    """Anonymous user should not be able to bulk delete."""
    mail_domain = factories.MailDomainFactory()
    alias_, _, _ = factories.AliasFactory.create_batch(3, domain=mail_domain)

    client = APIClient()
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/?local_part={alias_.local_part}",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert models.Alias.objects.count() == 3


def test_api_aliases_bulk_delete__no_access_get_404():
    """User with no access to domain should not be able to bulk delete."""
    mail_domain = factories.MailDomainFactory()
    alias_, _, _ = factories.AliasFactory.create_batch(3, domain=mail_domain)

    client = APIClient()
    client.force_login(core_factories.UserFactory())
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/?local_part={alias_.local_part}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert models.Alias.objects.count() == 3


def test_api_aliases_bulk_delete__viewer_get_403():
    """Viewer user should not be able to bulk delete."""
    access = factories.MailDomainAccessFactory(role=enums.MailDomainRoleChoices.VIEWER)
    alias_, _, _ = factories.AliasFactory.create_batch(3, domain=access.domain)

    client = APIClient()
    client.force_login(access.user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{access.domain.slug}/aliases/?local_part={alias_.local_part}",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert models.Alias.objects.count() == 3


@responses.activate
def test_api_aliases_bulk_delete__administrators_allowed_all_destination(
    dimail_token_ok,
):
    """
    Administrators of a domain should be allowed to bulk delete all aliases
    of a given local_part.
    """
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    alias_ = factories.AliasFactory(domain=mail_domain)
    factories.AliasFactory.create_batch(
        2, domain=mail_domain, local_part=alias_.local_part
    )

    # additional aliases that shouldn't be affected
    factories.AliasFactory.create_batch(
        2, domain=mail_domain, destination=alias_.destination
    )
    factories.AliasFactory(
        local_part=alias_.local_part,
        destination=alias_.destination,
    )

    # Mock dimail response
    responses.delete(
        re.compile(r".*/aliases/"),
        status=status.HTTP_204_NO_CONTENT,
        content_type="application/json",
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/?local_part={alias_.local_part}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert models.Alias.objects.count() == 3
    assert not models.Alias.objects.filter(
        domain=mail_domain, local_part=alias_.local_part
    ).exists()


def test_api_aliases_bulk_delete__no_local_part_bad_request():
    """Filtering by local part is mandatory when bulk deleting aliases."""
    authenticated_user = core_factories.UserFactory()
    mail_domain = factories.MailDomainFactory(
        users=[(authenticated_user, enums.MailDomainRoleChoices.ADMIN)]
    )
    alias_ = factories.AliasFactory(domain=mail_domain)
    factories.AliasFactory.create_batch(
        2, domain=mail_domain, local_part=alias_.local_part
    )

    client = APIClient()
    client.force_login(authenticated_user)
    response = client.delete(
        f"/api/v1.0/mail-domains/{mail_domain.slug}/aliases/",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert models.Alias.objects.count() == 3
