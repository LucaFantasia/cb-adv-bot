from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import requests
from requests import Session
from requests.exceptions import ConnectionError, RequestException, Timeout

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass
class HttpResponse:
    ok: bool
    status_code: int
    json: Any
    text: str
    headers: dict[str, str]


class HttpError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def make_idempotency_key() -> str:
    return str(uuid.uuid4())


class HttpClient:
    def __init__(
        self,
        session: Session | None = None,
        timeout: tuple[float, float] = (5.0, 15.0),
        max_retries: int = 4,
        backoff_base: float = 0.5,
        backoff_cap: float = 8.0,
    ) -> None:
        self._s = session or requests.Session()
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._backoff_cap = backoff_cap

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | None = None,
    ) -> HttpResponse:
        attempt = 0
        last_exc: Exception | None = None
        while True:
            try:
                r = self._s.request(
                    method, url, headers=headers, params=params, data=data, timeout=self._timeout
                )
                if not self._should_retry_response(r):
                    return self._to_response(r)
                delay = self._retry_delay(r, attempt)
            except (ConnectionError, Timeout) as e:
                last_exc = e
                if attempt >= self._max_retries:
                    raise HttpError(f"Network error on {method} {url}: {e}") from e
                delay = self._jitter_backoff(attempt)
            except RequestException as e:
                raise HttpError(f"Request error on {method} {url}: {e}") from e
            attempt += 1
            if attempt > self._max_retries:
                if "r" in locals():
                    return self._to_response(r)
                if last_exc:
                    raise HttpError(f"Max retries exceeded for {method} {url}") from last_exc
                raise HttpError(f"Max retries exceeded for {method} {url}")
            time.sleep(delay)

    @staticmethod
    def _to_response(r: requests.Response) -> HttpResponse:
        try:
            payload = r.json() if r.content else None
        except ValueError:
            payload = None
        headers = {k.lower(): v for k, v in r.headers.items()}
        return HttpResponse(r.ok, r.status_code, payload, r.text or "", headers)

    @staticmethod
    def _should_retry_response(r: requests.Response) -> bool:
        return r.status_code in (429, 500, 502, 503, 504)

    def _retry_delay(self, r: requests.Response, attempt: int) -> float:
        ra = r.headers.get("Retry-After") or r.headers.get("retry-after")
        if ra:
            try:
                seconds = float(ra)
                return min(seconds, self._backoff_cap)
            except ValueError:
                pass
        return self._jitter_backoff(attempt)

    def _jitter_backoff(self, attempt: int) -> float:
        exp = min(self._backoff_cap, self._backoff_base * (2**attempt))
        return random.uniform(0, exp)
