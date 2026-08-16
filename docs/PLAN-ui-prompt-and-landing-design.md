# Kế hoạch Chiến lược Thiết kế Giao diện & Bộ Khung Prompt UI (Anti-AI Cliché)

> **Mục tiêu:** Xây dựng định hướng thẩm mỹ cao cấp, nhân bản (Human-crafted), loại bỏ hoàn toàn cảm giác "AI generic", thiết lập cấu trúc Landing Page đột phá và tạo bộ Prompt chuẩn cho Google Stitch / Antigravity.  
> **Tài liệu sinh bởi:** `/plan` + `/frontend-design` + `/ui-ux-pro-max`  
> **Chế độ:** PLANNING & DESIGN STRATEGY (No Code)

---

## 1. Phân tích Hiện trạng: Vì sao các giao diện AI hiện nay bị "Quá AI" (AI Cliché)?

| Điểm nhận diện "Quá AI" (Cần tránh ❌) | Định hướng "Human & Editorial Precision" (Áp dụng ✅) |
| :--- | :--- |
| **Màu tím / Hồng Neon (Purple Ban):** Gradient tím mờ ảo xuất hiện ở 90% web AI. | **Obsidian & Emerald / Warm Slate:** Tông màu trầm tĩnh, uy tín kỹ thuật, điểm xuyết xanh ngọc lục bảo (sự nghiệp phát triển) hoặc Warm Editorial. |
| **Bento Grid 4 ô rập khuôn:** Mọi tính năng bị nhét vào các ô bo tròn giống hệt nhau. | **Asymmetric & Narrative Layout:** Bố cục bất đối xứng có chủ đích, dẫn dắt câu chuyện từ nỗi đau $\to$ giải pháp $\to$ tương tác thực tế. |
| **Bóng mờ lơ lửng & Mesh Gradient:** Hình cầu 3D, vòng tròn phát sáng vô nghĩa. | **Micro-borders & Crisp Surface:** Đường viền mảnh 1px (`border-slate-800`), độ phân cấp tương phản cao, các panel sắc nét như một công cụ chuyên nghiệp (Professional Instrument). |
| **Copywriting sáo rỗng:** "Revolutionize", "Empower", "Next-gen AI Magic". | **Ngôn ngữ cụ thể, tập trung vào kết quả:** "Tăng 85% tỷ lệ vượt qua vòng lọc CV ATS", "So khớp lỗ hổng kỹ năng trong 3 giây". |

---

## 2. Bản sắc Thị giác & Hệ thống Thiết kế (Design Identity)

### 2.1. Phong cách chủ đạo: **"Modern Technical Editorial"**
Kết hợp giữa sự sắc sảo của các công cụ phát triển hàng đầu (Linear, Raycast, Stripe) với sự trang nhã, đáng tin cậy của ấn phẩm học thuật/nghề nghiệp.

### 2.2. Bảng màu tuyển chọn (Curated Color Palettes)

#### Tùy chọn A: Dark Obsidian & Emerald (Đề xuất cho AI Command Center)
- **Background Base:** `#090D16` (Deep Obsidian - đen sâu có chiều sâu, không dùng đen thuần `#000000`)
- **Card / Panel Surface:** `#111827` (Slate 900) kết hợp viền `#1E293B`
- **Primary Brand (Tương lai & Tăng trưởng):** `#10B981` (Emerald Peak) — Nút bấm chính, Match score cao.
- **Secondary Indicator (AI Signal):** `#06B6D4` (Electric Cyan) — Nhịp đập suy luận của Agent.
- **Warning (Skill Gap):** `#F59E0B` (Warm Amber) — Kỹ năng còn thiếu cần bổ sung.
- **Typography:** `#F8FAFC` (Heading), `#94A3B8` (Muted text).

#### Tùy chọn B: Editorial Warm Light (Đề xuất nếu muốn trang sáng sủa, thanh lịch)
- **Background Base:** `#FAF9F6` (Off-white / Warm Canvas)
- **Surface:** `#FFFFFF` với bóng đổ đa tầng mịn (`box-shadow: 0 1px 3px rgba(0,0,0,0.05)`)
- **Primary Text:** `#0F172A` (Slate 900)
- **Accent:** `#047857` (Deep Forest) + `#D97706` (Cognac Amber)

---

### 2.3. Hệ thống Typography Phân tầng (Font Pairing)
1. **Tiêu đề Display & Hero:** `Plus Jakarta Sans` (Weight 700) hoặc kết hợp một chút Serif cao cấp `Newsreader` cho 1-2 từ khóa tạo điểm nhấn nhân bản, uy tín.
2. **Nội dung thân bài (Body UI):** `Inter` (Weight 400, 500) — Rõ ràng, thoáng đãng, dễ đọc ở mọi kích cỡ.
3. **Dữ liệu kỹ thuật (Scores, Code, AI Trace):** `JetBrains Mono` (Weight 500) — Thể hiện sự chính xác của số liệu.

