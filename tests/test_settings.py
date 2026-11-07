import unittest
from unittest.mock import patch

from pydantic import SecretStr, ValidationError

from luzes_natalino.settings import Settings


class SettingsTests(unittest.TestCase):
    def make_settings(self, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "_env_file": None,
            "tuya_device_id": "device-id",
            "tuya_api_key": "api-key",
            "tuya_api_secret": "api-secret",
            "tuya_api_region": "eu",
        }
        values.update(overrides)
        return Settings(**values)

    def test_validates_coordinates_and_timezone(self) -> None:
        settings = self.make_settings(
            latitude=-23.5, longitude=-46.6, timezone="America/Sao_Paulo"
        )

        self.assertEqual(settings.timezone, "America/Sao_Paulo")

    def test_rejects_invalid_coordinates(self) -> None:
        with self.assertRaises(ValidationError):
            self.make_settings(latitude=91)

    def test_requires_all_tuya_configuration(self) -> None:
        for field in ("tuya_device_id", "tuya_api_key", "tuya_api_secret", "tuya_api_region"):
            with self.subTest(field=field):
                values: dict[str, object] = {
                    "tuya_device_id": "device-id",
                    "tuya_api_key": "api-key",
                    "tuya_api_secret": "api-secret",
                    "tuya_api_region": "eu",
                }
                del values[field]
                with self.assertRaises(ValidationError):
                    Settings(_env_file=None, **values)

    def test_cloud_secrets_are_redacted_and_required_for_control(self) -> None:
        settings = self.make_settings(
            tuya_api_key=SecretStr("api-key"),
            tuya_api_secret=SecretStr("api-secret"),
            tuya_api_region="EU",
        )

        self.assertNotIn("api-secret", repr(settings))
        self.assertEqual(settings.require_tuya_credentials(), ("device-id", "api-key", "api-secret", "eu"))

    def test_loads_values_from_standard_environment_variables(self) -> None:
        environment = {
            "NATAL_LATITUDE": "-12.5",
            "NATAL_LONGITUDE": "-45.5",
            "NATAL_TIMEZONE": "America/Sao_Paulo",
            "NATAL_TUYA_DEVICE_ID": "device-id",
            "NATAL_TUYA_API_KEY": "api-key",
            "NATAL_TUYA_API_SECRET": "api-secret",
            "NATAL_TUYA_API_REGION": "EU",
        }
        with patch.dict("os.environ", environment):
            settings = Settings(_env_file=None)

        self.assertEqual(settings.latitude, -12.5)
        self.assertEqual(settings.tuya_api_region, "eu")
        self.assertEqual(settings.cron_environment()["NATAL_TUYA_API_SECRET"], "api-secret")

    def test_cron_environment_includes_required_tuya_credentials(self) -> None:
        settings = self.make_settings()

        self.assertEqual(settings.cron_environment()["NATAL_TUYA_API_SECRET"], "api-secret")


if __name__ == "__main__":
    unittest.main()
