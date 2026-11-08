"""موتور Workflow — ارکستریتور کل فلو.

فلو (به ترتیب):
  1) تحلیل و دسته‌بندی سؤال        → classifier.classify
  2) جستجو در پایگاه دانش (RAG)    → rag.retrieve  (فقط داخل همان دسته)
  3) ساخت جواب: اگر در پایگاه دانش بود همان جواب آماده،
     وگرنه پیام ارجاع به واحد مربوطه
  4) ثبت تیکت — در هر صورت، چه جواب پیدا شود چه نشود
  5) برگرداندن جواب + شناسه تیکت به کاربر
"""
from __future__ import annotations

from ..classifier.classifier import classify
from ..models import WorkflowResult
from ..rag.knowledge_base import KnowledgeBase
from ..rag.retriever import retrieve
from ..tickets.service import TicketService

FALLBACK_TEMPLATE = (
    "سؤال شما در دسته «{category_fa}» قرار گرفت، اما پاسخ آماده‌ای برای آن "
    "در پایگاه دانش پیدا نشد. تیکت شما ثبت و به کارشناسان {category_fa} "
    "ارجاع شد؛ پاسخ از طریق همین تیکت پیگیری می‌شود."
)


class CrmWorkflow:
    def __init__(self, kb: KnowledgeBase, ticket_service: TicketService):
        self.kb = kb
        self.ticket_service = ticket_service

    def run(self, question: str, user_name: str | None = None) -> WorkflowResult:
        question = (question or "").strip()
        if not question:
            raise ValueError("question نباید خالی باشد")

        # ۱) دسته‌بندی
        classification = classify(question)

        # ۲) و ۳) بازیابی RAG و ساخت جواب
        retrieved = retrieve(self.kb, classification.category_id, question)
        if retrieved.found:
            answer = retrieved.answer or ""
        else:
            answer = FALLBACK_TEMPLATE.format(category_fa=classification.category_fa)

        # ۴) ثبت تیکت — همیشه
        ticket = self.ticket_service.create(
            question=question,
            category_id=classification.category_id,
            category_fa=classification.category_fa,
            answer=answer,
            found_in_kb=retrieved.found,
            source_id=retrieved.source_id,
            user_name=user_name,
        )

        # ۵) خروجی
        return WorkflowResult(
            ticket_id=ticket.ticket_id,
            question=question,
            classification=classification,
            answer=answer,
            found_in_kb=retrieved.found,
            source_id=retrieved.source_id,
            status=ticket.status,
        )
