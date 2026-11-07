import unittest

from luzes_natalino.services.sun_schedule import make_cron_block
from luzes_natalino.utils.cron import (
    BEGIN_MARKER,
    END_MARKER,
    cron_minute,
    replace_managed_block,
)


class CronScheduleTests(unittest.TestCase):
    def test_rounds_up_only_when_seconds_are_present(self) -> None:
        self.assertEqual(cron_minute("08:12:00"), (12, 8))
        self.assertEqual(cron_minute("08:12:01"), (13, 8))
        self.assertEqual(cron_minute("23:59:30"), (0, 0))

    def test_schedule_block_uses_package_commands_and_timezone(self) -> None:
        block = make_cron_block(
            "America/Sao_Paulo",
            "08:12:58",
            "21:27:15",
            environment={
                "NATAL_LATITUDE": "-23.5",
                "NATAL_TUYA_API_KEY": "access-key",
            },
            python_executable="/opt/python/bin/python",
        )

        self.assertIn("CRON_TZ=America/Sao_Paulo", block)
        self.assertIn("NATAL_LATITUDE=-23.5", block)
        self.assertIn("NATAL_TUYA_API_KEY=access-key", block)
        self.assertIn("0 1 * * *", block)
        self.assertRegex(block, r"28 21 \* \* \* .*cli_control --action on")
        self.assertRegex(block, r"13 8 \* \* \* .*cli_control --action off")

    def test_rejects_whitespace_in_cron_environment_values(self) -> None:
        with self.assertRaises(ValueError):
            make_cron_block("UTC", "08:12:00", "21:27:00", environment={"NATAL_X": "a b"})

    def test_managed_block_preserves_other_cron_jobs(self) -> None:
        existing = "MAILTO=user@example.com\n0 4 * * * /usr/bin/backup\n"
        block = make_cron_block("UTC", "08:12:58", "21:27:15")

        updated = replace_managed_block(existing, block)
        self.assertIn("0 4 * * * /usr/bin/backup", updated)
        self.assertEqual(updated.count(BEGIN_MARKER), 1)
        self.assertEqual(updated.count(END_MARKER), 1)

    def test_replaces_existing_managed_block(self) -> None:
        original_block = f"{BEGIN_MARKER}\nold schedule\n{END_MARKER}"
        updated = replace_managed_block(f"0 4 * * * /usr/bin/backup\n{original_block}", "new schedule")

        self.assertNotIn("old schedule", updated)
        self.assertIn("new schedule", updated)
        self.assertIn("0 4 * * * /usr/bin/backup", updated)

    def test_rejects_malformed_managed_block(self) -> None:
        with self.assertRaises(ValueError):
            replace_managed_block(f"{END_MARKER}\n{BEGIN_MARKER}", "new schedule")


if __name__ == "__main__":
    unittest.main()
