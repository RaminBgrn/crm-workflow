"""ذخیره‌سازی تیکت‌ها در فایل JSON — ریپازیتوری ساده و قابل جایگزینی با دیتابیس."""
from __future__ import annotations

import json
from pathlib import Path

from ..config import TICKETS_PATH


class TicketRepository:
    def __init__(self, path: Path | str = TICKETS_PATH):
        self.path = Path(path)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save(self, tickets: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, ticket_dict: dict) -> dict:
        tickets = self._load()
        tickets.append(ticket_dict)
        self._save(tickets)
        return ticket_dict

    def all(self) -> list[dict]:
        return self._load()

    def get(self, ticket_id: str) -> dict | None:
        return next((t for t in self._load() if t["ticket_id"] == ticket_id), None)

    def count(self) -> int:
        return len(self._load())
