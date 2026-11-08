"""تنظیمات مرکزی پروژه — همه مسیرها و ثابت‌ها این‌جا."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# پایگاه دانش RAG (JSON)
KNOWLEDGE_BASE_PATH = Path(
    os.environ.get("CRM_KB_PATH", BASE_DIR / "crm" / "rag" / "data" / "knowledge_base.json")
)

# محل ذخیره تیکت‌ها (JSON) — در ران‌تایم ساخته می‌شود
TICKETS_PATH = Path(
    os.environ.get("CRM_TICKETS_PATH", BASE_DIR / "data" / "tickets.json")
)

# دسته پیش‌فرض وقتی هیچ کلیدواژه‌ای به سؤال نمی‌خورد
DEFAULT_CATEGORY_ID = "support"

# حداقل امتیاز بازیابی برای این‌که جواب «پیدا شده» حساب شود
RETRIEVAL_MIN_SCORE = 1.0
