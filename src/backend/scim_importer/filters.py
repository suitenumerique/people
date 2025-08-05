from django_scim.filters import GroupFilterQuery as BaseGroupFilterQuery
from django_scim.filters import UserFilterQuery as BaseUserFilterQuery


class UserFilterQuery(BaseUserFilterQuery):
    attr_map = {
        # attr, sub attr, uri
        ("userName", None, None): "scim_username",
        ("name", "familyName", None): "last_name",
        ("familyName", None, None): "last_name",
        ("name", "givenName", None): "first_name",
        ("givenName", None, None): "first_name",
        ("active", None, None): "is_active",
    }


class GroupFilterQuery(BaseGroupFilterQuery):
    attr_map = {}
