#!/usr/bin/env python3
"""Compatibility entry point for older crontab entries."""

from luzes_natalino.cli_schedule import main


if __name__ == "__main__":
    raise SystemExit(main())
