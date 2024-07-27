"""
Test for the Resource Server (RS) utils functions.
"""

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

import pytest
from joserfc.jwk import ECKey, RSAKey

from core.resource_server.utils import import_private_key_from_settings

PRIVATE_KEY_STR_MOCKED = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC3boG1kwEGUYL+
U58RPrVToIsF9jHB64S6WJIIInPmAclBciXFb6BWG11mbRIgo8ha3WVnC/tGHbXb
ndiKdrH2vKHOsDhV9AmgHgNgWaUK9L0uuKEb/xMLePYWsYlgzcQJx8RZY7RQyWqE
20WfzFxeuCE7QMb6VXSOgwQMnJsKocguIh3VCI9RIBq3B1kdgW35AD63YKOygmGx
qjcWwbjhKLvkF7LpBdlyAEzOKqg4T5uCcHMfksMW2+foTJx70RrZM/KHU+Zysuw7
uhhVsgPBG+CsqBSjHQhs7jzymqxtQAfe1FkrCRxOq5Pv2Efr7kgtVSkJJiX3KutM
vnWuEypxAgMBAAECggEAGqKS9pbrN+vnmb7yMsqYgVVnQn0aggZNHlLkl4ZLLnuV
aemlhur7zO0JzajqUC+AFQOfaQxiFu8S/FoJ+qccFdATrcPEVmTKbgPVqSyzLKlX
fByGll5eOVT95NMwN8yBGgt2HSW/ZditXS/KxxahVgamGqjAC9MTSutGz/8Ae1U+
DNDBJCc6RAqu3T02tV9A2pSpVC1rSktDMpLUTscnsfxpaEQATd9DJUcHEvIwoX8q
GJpycPEhNhdPXqpln5SoMHcf/zS5ssF/Mce0lJJXYyE0LnEk9X12jMWyBqmLqXUY
cKLyynaFbis0DpQppwKx2y8GpL76k+Ci4dOHIvFknQKBgQDj/2WRMcWOvfBrggzj
FHpcme2gSo5A5c0CVyI+Xkf1Zab6UR6T7GiImEoj9tq0+o2WEix9rwoypgMBq8rz
/rrJAPSZjgv6z71k4EnO2FIB5R03vQmoBRCN8VlgvLM0xv52zyjV4Wx66Q4MDjyH
EgkpHyB0FzRZh0UzhnE/pYSetQKBgQDN9eLB1nA4CBSr1vMGNfQyfBQl3vpO9EP4
VSS3KnUqCIjJeLu682Ylu7SFxcJAfzUpy5S43hEvcuJsagsVKfmCAGcYZs9/xq3I
vzYyhaEOS5ezNxLSh4+yCNBPlmrmDyoazag0t8H8YQFBN6BVcxbATHqdWGUhIhYN
eEpEMOh2TQKBgGBr7kRNTENlyHtu8IxIaMcowfn8DdUcWmsW9oBx1vTNHKTYEZp1
bG/4F8LF7xCCtcY1wWMV17Y7xyG5yYcOv2eqY8dc72wO1wYGZLB5g5URlB2ycJcC
LVIaM7ZZl2BGl+8fBSIOx5XjYfFvQ+HLmtwtMchm19jVAEseHF7SXRfRAoGAK15j
aT2mU6Yf9C9G7T/fM+I8u9zACHAW/+ut14PxN/CkHQh3P16RW9CyqpiB1uLyZuKf
Zm4cYElotDuAKey0xVMgYlsDxnwni+X3m5vX1hLE1s/5/qrc7zg75QZfbCI1U3+K
s88d4e7rPLhh4pxhZgy0pP1ADkIHMr7ppIJH8OECgYEApNfbgsJVPAMzucUhJoJZ
OmZHbyCtJvs4b+zxnmhmSbopifNCgS4zjXH9qC7tsUph1WE6L2KXvtApHGD5H4GQ
IH5em4M/pHIcsqCi1qggBMbdvzHBUtC3R4sK0CpEFHlN+Y59aGazidcN2FPupNJv
MbyqKyC6DAzv4jEEhHaN7oY=
-----END PRIVATE KEY-----
"""


@override_settings(OIDC_RS_PRIVATE_KEY_STR=PRIVATE_KEY_STR_MOCKED)
@pytest.mark.parametrize("mocked_private_key", [None, ""])
def test_import_private_key_from_settings_missing_or_empty_key(
    settings, mocked_private_key
):
    """Should raise an exception if the settings 'OIDC_RS_PRIVATE_KEY_STR' is missing or empty."""
    settings.OIDC_RS_PRIVATE_KEY_STR = mocked_private_key

    with pytest.raises(
        ImproperlyConfigured,
        match="OIDC_RS_PRIVATE_KEY_STR setting is missing or empty.",
    ):
        import_private_key_from_settings()


@pytest.mark.parametrize("mocked_private_key", ["123", "foo", "invalid_key"])
@override_settings(OIDC_RS_PRIVATE_KEY_STR=PRIVATE_KEY_STR_MOCKED)
@override_settings(OIDC_RS_ENCRYPTION_KEY_TYPE="RSA")
@override_settings(OIDC_RS_ENCRYPTION_ALGO="RS256")
def test_import_private_key_from_settings_incorrect_key(settings, mocked_private_key):
    """Should raise an exception if the setting 'OIDC_RS_PRIVATE_KEY_STR' has an incorrect value."""
    settings.OIDC_RS_PRIVATE_KEY_STR = mocked_private_key

    with pytest.raises(
        ImproperlyConfigured, match="OIDC_RS_PRIVATE_KEY_STR setting is wrong."
    ):
        import_private_key_from_settings()


@override_settings(OIDC_RS_PRIVATE_KEY_STR=PRIVATE_KEY_STR_MOCKED)
@override_settings(OIDC_RS_ENCRYPTION_KEY_TYPE="RSA")
@override_settings(OIDC_RS_ENCRYPTION_ALGO="RS256")
def test_import_private_key_from_settings_success_rsa_key():
    """Should import private key string as an RSA key."""
    private_key = import_private_key_from_settings()
    assert isinstance(private_key, RSAKey)


@override_settings(OIDC_RS_PRIVATE_KEY_STR=PRIVATE_KEY_STR_MOCKED)
@override_settings(OIDC_RS_ENCRYPTION_KEY_TYPE="EC")
@override_settings(OIDC_RS_ENCRYPTION_ALGO="ES256")
def test_import_private_key_from_settings_success_ec_key():
    """Should import private key string as an EC key."""
    private_key = import_private_key_from_settings()
    assert isinstance(private_key, ECKey)
