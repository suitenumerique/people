"""Throttles for the la suite plugin."""

from rest_framework import throttling


class OrganizationTokenAnonRateThrottle(throttling.AnonRateThrottle):
    """
    Throttle for organization token requests.
    """

    scope = "organization-token-anon"

    def get_rate(self):
        """
        Get the rate for the throttle.
        """
        return "5/min"
