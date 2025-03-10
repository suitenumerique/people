"""Useful functions for working with JSON schemas"""


def generate_default_from_schema(schema: dict) -> dict:
    """
    Generate default values based on a JSON schema
    """
    if not schema or "properties" not in schema:
        return {}

    result = {}

    for prop_name, prop_schema in schema.get("properties", {}).items():
        prop_type = prop_schema.get("type")

        match prop_type:
            case "object" if "properties" in prop_schema:
                result[prop_name] = generate_default_from_schema(prop_schema)
            case "array":
                result[prop_name] = []
            case "string":
                result[prop_name] = prop_schema.get("default", "")
            case "number" | "integer":
                result[prop_name] = prop_schema.get("default", None)
            case "boolean":
                result[prop_name] = prop_schema.get("default", False)
            case "null":
                result[prop_name] = None
            case _:
                result[prop_name] = None

    return result
