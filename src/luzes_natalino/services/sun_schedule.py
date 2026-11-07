"""Geração e instalação do agendamento diário das luzes."""

from __future__ import annotations

import re
import shlex
import sys
from collections.abc import Mapping

from luzes_natalino.utils.cron import BEGIN_MARKER, END_MARKER, cron_minute


def make_cron_block(
    timezone: str,
    sunrise: str,
    sunset: str,
    environment: Mapping[str, str] | None = None,
    python_executable: str | None = None,
) -> str:
    python = shlex.quote(python_executable or sys.executable)
    scheduler_command = f"{python} -m luzes_natalino.cli_schedule"
    controller_command = f"{python} -m luzes_natalino.cli_control"
    sunrise_minute, sunrise_hour = cron_minute(sunrise)
    sunset_minute, sunset_hour = cron_minute(sunset)
    environment_lines = []
    for name, value in (environment or {}).items():
        if not re.fullmatch(r"NATAL_[A-Z0-9_]+", name) or any(
            character.isspace() or character == "\0" for character in value
        ):
            raise ValueError(f"Valor de ambiente inválido para cron: {name!r}.")
        environment_lines.append(f"{name}={value}")

    return "\n".join(
        (
            BEGIN_MARKER,
            *environment_lines,
            f"CRON_TZ={timezone}",
            f"0 1 * * * {scheduler_command}",
            f"{sunset_minute} {sunset_hour} * * * {controller_command} --action on",
            f"{sunrise_minute} {sunrise_hour} * * * {controller_command} --action off",
            END_MARKER,
        )
    )
