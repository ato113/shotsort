"""Records moves so a run can be undone."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

JOURNAL_FILE = Path.home() / ".local" / "share" / "shotsort" / "journal.jsonl"


@dataclass
class Move:
    source: str
    destination: str


def record(moves: list[Move], journal: Path = JOURNAL_FILE) -> None:
    if not moves:
        return
    journal.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "moves": [{"source": m.source, "destination": m.destination} for m in moves],
    }
    with journal.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def last_batch(journal: Path = JOURNAL_FILE) -> dict | None:
    if not journal.is_file():
        return None
    lines = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else None


def drop_last(journal: Path = JOURNAL_FILE) -> None:
    if not journal.is_file():
        return
    lines = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    journal.write_text("\n".join(lines[:-1]) + ("\n" if len(lines) > 1 else ""), encoding="utf-8")
