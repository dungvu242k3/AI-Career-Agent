# 📋 KẾ HOẠCH: TÍCH HỢP OPENAI API LÀM LLM PROVIDER CHÍNH (CareerPilot AI)

> **File kế hoạch:** `docs/PLAN-openai-integration.md`  
> **Trạng thái:** Chờ User Review & Xác nhận trước khi code  
> **Mục tiêu:** Mở rộng engine AI sang OpenAI (`gpt-4o-mini`, `gpt-4o`) làm provider chính, giữ Gemini làm fallback, tạo file `.env` chuẩn.

---

## 🎯 1. MỤC TIÊU & YÊU CẦU

1. **OpenAI làm Provider chính:** Sử dụng OpenAI SDK (`AsyncOpenAI`) cho các tác vụ bóc tách CV, chấm điểm ATS và sinh gợi ý.
2. **Multi-Provider Architecture (SOLID):** Không xóa Gemini mà thiết kế dạng **Adapter Pattern** — chỉ cần đổi `AI_PROVIDER=openai` hoặc `AI_PROVIDER=gemini` trong `.env` là toàn bộ hệ thống tự động switch model mà không phải sửa lại code logic.
3. **OpenAI Structured Outputs (Chuẩn 2025):** Sử dụng tính năng `client.beta.chat.completions.parse(response_format=CandidateProfile)` của OpenAI để đảm bảo 100% dữ liệu trả về khớp đúng schema Pydantic v3.
4. **File Môi trường `.env` & `.env.example`:** Tạo mẫu cấu hình đầy đủ API Key, Model name, và tham số cho cả OpenAI và Google.

---

## 🏗️ 2. THIẾT KẾ KIẾN TRÚC MULTI-PROVIDER

```
┌─────────────────────────────────────────────────────────────┐
│                    CVIngestionPipeline                      │
└──────────────────────────────┬──────────────────────────────┘
                               │ phụ thuộc vào
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            BaseProfileExtractor (Abstract Interface)        │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼ (AI_PROVIDER=openai)          ▼ (AI_PROVIDER=gemini)
┌──────────────────────────────┐ ┌─────────────────────────────┐
│     OpenAICVExtractor        │ │      GeminiCVExtractor      │
│  (gpt-4o-mini + Pydantic)   │ │  (gemini-2.0-flash + JSON)  │
└──────────────────────────────┘ └─────────────────────────────┘
```

### 🔹 Model Mapping được đề xuất:

| Tác vụ AI | OpenAI Model (Chính) | Gemini Model (Phụ / Fallback) | Ước tính chi phí / 1 CV |
|---|---|---|---|
| **Bóc tách CV (Step 1)** | `gpt-4o-mini` | `gemini-2.0-flash` | ~$0.0003 (~8đ - 15đ) |
| **Chấm điểm ATS & STAR (Step 2)** | `gpt-4o` hoặc `gpt-4o-mini` | `gemini-2.5-flash` | ~$0.0015 (~35đ - 80đ) |
| **Sinh Vector Embedding (Step 3)** | `text-embedding-3-small` | `text-embedding-004` | ~$0.00002 (~0.5đ) |

---

## ⚙️ 3. CẤU TRÚC FILE `.env` & `.env.example` SẼ TẠO

```env
# ==========================================
# 🚀 CareerPilot AI — Environment Config
# ==========================================

# --- APP CONFIG ---
APP_NAME="CareerPilot AI"
DEBUG=false
API_PREFIX="/api/v1"
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# --- AI PROVIDER SELECTION ---
# Tùy chọn: "openai" (Mặc định) hoặc "gemini"
AI_PROVIDER="openai"

# --- OPENAI CONFIGURATION (CHÍNH) ---
OPENAI_API_KEY="sk-proj-YOUR_OPENAI_API_KEY_HERE"
OPENAI_EXTRACTION_MODEL="gpt-4o-mini"
OPENAI_REASONING_MODEL="gpt-4o"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# --- GOOGLE GEMINI CONFIGURATION (PHỤ / BACKUP) ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
GEMINI_FLASH_MODEL="gemini-2.5-flash-preview-05-20"
GEMINI_FLASH_LITE_MODEL="gemini-2.0-flash"

# --- STORAGE & DATABASE ---
DATABASE_URL="sqlite+aiosqlite:///./data/careerpilot.db"
UPLOAD_DIR="./data/uploads"
MAX_UPLOAD_SIZE_MB=10
```

---

## 📋 4. CÁC BƯỚC THỰC HIỆN CHI TIẾT

### Bước 1: Cài đặt & Cấu hình Dependencies
* Bổ sung thư viện `openai>=1.50.0` vào `be/requirements.txt` và cài đặt vào môi trường ảo.
* Cập nhật `ai/config.py` để bổ sung các trường cấu hình OpenAI (`openai_api_key`, `openai_extraction_model`, `ai_provider`).

### Bước 2: OpenAI Client Factory
* Cập nhật `ai/client.py` bổ sung hàm `get_openai_client() -> AsyncOpenAI`.
* Bọc an toàn `SecretStr` để bảo vệ khóa API.

### Bước 3: Xây dựng `OpenAICVExtractor`
* Tạo `ai/extractors/openai_extractor.py` kế thừa `BaseProfileExtractor`.
* Sử dụng cú pháp native structured parsing:
  ```python
  completion = await client.beta.chat.completions.parse(
      model=self.config.openai_extraction_model,
      messages=[
          {"role": "system", "content": self.system_instruction},
          {"role": "user", "content": f"<cv_document>\n{raw_text}\n</cv_document>"},
      ],
      response_format=CandidateProfile,
      temperature=0.1,
  )
  profile = completion.choices[0].message.parsed
  ```
* Tích hợp auto-healing (sanitization, deduplication, interval merging).

### Bước 4: Factory Routing trong `ai/pipeline.py`
* Cập nhật `get_default_ingestion_pipeline()` để tự động đọc `AI_PROVIDER` từ `AIConfig`:
  * Nếu `ai_provider == "openai"` $\rightarrow$ Inject `OpenAICVExtractor`.
  * Nếu `ai_provider == "gemini"` $\rightarrow$ Inject `GeminiCVExtractor`.

### Bước 5: Tạo file `.env.example` và file `.env` mẫu
* Tạo `.env.example` (không chứa key thật để commit git).
* Tạo `.env` ở thư mục gốc và thư mục `be/` để bạn chỉ việc paste API Key vào.

### Bước 6: Viết Unit Tests & Integration Tests
* Viết test mock cho `OpenAICVExtractor`.
* Chạy toàn bộ test suite để xác nhận 100% tương thích.

---

## ❓ 5. CÂU HỎI THỐNG NHẤT VỚI BẠN

1. **Model OpenAI mặc định:** Bạn có đồng ý dùng `gpt-4o-mini` cho việc bóc tách CV (vì tốc độ nhanh dưới 2s, cực rẻ và độ chính xác JSON 100%) và dành `gpt-4o` cho bước chấm điểm chuyên sâu không?
2. **Chế độ Fallback:** Bạn có muốn khi OpenAI gặp lỗi (hết quota / rate limit) thì hệ thống tự động fallback gọi sang Gemini không?
