"""ماژول دسته‌بندی (Classification)

سؤال کاربر را تحلیل می‌کند و آن را در یکی از دسته‌های پیش‌فرض
(فروش / پشتیبانی / واحد فنی) قرار می‌دهد.

الگوریتم فعلی: امتیازدهی بر اساس کلیدواژه — ساده، قابل توضیح و بدون
وابستگی. برای نسخه پیشرفته‌تر می‌توان همین اینترفیس (classify) را
با یک مدل ML یا LLM پیاده کرد، بدون این‌که بقیه سیستم عوض شود.
"""
from __future__ import annotations

import re

from ..config import DEFAULT_CATEGORY_ID
from ..models import ClassificationResult
from .categories import CATEGORIES, CATEGORY_BY_ID

_PUNCT = re.compile(r"[؟?!.،,؛;:\(\)\[\]«»\"']")


def normalize(text: str) -> str:
    """نرمال‌سازی متن فارسی/انگلیسی برای مقایسه."""
    text = (text or "").strip().lower()
    text = text.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    text = _PUNCT.sub(" ", text)
    return re.sub(r"\s+", " ", text)


def classify(question: str) -> ClassificationResult:
    normalized = normalize(question)

    scores: dict[str, list[str]] = {}
    for category in CATEGORIES:
        hits = [kw for kw in category.keywords if normalize(kw) in normalized]
        if hits:
            scores[category.id] = hits

    if not scores:
        default = CATEGORY_BY_ID[DEFAULT_CATEGORY_ID]
        return ClassificationResult(
            category_id=default.id,
            category_fa=default.name_fa,
            confidence=0.0,
            matched_keywords=[],
            is_default=True,
        )

    # بیشترین تعداد کلیدواژه برنده است؛ در تساوی، اولین دسته در لیست تعریف
    best_id = max(CATEGORIES, key=lambda c: len(scores.get(c.id, []))).id
    total_hits = sum(len(v) for v in scores.values())
    best = CATEGORY_BY_ID[best_id]
    return ClassificationResult(
        category_id=best.id,
        category_fa=best.name_fa,
        confidence=round(len(scores[best_id]) / total_hits, 2),
        matched_keywords=scores[best_id],
        is_default=False,
    )
