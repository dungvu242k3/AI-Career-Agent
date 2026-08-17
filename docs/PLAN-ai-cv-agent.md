# 🚀 PLAN: AI Career Agent — MVP → Production

> **Mục tiêu:** Xây dựng hệ thống AI tự động hóa quy trình ứng tuyển việc làm IT  
> **Kiến trúc:** Semi-auto Agent (AI chuẩn bị → User confirm → Thực thi)  
> **Tech:** Python FastAPI + Gemini 2.5 Flash + Vite React (FE đã có)  
> **Ngành:** Công nghệ thông tin  

---

## 📐 TỔNG QUAN KIẾN TRÚC

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vite + React)                   │
│  HomePage │ WorkspacePage (3-col) │ JobsPage │ Applications  │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Python FastAPI)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CHAT AGENT (Orchestrator)                │   │
│  │         Gemini 2.5 Flash + Function Calling          │   │
│  │  Hiểu intent → Gọi đúng Service → Trả kết quả      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  ┌────────┬───────────┼───────────┬──────────┬──────────┐   │
│  │        │           │           │          │          │   │
│  ▼        ▼           ▼           ▼          ▼          ▼   │
│ Parser  Analyzer   Crawler    Matcher   Rewriter   Mailer   │
│ (CV/JD) (ATS Score) (Jobs)   (CV↔Job)  (STAR CV) (Draft)   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  DATABASE (SQLite/PostgreSQL)         │   │
│  │  candidates │ jobs │ applications │ conversations    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PHÂN CHIA PHASE — MVP → PRODUCTION

| Phase | Tên | Mô tả | Timeline |
|-------|-----|-------|----------|
| **Phase 1** | CV Intelligence | Upload CV → Parse → Phân tích → Chấm điểm ATS | 2 tuần |
| **Phase 2** | Job Intelligence | Crawl jobs → So khớp CV↔Job → Ranking | 2 tuần |
| **Phase 3** | Automation Engine | Tailor CV + Cover Letter + Email draft + Confirm flow | 2 tuần |
| **Phase 4** | Agent & Tracking | Chat Agent điều phối + Application tracker + Dashboard | 2 tuần |

---

## 📋 PHASE 1: CV INTELLIGENCE (MVP Core)

> **Mục tiêu:** User upload CV (PDF) → Hệ thống trả về phân tích chi tiết + điểm ATS + gợi ý cải thiện

### 1.1 Luồng Chi Tiết

```
User upload PDF
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  PDF Parser │────▶│ LLM Extract  │────▶│ Candidate     │
│  (PyMuPDF)  │     │ (Gemini Flash)│    │ Profile JSON  │
└─────────────┘     └──────────────┘     └───────┬───────┘
                                                  │
                                    ┌─────────────┤
                                    ▼             ▼
                              ┌──────────┐  ┌──────────────┐
                              │ATS Score │  │ Skill Gap    │
                              │& Rubric  │  │ Analysis     │
                              └──────────┘  └──────────────┘
                                    │             │
                                    ▼             ▼
                              ┌──────────────────────────┐
                              │  CV Analysis Report      │
                              │  (JSON → Render trên FE) │
                              └──────────────────────────┘
```

### 1.2 Backend Folder Structure

```
be/
├── main.py                      # FastAPI app entry
├── config.py                    # Settings, API keys
├── requirements.txt
│
├── api/
│   └── v1/
│       ├── __init__.py
│       └── cv_router.py         # POST /api/v1/cv/upload
│                                # POST /api/v1/cv/analyze
│                                # GET  /api/v1/cv/{id}/report
│
├── services/
│   ├── __init__.py
│   ├── pdf_parser.py            # PyMuPDF: PDF → raw text
│   ├── cv_extractor.py          # Gemini Flash: text → structured JSON
│   └── cv_analyzer.py           # Gemini Flash: JSON → ATS score + recommendations
│
├── models/
│   ├── __init__.py
│   ├── candidate.py             # Pydantic: CandidateProfile schema
│   └── analysis.py              # Pydantic: AnalysisReport schema
│
├── prompts/
│   ├── extract_cv.txt           # Prompt template: bóc tách CV
│   └── analyze_cv.txt           # Prompt template: chấm điểm ATS
│
└── db/
    ├── __init__.py
    ├── database.py              # SQLite connection
    └── migrations/
```

