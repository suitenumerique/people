"""Tests for the raw SQL utility functions."""

from django.db.models.expressions import RawSQL

from core.models import Contact
from core.utils.raw_sql import gen_sql_filter_json_array


def test_gen_sql_filter_json_array():
    """Test the generation of a raw SQL query to filter on a JSON array."""
    raw_sql = gen_sql_filter_json_array(Contact, "data->'emails'", "value", "blah")

    assert isinstance(raw_sql, RawSQL)
    assert raw_sql.sql == (
        "SELECT people_contact.id FROM people_contact, "
        "jsonb_array_elements(data->'emails') AS temp_filter_table WHERE "
        "unaccent(temp_filter_table->>'value') ILIKE  unaccent(%s)"
    )
    assert raw_sql.params == ["%blah%"]
