"""Tests for cleanup_expired_tokens management command."""

import logging
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.utils import timezone

import pytest

from token_exchange.factories import ExchangedTokenFactory
from token_exchange.models import ExchangedToken
from token_exchange.tasks import cleanup_expired_tokens_task

pytestmark = pytest.mark.django_db


def test_cleanup_deletes_old_expired_tokens():
    """Test that cleanup deletes tokens expired more than N days ago."""
    valid_token = ExchangedTokenFactory()
    expired_recent_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=3),
    )
    expired_old_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=10),
    )

    out = StringIO()

    # Default is 7 days, should delete only expired_old_token (10 days)
    call_command("cleanup_expired_tokens", stdout=out)

    # Check that old expired token was deleted
    assert not ExchangedToken.objects.filter(id=expired_old_token.id).exists()

    # Check that recent expired token still exists (only 3 days old)
    assert ExchangedToken.objects.filter(id=expired_recent_token.id).exists()

    # Check that valid token still exists
    assert ExchangedToken.objects.filter(id=valid_token.id).exists()


def test_cleanup_preserves_non_expired_tokens():
    """Test that cleanup preserves non-expired tokens."""
    valid_token = ExchangedTokenFactory()

    out = StringIO()

    call_command("cleanup_expired_tokens", stdout=out)

    # Valid token should still exist
    assert ExchangedToken.objects.filter(id=valid_token.id).exists()


def test_cleanup_with_custom_days_parameter():
    """Test cleanup with custom --days parameter."""
    expired_recent_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=3),
    )
    expired_old_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=10),
    )

    out = StringIO()

    # Set days=2, should delete both tokens (10 days and 3 days)
    call_command("cleanup_expired_tokens", "--days=2", stdout=out)

    # Both expired tokens should be deleted
    assert not ExchangedToken.objects.filter(id=expired_old_token.id).exists()
    assert not ExchangedToken.objects.filter(id=expired_recent_token.id).exists()


def test_cleanup_dry_run_does_not_delete():
    """Test that --dry-run option doesn't actually delete tokens."""
    expired_old_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=10),
    )
    out = StringIO()

    call_command("cleanup_expired_tokens", "--dry-run", stdout=out)

    # Token should still exist after dry-run
    assert ExchangedToken.objects.filter(id=expired_old_token.id).exists()

    # Output should indicate dry-run
    assert "DRY RUN" in out.getvalue() or "Would delete" in out.getvalue()


def test_cleanup_displays_correct_count():
    """Test that cleanup displays correct count of deleted tokens."""
    out = StringIO()

    # Create multiple old expired tokens
    ExchangedTokenFactory.create_batch(
        6,
        expires_at=timezone.now() - timedelta(days=10),
    )

    call_command("cleanup_expired_tokens", stdout=out)

    output = out.getvalue()
    # Should mention deletion of 6 tokens
    assert "6" in output or "six" in output.lower()


def test_cleanup_with_no_expired_tokens():
    """Test cleanup when there are no expired tokens to delete."""
    valid_token = ExchangedTokenFactory()

    out = StringIO()

    call_command("cleanup_expired_tokens", stdout=out)

    output = out.getvalue()
    assert "No expired tokens" in output or "0" in output


def test_cleanup_preserves_revoked_but_not_expired_tokens():
    """Test that cleanup doesn't delete revoked tokens that haven't expired."""
    # Create a revoked but not expired token
    token = ExchangedTokenFactory()
    token.revoke()

    out = StringIO()
    call_command("cleanup_expired_tokens", stdout=out)

    # Token should still exist (not expired)
    assert ExchangedToken.objects.filter(id=token.id).exists()


def test_cleanup_logs_deletion(caplog):
    """Test that cleanup logs the deletion."""
    _expired_old_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=10),
    )

    caplog.set_level(logging.INFO)

    out = StringIO()
    call_command("cleanup_expired_tokens", stdout=out)

    assert "Cleaned up" in caplog.text
    assert "expired tokens" in caplog.text


def test_cleanup_dry_run_logs_simulation(caplog):
    """Test that dry-run logs simulation message."""
    _expired_old_token = ExchangedTokenFactory(
        expires_at=timezone.now() - timedelta(days=10),
    )

    caplog.set_level(logging.INFO)

    out = StringIO()
    call_command("cleanup_expired_tokens", "--dry-run", stdout=out)

    assert "DRY RUN" in caplog.text or "Would clean up" in caplog.text


@mock.patch("token_exchange.tasks.call_command")
def test_celery_task_calls_cleanup_command(mock_call_command):
    """Test that Celery task calls the cleanup command."""

    cleanup_expired_tokens_task()

    mock_call_command.assert_called_once_with("cleanup_expired_tokens")