### 1.3 Task Breakdown Phase 1

| # | Task | Chi tiết | Effort |
|---|------|----------|--------|
| 1.1 | Setup FastAPI project | Cấu trúc thư mục, requirements, config | 2h |
| 1.2 | PDF Parser service | PyMuPDF đọc PDF → text thuần | 3h |
| 1.3 | CV Extractor service | Gemini Flash: text → CandidateProfile JSON | 4h |
| 1.4 | Candidate Profile schema | Pydantic model chuẩn hóa | 2h |
| 1.5 | CV Analyzer service | Gemini Flash: profile → ATS score + rubric | 4h |
| 1.6 | Analysis Report schema | Pydantic model cho output report | 2h |
| 1.7 | API endpoints | Upload + Analyze + Get Report | 3h |
| 1.8 | Prompt engineering | Viết + test 2 prompt templates | 4h |
| 1.9 | Database setup | SQLite + table candidates, analyses | 2h |
| 1.10 | FE integration | Kết nối WorkspacePage với API | 4h |
| 1.11 | Testing | Unit test services + API integration test | 4h |

**Tổng Phase 1: ~34h (~2 tuần part-time)**

### 1.4 Schema Chi Tiết

#### CandidateProfile (Output của CV Extractor)

```python
class SkillItem(BaseModel):
    name: str                           # "Python", "FastAPI"
    level: str                          # "expert", "intermediate", "beginner"
    category: str                       # "programming", "framework", "devops"

class WorkItem(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str | None                # None = hiện tại
    bullets: list[str]                  # Các mô tả kinh nghiệm

class CandidateProfile(BaseModel):
    # Thông tin cá nhân
    full_name: str
    email: str | None
    phone: str | None
    location: str | None
    linkedin: str | None
    github: str | None
    portfolio: str | None

    # Tổng quan
    title: str                          # "AI Engineer"
    summary: str | None
    experience_years: int

    # Chi tiết
    skills: list[SkillItem]
    education: list[EducationItem]
    work_history: list[WorkItem]
    projects: list[ProjectItem]
    certifications: list[str]

    # Mục tiêu
    preferred_roles: list[str]
    preferred_locations: list[str]
    salary_expectation: str | None
```

#### AnalysisReport (Output của CV Analyzer)

```python
class RubricItem(BaseModel):
    category: str                       # "skills_relevance"
    score: int                          # 18
    max_score: int                      # 20
    feedback: str                       # "Core tech stack mạnh, thiếu Cloud"

class Recommendation(BaseModel):
    priority: str                       # "HIGH", "MEDIUM", "LOW"
    category: str                       # "work_experience"
    current: str                        # Câu gốc trong CV
    suggested: str                      # Câu đề xuất viết lại
    reason: str                         # Lý do cần sửa

class AnalysisReport(BaseModel):
    # Điểm tổng
    ats_score: int                      # 0-100
    ats_grade: str                      # "A", "B+", "C"

    # Điểm chi tiết (Rubric 7 hạng mục, tổng 100đ)
    rubric: list[RubricItem]
    # Categories:
    #   - contact_info (10đ)
    #   - professional_summary (10đ)
    #   - skills_relevance (20đ)
    #   - work_experience_quality (25đ)
    #   - impact_metrics (15đ)
    #   - education_certs (10đ)
    #   - formatting_ats (10đ)

    # Phân tích kỹ năng
    strong_skills: list[str]
    weak_skills: list[str]
    missing_for_market: list[str]       # Kỹ năng trending mà CV thiếu
    
    # Đề xuất cải thiện
    recommendations: list[Recommendation]

    # Câu văn cần viết lại
    bullets_to_improve: list[BulletImprovement]
```

