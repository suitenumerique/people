# pylint: disable=line-too-long
"""Define here some fake data from dimail, useful to mock dimail response"""

import json
import re

import responses
from rest_framework import status


## USERS
def response_user_created(user_sub):
    """mimic dimail response upon successful user creation."""
    return json.dumps(
        {
            "name": user_sub,
            "is_admin": "false",
            "uuid": "user-uuid-on-dimail",
            "perms": [],
        }
    )


def response_login_code_ok(domain, local_part):
    """Mock dimail's response when requesting login code."""
    return responses.add(
        responses.POST,
        re.compile(rf".*/domains/{domain}/mailboxes/{local_part}/code"),
        json={
            "email": f"{local_part}@{domain}",
            "code": "OneTimeCode",
            "expires_at": 1774900909,
            "expires_in": 3599,
            "maxuse": 1,
            "nbuse": 0,
        },
        status=status.HTTP_200_OK,
        content_type="application/json",
    )


## DOMAINS
CHECK_DOMAIN_BROKEN = {
    "name": "example.fr",
    "state": "broken",
    "valid": False,
    "delivery": "virtual",
    "features": ["webmail", "mailbox"],
    "webmail_domain": None,
    "imap_domain": None,
    "smtp_domain": None,
    "context_name": "example.fr",
    "transport": None,
    "domain_exist": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "mx": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "wrong_mx",
                "detail": "Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr., or je trouve example-fr.mail.protection.outlook.com.",
            }
        ],
    },
    "cname_imap": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "no_cname_imap",
                "detail": "Il faut un CNAME 'imap.example.fr' qui renvoie vers 'imap.ox.numerique.gouv.fr.'",
            }
        ],
    },
    "cname_smtp": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "wrong_cname_smtp",
                "detail": "Le CNAME pour 'smtp.example.fr' n'est pas bon, il renvoie vers 'ns0.ovh.net.' et je veux 'smtp.ox.numerique.gouv.fr.'",
            }
        ],
    },
    "cname_webmail": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "no_cname_webmail",
                "detail": "Il faut un CNAME 'webmail.example.fr' qui renvoie vers 'webmail.ox.numerique.gouv.fr.'",
            }
        ],
    },
    "spf": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "wrong_spf",
                "detail": "Le SPF record ne contient pas include:_spf.ox.numerique.gouv.fr",
            }
        ],
    },
    "dkim": {
        "ok": False,
        "internal": False,
        "errors": [
            {"code": "no_dkim", "detail": "Il faut un DKIM record, avec la bonne clef"}
        ],
    },
    "postfix": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "ox": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "cert": {
        "ok": False,
        "internal": True,
        "errors": [
            {"code": "no_cert", "detail": "Pas de certificat pour ce domaine (ls)"}
        ],
    },
}


CHECK_DOMAIN_BROKEN_INTERNAL = {
    "name": "example.fr",
    "state": "broken",
    "valid": False,
    "delivery": "virtual",
    "features": ["webmail", "mailbox"],
    "webmail_domain": None,
    "imap_domain": None,
    "smtp_domain": None,
    "context_name": "example.fr",
    "transport": None,
    "domain_exist": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "mx": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "cname_imap": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "cname_smtp": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "cname_webmail": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "spf": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "dkim": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "postfix": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "ox": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "cert": {
        "ok": False,
        "internal": True,
        "errors": [
            {"code": "no_cert", "detail": "Pas de certificat pour ce domaine (ls)"}
        ],
    },
}

CHECK_DOMAIN_BROKEN_EXTERNAL = {
    "name": "example.fr",
    "state": "broken",
    "valid": False,
    "delivery": "virtual",
    "features": ["webmail", "mailbox"],
    "webmail_domain": None,
    "imap_domain": None,
    "smtp_domain": None,
    "context_name": "example.fr",
    "transport": None,
    "domain_exist": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "mx": {
        "ok": False,
        "internal": False,
        "errors": [
            {
                "code": "wrong_mx",
                "detail": "Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr., or je trouve example-fr.mail.protection.outlook.com.",
            }
        ],
    },
    "cname_imap": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "cname_smtp": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "cname_webmail": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "spf": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "dkim": {
        "ok": True,
        "internal": False,
        "errors": [],
    },
    "postfix": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "ox": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
    "cert": {
        "ok": True,
        "internal": True,
        "errors": [],
    },
}


CHECK_DOMAIN_OK = {
    "name": "example.fr",
    "state": "ok",
    "valid": True,
    "delivery": "virtual",
    "features": ["webmail", "mailbox"],
    "webmail_domain": None,
    "imap_domain": None,
    "smtp_domain": None,
    "context_name": "example.fr",
    "transport": None,
    "domain_exist": {"ok": True, "internal": False, "errors": []},
    "mx": {"ok": True, "internal": False, "errors": []},
    "cname_imap": {"ok": True, "internal": False, "errors": []},
    "cname_smtp": {"ok": True, "internal": False, "errors": []},
    "cname_webmail": {"ok": True, "internal": False, "errors": []},
    "spf": {"ok": True, "internal": False, "errors": []},
    "dkim": {"ok": True, "internal": False, "errors": []},
    "postfix": {"ok": True, "internal": True, "errors": []},
    "ox": {"ok": True, "internal": True, "errors": []},
    "cert": {"ok": True, "internal": True, "errors": []},
}

# pylint: disable=line-too-long
DOMAIN_SPEC = [
    {"target": "", "type": "mx", "value": "mx.ox.numerique.gouv.fr."},
    {
        "target": "dimail._domainkey",
        "type": "txt",
        "value": "v=DKIM1; h=sha256; k=rsa; p=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    },
    {"target": "imap", "type": "cname", "value": "imap.ox.numerique.gouv.fr."},
    {"target": "smtp", "type": "cname", "value": "smtp.ox.numerique.gouv.fr."},
    {
        "target": "",
        "type": "txt",
        "value": "v=spf1 include:_spf.ox.numerique.gouv.fr -all",
    },
    {"target": "webmail", "type": "cname", "value": "webmail.ox.numerique.gouv.fr."},
]


## ALLOWS
def response_allows_created(user_name, domain_name):
    """mimic dimail response upon successful allows creation.
    Dimail expects a name but our names are ProConnect's uuids."""
    return json.dumps({"user": user_name, "domain": domain_name})


## MAILBOXES
def response_mailbox_created(email_address):
    """mimic dimail response upon successful mailbox creation."""
    return json.dumps({"email": email_address.lower(), "password": "password"})


# Fixture
def response_connexion_code(email):
    """Mock dimail response when /token/ endpoit is given valid credentials."""

    local_part, domain = email.split("@")

    return responses.post(
        re.compile(rf".*/domains/{domain}/mailboxes/{local_part}/code"),
        json={
            "email": "string",
            "code": "string",
            "expires_at": 0,
            "expires_in": 0,
            "maxuse": 0,
            "nbuse": 0,
        },
        status=status.HTTP_200_OK,
        content_type="application/json",
    )
