# 📋 KẾ HOẠCH TRIỂN KHAI PHASE 2: JD Matching Engine + ATS Scorer + STAR Rewriter

> **Mã tài liệu:** `PLAN-phase2-jd-matching`
> **Trạng thái:** 📋 KẾ HOẠCH HOÀN CHỈNH (Chờ duyệt — NO CODE)
> **Quyết định đã xác nhận:**
> - ✅ Trọng số ATS: **50/30/20** (Skills / Experience / Format) — chuẩn quốc tế
> - ✅ **KHÔNG** làm Chat AI (Cột 2) trong Phase 2 — dời sang Phase 3
> - ✅ JD file xử lý In-Memory, giải phóng RAM ngay
> - ✅ Output 100% Tiếng Việt

---

## 🔍 PHẦN A: KIỂM TRA ỔN ĐỊNH PHASE 1 (CV UPLOAD)

Đã audit kỹ 7 file core của Phase 1. Kết quả:

### ✅ Đã ổn định — KHÔNG cần sửa

| File | Trạng thái | Ghi chú |
|------|------------|---------|
| `be/api/v1/cv_router.py` | ✅ Ổn | Upload + Preview + Update + Download — đầy đủ validation, path traversal protection, 2MB limit |
| `ai/pipeline.py` | ✅ Ổn | Multi-provider fallback (OpenAI → Gemini), auto-resolve PDF/DOCX parser |
| `be/core/storage.py` | ✅ Ổn | MinIO + Local fallback, presigned URLs, delete on error |
| `ai/models/candidate.py` | ✅ Ổn | 8-group SkillsTaxonomy, CVMetadata, 148 dòng — schema chuẩn |
| `be/db/database.py` | ✅ Ổn | PostgreSQL + SQLite fallback, bảng `analyses` đã sẵn sàng cho Phase 2 |
| `be/core/rate_limiter.py` | ✅ Ổn | Sliding window, IP-based, cleanup stale entries |
| `be/main.py` | ✅ Ổn | Security headers, CORS, lifespan quản lý DB pool |

### ⚠️ Vấn đề nhỏ — sửa luôn khi bắt đầu Phase 2

| # | File | Vấn đề | Cách sửa |
|---|------|--------|----------|
| 1 | `ai/config.py` L63 | `max_file_size_mb = 10` nhưng BE config = 2MB → **không đồng bộ** | Đồng bộ về `2` |
| 2 | `be/api/v1/schemas.py` | Chưa có schema cho ATS response | Thêm khi làm Bước 6 |

### 📊 Test Coverage Phase 1: 6 tests API + 6 test files AI → ĐỦ

> **Kết luận Phase 1: ỔN ĐỊNH, sẵn sàng cho Phase 2.**

---

## 🏗️ PHẦN B: KIẾN TRÚC PHASE 2

