from django.conf import settings
from radicale.rights import BaseRights
from radicale import pathutils
from urllib.parse import unquote


class Rights(BaseRights):
    def authorization(self, user: str, path: str) -> str:
        """Return the set of allowed actions for user on path."""
        sane_path = pathutils.strip_path(path)
        if not sane_path:
            return "RW"  # Full access to root
            
        parts = unquote(sane_path).split('/')
        if not parts:
            return "RW"
            
        # Always allow access to own principal path
        if len(parts) <= 2 and parts[0] == user:
            return "RW"
        
        return ""

    def authorized(self, user: str, path: str, permissions: str) -> bool:
        """Check if user has permissions on path."""
        auth = self.authorization(user, path)
        return all(p in auth for p in permissions)
