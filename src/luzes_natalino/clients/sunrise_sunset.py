"""Cliente HTTP para a API Sunrise Sunset."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests


class SunriseSunsetClient:
    API_URL = "https://api.sunrisesunset.io/json"

    def __init__(self, session: requests.Session | None = None, timeout: float = 20) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout

    def get_sun_times(
        self,
        latitude: float,
        longitude: float,
        timezone: str,
        query_date: date | None = None,
    ) -> dict[str, str]:
        solar_date = query_date or datetime.now(ZoneInfo(timezone)).date()
        response = self._session.get(
            self.API_URL,
            params={
                "lat": latitude,
                "lng": longitude,
                "date": solar_date.isoformat(),
                "timezone": timezone,
                "time_format": "24",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload: Any = response.json()

        if not isinstance(payload, dict) or payload.get("status") != "OK":
            raise RuntimeError(f"A API Sunrise Sunset retornou uma resposta inesperada: {payload!r}")
        results = payload.get("results")
        if not isinstance(results, dict):
            raise RuntimeError("A API Sunrise Sunset não retornou o objeto 'results'.")

        sunrise = results.get("sunrise")
        sunset = results.get("sunset")
        if not isinstance(sunrise, str) or not isinstance(sunset, str):
            raise RuntimeError("A API Sunrise Sunset não retornou sunrise e sunset válidos.")
        return {"sunrise": sunrise, "sunset": sunset}
