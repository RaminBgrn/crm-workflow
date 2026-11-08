"""مدل‌های داده مشترک پروژه — فقط dataclass، بدون وابستگی خارجی."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ClassificationResult:
    category_id: str          # sales | support | technical
    category_fa: str          # فروش | پشتیبانی | واحد فنی
    confidence: float         # 0.0 .. 1.0
    matched_keywords: list[str] = field(default_factory=list)
    is_default: bool = False  # True یعنی هیچ کلیدواژه‌ای نخورد و پیش‌فرض انتخاب شد

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RetrievedAnswer:
    found: bool
    answer: str | None
    source_id: str | None     # id آیتم پایگاه دانش، مثل sales-001
    source_question: str | None
    score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Ticket:
    ticket_id: str
    question: str
    category_id: str
    category_fa: str
    answer: str
    found_in_kb: bool
    source_id: str | None
    status: str               # auto_resolved | open
    user_name: str | None = None
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkflowResult:
    """خروجی نهایی فلو — همان چیزی که API به کاربر برمی‌گرداند."""
    ticket_id: str
    question: str
    classification: ClassificationResult
    answer: str
    found_in_kb: bool
    source_id: str | None
    status: str

    def to_dict(self) -> dict:
        data = asdict(self)
        return data
