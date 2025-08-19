from rest_framework import throttling


class OrganizationTokenAnonRateThrottle(throttling.AnonRateThrottle):

    scope = "organization-token-anon"

    def get_rate(self):
        return "5/min"
