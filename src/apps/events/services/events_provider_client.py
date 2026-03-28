import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class EventsProviderClient:
    """Клиент для взаимодействия с Events Provider API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout, trust_env=False)

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key}

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Выполняет HTTP-запрос и возвращает JSON."""
        url = f"{self.base_url}{path}"
        headers = self._headers()

        logger.debug("Sending %s request to %s with params %s, json %s",
                     method, url, kwargs.get('params'), kwargs.get('json'))

        try:
            response = self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            logger.debug("Response status: %s, body: %s", response.status_code, response.text)
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error %s for %s: %s", e.response.status_code, url, e.response.text)
            raise
        except httpx.RequestError as e:
            logger.error("Request error for %s: %s", url, e)
            raise

    def events(self, changed_at: str, cursor: Optional[str] = None) -> dict[str, Any]:
        """Получить список событий, изменённых после указанной даты."""
        params = {"changed_at": changed_at}
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/api/events/", params=params)

    def seats(self, event_id: str) -> dict[str, Any]:
        """Получить список свободных мест для события."""
        return self._request("GET", f"/api/events/{event_id}/seats/")

    def register(self, event_id: str, first_name: str, last_name: str,
                 email: str, seat: str) -> dict[str, Any]:
        """Зарегистрировать участника на событие."""
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        return self._request("POST", f"/api/events/{event_id}/register/", json=data)

    def unregister(self, event_id: str, ticket_id: str) -> dict[str, Any]:
        """Отменить регистрацию по ticket_id."""
        data = {"ticket_id": ticket_id}
        return self._request("DELETE", f"/api/events/{event_id}/unregister/", json=data)