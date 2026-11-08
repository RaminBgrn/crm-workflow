"""تست‌های فلو کامل — اجرا: python -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crm.classifier.classifier import classify
from crm.rag.knowledge_base import KnowledgeBase
from crm.rag.retriever import retrieve
from crm.tickets.repository import TicketRepository
from crm.tickets.service import TicketService
from crm.workflow.engine import CrmWorkflow


class ClassifierTest(unittest.TestCase):
    def test_sales(self):
        self.assertEqual(classify("قیمت پلن‌ها چقدره؟ می‌خوام بخرم").category_id, "sales")

    def test_support(self):
        self.assertEqual(classify("رمز عبورم را فراموش کردم").category_id, "support")

    def test_technical(self):
        self.assertEqual(classify("برنامه نصب نمیشه و خطا میده").category_id, "technical")

    def test_unknown_defaults_to_support(self):
        result = classify("سلام، ممنون از لطفتون")
        self.assertEqual(result.category_id, "support")
        self.assertTrue(result.is_default)


class RagTest(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()

    def test_finds_answer_in_own_category(self):
        r = retrieve(self.kb, "sales", "قیمت پلن و تعرفه اشتراک چنده؟")
        self.assertTrue(r.found)
        self.assertEqual(r.source_id, "sales-001")

    def test_no_answer_for_unrelated_question(self):
        r = retrieve(self.kb, "technical", "قیمت پلن چنده؟")
        self.assertFalse(r.found)  # جستجو فقط داخل دسته فنی است


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        self.repo = TicketRepository(tmp.name)
        self.workflow = CrmWorkflow(KnowledgeBase(), TicketService(self.repo))

    def test_known_question_answers_and_still_creates_ticket(self):
        result = self.workflow.run("قیمت پلن‌ها چقدر است؟")
        self.assertTrue(result.found_in_kb)
        self.assertEqual(result.classification.category_id, "sales")
        self.assertTrue(result.ticket_id.startswith("TKT-"))
        self.assertEqual(result.status, "auto_resolved")
        self.assertIsNotNone(self.repo.get(result.ticket_id))

    def test_unknown_question_still_creates_open_ticket(self):
        result = self.workflow.run("آیا شعبه شیراز دارید؟")
        self.assertTrue(result.ticket_id.startswith("TKT-"))
        self.assertEqual(result.status, "open")
        self.assertIsNotNone(self.repo.get(result.ticket_id))

    def test_ticket_ids_are_unique(self):
        a = self.workflow.run("قیمت پلن چنده؟")
        b = self.workflow.run("رمز عبورم را فراموش کردم")
        self.assertNotEqual(a.ticket_id, b.ticket_id)


if __name__ == "__main__":
    unittest.main()
