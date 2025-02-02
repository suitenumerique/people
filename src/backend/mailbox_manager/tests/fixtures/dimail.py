# pylint: disable=line-too-long
"""Define here some fake data from dimail, useful to mock dimail response"""

import json

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
    "domain_exist": {"ok": True, "internal": False, "errors": []},
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
    "postfix": {"ok": True, "internal": True, "errors": []},
    "ox": {"ok": True, "internal": True, "errors": []},
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
    "domain_exist": {"ok": True, "internal": False, "errors": []},
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
    "postfix": {"ok": True, "internal": True, "errors": []},
    "ox": {"ok": True, "internal": True, "errors": []},
    "cert": {
        "ok": False,
        "internal": True,
        "errors": [
            {"code": "no_cert", "detail": "Pas de certificat pour ce domaine (ls)"}
        ],
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

## TOKEN

TOKEN_OK = json.dumps({"access_token": "token", "token_type": "bearer"})

## MAILBOXES


def response_mailbox_created(email_address):
    """mimic dimail response upon succesfull mailbox creation."""
    return json.dumps({"email": email_address, "password": "password"})
