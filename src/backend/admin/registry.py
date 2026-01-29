"""
Registry for custom admin views.

It allows to automatically register all views that inherit from
`BaseSelftestAdminPageView` and add them to the admin site.
"""

import inspect

from . import views


class ViewRegistry:
    """Registry for custom admin views."""

    def __init__(self):
        """Initialize the registry."""
        self.views = []
        self._register_views()

    def register(self, view_class, name, path):
        """Register a view with its name and path."""
        self.views.append(
            {
                "view_class": view_class,
                "name": name,
                "title": view_class.title,
                "path": path,
            }
        )

    def _register_views(self):
        """Register all views."""

        for name, obj in inspect.getmembers(views):
            if (
                inspect.isclass(obj)
                and issubclass(obj, views.BaseSelftestAdminPageView)
                and not obj == views.BaseSelftestAdminPageView
            ):
                # Extract name and path from class name
                base_name = name.replace("SelftestAdminPageView", "").lower()
                self.register(
                    view_class=obj,
                    name=base_name,
                    path=obj.path,
                )

    def get_views(self):
        """Get all registered views."""
        return self.views


# Create a registry instance
view_registry = ViewRegistry()
