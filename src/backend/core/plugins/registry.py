"""Registry for hooks."""

import logging
from typing import Callable, Dict, List, Set

logger = logging.getLogger(__name__)


class HooksRegistry:
    """Registry for hooks."""

    _available_hooks = {
        "organization_created",
        "organization_access_granted",
    }

    def __init__(self):
        """Initialize the registry."""
        self._hooks: Dict[str, List[Callable]] = {
            hook_name: [] for hook_name in self._available_hooks
        }
        self._registered_apps: Set[str] = set()

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback.

        Args:
            hook_name: The name of the hook.
            callback: The callback function to register.
        """
        try:
            self._hooks[hook_name].append(callback)
        except KeyError as exc:
            logger.exception(
                "Failed to register hook '%s' is not a valid hook: %s", hook_name, exc
            )
        logger.info("Registered hook %s: %s", hook_name, callback)

    def get_registered_hooks(self):
        """Get all registered hooks."""
        return self._hooks.items()

    def register_app(self, app_name: str) -> None:
        """
        Register an app as having hooks.

        Args:
            app_name: The name of the app.
        """
        if app_name in self._registered_apps:
            return

        self._registered_apps.add(app_name)
        try:
            # Try to import the hooks module from the app
            __import__(f"{app_name}.hooks")
            logger.info("Registered hooks from app: %s", app_name)
        except ImportError:
            # It's okay if the app doesn't have a hooks module
            logger.info("App %s has no hooks module", app_name)

    def get_callbacks(self, hook_name: str) -> List[Callable]:
        """
        Get all callbacks for a hook.

        Args:
            hook_name: The name of the hook.

        Returns:
            A list of callback functions.
        """
        try:
            return self._hooks[hook_name]
        except KeyError as exc:
            logger.exception(
                "Failed to get callbacks for hook '%s' is not a valid hook: %s",
                hook_name,
                exc,
            )
            return []

    def execute_hook(self, hook_name: str, *args, **kwargs):
        """
        Execute all callbacks for a hook.

        Args:
            hook_name: The name of the hook.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.

        Returns:
            A list of results from the callbacks.
        """
        results = []
        for callback in self.get_callbacks(hook_name):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:  # pylint: disable=broad-except
                logger.exception("Error executing hook %s: %s", hook_name, e)
        return results

    def reset(self):
        """Function to reset the registry, to be used in test only."""
        self._hooks = {hook_name: [] for hook_name in self._available_hooks}
        self._registered_apps = set()


# Create a singleton instance of the registry
registry = HooksRegistry()


def register_hook(hook_name: str):
    """
    Decorator to register a function as a hook callback.

    Args:
        hook_name: The name of the hook.

    Returns:
        A decorator function.
    """

    def decorator(func):
        registry.register_hook(hook_name, func)
        return func

    return decorator