---

## 3. Kiến trúc Cấu trúc Landing Page (Wireframe & Storytelling)

Landing page không chỉ để giới thiệu, mà phải chứng minh năng lực của AI Career Agent ngay trước khi người dùng đăng ký:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. HEADER: Logo tối giản, Nav links (Tính năng, Bảng giá, Lộ trình), CTA │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. HERO SECTION:                                                        │
│    • Tiêu đề lớn: "Người đồng hành AI cho sự nghiệp công nghệ của bạn"  │
│    • Phụ đề: Phân tích CV, phát hiện khoảng trống kỹ năng & mock phỏng  │
│      vấn theo thời gian thực.                                           │
│    • Dual CTA: [Bắt đầu phân tích CV miễn phí] | [Xem Agent Demo]       │
│    • LIVE INTERACTIVE PREVIEW: Widget mô phỏng quét CV -> hiển thị      │
│      Match Score 87% ngay tại Hero (Không dùng ảnh tĩnh).               │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. SOCIAL PROOF & METRICS TICKER:                                       │
│    • 10,000+ Kỹ năng được chuẩn hóa | 94% Tương thích chuẩn ATS         │
│    • Được tin dùng bởi sinh viên & kỹ sư IT từ các trường/công ty lớn. │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. THE 4 PILLARS (Sự khác biệt cốt lõi):                                │
│    [01] Smart CV Parser: Bóc tách kinh nghiệm & định lượng thành tựu    │
│    [02] JD Gap Matcher: Ma trận kỹ năng còn thiếu & giải pháp bù đắp    │
│    [03] AI Mock Arena: Phỏng vấn giả lập theo câu hỏi tình huống thực tế│
│    [04] Adaptive Learning Roadmap: Lộ trình học cá nhân hóa theo tuần   │
├─────────────────────────────────────────────────────────────────────────┤
│ 5. INTERACTIVE WORKSPACE WALKTHROUGH:                                   │
│    Trực quan hóa không gian làm việc 3-Pane (Source -> Chat -> Insight) │
├─────────────────────────────────────────────────────────────────────────┤
│ 6. TESTIMONIALS & CASE STUDIES:                                         │
│    Câu chuyện thực tế: "Từ Junior lên Middle nhờ lộ trình 30 ngày"      │
├─────────────────────────────────────────────────────────────────────────┤
│ 7. PRICING & FAQ:                                                       │
│    Bảng giá minh bạch (Free cho sinh viên / Pro cho kỹ sư tìm việc)     │
├─────────────────────────────────────────────────────────────────────────┤
│ 8. FINAL CTA & FOOTER:                                                  │
│    CTA kích thích hành động & hệ thống liên kết minh bạch.              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Bộ Công thức & Prompt Mẫu nạp vào Google Stitch / AI Designer

Khi dùng Google Stitch hoặc AI tạo màn hình, prompt phải có cấu trúc 5 phần chuẩn:
`[Context & Role] + [Visual Theme & Palette] + [Layout Architecture] + [Specific Components & Data] + [Anti-Patterns to Avoid]`

---

### 🟢 Prompt 1: Landing Page — **v2.1 (Pro Micro-Interactions & Real Feature Mega Menu)**

