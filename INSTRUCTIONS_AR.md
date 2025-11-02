# تعليمات تشغيل Policy Navigator Agent

## التحديثات الجديدة ✨

### 1. الحفظ الدائم لاستخراج المحتوى من URLs
- **المشكلة السابقة**: كان المحتوى المستخرج من المواقع يُحفظ مؤقتاً فقط ويختفي بعد إعادة التشغيل
- **الحل**: الآن يتم حفظ المحتوى تلقائياً في قاعدة بيانات FAISS على القرص
- **النتيجة**: جميع المستندات المستخرجة تبقى دائماً ويمكن البحث فيها في أي وقت

### 2. زر حذف جميع المستندات (Clear All)
- **الميزة الجديدة**: زر أحمر في الواجهة لحذف جميع المستندات من قاعدة البيانات
- **الفائدة**: تنظيف الذاكرة وتجنب امتلاء قاعدة البيانات
- **الأمان**: يطلب تأكيد قبل الحذف لتجنب الحذف العرضي

## متطلبات التشغيل

### 1. تثبيت المكتبات المطلوبة
```bash
pip install faiss-cpu sentence-transformers flask flask-cors aixplain beautifulsoup4 requests python-dotenv
```

### 2. التأكد من وجود ملف `.env`
يجب أن يحتوي على:
```
AIXPLAIN_API_KEY 
```

## تشغيل الخادم

### الطريقة الصحيحة (مع تصدير API Key):
```bash
cd policy-navigator-agent/demo
export AIXPLAIN_API_KEY=
python app_faiss.py
```

### على Windows (PowerShell):
```powershell
cd policy-navigator-agent\demo
$env:AIXPLAIN_API_KEY=
python app_faiss.py
```

### على Windows (CMD):
```cmd
cd policy-navigator-agent\demo
set AIXPLAIN_API_KEY
python app_faiss.py
```

## استخدام الواجهة

### 1. فتح المتصفح
افتح: `http://localhost:5001`

### 2. استخراج محتوى من موقع
1. انتقل إلى قسم "Extract from URL"
2. أدخل رابط الموقع (مثل: `https://www.epa.gov/laws-regulations`)
3. اضغط "Extract Content"
4. **المحتوى سيُحفظ دائماً** في قاعدة البيانات

### 3. رفع ملفات
1. انتقل إلى قسم "Upload Documents"
2. اسحب وأفلت ملف XML أو TXT
3. أو اضغط على المنطقة لاختيار ملف

### 4. البحث والاستعلام
1. اكتب سؤالك في حقل "Ask a Question"
2. اضغط "Submit Query"
3. ستحصل على إجابة ذكية من الـ LLM بناءً على المستندات المحفوظة

### 5. حذف جميع المستندات
1. انتقل إلى قسم "Database Management"
2. اضغط زر "⚠️ Clear All Documents"
3. أكّد الحذف في النافذة المنبثقة
4. **جميع المستندات ستُحذف نهائياً**

## ملفات قاعدة البيانات

تُحفظ قاعدة البيانات في:
```
policy-navigator-agent/faiss_db/
├── faiss.index      # فهرس الـ vectors
└── metadata.pkl     # بيانات المستندات
```

## التحقق من الحفظ الدائم

لاختبار أن المحتوى يُحفظ دائماً:
1. استخرج محتوى من موقع
2. أوقف الخادم (Ctrl+C)
3. أعد تشغيل الخادم
4. افتح المتصفح - ستجد عدد المستندات كما هو
5. ابحث عن المحتوى - ستجده موجوداً

## حل المشاكل الشائعة

### مشكلة: `AIXPLAIN_API_KEY not set`
**الحل**: تأكد من تصدير المتغير قبل تشغيل الخادم (انظر أعلاه)

### مشكلة: `ModuleNotFoundError: No module named 'faiss'`
**الحل**: 
```bash
pip install faiss-cpu sentence-transformers
```

### مشكلة: الخادم لا يعمل على Windows
**الحل**: استخدم Python 3.9 أو أحدث، وتأكد من تثبيت جميع المكتبات

### مشكلة: المحتوى المستخرج لا يُحفظ
**الحل**: هذه المشكلة تم حلها! تأكد من استخدام أحدث نسخة من الكود

## الملفات المُعدّلة

1. **src/data/faiss_vector_store.py**
   - إضافة دالة `clear_all()` لحذف جميع المستندات
   - الحفظ التلقائي بعد كل عملية إضافة

2. **demo/app_faiss.py**
   - إضافة endpoint `/api/clear-all` لحذف المستندات
   - الحفظ التلقائي بعد استخراج المحتوى من URLs

3. **demo/templates/index.html**
   - إضافة قسم "Database Management"
   - إضافة زر "Clear All Documents" مع تأكيد
   - إضافة دالة JavaScript `clearAllDocuments()`

## الميزات المتقدمة

### استخدام مع venv (بيئة افتراضية)
```bash
# إنشاء بيئة افتراضية
python -m venv venv

# تفعيلها (Linux/Mac)
source venv/bin/activate

# تفعيلها (Windows)
venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل الخادم
export AIXPLAIN_API_KEY=
python demo/app_faiss.py
```

## الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- GitHub: https://github.com/omar-qasem/policy-navigator-agent
- Issues: https://github.com/omar-qasem/policy-navigator-agent/issues

---
