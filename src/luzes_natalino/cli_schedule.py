"""CLI que atualiza os horários do sol no crontab."""

from __future__ import annotations

import sys

import requests
from pydantic import ValidationError

from luzes_natalino.clients.sunrise_sunset import SunriseSunsetClient
from luzes_natalino.services.sun_schedule import make_cron_block
from luzes_natalino.settings import Settings
from luzes_natalino.utils.cron import install_crontab, read_crontab, replace_managed_block


def main() -> int:
    try:
        settings = Settings()
        settings.require_tuya_credentials()
        sun_times = SunriseSunsetClient().get_sun_times(
            settings.latitude,
            settings.longitude,
            settings.timezone,
        )
        block = make_cron_block(
            settings.timezone,
            sun_times["sunrise"],
            sun_times["sunset"],
            environment=settings.cron_environment(),
        )
        install_crontab(replace_managed_block(read_crontab(), block))
    except (OSError, ValueError, RuntimeError, requests.RequestException, ValidationError) as error:
        print(f"Erro ao agendar as luzes: {error}", file=sys.stderr)
        return 1

    print(
        f"Crontab atualizado para {settings.timezone}: ligar no pôr do sol "
        f"({sun_times['sunset']}) e desligar no nascer do sol ({sun_times['sunrise']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
