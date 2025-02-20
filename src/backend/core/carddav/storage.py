from contextlib import nullcontext
from typing import Iterator, Optional, Callable, ContextManager, Iterable, Set, Mapping
from urllib.parse import unquote

from radicale.storage import BaseCollection, BaseStorage
from radicale import pathutils, types

from core.carddav.collection import Collection


@types.contextmanager
def _null_child_context_manager(
        path: str,
        href: Optional[str]
) -> Iterator[None]:
    yield

class Storage(BaseStorage):
    _collection_class = Collection

    def discover(
            self, path: str, depth: str = "0",
            child_context_manager: Optional[
                Callable[[str, Optional[str]], ContextManager[None]]] = None,
            user_groups: Optional[Set[str]] = None,
    ) -> Iterable["types.CollectionOrItem"]:
        if child_context_manager is None:
            child_context_manager = _null_child_context_manager

        sane_path = pathutils.strip_path(path)
        collection_types = ["organization", "personal"]

        if not sane_path:  # Root path
            with child_context_manager(sane_path, None):
                root = Collection(self, "")
                root.user = "admin@example.com"
                yield root
            return

        parts = unquote(sane_path).split("/")
        user_email = parts[0]

        with child_context_manager(sane_path, None):
            if len(parts) == 1:  # Principal path
                principal = Collection(self, sane_path)
                principal._is_principal = True
                principal.user = user_email
                yield principal

                if depth != "0":  # List address books if depth > 0
                    for col_type in collection_types:
                        child_path = f"{user_email}/{col_type}"
                        with child_context_manager(child_path, None):
                            child = Collection(self, child_path)
                            child.user = user_email
                            child.collection_type = col_type
                            yield child

            elif len(parts) >= 2 and parts[1] in collection_types:
                collection = Collection(self, sane_path)
                collection.user = user_email
                collection.collection_type = parts[1]
                yield collection

    def move(self, item: "radicale_item.Item", to_collection: BaseCollection,
             to_href: str) -> None:
        raise NotImplementedError

    def create_collection(
            self, href: str,
            items: Optional[Iterable["radicale_item.Item"]] = None,
            props: Optional[Mapping[str, str]] = None) -> BaseCollection:
        raise NotImplementedError

    @types.contextmanager
    def acquire_lock(self, mode: str, user: str = "") -> Iterator[None]:
        """Set a context manager to lock the whole storage.

        ``mode`` must either be "r" for shared access or "w" for exclusive
        access.

        ``user`` is the name of the logged in user or empty.

        """
        yield
