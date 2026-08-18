# 📋 KẾ HOẠCH THIẾT KẾ & TRIỂN KHAI: AI CAREER CHAT & WORKFLOW TÌM VIỆC ĐA NỀN TẢNG

> **Mã kế hoạch:** `docs/PLAN-job-search-chat-copilot.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Lập kế hoạch kiến trúc)**  
> **Kiến trúc sư:** `@[project-planner]`, `@[backend-specialist]`, `@[frontend-specialist]`  
> **Mục tiêu:** Xây dựng khung Chat AI Career Copilot tự nhiên ở Cột 2 kết hợp **Workflow Tìm kiếm việc làm thông minh đa nền tảng (ITviec, TopCV, LinkedIn, VietnamWorks...)** dựa trên hồ sơ ứng viên và câu lệnh chat.

---

## 🏗️ 1. TỔNG QUAN KIẾN TRÚC WORKFLOW (ARCHITECTURE OVERVIEW)

Hệ thống kết hợp giữa **Chat đàm thoại tự nhiên** và **Công cụ tìm kiếm việc làm tự động (Job Search Tool / Intent Detection)**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            KIẾN TRÚC AI CHAT & JOB SEARCH WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  [ỨNG VIÊN CHAT HOẶC BẤM NÚT]                                                               │
│  "Tìm việc Backend Golang Remote lương > $2000" HOẶC "Tìm việc phù hợp với CV của tôi"      │
│                                  │                                                          │
│                                  ▼                                                          │
│  [AI COPILOT AGENT (INTENT CLASSIFIER & CONTEXT INJECTION)]                                 │
│  • Đọc CandidateProfile (Kỹ năng, Kinh nghiệm, Title) từ Cột 1                              │
│  • Phân loại ý định:                                                                        │
│    ├── 1. Chat thông thường ➔ Trả lời Streaming Markdown (Tư vấn CV, Cover Letter, FAQ)    │
│    └── 2. Ý định tìm việc ➔ Kích hoạt `job_search_engine`                                   │
│                                  │                                                          │
│                                  ▼                                                          │
│  [MULTI-PLATFORM JOB SEARCH ENGINE (Backend Aggregator)]                                    │
│  • Lấy dữ liệu việc làm thực tế từ các nguồn: ITviec, TopCV, LinkedIn, VietnamWorks         │
│  • Tự động chấm độ khớp nhanh (% Match Score) so với CV của ứng viên                       │
│                                  │                                                          │
│                                  ▼                                                          │
│  [GIAO DIỆN INTERACTIVE JOB CARDS TRONG KHUNG CHAT (Cột 2)]                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 🏢 Senior Backend Engineer (Go/PostgreSQL) — VNG Corporation                          │  │
│  │ 📍 TP. HCM (Hybrid) | 💰 $2,500 - $3,500 | 🎯 Khớp 92% với CV của bạn                │  │
│  │ 🏷️ [Golang] [PostgreSQL] [Kafka] [Docker]                                             │  │
│  │                                                                                       │  │
│  │ [🎯 Nạp JD này để So Khớp & May Đo CV]      [🔗 Xem bài đăng gốc trên ITviec]        │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                  │                                                          │
│                                  ▼ (Khi bấm nút "Nạp JD này")                               │
│  ➔ Tự động điền JD vào Cột 1, kích hoạt ATS Scorer & Động cơ May đo Harvard CV ở Cột 3!    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 2. CHI TIẾT CÁC HẠNG MỤC TRIỂN KHAI

### 📦 Hạng mục 1: Backend & AI Engine
1. **Module Tìm kiếm việc làm (`be/core/job_search.py`):**
   - Bộ tổng hợp việc làm đa nguồn (ITviec, TopCV, LinkedIn, VietnamWorks) hỗ trợ tìm theo: `keywords`, `location`, `level`, `salary_min`, `skills`.
   - Thuật toán xếp hạng độ khớp nhanh (`calculate_quick_match(candidate_profile, job_item)`).
2. **AI Chat Engine & Intent Handler (`ai/analysis/chat_agent.py`):**
   - System Prompt thông minh nhận biết ngữ cảnh ứng viên:
     - Trả lời tư vấn lộ trình sự nghiệp, tối ưu CV, viết email/cover letter.
     - Tự động gọi tool `job_search` khi người dùng có nhu cầu tìm việc.
3. **API Endpoint Chat Streaming (`be/api/v1/chat_router.py`):**
   - `POST /api/v1/chat/message`: Hỗ trợ phản hồi hội thoại có đính kèm danh sách `jobs_found: List[JobCard]`.
   - `GET /api/v1/jobs/recommendations?candidate_id=...`: Lấy danh sách việc làm gợi ý tự động theo kỹ năng trong CV.

---

### 🎨 Hạng mục 2: Giao diện Người dùng (Frontend Studio Cột 2)
1. **Nâng cấp Khung Chat tương tác (`fe/src/components/AIChatCopilot.tsx`):**
   - Thay thế khung reasoning tĩnh hiện tại bằng hội thoại 2 chiều mượt mà.
   - Hỗ trợ hiển thị tin nhắn Text/Markdown + Thẻ công việc tương tác (**Interactive Job Cards**).
2. **Các nút Shortcut 1-chạm nhanh chóng (Action Chips):**
   - 🔍 *"Tìm việc phù hợp nhất với CV của tôi"*
   - 🇻🇳 *"Tìm việc Backend tại Hà Nội / TP.HCM"*
   - 🌍 *"Tìm việc Remote toàn cầu"*
   - ✍️ *"Viết giúp tôi Cover Letter cho vị trí này"*
3. **Hành động 1-Click "So Khớp JD Ngay" (Seamless Workflow Bridge):**
   - Khi bấm vào 1 công việc trong chat ➔ Tự động chuyển nội dung JD sang Khung JD ở Cột 1 và kích hoạt tính điểm ATS + sinh CV May Đo chuẩn Harvard ở Cột 3 mà không cần copy/paste thủ công!

---

## 🎯 3. KẾ HOẠCH BẢO VỆ & AN TOÀN (TESTING & SECURITY)
- Rate limiting cho endpoint Chat và Job Search (ngăn spam bot).
- Sanitize HTML/Markdown trong tin nhắn chat chống XSS.
- Unit test cho Job Search Engine, Chat Router và UI Component.
