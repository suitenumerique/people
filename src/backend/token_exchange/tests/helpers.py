"""Helper function to create token exchange rules and grants for tests."""

from token_exchange.factories import (
    ScopeGrantFactory,
    TokenExchangeRuleFactory,
)


class DummyBackend:
    """Dummy backend for mocking resource server introspection in tests."""

    # Class attributes to store test data
    _test_user_info = None
    _test_origin = None

    def __init__(self):
        """Initialize DummyBackend with test data from class attributes."""
        user_info = self._test_user_info or {}
        origin = self._test_origin
        self.user_info = user_info
        self.token_origin_audience = origin or user_info.get("aud")
        self._scopes = []

    def get_user_info_with_introspection(self, token):
        """Return the mocked user info."""
        return self.user_info


def create_token_exchange_rule_with_scopes(source_sp, target_sp, scopes):
    """
    Create a TokenExchangeRule with ScopeGrants for the given scopes.

    Each scope in the source token is mapped to the same scope in the target service
    to quickly build symmetric grants for tests.

    Args:
        source_sp: Source ServiceProvider
        target_sp: Target ServiceProvider
        scopes: List of scope strings

    Returns:
        The created TokenExchangeRule
    """

    rule = TokenExchangeRuleFactory(
        source_service=source_sp,
        target_service=target_sp,
    )

    for scope in scopes:
        ScopeGrantFactory(
            rule=rule,
            source_scope=scope,
            granted_scope=scope,
        )

    return rule
