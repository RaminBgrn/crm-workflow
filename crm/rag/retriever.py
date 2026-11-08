"""ماژول بازیابی RAG (Retrieval)

در دسته‌ای که کلاسیفایر مشخص کرده، داخل پایگاه دانش JSON جستجو می‌کند
و نزدیک‌ترین سؤال/جواب آماده را برمی‌گرداند.

امتیاز هر آیتم = تعداد کلیدواژه‌های مشترک + تعداد واژه‌های مشترک با
متن سؤالِ ذخیره‌شده. این پیاده‌سازی ساده و بدون وابستگی است؛ در نسخه
پیشرفته می‌توان همین اینترفیس (retrieve) را با Embedding و جستجوی
برداری (Vector DB) جایگزین کرد — بقیه سیستم دست نمی‌خورد.
"""
from __future__ import annotations

from ..classifier.classifier import normalize
from ..config import RETRIEVAL_MIN_SCORE
from ..models import RetrievedAnswer
from .knowledge_base import KnowledgeBase


def _score(question_norm: str, item: dict) -> float:
    score = 0.0
    for kw in item.get("keywords", []):
        if normalize(kw) in question_norm:
            score += 2.0  # کلیدواژه وزن بیشتری از واژه عادی دارد
    question_words = set(normalize(item.get("question", "")).split())
    asked_words = set(question_norm.split())
    score += len(question_words & asked_words)
    return score


def retrieve(kb: KnowledgeBase, category_id: str, question: str) -> RetrievedAnswer:
    question_norm = normalize(question)
    best_item, best_score = None, 0.0
    for item in kb.items_for(category_id):
        s = _score(question_norm, item)
        if s > best_score:
            best_item, best_score = item, s

    if best_item is None or best_score < RETRIEVAL_MIN_SCORE:
        return RetrievedAnswer(found=False, answer=None, source_id=None,
                               source_question=None, score=best_score)
    return RetrievedAnswer(
        found=True,
        answer=best_item["answer"],
        source_id=best_item["id"],
        source_question=best_item["question"],
        score=best_score,
    )
