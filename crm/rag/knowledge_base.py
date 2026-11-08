"""بارگذاری پایگاه دانش JSON.

ساختار فایل knowledge_base.json:
{
  "categories": [
    {"id": "sales", "name_fa": "فروش",
     "items": [{"id": "sales-001", "question": "...",
                "keywords": ["..."], "answer": "..."}]}
  ]
}
"""
from __future__ import annotations

import json
from pathlib import Path

from ..config import KNOWLEDGE_BASE_PATH


class KnowledgeBase:
    def __init__(self, path: Path | str = KNOWLEDGE_BASE_PATH):
        self.path = Path(path)
        with self.path.open(encoding="utf-8") as f:
            raw = json.load(f)
        self._by_category: dict[str, list[dict]] = {
            cat["id"]: cat.get("items", []) for cat in raw.get("categories", [])
        }

    def items_for(self, category_id: str) -> list[dict]:
        return self._by_category.get(category_id, [])

    def categories(self) -> list[str]:
        return list(self._by_category.keys())
