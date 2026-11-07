"""Configuração validada a partir das variáveis de ambiente."""

from __future__ import annotations

import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NATAL_", extra="ignore")

    latitude: float = -23.595211811344527
    longitude: float = -46.578204936374995
    timezone: str = "UTC"
    tuya_device_id: str
    tuya_api_key: SecretStr
    tuya_api_secret: SecretStr
    tuya_api_region: str
    tuya_switch_code: str = "switch_1"

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("latitude deve estar entre -90 e 90.")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("longitude deve estar entre -180 e 180.")
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError(f"Fuso horário IANA inválido: {value}") from error
        return value

    @field_validator("tuya_api_region")
    @classmethod
    def validate_tuya_region(cls, value: str) -> str:
        region = value.lower()
        if region not in {"cn", "us", "us-e", "eu", "eu-w", "in", "sg"}:
            raise ValueError("tuya_api_region deve ser cn, us, us-e, eu, eu-w, in ou sg.")
        return region

    @field_validator("tuya_switch_code")
    @classmethod
    def validate_switch_code(cls, value: str) -> str:
        switch_code = value.strip()
        if not switch_code:
            raise ValueError("tuya_switch_code não pode estar vazio.")
        return switch_code

    def cron_environment(self) -> dict[str, str]:
        values = {
            "NATAL_LATITUDE": str(self.latitude),
            "NATAL_LONGITUDE": str(self.longitude),
            "NATAL_TIMEZONE": self.timezone,
            "NATAL_TUYA_SWITCH_CODE": self.tuya_switch_code,
            "NATAL_TUYA_DEVICE_ID": self.tuya_device_id,
            "NATAL_TUYA_API_KEY": self.tuya_api_key.get_secret_value(),
            "NATAL_TUYA_API_SECRET": self.tuya_api_secret.get_secret_value(),
            "NATAL_TUYA_API_REGION": self.tuya_api_region,
        }

        for name, value in values.items():
            if not re.fullmatch(r"NATAL_[A-Z0-9_]+", name):
                raise ValueError(f"Nome de variável inválido para cron: {name!r}.")
            if any(character.isspace() or character == "\0" for character in value):
                raise ValueError(f"O valor de {name} não pode conter espaços, quebras de linha ou NUL.")
        return values

    def require_tuya_credentials(self) -> tuple[str, str, str, str]:
        if not self.tuya_device_id:
            raise ValueError("NATAL_TUYA_DEVICE_ID não pode estar vazio.")
        if not self.tuya_api_key.get_secret_value():
            raise ValueError("NATAL_TUYA_API_KEY não pode estar vazio.")
        if not self.tuya_api_secret.get_secret_value():
            raise ValueError("NATAL_TUYA_API_SECRET não pode estar vazio.")
        return (
            self.tuya_device_id,
            self.tuya_api_key.get_secret_value(),
            self.tuya_api_secret.get_secret_value(),
            self.tuya_api_region,
        )