### 1.5 Prompt Strategy

| Prompt | LLM | Tokens | Chi phí | Kỹ thuật |
|--------|-----|--------|---------|----------|
| CV Extraction | Gemini 2.0 Flash | ~3,000 | ~200đ | JSON mode, temp=0.1 |
| CV Analysis | Gemini 2.5 Flash | ~5,000 | ~600đ | Thinking ON, few-shot, temp=0.3 |

---

## 📋 PHASE 2: JOB INTELLIGENCE

> **Mục tiêu:** Crawl việc làm IT từ nhiều nguồn → So khớp với CV → Ranking top matches

### 2.1 Luồng

```
┌──────────────────────────────────────────────┐
│  Job Crawler (scheduled hoặc on-demand)      │
│                                              │
│  ITviec ──┐                                  │
│  TopCV ───┤──▶ Normalize ──▶ Jobs Database   │
│  LinkedIn ┘                                  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Matcher Service                             │
│  CandidateProfile + Jobs[] → Ranked Results  │
│                                              │
│  Scoring:                                    │
│  - Skills overlap (40%)                      │
│  - Experience level fit (20%)                │
│  - Location match (15%)                      │
│  - Salary range fit (10%)                    │
│  - Company culture signals (15%)             │
└──────────────────────────────────────────────┘
```

### 2.2 Folder Structure Additions

```
be/services/crawlers/
├── base_crawler.py          # Abstract base class
├── itviec_crawler.py        # ITviec scraper
├── topcv_crawler.py         # TopCV scraper
└── linkedin_crawler.py      # LinkedIn scraper (Playwright)

be/services/
├── job_normalizer.py        # Raw HTML → JobPosting schema
└── job_matcher.py           # Profile + Jobs → Ranked matches

be/api/v1/
└── job_router.py            # GET /jobs/search, GET /jobs/match/{id}
```

### 2.3 Task Breakdown Phase 2

| # | Task | Effort |
|---|------|--------|
| 2.1 | Base crawler + rate limiting | 3h |
| 2.2 | ITviec crawler | 4h |
| 2.3 | TopCV crawler | 4h |
| 2.4 | LinkedIn crawler (Playwright) | 6h |
| 2.5 | Job normalizer | 3h |
| 2.6 | JobPosting schema | 2h |
| 2.7 | Job matcher (Gemini Flash) | 4h |
| 2.8 | Jobs DB + API endpoints | 3h |
| 2.9 | FE: JobsPage kết nối API | 4h |
| 2.10 | Testing | 3h |

**Tổng Phase 2: ~36h (~2 tuần)**

---

## 📋 PHASE 3: AUTOMATION ENGINE

> **Mục tiêu:** Matched jobs → Tự tạo CV tailored + Cover Letter + Email draft → User confirm → Gửi

### 3.1 Luồng Semi-Auto

```
User chọn Job muốn apply
        │
        ▼
  CV Tailor Service → Viết lại bullets theo JD (Gemini Flash)
        │
        ▼
  Cover Letter Service → Sinh Cover Letter (Gemini Flash)
        │
        ▼
  Email Draft Service → Tạo email + đính kèm
        │
        ▼
  🔔 CONFIRMATION QUEUE
  ├── ✅ CV tailored (PDF preview)
  ├── ✅ Cover Letter
  ├── ✅ Email subject + body
  └── [Chỉnh sửa] [Bỏ qua] [GỬI ✓]
        │
   User confirm
        │
        ▼
  Send via SMTP (email) hoặc Playwright (form)
```

### 3.2 Task Breakdown Phase 3

