"""Operações de baixo nível sobre expressões e crontab."""

from __future__ import annotations

import subprocess
from datetime import datetime


BEGIN_MARKER = "# BEGIN luzes-natal gerenciado"
END_MARKER = "# END luzes-natal gerenciado"


def cron_minute(time_value: str) -> tuple[int, int]:
    try:
        parsed_time = datetime.strptime(time_value, "%H:%M:%S").time()
    except ValueError as error:
        raise ValueError(f"Horário solar inválido recebido da API: {time_value!r}") from error

    minute_of_day = parsed_time.hour * 60 + parsed_time.minute + (parsed_time.second > 0)
    minute_of_day %= 24 * 60
    return minute_of_day % 60, minute_of_day // 60


def replace_managed_block(crontab: str, new_block: str) -> str:
    lines = crontab.splitlines()
    begin_positions = [index for index, line in enumerate(lines) if line == BEGIN_MARKER]
    end_positions = [index for index, line in enumerate(lines) if line == END_MARKER]
    if len(begin_positions) != len(end_positions) or len(begin_positions) > 1:
        raise ValueError("O crontab contém marcadores do agendador inconsistentes ou duplicados.")
    if begin_positions and begin_positions[0] > end_positions[0]:
        raise ValueError("A ordem dos marcadores do agendador no crontab está inválida.")
    if begin_positions:
        del lines[begin_positions[0] : end_positions[0] + 1]

    preserved = "\n".join(lines).rstrip()
    return f"{preserved}\n\n{new_block}\n" if preserved else f"{new_block}\n"


def read_crontab() -> str:
    result = subprocess.run(
        ["crontab", "-l"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout
    if "no crontab for" in result.stderr.lower():
        return ""
    raise RuntimeError(f"Não foi possível ler o crontab: {result.stderr.strip()}")


def install_crontab(crontab: str) -> None:
    result = subprocess.run(
        ["crontab", "-"],
        input=crontab,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Não foi possível atualizar o crontab: {result.stderr.strip()}")
