"""Tests for token limit per user."""

import logging

from django.utils import timezone

import pytest

from token_exchange.factories import ExchangedTokenFactory, ExpiredExchangedTokenFactory
from token_exchange.models import ExchangedToken

pytestmark = pytest.mark.django_db


def test_allows_tokens_up_to_limit(settings):
    """Test that tokens can be created up to the max limit."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 5
    sub = "user-limit-1"

    # Create 5 tokens (at limit)
    for _i in range(5):
        ExchangedTokenFactory(subject_sub=sub)

    # All 5 should exist
    assert (
        ExchangedToken.objects.filter(
            subject_sub=sub, expires_at__gt=timezone.now(), revoked_at__isnull=True
        ).count()
        == 5
    )


def test_deletes_oldest_when_exceeding_limit(settings):
    """Test that oldest tokens are deleted when limit is exceeded."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 3
    sub = "user-limit-2"

    tokens = []
    for _i in range(5):
        token = ExchangedTokenFactory(subject_sub=sub)
        tokens.append(token)

    # Should only have 3 tokens (newest ones)
    remaining_tokens = ExchangedToken.objects.filter(
        subject_sub=sub, expires_at__gt=timezone.now(), revoked_at__isnull=True
    ).order_by("created_at")

    assert remaining_tokens.count() == 3

    # First two tokens should be deleted
    assert not ExchangedToken.objects.filter(id=tokens[0].id).exists()
    assert not ExchangedToken.objects.filter(id=tokens[1].id).exists()

    # Last three tokens should still exist
    assert ExchangedToken.objects.filter(id=tokens[2].id).exists()
    assert ExchangedToken.objects.filter(id=tokens[3].id).exists()
    assert ExchangedToken.objects.filter(id=tokens[4].id).exists()


def test_preserves_recent_tokens_when_enforcing_limit(settings):
    """Test that recently created tokens are preserved when enforcing limit."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 2
    sub = "user-limit-3"

    # Create 3 tokens
    token1 = ExchangedTokenFactory(subject_sub=sub)
    token2 = ExchangedTokenFactory(subject_sub=sub)
    token3 = ExchangedTokenFactory(subject_sub=sub)  # Newest

    # Token 1 (oldest) should be deleted
    assert not ExchangedToken.objects.filter(id=token1.id).exists()

    # Tokens 2 and 3 should exist
    assert ExchangedToken.objects.filter(id=token2.id).exists()
    assert ExchangedToken.objects.filter(id=token3.id).exists()


def test_limit_isolated_between_users(settings):
    """Test that token limit is enforced per user independently."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 2
    sub1 = "user-limit-4a"
    sub2 = "user-limit-4b"

    # Create 3 tokens for each user
    for _i in range(3):
        ExchangedTokenFactory(subject_sub=sub1)
        ExchangedTokenFactory(subject_sub=sub2)

    # Each user should have exactly 2 tokens
    user_tokens = ExchangedToken.objects.filter(
        subject_sub=sub1, expires_at__gt=timezone.now(), revoked_at__isnull=True
    ).count()

    other_user_tokens = ExchangedToken.objects.filter(
        subject_sub=sub2, expires_at__gt=timezone.now(), revoked_at__isnull=True
    ).count()

    assert user_tokens == 2
    assert other_user_tokens == 2


def test_revoked_tokens_count_toward_limit(settings):
    """Test that revoked tokens still count toward the active limit."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 3
    sub = "user-limit-5"

    # Create 2 active tokens
    token1 = ExchangedTokenFactory(subject_sub=sub)
    token2 = ExchangedTokenFactory(subject_sub=sub)

    # Revoke one
    token1.revoke()

    # Create 3 more tokens
    for _i in range(3):
        ExchangedTokenFactory(subject_sub=sub)

    # Should have 3 active (non-revoked) tokens
    active_count = ExchangedToken.objects.filter(
        subject_sub=sub, expires_at__gt=timezone.now(), revoked_at__isnull=True
    ).count()

    assert active_count == 3


def test_expired_tokens_excluded_from_limit_count(settings):
    """Test that expired tokens are not counted in the active limit."""
    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 3
    sub = "user-limit-6"

    # Create 2 expired tokens
    for _i in range(2):
        ExpiredExchangedTokenFactory(subject_sub=sub)

    # Create 3 active tokens
    for _i in range(3):
        ExchangedTokenFactory(subject_sub=sub)

    # Should have exactly 3 active tokens (expired ones don't count)
    active_count = ExchangedToken.objects.filter(
        subject_sub=sub, expires_at__gt=timezone.now(), revoked_at__isnull=True
    ).count()

    assert active_count == 3

    # Expired tokens should still exist in DB
    expired_count = ExchangedToken.objects.filter(
        subject_sub=sub, expires_at__lte=timezone.now()
    ).count()

    assert expired_count == 2


def test_logs_token_deletion_when_limit_exceeded(settings, caplog):
    """Test that token deletion due to limit is logged."""

    caplog.set_level(logging.INFO)

    settings.TOKEN_EXCHANGE_MAX_ACTIVE_TOKENS_PER_USER = 2
    sub = "user-limit-7"

    # Create 3 tokens to exceed limit
    for _i in range(3):
        ExchangedTokenFactory(subject_sub=sub)

    # Check logging
    assert "Enforced token limit" in caplog.text
    assert sub in caplog.text
