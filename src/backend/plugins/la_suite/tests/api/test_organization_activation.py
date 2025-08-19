"""Test the organization activation API."""

import re

from django.urls import reverse

import pytest
import responses
from rest_framework import status
from rest_framework.test import APIClient

from mailbox_manager import factories as mailbox_factories
from mailbox_manager import models as mailbox_models
from mailbox_manager.tests.fixtures.dimail import (
    TOKEN_OK,
    response_mailbox_created,
)
from plugins.la_suite import factories

pytestmark = pytest.mark.django_db


API_URL = reverse("la-suite:organizations-activate-organization")


# pylint: disable=unused-argument
def test_organization_activation_unauthorized(plugin_urls):
    """Test the organization activation API unauthorized"""
    client = APIClient()
    response = client.post(API_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# pylint: disable=unused-argument
@responses.activate
def test_organization_activation_authorized(plugin_urls):
    """Test the organization activation API authorized"""
    # create one-time token for mailbox provisioning
    token = factories.OrganizationOneTimeTokenFactory()
    organization = token.organization

    # create domain linked to organization
    domain = mailbox_factories.MailDomainEnabledFactory(
        organization=organization, name="example.com"
    )

    # mailbox data to be used in API call to create the firstmailbox
    mailbox_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email_local_part": "john.doe",
        "password": "password1234",
    }

    # mock dimail API call for mailbox creation
    responses.add(
        responses.GET,
        re.compile(r".*/token/"),
        body=TOKEN_OK,
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        re.compile(rf".*/domains/{domain.name}/mailboxes/"),
        body=response_mailbox_created(
            f"{mailbox_data['email_local_part']}@{domain.name}"
        ),
        status=status.HTTP_201_CREATED,
        content_type="application/json",
    )

    # call API
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"OrganizationToken {token.key}")
    response = client.post(API_URL, data=mailbox_data)
    assert response.status_code == status.HTTP_201_CREATED

    # check organization is activated
    organization.refresh_from_db()
    assert organization.is_active

    # check user is created
    mailbox = mailbox_models.Mailbox.objects.get()
    assert mailbox.first_name == "John"
    assert mailbox.last_name == "Doe"
    assert mailbox.local_part == "john.doe"
    assert mailbox.domain == domain
    assert mailbox.password

    # check one-time token is disabled
    token.refresh_from_db()
    assert token.enabled is False
