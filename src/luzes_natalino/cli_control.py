"""CLI para ligar e desligar as luzes via Tuya Cloud."""

from __future__ import annotations

import argparse
import sys

import requests
from pydantic import ValidationError

from luzes_natalino.clients.tuya_cloud import TuyaCloudClient
from luzes_natalino.services.light_control import set_lights
from luzes_natalino.settings import Settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Controla a tomada das luzes de Natal pela Tuya Cloud.")
    parser.add_argument("--action", choices=("on", "off"), required=True)
    args = parser.parse_args()

    try:
        settings = Settings()
        set_lights(TuyaCloudClient(settings), args.action)
    except (OSError, ValueError, RuntimeError, requests.RequestException, ValidationError) as error:
        verb = "ligar" if args.action == "on" else "desligar"
        print(f"Não foi possível {verb} a tomada: {error}", file=sys.stderr)
        return 1

    verb = "ligar" if args.action == "on" else "desligar"
    print(f"Comando para {verb} a tomada enviado pela Tuya Cloud.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
