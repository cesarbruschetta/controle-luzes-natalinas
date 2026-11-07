"""Casos de uso para controle das luzes."""

from __future__ import annotations

from typing import Protocol


class PowerControlClient(Protocol):
    def set_power(self, enabled: bool) -> dict[str, object]: ...


def set_lights(client: PowerControlClient, action: str) -> dict[str, object]:
    if action not in {"on", "off"}:
        raise ValueError("A ação deve ser 'on' ou 'off'.")
    return client.set_power(enabled=action == "on")
