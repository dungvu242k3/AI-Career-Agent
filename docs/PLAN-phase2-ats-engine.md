# 🚀 Kế Hoạch Triển Khai Phase 2: Bộ Máy Chấm Điểm ATS & Trình Viết Lại STAR (CareerPilot AI)

> **Mã kế hoạch:** `PLAN-phase2-ats-engine`  
> **Người lập:** `project-planner` & `architect-review`  
> **Trạng thái:** 📋 ĐANG LẬP KẾ HOẠCH (PLANNING ONLY - NO CODE)  
> **Mục tiêu cốt lõi:** Xây dựng bộ não AI phân tích độ khớp CV với Job Description (ATS Scoring), tái cấu trúc thành tựu theo chuẩn STAR, và kết nối Trợ lý AI Chat trên giao diện Workspace.

---

## 🗺️ TỔNG QUAN KIẾN TRÚC PHASE 2

```
[ FRONTEND WORKSPACE ]
  ├── Cột 1: Hồ sơ Ứng viên (Đã hoàn thành Phase 1)
  ├── Cột 2: AI Career Assistant Chat (Phase 2) ──────► POST /api/v1/chat/message
  └── Cột 3: ATS Studio & STAR Rewriter (Phase 2) ──► POST /api/v1/ats/score & rewrite
                                                              │
                                                              ▼
[ BACKEND FASTAPI (:8000) ]
  ├── `be/api/v1/ats_router.py` (Endpoints phân tích ATS & Viết lại STAR)
  └── `be/api/v1/chat_router.py` (Endpoint trò chuyện AI ngữ cảnh CV)
                                                              │
                                                              ▼
[ AI CORE (`ai/`) ]
  ├── 1. `ai/analysis/ats_scorer.py`: Tính điểm 3 tiêu chí (Kỹ năng 40%, Số liệu 30%, Định dạng 30%)
  ├── 2. `ai/analysis/star_rewriter.py`: Chuyển đổi bullet points sang Situation-Task-Action-Result
  └── 3. `ai/analysis/career_chat.py`: Trợ lý AI tư vấn chiến lược CV & Phỏng vấn
```

---

## 📋 CHI TIẾT CÁC GIAI ĐOẠN TRIỂN KHAI (TASK BREAKDOWN)

### 🔹 Giai đoạn 2.1: Thiết Kế Schema & Prompts Chấm Điểm ATS (`ai/`)
- **Phân công:** `ai-engineer` & `backend-specialist`
- **Nội dung:**
  1. Xây dựng Schema Pydantic `ATSScoreReport`:
     - `overall_score`: Điểm tổng thể (0 - 100).
     - `skill_match_score` (40%): Danh sách `matched_skills`, `missing_critical_skills`, `good_to_have_skills`.
     - `impact_metrics_score` (30%): Tỷ lệ các bullet point có chứa số liệu định lượng (%, $, số lượng).
     - `formatting_score` (30%): Độ dài phù hợp, động từ hành động mạnh (Power Verbs), cấu trúc chuẩn ATS.
     - `actionable_recommendations`: Top 3 lời khuyên sửa nhanh để tăng ngay 15 - 30 điểm.
  2. Tạo Prompt Modular:
     - `ai/prompts/ats_scoring.md`: Hệ quy chiếu đánh giá ATS quốc tế (Greenhouse, Lever, Workday).
     - `ai/prompts/star_rewrite.md`: Công thức viết lại bullet point: [Action Verb mạnh] + [Task/Công nghệ cụ thể] + [Kết quả định lượng].

---

### 🔹 Giai đoạn 2.2: Xây Dựng Bộ Máy Phân Tích AI Core (`ai/analysis/`)
- **Phân công:** `ai-engineer`
- **Nội dung:**
  1. `ai/analysis/ats_scorer.py`:
     - Hàm `score_candidate_against_jd(profile: CandidateProfile, jd_text: str) -> ATSScoreReport`.
     - Hỗ trợ cả 2 Provider: **OpenAI** (Structured Outputs) và **Google Gemini** (`response_schema=ATSScoreReport`).
     - Tự động lưu trữ lịch sử phân tích vào bảng `analyses` trong Database.
  2. `ai/analysis/star_rewriter.py`:
     - Hàm `rewrite_bullet_point(raw_bullet: str, target_role: str) -> dict`.
     - Sinh ra 2 phiên bản: **Version 1 (Cân bằng chuẩn STAR)** vs **Version 2 (Tối đa hóa số liệu & Impact)**.
  3. `ai/analysis/career_chat.py`:
     - Lưu context lịch sử chat ngắn hạn, gắn kèm toàn bộ hồ sơ `CandidateProfile` và báo cáo ATS vào System Prompt.

