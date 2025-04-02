"""Global fixtures for the backend tests."""

import pytest
from urllib3.connectionpool import HTTPConnectionPool


@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    """
    Prevents HTTP requests from being made during tests.
    This is useful for tests that do not require actual HTTP requests
    and helps to avoid network-related issues.

    Credits: https://blog.jerrycodes.com/no-http-requests/
    """

    allowed_hosts = {"localhost"}
    original_urlopen = HTTPConnectionPool.urlopen

    def urlopen_mock(self, method, url, *args, **kwargs):
        if self.host in allowed_hosts:
            return original_urlopen(self, method, url, *args, **kwargs)

        raise RuntimeError(
            f"The test was about to {method} {self.scheme}://{self.host}{url}"
        )

    monkeypatch.setattr(
        "urllib3.connectionpool.HTTPConnectionPool.urlopen", urlopen_mock
    )
