"""لایه API — Flask. فقط HTTP را مدیریت می‌کند؛ منطق در workflow است.

Endpointها:
  POST /api/ask          {question, user_name?} → جواب + ticket_id
  GET  /api/tickets      لیست تیکت‌های ثبت‌شده
  GET  /api/tickets/<id> جزئیات یک تیکت
  GET  /api/categories   دسته‌بندی‌های پیش‌فرض
  GET  /health
  GET  /                 صفحه چت ساده
"""
from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from ..classifier.categories import CATEGORIES
from ..config import KNOWLEDGE_BASE_PATH, TICKETS_PATH
from ..rag.knowledge_base import KnowledgeBase
from ..tickets.repository import TicketRepository
from ..tickets.service import TicketService
from ..workflow.engine import CrmWorkflow

STATIC_DIR = Path(__file__).parent / "static"


def create_app(kb_path=KNOWLEDGE_BASE_PATH, tickets_path=TICKETS_PATH) -> Flask:
    app = Flask(__name__)
    workflow = CrmWorkflow(
        kb=KnowledgeBase(kb_path),
        ticket_service=TicketService(TicketRepository(tickets_path)),
    )
    tickets_repo = workflow.ticket_service.repository

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.get("/api/categories")
    def categories():
        return jsonify([
            {"id": c.id, "name_fa": c.name_fa, "description": c.description}
            for c in CATEGORIES
        ])

    @app.post("/api/ask")
    def ask():
        body = request.get_json(silent=True) or {}
        question = (body.get("question") or "").strip()
        if not question:
            return jsonify({"error": "فیلد question الزامی است"}), 400
        result = workflow.run(question, user_name=body.get("user_name"))
        return jsonify(result.to_dict())

    @app.get("/api/tickets")
    def tickets():
        return jsonify(tickets_repo.all())

    @app.get("/api/tickets/<ticket_id>")
    def ticket_detail(ticket_id: str):
        ticket = tickets_repo.get(ticket_id)
        if ticket is None:
            return jsonify({"error": "تیکت پیدا نشد"}), 404
        return jsonify(ticket)

    return app
