from typing import Any, Iterator, Optional
from urllib.parse import parse_qs, urlparse

from .services.events_provider_client import EventsProviderClient


class EventsPaginator:
    """Итератор для постраничной загрузки событий из Events Provider API."""

    def __init__(self, client: EventsProviderClient, changed_at: str):
        self.client = client
        self.changed_at = changed_at
        self._current_page = None
        self._items = []
        self._index = 0

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return self

    def __next__(self) -> dict[str, Any]:
        if self._items is None:
            raise StopIteration
        if self._index >= len(self._items):
            self._fetch_next_page()
            if self._index >= len(self._items):
                raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item

    def _fetch_next_page(self) -> None:
        if self._current_page is None:
            self._current_page = self.client.events(self.changed_at)
        else:
            next_url = self._current_page.get("next")
            if not next_url:
                self._items = []
                return
            cursor = self._extract_cursor(next_url)
            if cursor is None:
                self._items = []
                return
            self._current_page = self.client.events(self.changed_at, cursor=cursor)
        self._items = self._current_page.get("results", [])
        self._index = 0

    def _extract_cursor(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        cursors = query_params.get("cursor")
        return cursors[0] if cursors else None