```
┌───────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + TypeScript)                   │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐│
│  │ Cột 1        │  │ Cột 2        │  │ Cột 3: ATS Studio        ││
│  │ CV Preview   │  │ [Phase 3]    │  │ ┌──────────────────────┐ ││
│  │ (Phase 1 ✅)  │  │ Chat AI      │  │ │ JDInput Component    │ ││
│  │              │  │              │  │ │ • Tab: Dán text      │ ││
│  │              │  │              │  │ │ • Tab: Upload file   │ ││
│  │              │  │              │  │ └──────────────────────┘ ││
│  │              │  │              │  │ ┌──────────────────────┐ ││
│  │              │  │              │  │ │ ATSResult Component  │ ││
│  │              │  │              │  │ │ • Gauge điểm 0-100   │ ││
│  │              │  │              │  │ │ • Skill tags 🟢🟡🔴  │ ││
│  │              │  │              │  │ │ • Click 🔴 → STAR    │ ││
│  │              │  │              │  │ │ • Recommendations    │ ││
│  │              │  │              │  │ └──────────────────────┘ ││
│  └──────────────┘  └──────────────┘  └──────────────────────────┘│
└───────────────────────────────────────────────────────────────────┘
                              │
           POST /api/v1/ats/match  │  POST /api/v1/ats/rewrite-star
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI :8000)                         │
│                                                                   │
│  [ats_router.py]                                                  │
│  ├─ POST /ats/match        → JD Parse + ATS Score → JDMatchReport│
│  ├─ POST /ats/rewrite-star → STAR Rewrite → STARResult           │
│  └─ GET  /ats/history/{id} → Lịch sử analyses                   │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                   AI CORE (ai/)                                   │
│                                                                   │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────────────────┐   │
│  │ JD Parser   │  │ ATS Matcher   │  │ STAR Rewriter        │   │
│  │             │  │               │  │                      │   │
│  │ • Text → JD │  │ Skill Match   │  │ Raw → STAR v1 + v2   │   │
│  │ • File → JD │  │  50% weight   │  │ Missing → STAR       │   │
│  │ • RAM free  │  │ Experience    │  │ Power Verbs           │   │
│  │             │  │  30% weight   │  │ 100% Tiếng Việt      │   │
│  │             │  │ Format        │  │                      │   │
│  │             │  │  20% weight   │  │                      │   │
│  └─────────────┘  └───────────────┘  └──────────────────────┘   │
│                                                                   │
│  Prompts: jd_extraction.md │ ats_scoring.md │ star_rewrite.md     │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📋 PHẦN C: 10 BƯỚC TRIỂN KHAI CHI TIẾT

### Sơ đồ phụ thuộc

```
  Bước 1 (JDProfile Schema)
    ├──→ Bước 2 (JDMatchReport + STARResult Schema)
    │       ├──→ Bước 4 (ATS Matcher Core) ←── Bước 3
    │       └──→ Bước 5 (STAR Rewriter)
    └──→ Bước 3 (JD Parser)
            └──→ Bước 6 (Backend API) ←── Bước 4, 5
                    └──→ Bước 9 (FE API Service) ←── Bước 8
                            └──→ Bước 10 (Integration Test)

  Bước 7 (FE JD Input) ──→ Bước 8 (FE ATS Result)
  ↑ CÓ THỂ LÀM SONG SONG với Bước 3-5
