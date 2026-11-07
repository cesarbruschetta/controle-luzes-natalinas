import unittest
from datetime import date

from luzes_natalino.clients.sunrise_sunset import SunriseSunsetClient
from luzes_natalino.clients.tuya_cloud import TuyaCloudClient
from luzes_natalino.services.light_control import set_lights
from luzes_natalino.settings import Settings


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {
            "status": "OK",
            "results": {"sunrise": "06:00:00", "sunset": "18:00:00"},
        }


class FakeSession:
    def __init__(self) -> None:
        self.url: str | None = None
        self.params: dict[str, object] | None = None

    def get(self, url: str, params: dict[str, object], timeout: float) -> FakeResponse:
        self.url = url
        self.params = params
        return FakeResponse()


class FakeCloud:
    error: object = None

    def __init__(self) -> None:
        self.device_id: str | None = None
        self.commands: dict[str, object] | None = None

    def sendcommand(self, deviceid: str, commands: dict[str, object]) -> object:
        self.device_id = deviceid
        self.commands = commands
        return {"success": True}


class ClientTests(unittest.TestCase):
    def test_sunrise_client_uses_requests_parameters_and_parses_times(self) -> None:
        session = FakeSession()
        client = SunriseSunsetClient(session=session)  # type: ignore[arg-type]

        times = client.get_sun_times(
            -23.5,
            -46.6,
            "UTC",
            query_date=date(2026, 11, 6),
        )

        self.assertEqual(times, {"sunrise": "06:00:00", "sunset": "18:00:00"})
        self.assertEqual(session.params["date"], "2026-11-06")
        self.assertEqual(session.params["time_format"], "24")

    def test_tuya_cloud_client_sends_expected_switch_command(self) -> None:
        settings = Settings(
            _env_file=None,
            tuya_device_id="device-id",
            tuya_api_key="api-key",
            tuya_api_secret="api-secret",
            tuya_api_region="us",
            tuya_switch_code="switch_2",
        )
        cloud = FakeCloud()
        client = TuyaCloudClient(settings, cloud=cloud)

        set_lights(client, "on")

        self.assertEqual(cloud.device_id, "device-id")
        self.assertEqual(
            cloud.commands,
            {"commands": [{"code": "switch_2", "value": True}]},
        )

    def test_rejects_invalid_light_action(self) -> None:
        with self.assertRaises(ValueError):
            set_lights(FakeCloud(), "toggle")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