---

### 🔹 Giai đoạn 2.3: Xây Dựng REST API Endpoints (`be/api/v1/`)
- **Phân công:** `backend-specialist`
- **Nội dung:**
  1. `POST /api/v1/ats/score`:
     - Input: `{ "candidate_id": 1, "job_description": "..." }`
     - Dependency: Rate limiter (10 req/min).
     - Trả về: `ATSScoreReport` chi tiết.
  2. `POST /api/v1/ats/rewrite-bullet`:
     - Input: `{ "raw_bullet": "Làm backend bằng FastAPI", "target_role": "Senior Backend Engineer" }`
     - Trả về: `{ "v1": "...", "v2": "...", "improvements": [...] }`
  3. `POST /api/v1/chat/message`:
     - Input: `{ "candidate_id": 1, "messages": [...] }`
     - Trả về: Tin nhắn tư vấn chiến lược từ AI.

---

### 🔹 Giai đoạn 2.4: Nâng Cấp Giao Diện Cột 2 & Cột 3 Workspace (`fe/`)
- **Phân công:** `frontend-developer`
- **Nội dung:**
  1. **Cột 3 (ATS Studio & Job Match):**
     - Hộp nhập Job Description với nút *"Phân Tích Độ Khớp Ngay"*.
     - Đồng hồ đo điểm ATS hình tròn (Radial Gauge 0-100) đổi màu động (Đỏ <60, Vàng 60-79, Xanh 80+).
     - Danh sách kỹ năng còn thiếu hiển thị dạng Tag đỏ (Click để xem giải thích cách bổ sung).
     - Trình viết lại STAR: Cho phép chọn 1 dòng kinh nghiệm từ Cột 1 ──► Bấm "Tối ưu STAR" ──► Xem so sánh Trước/Sau ──► Bấm "Áp dụng vào CV".
  2. **Cột 2 (AI Assistant Chat):**
     - Kết nối chat trực tiếp với API backend, hiển thị hiệu ứng gõ chữ (Streaming typing effect).
     - Các nút gợi ý thông minh: *"Tại sao điểm ATS của tôi thấp?"*, *"Tối ưu hóa kinh nghiệm gần nhất"*, *"Dự đoán 5 câu hỏi phỏng vấn kỹ thuật"*.

---

### 🔹 Giai đoạn 2.5: Kiểm Thử Toàn Diện (TDD & Verification)
- **Phân công:** `test-engineer`
- **Nội dung:**
  1. Unit tests: `ai/tests/test_ats_scorer.py`, `ai/tests/test_star_rewriter.py`.
  2. API Integration tests: `be/tests/test_ats_api.py`, `be/tests/test_chat_api.py`.
  3. Kiểm thử Frontend Build (`npm run build` đạt 0 lỗi).
  4. Chạy Master Checklist (`checklist.py` 6/6 PASS).

---

## 👥 PHÂN BỔ AGENTS & SKILLS

| Agent / Chuyên gia | Vai trò chính trong Phase 2 | Kỹ năng (Skills) áp dụng |
|:---|:---|:---|
| 🧠 **`ai-engineer`** | Thiết kế thuật toán chấm điểm ATS & Viết lại STAR | `ai-native-cli`, `gemini-api-dev`, `python-patterns` |
| 🛡️ **`backend-specialist`** | Xây dựng API routers, validate dữ liệu & lưu Database | `api-patterns`, `clean-code`, `database-design` |
| 💻 **`frontend-developer`** | Hoàn thiện UI Cột 2 (Chat) & Cột 3 (ATS Studio) | `frontend-design`, `design-taste-frontend`, `clean-code` |
| 🧪 **`test-engineer`** | Viết test suite toàn diện theo quy trình TDD (AAA Pattern) | `tdd-workflow`, `testing-patterns`, `performance-profiling` |

---

## 🏁 KẾT QUẢ ĐẠT ĐƯỢC SAU KHI HOÀN THÀNH PHASE 2

1. **Người dùng nhận được điểm số ATS chính xác từng tiêu chí** thay vì chỉ bóc tách thông tin thô.
2. **Biết chính xác những kỹ năng còn thiếu** so với yêu cầu tuyển dụng của doanh nghiệp.
3. **Có thể biến các câu văn sơ sài thành câu thành tựu chuẩn STAR ấn tượng** chỉ bằng 1 cú click chuột.
4. **Có một chuyên gia tư vấn nghề nghiệp AI đồng hành 24/7** trả lời mọi thắc mắc về hồ sơ.
