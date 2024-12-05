"""Helper functions to generate raw SQL queries for Django models."""

from typing import Type

from django.db import models
from django.db.models.expressions import RawSQL


def gen_sql_filter_json_array(
    model: Type[models.Model],
    lookup_path: str,
    nested_key: str,
    lookup_value: str,
) -> RawSQL:
    """
    Filter a queryset on a nested JSON key in an array field with
    a case-insensitive and unaccent match.

    Highly inspired from
    https://gist.github.com/TobeTek/df2e9783a64e431c228c513441eaa8df#file-utils-py

    :param Type[models.Model] model: Your Django model to filter on
    :param str lookup_path: The lookup path of the array field/key in
           Postgres format e.g `data->"sub-key1"->"sub-key2"`
    :param str nested_key: The name of the nested key to filter on
    :param str lookup_value: The value to match/filter the queryset on
    """
    # Disabling S608 Possible SQL injection vector through string-based query construction
    # because we are using Django's RawSQL with parameters.
    # Disabling S611 Use of `RawSQL` can lead to SQL injection vulnerabilities
    # for the same reason.

    table_name = model._meta.db_table  # noqa: SLF001

    query = (
        f"SELECT {table_name}.id FROM {table_name}, "  # noqa: S608
        f"jsonb_array_elements({lookup_path}) AS temp_filter_table "
        f"WHERE unaccent(temp_filter_table->>'{nested_key}') ILIKE  unaccent(%s)"
    )

    return RawSQL(sql=query, params=[f"%{lookup_value}%"])  # noqa: S611
