"""Cliente TinyTuya para comandos via Tuya Cloud."""

from __future__ import annotations

from typing import Protocol

from luzes_natalino.settings import Settings


class CloudApi(Protocol):
    error: object

    def sendcommand(self, deviceid: str, commands: dict[str, object]) -> object: ...


class TuyaCloudClient:
    def __init__(self, settings: Settings, cloud: CloudApi | None = None) -> None:
        device_id, api_key, api_secret, region = settings.require_tuya_credentials()
        if cloud is None:
            try:
                import tinytuya
            except ImportError as error:
                raise RuntimeError(
                    "TinyTuya não está instalado; execute `poetry install`."
                ) from error

            cloud = tinytuya.Cloud(
                apiRegion=region,
                apiKey=api_key,
                apiSecret=api_secret,
                apiDeviceID=device_id,
            )

        if cloud.error:
            raise RuntimeError(f"Falha ao autenticar na Tuya Cloud: {cloud.error}")
        self._cloud = cloud
        self._device_id = device_id
        self._switch_code = settings.tuya_switch_code

    def set_power(self, enabled: bool) -> dict[str, object]:
        response = self._cloud.sendcommand(
            self._device_id,
            {"commands": [{"code": self._switch_code, "value": enabled}]},
        )
        if not isinstance(response, dict) or response.get("success") is not True:
            if isinstance(response, dict):
                code = response.get("code", "desconhecido")
                message = response.get("msg", "resposta inválida da API")
                raise RuntimeError(f"Tuya Cloud rejeitou o comando (código {code}): {message}")
            raise RuntimeError("Tuya Cloud retornou uma resposta inválida ao comando.")
        return response
