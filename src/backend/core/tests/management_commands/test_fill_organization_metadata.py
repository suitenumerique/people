"""Tests for the fill_organization_metadata management command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

import pytest

from core import factories

pytestmark = pytest.mark.django_db


@pytest.fixture(name="command_output")
def command_output_fixture():
    """Capture command output."""
    out = StringIO()
    return out


@pytest.mark.django_db
def test_fill_organization_metadata_no_schema(command_output):
    """Test command behavior when no schema is available."""
    organization_1 = factories.OrganizationFactory(
        name="Org with empty metadata",
        metadata={},
        with_registration_id=True,
    )
    organization_2 = factories.OrganizationFactory(
        name="Org with partial metadata",
        metadata={"existing_key": "existing_value"},
        with_registration_id=True,
    )

    # Mock the schema function to return None (no schema)
    with patch("core.models.get_organization_metadata_schema") as mock_get_schema:
        mock_get_schema.return_value = None

        # Call the command
        call_command("fill_organization_metadata", stdout=command_output)

    # Check the command output
    assert "No organization metadata schema defined" in command_output.getvalue()

    organization_1.refresh_from_db()
    assert organization_1.metadata == {}

    organization_2.refresh_from_db()
    assert organization_2.metadata == {"existing_key": "existing_value"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "existing_metadata,expected_result",
    [
        ({}, {"field1": "default_value"}),  # Empty metadata gets defaults
        ({"field1": "custom"}, {"field1": "custom"}),  # Existing values preserved
        (
            {"other_field": "value"},
            {"other_field": "value", "field1": "default_value"},
        ),  # Mixed case
    ],
)
def test_metadata_merging_scenarios(existing_metadata, expected_result):
    """Test various metadata merging scenarios."""
    # Create a simple schema with one field
    simple_schema = {
        "type": "object",
        "properties": {
            "field1": {"type": "string", "default": "default_value"},
        },
    }

    # Create an organization with the specified metadata
    organization = factories.OrganizationFactory(
        name="Test organization",
        metadata=existing_metadata,
        with_registration_id=True,
    )

    # Mock the schema function to return our simple schema
    with patch("core.models.get_organization_metadata_schema") as mock_get_schema:
        mock_get_schema.return_value = simple_schema

        # Call the command
        call_command("fill_organization_metadata")

    # Refresh from DB and check
    organization.refresh_from_db()

    # Check that the metadata has been merged correctly
    for key, value in expected_result.items():
        assert organization.metadata[key] == value
