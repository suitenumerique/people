"""
Unit tests for admin actions
"""

import json
import re

from django.urls import reverse

import pytest
import responses

from core import factories as core_factories

from mailbox_manager import enums, factories

from .fixtures.dimail import CHECK_DOMAIN_BROKEN, CHECK_DOMAIN_OK


@pytest.mark.django_db
def test_admin_action__fetch_domain_status_from_dimail(client):
    """Test admin action to check health of some domains"""
    admin = core_factories.UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    domain1 = factories.MailDomainEnabledFactory()
    domain2 = factories.MailDomainEnabledFactory()
    data = {
        "action": "fetch_domain_status_from_dimail",
        "_selected_action": [
            domain1.id,
            domain2.id,
        ],
    }
    url = reverse("admin:mailbox_manager_maildomain_changelist")

    with responses.RequestsMock() as rsps:
        body_content_domain1 = CHECK_DOMAIN_BROKEN.copy()
        body_content_domain1["name"] = domain1.name
        body_content_domain2 = CHECK_DOMAIN_BROKEN.copy()
        body_content_domain2["name"] = domain2.name
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain1.name}/check/"),
            body=json.dumps(body_content_domain1),
            status=200,
            content_type="application/json",
        )
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain2.name}/check/"),
            body=json.dumps(body_content_domain2),
            status=200,
            content_type="application/json",
        )
        response = client.post(url, data, follow=True)
        assert response.status_code == 200
        domain1.refresh_from_db()
        domain2.refresh_from_db()
        assert domain1.status == enums.MailDomainStatusChoices.FAILED
        assert domain2.status == enums.MailDomainStatusChoices.FAILED
        assert "Check domains done with success" in response.content.decode("utf-8")

        # check with a valid domain info from dimail
        body_content_domain1 = CHECK_DOMAIN_OK.copy()
        body_content_domain1["name"] = domain1.name
        rsps.add(
            rsps.GET,
            re.compile(rf".*/domains/{domain1.name}/check/"),
            body=json.dumps(body_content_domain1),
            status=200,
            content_type="application/json",
        )
        response = client.post(url, data, follow=True)
        assert response.status_code == 200
        domain1.refresh_from_db()
        domain2.refresh_from_db()
        assert domain1.status == enums.MailDomainStatusChoices.ENABLED
        assert domain2.status == enums.MailDomainStatusChoices.FAILED
        assert "Check domains done with success" in response.content.decode("utf-8")
