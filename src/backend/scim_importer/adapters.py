"""
Adapters are used to convert the data model described by the SCIM 2.0
specification to a data model that fits the data provided by the application
implementing a SCIM api.

For example, in a Django app, there are User and Group models that do
not have the same attributes/fields that are defined by the SCIM 2.0
specification. The Django User model has both ``first_name`` and ``last_name``
attributes but the SCIM speicifcation requires this same data be sent under
the names ``givenName`` and ``familyName`` respectively.

An adapter is instantiated with a model instance. Eg::

    user = get_user_model().objects.get(id=1)
    scim_user = SCIMUser(user)
    ...

"""

import uuid
from urllib.parse import urljoin

from django.core.exceptions import ValidationError
from django.urls import reverse

from django_scim import constants, exceptions
from django_scim.adapters import SCIMGroup as BaseSCIMGroup
from django_scim.adapters import SCIMUser as BaseSCIMUser
from django_scim.utils import get_user_adapter, get_user_model


class SCIMUser(BaseSCIMUser):
    """
    Adapter for adding SCIM functionality to a Django User object.

    This adapter can be overridden; see the ``USER_ADAPTER`` setting
    for details.
    """

    @property
    def display_name(self):
        """
        Return the displayName of the user per the SCIM spec.
        """
        if self.obj.first_name and self.obj.last_name:
            return f"{self.obj.first_name} {self.obj.last_name}".strip()
        return self.obj.scim_username

    @property
    def meta(self):
        """
        Return the meta object of the user per the SCIM spec.
        """
        d = {
            "resourceType": self.resource_type,
            "created": self.obj.created_at.isoformat(),
            "lastModified": self.obj.updated_at.isoformat(),
            "location": self.location,
        }

        return d

    def to_dict(self):
        """
        Return a ``dict`` conforming to the SCIM User Schema,
        ready for conversion to a JSON object.
        """
        return {
            "id": self.id,
            # "externalId": self.obj.scim_external_id,
            "schemas": [constants.SchemaURI.USER],
            "userName": self.obj.scim_username,
            "name": {
                "givenName": self.obj.first_name,
                "familyName": self.obj.last_name,
                "formatted": self.display_name,
            },
            "displayName": self.display_name,
            "emails": self.emails,
            "active": self.obj.is_active,
            "groups": self.groups,
            "meta": self.meta,
        }

    def from_dict(self, d):
        """
        Consume a ``dict`` conforming to the SCIM User Schema, updating the
        internal user object with data from the ``dict``.

        Please note, the user object is not saved within this method. To
        persist the changes made by this method, please call ``.save()`` on the
        adapter. Eg::

            scim_user.from_dict(d)
            scim_user.save()
        """
        self.obj.client = self.request.user

        scim_external_id = d.get("externalId")
        self.obj.scim_external_id = scim_external_id or ""

        if self.obj.scim_id is None:
            self.obj.scim_id = uuid.uuid4()

        username = d.get("userName")
        self.obj.scim_username = username or ""

        # self.obj.scim_username = self.obj.username

        first_name = d.get("name", {}).get("givenName")
        self.obj.first_name = first_name or ""

        last_name = d.get("name", {}).get("familyName")
        self.obj.last_name = last_name or ""

        emails = d.get("emails", [])
        self.parse_emails(emails)

        # cleartext_password = d.get('password')
        # if cleartext_password:
        #    self.obj.set_password(cleartext_password)

        active = d.get("active")
        if active is not None:
            self.obj.is_active = active

        try:
            self.obj.full_clean()
        except ValidationError as exc:
            raise exceptions.IntegrityError(str(exc)) from exc


class SCIMGroup(BaseSCIMGroup):
    """
    Adapter for adding SCIM functionality to a Django Group object.

    This adapter can be overridden; see the ``GROUP_ADAPTER``
    setting for details.
    """

    @property
    def display_name(self):
        """
        Return the displayName of the group per the SCIM spec.
        """
        return self.obj.scim_display_name

    def to_dict(self):
        """
        Return a ``dict`` conforming to the SCIM Group Schema,
        ready for conversion to a JSON object.
        """
        return {
            "id": self.id,
            "schemas": [constants.SchemaURI.GROUP],
            "displayName": self.obj.scim_display_name,
            "members": self.members,
            "meta": self.meta,
        }

    def from_dict(self, d):
        """
        Consume a ``dict`` conforming to the SCIM Group Schema, updating the
        internal group object with data from the ``dict``.

        Please note, the group object is not saved within this method. To
        persist the changes made by this method, please call ``.save()`` on the
        adapter. Eg::

            scim_group.from_dict(d)
            scim_group.save()
        """
        super().from_dict(d)

        if self.obj.scim_id is None:
            self.obj.scim_id = uuid.uuid4()

        display_name = d.get("displayName")
        self.obj.scim_display_name = display_name or ""

        self.obj.client = self.request.user

    def handle_add(self, path, value, operation):
        """
        Handle add operations.
        """
        if path.first_path == ("members", None, None):
            members = value or []
            ids = [member.get("value") for member in members]
            users = get_user_model().objects.filter(scim_id__in=ids)

            if len(ids) != users.count():
                raise exceptions.BadRequestError(
                    "Can not add a non-existent user to group"
                )

            for user in users:
                self.obj.user_set.add(user)

        else:
            raise exceptions.NotImplementedError

    def handle_remove(self, path, value, operation):
        """
        Handle remove operations.
        """
        if path.first_path == ("members", None, None):
            members = value or []
            ids = [member.get("value") for member in members]
            users = get_user_model().objects.filter(scim_id__in=ids)

            if len(ids) != users.count():
                raise exceptions.BadRequestError(
                    "Can not remove a non-existent user from group"
                )

            for user in users:
                self.obj.user_set.remove(user)

        else:
            raise exceptions.NotImplementedError

    def handle_replace(self, path, value, operation):
        """
        Handle the replace operations.
        """
        if path.first_path == ("displayName", None, None):
            self.obj.scim_display_name = value
            self.save()

        else:
            raise exceptions.NotImplementedError
