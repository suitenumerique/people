from typing import Optional, Union, Mapping, List
from urllib.parse import unquote

import vobject
from radicale.item import Item
from radicale.storage import BaseCollection

from core.models import Contact


class Collection(BaseCollection):
    def __init__(self, storage, path):
        self._storage = storage
        self._path = path
        parts = unquote(self._path.strip('/')).split('/')
        self.user = parts[0] if parts else ""
        self.collection_type = parts[1] if len(parts) > 1 else None
        self._is_principal = False  # Use instance variable instead of property

    @property
    def path(self) -> str:
        return self._path.strip("/")

    def get_meta(self, key: Optional[str] = None) -> Union[Mapping[str, str], Optional[str]]:
        dav_ns = "DAV:"
        card_ns = "urn:ietf:params:xml:ns:carddav"
        xmlns = f"xmlns:D='{dav_ns}' xmlns:CR='{card_ns}'"

        if not self._path:  # Root collection
            meta = {
                "D:resourcetype": f"<D:resourcetype {xmlns}><D:collection/></D:resourcetype>",
                "D:displayname": "CardDAV Server",
                "D:current-user-principal": f"<D:href>/carddav/{self.user}/</D:href>"
            }
        elif self._is_principal:  # Principal collection
            meta = {
                "D:resourcetype": f"<D:resourcetype {xmlns}><D:collection/></D:resourcetype>",
                "D:displayname": f"CardDAV - {self.user}",
                "CR:addressbook-home-set": (
                    f"<CR:addressbook-home-set {xmlns}>"
                    f"<D:href>/carddav/{self.user}/organization/</D:href>"
                    f"<D:href>/carddav/{self.user}/personal/</D:href>"
                    "</CR:addressbook-home-set>"
                )
            }
        else:  # Address book collection
            meta = {
                "D:resourcetype": (
                    f"<D:resourcetype {xmlns}>"
                    "<D:collection/>"
                    "<CR:addressbook/>"
                    "</D:resourcetype>"
                ),
                "D:displayname": self.collection_type.title(),
                "CR:addressbook-description": f"{self.collection_type.title()} Contacts",
                "getctag": "0",
                "D:sync-token": "0",
                "CR:supported-address-data": (
                    f"<CR:supported-address-data {xmlns}>"
                    "<CR:address-data-type content-type='text/vcard' version='3.0'/>"
                    "</CR:supported-address-data>"
                )
            }

        # Add common properties
        meta.update({
            "D:current-user-privilege-set": (
                f"<D:current-user-privilege-set {xmlns}>"
                "<D:privilege><D:read/></D:privilege>"
                "<D:privilege><D:write/></D:privilege>"
                "</D:current-user-privilege-set>"
            )
        })

        return meta.get(key) if key else meta

    def get_all(self) -> List[Item]:
        items = []

        # Only return contacts for principal and address book collections
        if not self._path:  # Root collection should be empty
            return items

        # Get all contacts for the user
        if self._is_principal or self.collection_type:
            contacts_query = Contact.objects.filter(user__email=self.user)
            
            # Filter by collection type if not principal
            if not self._is_principal and self.collection_type:
                contacts_query = contacts_query.filter(
                    organization_id__isnull=self.collection_type != "organization"
                )
            
            for contact in contacts_query:
                vcard = vobject.vCard()
                vcard.add('fn').value = contact.full_name

                # Add UID and required fields
                vcard.add('uid').value = str(contact.pk)
                vcard.add('rev').value = contact.updated_at.strftime('%Y%m%dT%H%M%SZ') if contact.updated_at else ''
                
                item = Item(
                    collection=self,
                    vobject_item=vcard,
                    href=f"{contact.id}.vcf",
                    last_modified=contact.updated_at.timestamp() if contact.updated_at else None
                )
                items.append(item)
        
        return items

    def get_multi(self, hrefs):
        items = []
        for item in self.get_all():
            if item.href in hrefs:
                items.append(item)
        return items

    def has_uid(self, uid):
        return Contact.objects.filter(id=uid).exists()

