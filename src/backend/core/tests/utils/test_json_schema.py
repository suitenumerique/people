"""Tests for the JSON schema `generate_default_from_schema` utility functions."""

import pytest

from core.utils.json_schema import generate_default_from_schema


@pytest.mark.parametrize(
    "schema,expected",
    [
        # Test empty schema
        ({}, {}),
        # Test schema with no properties
        ({"type": "object"}, {}),
        # Test basic property types
        (
            {
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "active": {"type": "boolean"},
                    "data": {"type": "null"},
                }
            },
            {"name": "", "age": None, "active": False, "data": None},
        ),
        # Test default values
        (
            {
                "properties": {
                    "name": {"type": "string", "default": "John Doe"},
                    "age": {"type": "integer", "default": 30},
                    "active": {"type": "boolean", "default": True},
                }
            },
            {
                "name": "John Doe",
                "age": 30,
                "active": True,
            },
        ),
        # Test array type
        (
            {"properties": {"items": {"type": "array"}, "tags": {"type": "array"}}},
            {"items": [], "tags": []},
        ),
        # Test nested object
        (
            {
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "details": {
                                "type": "object",
                                "properties": {
                                    "age": {"type": "integer"},
                                    "active": {"type": "boolean", "default": True},
                                },
                            },
                        },
                    }
                }
            },
            {"user": {"name": "", "details": {"age": None, "active": True}}},
        ),
        # Test complex schema with multiple types and nesting
        (
            {
                "properties": {
                    "id": {"type": "string", "default": "user-123"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "age": {"type": "number", "default": 25},
                        },
                    },
                    "roles": {"type": "array"},
                    "settings": {
                        "type": "object",
                        "properties": {
                            "notifications": {"type": "boolean", "default": False},
                            "theme": {"type": "string", "default": "light"},
                        },
                    },
                    "unknown": {"type": "something-else"},
                }
            },
            {
                "id": "user-123",
                "profile": {"firstName": "", "lastName": "", "age": 25},
                "roles": [],
                "settings": {"notifications": False, "theme": "light"},
                "unknown": None,
            },
        ),
    ],
)
def test_generate_default_from_schema(schema, expected):
    """Test the generate_default_from_schema function with various schema inputs."""
    result = generate_default_from_schema(schema)
    assert result == expected


def test_with_invalid_inputs():
    """Test the function with invalid inputs to ensure it handles them gracefully."""
    # pylint: disable=use-implicit-booleaness-not-comparison

    # None input
    assert generate_default_from_schema(None) == {}

    # Invalid schema type
    assert generate_default_from_schema([]) == {}
    assert generate_default_from_schema("not-a-schema") == {}

    # Empty properties
    assert generate_default_from_schema({"properties": {}}) == {}


def test_complex_nested_arrays():
    """Test handling of complex schemas with nested arrays and objects."""
    schema = {
        "properties": {
            "users": {
                "type": "array",
            },
            "config": {
                "type": "object",
                "properties": {
                    "features": {
                        "type": "object",
                        "properties": {
                            "enabledFlags": {"type": "array"},
                            "limits": {
                                "type": "object",
                                "properties": {
                                    "maxUsers": {"type": "integer", "default": 10},
                                    "maxStorage": {"type": "integer", "default": 5120},
                                },
                            },
                        },
                    }
                },
            },
        }
    }

    expected = {
        "users": [],
        "config": {
            "features": {
                "enabledFlags": [],
                "limits": {"maxUsers": 10, "maxStorage": 5120},
            }
        },
    }

    result = generate_default_from_schema(schema)
    assert result == expected