```

---

### 🔹 Bước 1: Schema JDProfile — `ai/models/jd.py` (NEW)

**Mục tiêu:** Pydantic model cho JD đã phân tích cấu trúc.

| Field | Type | Mô tả |
|-------|------|--------|
| `job_title` | `str` | Vị trí tuyển dụng |
| `company_name` | `str \| None` | Tên công ty (nếu có) |
| `must_have_skills` | `list[str]` | Kỹ năng BẮT BUỘC |
| `nice_to_have_skills` | `list[str]` | Kỹ năng ƯU TIÊN |
| `min_experience_years` | `int \| None` | Số năm kinh nghiệm tối thiểu |
| `education_requirement` | `str \| None` | Yêu cầu bằng cấp |
| `responsibilities` | `list[str]` | Mô tả công việc |
| `benefits` | `list[str]` | Phúc lợi (optional) |
| `raw_text` | `str` | Full JD text gốc |
| `language` | `Literal["en","vi","mixed"]` | Ngôn ngữ phát hiện |

**Tại sao tách `must_have` vs `nice_to_have`?**
- ATS thật (Greenhouse, Lever) đều phân loại: Required vs Preferred
- Missing required → trừ x2 điểm so với missing preferred
- Người dùng biết đâu là ưu tiên #1

**Tests:** `test_jd_profile_valid`, `test_defaults`, `test_language_literal`
**Thời gian:** ~30 phút

---

### 🔹 Bước 2: Schema JDMatchReport + STARResult — `ai/models/jd.py` + `ai/models/star.py` (NEW)

**JDMatchReport:**

| Field | Type | Mô tả |
|-------|------|--------|
| `overall_score` | `int` (0-100) | Trọng số: Skills 50% + Exp 30% + Format 20% |
| `overall_grade` | `str` | A+ / A / B+ / B / C |
| `verdict` | `str` | Nhận xét tổng (Tiếng Việt) |
| `skill_match_score` | `int` | 0-100 |
| `experience_fit_score` | `int` | 0-100 |
| `format_quality_score` | `int` | 0-100 |
| `matched_skills` | `list[SkillMatchItem]` | 🟢 + 🟡 |
| `missing_skills` | `list[SkillMatchItem]` | 🔴 |
| `excess_skills` | `list[str]` | ⚪ |
| `top_recommendations` | `list[str]` | Top 3 hành động |
| `experience_gap_analysis` | `str` | Phân tích gap |
| `jd_title` | `str` | Vị trí |

**SkillMatchItem:** `skill_name`, `match_type` (exact/semantic/missing), `cv_evidence`, `jd_requirement`, `importance` (required/preferred)

**Grade mapping:** 90-100=A+, 80-89=A, 70-79=B+, 60-69=B, <60=C

**STARResult:** `original`, `star_v1`, `star_v2`, `action_verb`, `improvements[]`

**Tests:** `test_grade_mapping`, `test_skill_match_types`, `test_star_result`
**Thời gian:** ~30 phút

---

### 🔹 Bước 3: JD Parser — `ai/parsers/jd_parser.py` + `ai/prompts/jd_extraction.md` (NEW)

**Luồng:**
```
jd_text → validate (rỗng? >10K?) → LLM extract → JDProfile
jd_file → reuse PyMuPDF/Docx parser → bóc text → del bytes → parse_jd_text()
```

**Validation:** rỗng → ValueError; >10K chars → truncate; file >2MB → reject
**Tái sử dụng:** `PyMuPDFParser`, `DocxDocumentParser` từ Phase 1
**RAM:** `del content_bytes` ngay sau bóc text

**Prompt `jd_extraction.md`:** LLM đóng vai HR Expert, output JDProfile JSON, few-shot EN + VI

**Tests (8):** parse text EN/VI, parse file PDF/DOCX, empty error, too long truncate, file too large, memory released
**Thời gian:** ~2 giờ

---

### 🔹 Bước 4: ATS Matcher Core — `ai/analysis/ats_matcher.py` + `ai/prompts/ats_scoring.md` (NEW)

> Bước **phức tạp nhất** và **quan trọng nhất**.

**Hàm:** `match_cv_against_jd(profile: CandidateProfile, jd: JDProfile) -> JDMatchReport`

**Thuật toán 3 tầng:**

| Tầng | Trọng số | Logic |
|------|----------|-------|
| **Skill Match** | **50%** | CV.skills vs JD.skills → exact🟢(100đ) / semantic🟡(70đ) / missing🔴(0đ). Must-have x2, nice-to-have x1 |
| **Experience Fit** | **30%** | CV.YoE vs JD.YoE + bullet depth vs responsibilities |
| **Format Quality** | **20%** | % bullets có số liệu, Power Verbs, cấu trúc STAR |

**Tổng:** `overall = skill×0.5 + exp×0.3 + format×0.2`

**Caching:** `hash(candidate_id + jd_text)` → check DB `analyses` → return cached nếu có

**Prompt `ats_scoring.md`:** ATS Expert, input CV+JD JSON, output JDMatchReport 100% Tiếng Việt

**Tests (9):** perfect match, partial, no overlap, semantic, must-have weight, experience gap, Vietnamese output, caching, grade mapping
**Thời gian:** ~3 giờ

---

### 🔹 Bước 5: STAR Rewriter — `ai/analysis/star_rewriter.py` + `ai/prompts/star_rewrite.md` (NEW)

**2 chế độ:**
- **Missing Skill:** `"Redis"` + role → câu STAR mẫu
- **Weak Bullet:** `"Làm backend"` + role → viết lại STAR

**Hàm:** `rewrite_to_star(raw_input, target_role, context?) -> STARResult`

**Quy tắc:** Power Verb đầu tiên → Công nghệ cụ thể → Kết quả định lượng → ≤ 2 dòng → Tiếng Việt
**Sinh 2 versions:** V1 (Cân bằng) + V2 (Max Impact)

**Tests (6):** weak bullet rewrite, missing skill generate, power verb, two versions, Vietnamese, under 2 lines
**Thời gian:** ~2 giờ

---

### 🔹 Bước 6: Backend API — `be/api/v1/ats_router.py` (NEW) + sửa files

**3 Endpoints:**

| Method | Path | Rate Limit |
|--------|------|-----------|
| `POST` | `/api/v1/ats/match` | 10/phút |
| `POST` | `/api/v1/ats/rewrite-star` | 20/phút |
| `GET` | `/api/v1/ats/history/{id}` | 30/phút |

**Validation `/ats/match`:** candidate_id tồn tại (404), jd_text hoặc jd_file phải có (400), text ≤ 10K (400), file ≤ 2MB (400)

**Files sửa:** `main.py` (register router), `rate_limiter.py` (+2 limiters), `schemas.py` (+DTOs), `ai/models/__init__.py` (exports), `ai/config.py` (sync 2MB)

**Tests (11):** match text, file PDF, file DOCX, 404, empty 400, too long, too large, star success, star empty, history, rate limit
**Thời gian:** ~2 giờ

---

### 🔹 Bước 7: FE — JD Input — `fe/src/components/JDInput.tsx` (NEW)

**2 tabs:** Dán Text / Tải File (drag & drop)
**Features:** Character counter (max 10K), file validation, disabled state, loading skeleton
**Song song:** Có thể làm cùng lúc với Bước 3-5
**Thời gian:** ~2 giờ

---

### 🔹 Bước 8: FE — ATS Result + STAR Modal — `ATSResult.tsx` + `STARModal.tsx` (NEW)

**Components:** Radial Gauge (màu động), Skill Tags (🟢🟡🔴 clickable), STARModal (V1+V2 + Copy), Recommendations
**Thời gian:** ~3 giờ

---

### 🔹 Bước 9: FE — API Service + Types — `atsApi.ts` + `ats.ts` (NEW)

**Functions:** `matchJDText()`, `matchJDFile()`, `rewriteSTAR()`, `getATSHistory()`
**Sửa:** `WorkspacePage.tsx` — tích hợp ATS Studio vào Cột 3
**Thời gian:** ~1 giờ

---

### 🔹 Bước 10: Integration Test + Verification

**E2E:** Upload CV → Paste JD → Match → Click Missing → STAR → Cached → History
**Commands:** `pytest tests/ -v` (BE+AI), `npm run build` (FE)
**Thời gian:** ~2 giờ

---

## 📊 PHẦN D: TỔNG HỢP

| Bước | Module | Thời gian | Layer |
|------|--------|-----------|-------|
| 1 | Schema JDProfile | 30 phút | AI |
| 2 | Schema JDMatchReport + STARResult | 30 phút | AI |
| 3 | JD Parser + Prompt | 2 giờ | AI |
| 4 | **ATS Matcher Core** | **3 giờ** | AI |
| 5 | STAR Rewriter | 2 giờ | AI |
| 6 | Backend API | 2 giờ | BE |
| 7 | FE: JD Input *(song song)* | 2 giờ | FE |
| 8 | FE: ATS Result + STAR Modal | 3 giờ | FE |
| 9 | FE: API Service + Types | 1 giờ | FE |
| 10 | Integration Test | 2 giờ | Test |
| **Tổng** | | **~18 giờ** | |

### Danh sách file: 17 NEW + 5 MODIFY

**NEW:** `ai/models/jd.py`, `ai/models/star.py`, `ai/parsers/jd_parser.py`, `ai/analysis/ats_matcher.py`, `ai/analysis/star_rewriter.py`, `ai/prompts/jd_extraction.md`, `ai/prompts/ats_scoring.md`, `ai/prompts/star_rewrite.md`, `be/api/v1/ats_router.py`, `fe/src/components/JDInput.tsx`, `fe/src/components/ATSResult.tsx`, `fe/src/components/STARModal.tsx`, `fe/src/services/atsApi.ts`, `fe/src/types/ats.ts`, `ai/tests/test_jd_parser.py`, `ai/tests/test_ats_matcher.py`, `be/tests/test_ats_api.py`

**MODIFY:** `be/main.py`, `be/core/rate_limiter.py`, `be/api/v1/schemas.py`, `ai/models/__init__.py`, `ai/config.py`

---

## 🗺️ ROADMAP SAU PHASE 2

| Phase | Tính năng | Ưu tiên |
|-------|-----------|---------|
| **Phase 2** ← ĐANG LÀM | Core ATS Match + STAR Rewrite + Skill Tags | 🔴 Cao nhất |
| **Phase 3** | AI Career Chat (Cột 2) + Keyword Heatmap | 🟡 Cao |
| **Phase 4** | Interview Predictor + Tailored CV | 🟡 Trung bình |
| **Phase 5** | Salary Fit + Multi-JD | 🟢 Thấp |
