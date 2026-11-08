"""سرویس تیکت — ساخت تیکت با شناسه یکتا و وضعیت مشخص."""
from __future__ import annotations

from datetime import datetime, timezone

from ..models import Ticket
from .repository import TicketRepository


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def _next_ticket_id(self) -> str:
        """مثال: TKT-20261108-0001 — تاریخ + شماره ترتیبی روزانه"""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        todays = [t for t in self.repository.all()
                  if t["ticket_id"].startswith(f"TKT-{today}-")]
        return f"TKT-{today}-{len(todays) + 1:04d}"

    def create(self, *, question: str, category_id: str, category_fa: str,
               answer: str, found_in_kb: bool, source_id: str | None,
               user_name: str | None = None) -> Ticket:
        ticket = Ticket(
            ticket_id=self._next_ticket_id(),
            question=question,
            category_id=category_id,
            category_fa=category_fa,
            answer=answer,
            found_in_kb=found_in_kb,
            source_id=source_id,
            # اگر جواب از پایگاه دانش آمد، تیکت خودکار حل‌شده است؛
            # وگرنه باز می‌ماند تا کارشناس همان واحد جواب دهد.
            status="auto_resolved" if found_in_kb else "open",
            user_name=user_name,
        )
        self.repository.add(ticket.to_dict())
        return ticket
