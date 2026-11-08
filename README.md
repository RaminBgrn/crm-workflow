# CRM Workflow — پاسخ‌گویی آنلاین و ثبت تیکت

یک سیستم CRM مبتنی بر **Workflow** که به‌صورت آنلاین به سؤال کاربر پاسخ می‌دهد:

1. سؤال را **تحلیل و دسته‌بندی** می‌کند: فروش، پشتیبانی یا واحد فنی
2. با سیستم **RAG** داخل پایگاه دانش همان دسته (فایل JSON) دنبال جواب آماده می‌گردد
3. اگر جواب پیدا شود، همان را برمی‌گرداند؛ اگر نشود، سؤال را به واحد مربوطه ارجاع می‌دهد
4. **در هر صورت یک تیکت ثبت می‌کند** و شناسه تیکت (`ticket_id`) را به کاربر برمی‌گرداند

## ساختار ماژولار

```
crm/
├── models.py              # مدل‌های داده (Ticket, Classification, ...)
├── config.py              # تنظیمات و مسیرها
├── classifier/            # دسته‌بندی سؤال
│   ├── categories.py      #   تعریف ۳ دسته پیش‌فرض + کلیدواژه‌ها
│   └── classifier.py      #   منطق دسته‌بندی
├── rag/                   # سیستم RAG
│   ├── knowledge_base.py  #   بارگذاری پایگاه دانش
│   ├── retriever.py       #   جستجو و بازیابی جواب
│   └── data/knowledge_base.json   # پایگاه دانش (JSON)
├── tickets/               # ثبت و ذخیره تیکت
│   ├── repository.py      #   ذخیره‌سازی JSON
│   └── service.py         #   ساخت تیکت با شناسه یکتا
├── workflow/
│   └── engine.py          # ارکستریتور فلو (۵ قدم بالا)
└── api/
    ├── app.py             # API با Flask
    └── static/index.html  # صفحه چت ساده
app.py                     # نقطه ورود
tests/test_workflow.py     # تست‌های کلاسیفایر، RAG و فلو
docs/WORKFLOW.md           # نمودار و قواعد فلو
examples/sample_requests.json
```

هر ماژول اینترفیس مشخصی دارد و مستقل قابل تعویض است؛ مثلاً کلاسیفایر
کلیدواژه‌ای را می‌توان با مدل ML/LLM و بازیابی ساده را با Embedding و
Vector DB جایگزین کرد، بدون تغییر بقیه سیستم.

## اجرا

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

## API

### پرسش و پاسخ (فلو کامل)

```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "قیمت پلن‌ها چقدر است؟"}'
```

پاسخ:

```json
{
  "ticket_id": "TKT-20261108-0001",
  "question": "قیمت پلن‌ها چقدر است؟",
  "classification": {
    "category_id": "sales",
    "category_fa": "فروش",
    "confidence": 1.0,
    "matched_keywords": ["قیمت", "پلن"],
    "is_default": false
  },
  "answer": "اشتراک در سه پلن ارائه می‌شود: ...",
  "found_in_kb": true,
  "source_id": "sales-001",
  "status": "auto_resolved"
}
```

| Endpoint | توضیح |
|---|---|
| `POST /api/ask` | اجرای فلو: دسته‌بندی ← RAG ← ثبت تیکت ← جواب + `ticket_id` |
| `GET /api/tickets` | لیست تیکت‌های ثبت‌شده |
| `GET /api/tickets/<id>` | جزئیات یک تیکت |
| `GET /api/categories` | دسته‌بندی‌های پیش‌فرض |
| `GET /health` | سلامت سرویس |

## پایگاه دانش (RAG)

دانش سیستم در `crm/rag/data/knowledge_base.json` است — برای هر دسته،
لیستی از آیتم‌های `{id, question, keywords, answer}`.
برای اضافه‌کردن جواب جدید فقط همین فایل JSON را ویرایش کنید؛ کد لازم نیست عوض شود.

## تست

```bash
python -m unittest discover -s tests -v
```
