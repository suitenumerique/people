"""Test module for the JSON schema validation."""

import json
import os

import pytest


def test_all_json_schemas_load_correctly(settings):
    """Test that all JSON schema files in the jsonschema directory load correctly."""
    # Get the base directory for jsonschema files
    schema_dir = os.path.join(settings.BASE_DIR, "core", "jsonschema")

    # List to store any errors encountered
    errors = []
    loaded_schemas = 0

    # Walk through the jsonschema directory and its subdirectories
    for root, _, files in os.walk(schema_dir):
        for file in files:
            if file.endswith(".json"):
                schema_path = os.path.join(root, file)
                rel_path = os.path.relpath(schema_path, schema_dir)

                try:
                    # Try to load the schema
                    with open(schema_path, "r", encoding="utf-8") as schema_file:
                        schema = json.load(schema_file)

                    # Verify it's a dictionary (basic schema validation)
                    assert isinstance(schema, dict), (
                        f"Schema in {rel_path} is not a dictionary"
                    )

                    # Check for common schema properties
                    if "$schema" not in schema:
                        errors.append(
                            f"Warning: {rel_path} does not contain a $schema property"
                        )

                    loaded_schemas += 1

                except json.JSONDecodeError as e:
                    errors.append(f"Failed to decode {rel_path}: {e}")
                except Exception as e:  # noqa: BLE001 pylint: disable=broad-except
                    errors.append(f"Error loading {rel_path}: {e}")

    # Ensure we found and loaded at least one schema
    assert loaded_schemas > 0, "No JSON schema files were found"

    # If any errors were encountered, fail the test
    if errors:
        pytest.fail("\n".join(errors))