> 📄 **Xem prompt v2.1 hoàn chỉnh:** [prompt-landing-page-v2.md](file:///c:/Users/dungv/AI-Career-Agent/docs/prompt-landing-page-v2.md)

**Các nâng cấp đột phá ở bản v2.1:**
- **Header Mega Menu Dropdown:** Tích hợp 5 module thực tế của hệ thống (`cv-analysis`, `job-matching`, `interview`, `learning`, `career-workspace`) kèm mô tả súc tích và SVG icons.
- **Live AI Pulse Indicator:** Chấm tròn Cyan `#06B6D4` nhấp nháy êm ái (`AI Engine Online`).
- **Simulated Typewriter / Streaming:** Luồng suy luận Agent trực quan ngay Hero Card.
- **Tech Stack Ticker:** Dải logo nhận diện công nghệ (Python, FastAPI, React, Docker, PostgreSQL) thay cho ảnh stock.
- **Vector SVG Icons (Lucide):** Loại bỏ emoji ở UI controls để giữ tính chuyên nghiệp tối đa.

---

### 🟢 Prompt 2: Career Workspace (3-Pane Command Center)

```text
Design the core SaaS application screen: "Career AI Workspace" (Desktop 3-Pane Layout).

STYLE & MOOD:
- Theme: Dark Obsidian IDE vibe (#090D16 background, #111827 panels).
- Clean, focused ergonomic workspace with zero visual clutter.

3-PANE LAYOUT:
1. Left Panel (Width: 260px) - "Source Explorer":
   - Active Resume tab with file metadata (PDF icon, "Senior_Backend_Resume.pdf", 4.2 MB).
   - Target Job Description selector dropdown ("Staff AI Engineer @ Google / Remote").
   - Quick source switcher and "Upload New JD/CV" button.
2. Center Panel (Flex-1) - "AI Co-pilot Stream":
   - Header with Session Status: "⚡ Multi-Agent Analysis Running: Matching Agent active".
   - Interactive Chat Stream showing step-by-step reasoning tokens, collapsible thought cards ("✓ CV Extracted", "✓ JD Requirements Parsed", "⟳ Comparing System Design experience").
   - Bottom floating Command Input bar with quick prompt chips ("Optimize for ATS", "Generate 5 Mock Questions", "Create 14-day Study Plan").
3. Right Panel (Width: 340px) - "Live Insight & Gap Matrix":
   - Top ATS Compatibility Score: Circular gauge showing 84% with breakdown (Hard Skills: 90%, Soft Skills: 75%, Experience: 88%).
   - Missing Skills Tag Cloud: Warning chips ("Docker", "Distributed Tracing") with "+ Add to Roadmap" action.
   - Quick Action CTA: Primary Emerald button "Generate Tailored Resume Diff".
```

---

### 🟢 Prompt 3: AI Mock Interview Arena

```text
Design a focused, interactive screen for "AI Mock Interview Arena".

STYLE & MOOD:
- Theme: Minimalist Dark Focus Mode. Dark background with high contrast readable text.
- Clean distraction-free view designed for voice/text interview practice.

LAYOUT COMPONENTS:
1. Top Bar: Interview Timer (e.g. "14:20 / 30:00"), Difficulty Badge ("Senior System Design"), and Progress dots (Question 3 of 5).
2. Question Card (Center Top): Large crisp typography displaying the situational interview question:
   "How would you architect a real-time SSE streaming service to handle 50,000 concurrent AI agents?"
3. AI Voice Waveform & Speech-to-text Box:
   - Subtle animated Cyan voice wave indicator indicating the AI speaking/listening.
   - Text transcript area with real-time speech input preview and "Record Answer" button.
4. Real-time Coaching HUD (Right or Bottom Drawer):
   - Key Keywords to Mention checklist ("EventSource", "Backpressure", "Load Balancing").
   - Clarity & Pacing gauge ("Pacing: Optimal - 130 WPM").
   - Action buttons: "Submit Answer", "Skip Question", "Request Hint from Agent".
```

---

### 🟢 Prompt 4: Job Matching & Skill Gap Roadmap

```text
Design the "Job Matching & Adaptive Learning Roadmap" screen.

STYLE & MOOD:
- Theme: Dark Obsidian with Emerald (#10B981) and Warm Amber (#F59E0B) accents.
- Data-rich dashboard with structured cards, clean data tables, and progress trees.

LAYOUT:
1. Job Match Breakdown Header: Job title, Company logo, Salary range, and Overall Fit Score (82%).
2. Two-Column Comparison Table:
   - Left Column: "Your Demonstrated Skills" (Tagged with verified projects/experience badges).
   - Right Column: "Required by Employer" (Categorized by Must-have vs Nice-to-have).
3. Skill Gap Tree & Action Plan:
   - A step-by-step 3-week visual learning timeline:
     - Week 1: "Master Redis Pub/Sub & Caching Patterns" (Estimated 6 hours, 2 curated articles, 1 project repo).
     - Week 2: "FastAPI Async Architecture & Background Workers".
     - Week 3: "Mock System Design Simulation".
   - Each item has a progress checkbox, estimated duration, and "Start Learning Module" button.
```

---

## 5. Kế hoạch Các bước Thực hiện (Action Checklist)

- [x] **Giai đoạn 1: Thiết lập Bản sắc & Thẩm mỹ**
  - Khắc phục các lỗi "AI generic", định hình phong cách *Modern Technical Editorial*.
  - Chốt 2 hệ màu (Dark Obsidian Emerald & Warm Light) và Typography scale.
- [x] **Giai đoạn 2: Cấu trúc Landing Page & Bounded Contexts**
  - Xây dựng 8 phần cốt lõi của Landing Page với live interactive preview.
  - Phác thảo 3 màn hình ứng dụng trọng tâm (Workspace 3-Pane, Mock Interview, Skill Gap).
- [x] **Giai đoạn 3: Bộ Prompts Chuẩn cho Google Stitch / AI Generator**
  - Soạn thảo 4 prompt chi tiết, cấu trúc 5 tầng, copy-paste ready cho Stitch.
- [ ] **Giai đoạn 4: Nạp Prompt vào Stitch & Xuất Code vào `fe/`**
  - Dùng Stitch MCP để sinh màn hình và tải mã HTML/Tailwind về các feature tương ứng.
