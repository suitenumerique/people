"""Base plugin class for organization plugins."""


class BaseOrganizationPlugin:
    """
    Base class for organization plugins.

    Plugins must implement all methods of this class even if it is only to "pass".
    """

    def run_after_create(self, organization) -> None:
        """Method called after creating an organization."""
        raise NotImplementedError("Plugins must implement the run_after_create method")

    def run_after_grant_access(self, organization_access) -> None:
        """Method called after creating an organization."""
        raise NotImplementedError(
            "Plugins must implement the run_after_grant_access method"
        )