| # | Task | Effort |
|---|------|--------|
| 3.1 | CV Rewriter (STAR optimization) | 4h |
| 3.2 | Cover Letter generator | 3h |
| 3.3 | Email drafter | 3h |
| 3.4 | PDF exporter (WeasyPrint) | 4h |
| 3.5 | Confirmation queue API | 4h |
| 3.6 | SMTP email sender | 3h |
| 3.7 | Playwright form submitter | 6h |
| 3.8 | Application schema + DB | 2h |
| 3.9 | FE: Apply flow UI + Preview | 6h |
| 3.10 | Testing | 3h |

**Tổng Phase 3: ~38h (~2 tuần)**

---

## 📋 PHASE 4: AGENT & TRACKING

> **Mục tiêu:** Chat Agent điều phối toàn bộ + Dashboard theo dõi applications

### 4.1 Chat Agent (Function Calling)

```
User: "Tìm việc AI Engineer ở HCM, apply top 3"

Agent (Gemini 2.5 Flash):
  1. job_matcher.search(skills, location="HCM")
  2. cv_rewriter.tailor(profile, top_3_jds)
  3. cover_letter.generate(profile, top_3_jds)
  4. email_drafter.compose(3 drafts)
  5. → "Đã chuẩn bị 3 bộ hồ sơ, xem tại /applications"
```

### 4.2 Application Tracker

```
┌──────────────────────────────────────────────┐
│  📊 15 applied │ 3 interview │ 1 offer       │
│                                              │
│  VNG - AI Engineer     │ 96% │ 📧 Sent       │
│  MoMo - Backend Dev    │ 89% │ 📞 Interview  │
│  Shopee - ML Engineer  │ 85% │ ⏳ Waiting    │
│  Tiki - Data Engineer  │ 78% │ ❌ Rejected   │
└──────────────────────────────────────────────┘
```

### 4.3 Task Breakdown Phase 4

| # | Task | Effort |
|---|------|--------|
| 4.1 | Chat Agent + function calling | 6h |
| 4.2 | Agent tools definition (5 tools) | 4h |
| 4.3 | Conversation memory (SQLite) | 3h |
| 4.4 | Application tracker API | 4h |
| 4.5 | Status update flow | 3h |
| 4.6 | FE: ApplicationsPage | 5h |
| 4.7 | FE: Chat UI in WorkspacePage | 5h |
| 4.8 | E2E Testing | 4h |

**Tổng Phase 4: ~34h (~2 tuần)**

---

## 🏗️ TECH STACK

| Layer | Technology | Lý do |
|-------|-----------|-------|
| **Frontend** | Vite + React 19 + TS | Đã có sẵn |
| **Backend** | Python 3.12 + FastAPI | Async, AI ecosystem |
| **LLM** | Gemini 2.5 Flash | Rẻ nhất, Thinking, Function Calling |
| **PDF Parse** | PyMuPDF | Nhanh, lightweight |
| **PDF Export** | WeasyPrint | HTML → PDF |
| **Scraping** | httpx + BS4 + Playwright | Static + Dynamic |
| **Database** | SQLite → PostgreSQL | Zero config MVP |
| **Email** | smtplib | Built-in |
| **AI SDK** | google-genai | Official, lightweight |

---

## 💰 CHI PHÍ

| Hạng mục | /tháng |
|----------|--------|
| Gemini API (100 phiên) | ~340,000đ (~$14) |
| Server (free tier) | 0đ |
| **Tổng MVP** | **~340,000đ** |

---

## 📅 TIMELINE

```
Tuần 1-2:  Phase 1 — CV Intelligence (MVP 🏁)
Tuần 3-4:  Phase 2 — Job Intelligence
Tuần 5-6:  Phase 3 — Automation Engine
Tuần 7-8:  Phase 4 — Agent & Tracking
Tuần 9:    Polish + Testing + Deploy
```

**Tổng: ~9 tuần part-time → Production-ready**
