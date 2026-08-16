# 📋 Project Plan: Unified CV & Job Matching AI Studio (Gộp Phân Tích CV & Tìm Việc)

> **File:** `docs/PLAN-unified-cv-job-dashboard.md`  
> **Chế độ:** `PLANNING ONLY (Không viết code)`  
> **Trọng tâm cốt lõi:** Hợp nhất **Phân Tích CV** và **Tìm Việc So Khớp** thành **Vòng lặp Giá Trị Duy Nhất (Single Value Loop)** trên Giao diện 3 Cột.

---

## 🎯 1. Tầm Nhìn & Triết Lý Sản Phẩm (Core Product Vision)

Thay vì phân tán người dùng qua nhiều trang riêng lẻ (Trang phân tích CV riêng, Trang tìm việc riêng, Trang sửa CV riêng), chúng ta hợp nhất tất cả vào **1 Không Gian Làm Việc Duy Nhất (Unified AI Career Studio)**.

### 🔄 Vòng Lặp Trải Nghiệm Khép Kín (The Ultimate 5-Step Loop):
```text
[1. Upload CV] ──> [2. AI Phân Tích ATS & Kỹ Năng] ──> [3. Tự Động So Khớp Top Jobs]
                                                                  │
[5. Tải CV Chuẩn ATS & Ứng Tuyển] <── [4. AI Tailor CV Theo JD Khách Hàng Chọn]
```

---

## 🏛️ 2. Bố Cục Kiến Trúc 3 Cột Hợp Nhất (Unified 3-Column Layout)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚀 CareerPilot AI           [ 🔍 Tìm kiếm việc làm, kỹ năng... ]                 (⚡ Pro Plan) [👤 Avatar] │
├────────────────────────────┬───────────────────────────────────────────┬───────────────────────────────────┤
│          CỘT 1             │                   CỘT 2                   │               CỘT 3               │
│          MY CV             │               AI ASSISTANT                │         JOB MATCH & STUDIO        │
│        (26% Width)         │                (44% Width)                │            (30% Width)            │
├────────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────┤
│ • Dropzone Upload PDF/DOCX │ • Header: Agent Profile & Active Context  │ • Tab 1: 🎯 Việc Làm So Khớp (5)  │
│ • Parsed Profile Summary   │ • Chat Stream (Markdown, Code, Bullets)   │   - Thẻ Job: % Match (92%)        │
│ • Điểm ATS Gauge (82/100)  │ • AI Reasoning Accordion (Các bước tư duy)│   - Skill Match ✓ & Gap ⚠         │
│ • Kỹ năng (18) & Phân loại │ • STAR Diff Block (So sánh trước/sau)     │   - Nút: [Xem Chi Tiết] [Tailor]  │
│ • Timeline Kinh nghiệm     │ • Context Action Chips (⚡ Gợi ý lệnh)    │ • Tab 2: 📑 Studio Tailor CV      │
│ • Nút: [Đổi CV] [Tải gốc]  │ • Docked Prompt Bar (Đính kèm Job/CV)     │   - So sánh Bản gốc vs Bản sửa    │
│                            │                                           │   - Nút: [Tải Xuống PDF ATS]      │
└────────────────────────────┴───────────────────────────────────────────┴───────────────────────────────────┘
```

---

## 🚀 3. Lộ Trình Triển Khai 6 Giai Đoạn Tinh Gọn (6-Phase Modular Roadmap)

### 🔹 Phase 1: Framework & 3-Column Command Center (Khung Cơ Sở)
- **Mục tiêu:** Dựng khung chuẩn Responsive, thanh Header cố định, và 3 cột cuộn độc lập với thanh cuộn siêu mảnh.
- **Component cần làm:**
  - `components/layout/Header.tsx` (Logo, Global Search Bar, Avatar profile)
  - `components/layout/StudioLayout.tsx` (3 Cột: Left Panel, Center Chat, Right Studio)
  - `components/ui/Badge.tsx`, `components/ui/Button.tsx`, `components/ui/Card.tsx`, `components/ui/Drawer.tsx`

---

### 🔹 Phase 2: My CV Panel (Quản Lý & Hiển Thị Hồ Sơ Ứng Viên - Cột 1)
- **Mục tiêu:** Cho phép người dùng kéo thả upload file CV, hiển thị thông tin đã bóc tách và điểm số ATS tổng quan.
- **Trạng thái giao diện (UI States):**
  1. *Empty State:* Drag & Drop zone ấn tượng, hỗ trợ PDF/DOCX.
  2. *Parsing State:* Skeleton loader + Đèn quét laser mô phỏng AI bóc tách sections.
  3. *Loaded State:* 
     - Tên, Chức danh mục tiêu (AI Engineer / Backend Lead).
     - ATS Score Gauge (82/100) kèm 3 trục (Kỹ năng, Tác động định lượng, Cấu trúc).
     - Skill Badges (Phân nhóm: Core Tech, Cloud/DevOps, Database).
     - Experience Timeline thu nhỏ.
     - Nút `[Thay CV khác]` / `[Xem file gốc]`.

---

### 🔹 Phase 3: AI Assistant Center (Trung Tâm Đối Thoại Chuyên Sâu - Cột 2)
- **Mục tiêu:** Đối thoại 2 chiều thông minh, tự động nhận biết ngữ cảnh từ CV (Cột 1) và Job đang chọn (Cột 3).
- **Tính năng trọng tâm:**
  - Chat history mượt mà với Markdown & cú pháp code highlight.
  - **Quick Action Prompt Chips:**
    - `⚡ Phân tích điểm yếu lớn nhất trong CV`
    - `⚡ So sánh CV với JD VNG / MoMo`
    - `⚡ Tối ưu câu kinh nghiệm theo chuẩn STAR`
    - `⚡ Tạo câu hỏi phỏng vấn cho dự án này`
  - **AI Reasoning Accordion:** Xem từng bước suy luận của AI (Đã quét từ khóa, phát hiện điểm thiếu, chuẩn bị đề xuất).
  - Docked multiline prompt bar hỗ trợ phím tắt `Enter` để gửi, `Shift + Enter` xuống dòng.

---

### 🔹 Phase 4: Job Match Feed & Drawer Chi Tiết (So Khớp Việc Làm - Cột 3 / Tab 1)
- **Mục tiêu:** Biến Cột 3 thành sàn việc làm được cá nhân hóa 100% theo CV hiện tại.
- **Cấu trúc Thẻ Job (Job Card):**
  - Tiêu đề vị trí, Tên công ty, Mức lương ($2,500 - $3,500), Địa điểm.
  - **Huy hiệu % Match:** `96% Match`, `92% Match`, `85% Match`.
  - **Bộ đối chiếu kỹ năng trực quan:**
    - Kỹ năng khớp: `Python ✓`, `FastAPI ✓`, `PostgreSQL ✓` (Màu xanh Emerald).
    - Kỹ năng còn thiếu: `Kubernetes ⚠`, `AWS ⚠` (Màu vàng Amber).
  - **Hành động tức thì:**
    - Nút `[Xem chi tiết JD]` $\rightarrow$ Mở Drawer bên phải mà không làm mất trang.
    - Nút `[Tailor CV cho Job này]` $\rightarrow$ Tự động chuyển sang Tab Studio Tailor.
- **Bộ lọc nhanh (Quick Filter Chips):** `Tất cả`, `Lương > 30M`, `Remote / Hybrid`, `Match > 90%`.

---

### 🔹 Phase 5: Studio Tailor CV & STAR Diff Viewer (Cột 3 / Tab 2)
- **Mục tiêu:** Xem sự biến đổi thần tốc của CV trước và sau khi AI tối ưu hóa theo JD mục tiêu.
- **Tính năng Studio:**
  - **Version Switcher:** Chuyển đổi qua lại giữa `v2 (Đã tối ưu theo JD)` và `v1 (Bản gốc)`.
  - **STAR Diff Viewer:** Đánh dấu màu nổi bật những câu văn đã được viết lại thêm số liệu định lượng (Ví dụ: *Tăng tốc độ xử lý 35%, chịu tải 10,000+ RPS*).
  - **Điểm ATS tăng trưởng:** Hiển thị điểm số tăng từ `82%` $\rightarrow$ `95%`.
  - **Export PDF Button:** Nút tải bản PDF sạch chuẩn ATS 2026.

---

### 🔹 Phase 6: Deep Integration 3 Cột (Sự Kết Nối Liền Mạch)
- **Mục tiêu:** Người dùng không cần copy/paste qua lại giữa các cửa sổ.
  - Click vào 1 Job bất kỳ ở Cột 3 $\rightarrow$ AI ở Cột 2 tự động chào: *"Tôi thấy bạn đang quan tâm vị trí Senior AI Engineer tại ABC Tech, bạn có muốn tôi viết lại mục Tóm tắt để nhấn mạnh kinh nghiệm RAG không?"*
  - Click `[Áp dụng vào CV]` ở Cột 2 $\rightarrow$ Cột 3 tự động cập nhật bản CV mới thời gian thực.

---

## 🎨 4. Cấu Trúc Thư Mục Thành Phần Đề Xuất (`fe/src/`)

```text
fe/src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx              # Navbar cố định (Logo, Search, User)
│   │   └── StudioLayout.tsx        # Container 3 cột có resizable/independent scroll
│   ├── cv/
│   │   ├── CvUploadDropzone.tsx    # Kéo thả nộp CV
│   │   ├── CvProfileSummary.tsx    # Tóm tắt ứng viên + Kỹ năng
│   │   └── AtsScoreGauge.tsx       # Vòng đo điểm ATS + 3 trục
│   ├── chat/
│   │   ├── ChatMessageStream.tsx   # Danh sách tin nhắn AI / User
│   │   ├── AiReasoningBox.tsx      # Quá trình suy luận AI
│   │   ├── StarDiffCard.tsx        # So sánh Before/After câu văn STAR
│   │   └── PromptInputDock.tsx     # Ô gõ lệnh cố định đáy cột 2
│   ├── jobs/
│   │   ├── JobMatchCard.tsx        # Thẻ việc làm với % Match & Skill gap
│   │   ├── JobFilterBar.tsx        # Lọc nhanh theo lương, địa điểm, role
│   │   └── JobDetailDrawer.tsx     # Drawer trượt xem toàn văn JD
│   ├── studio/
│   │   ├── TailorCvViewer.tsx      # Bản xem trước CV live
│   │   └── VersionSelector.tsx     # Chuyển đổi v1 vs v2
│   └── ui/                         # Atomic components (Button, Badge, Modal...)
└── pages/
    └── StudioWorkspacePage.tsx     # Trang trung tâm hợp nhất toàn bộ
```

---

## 💡 5. Ưu Điểm Khi Hợp Nhất So Với Tách Rời:

1. **Giảm 80% thao tác chuyển trang:** Ứng viên vừa nhìn thấy điểm yếu CV của mình, vừa thấy ngay các công ty đang tuyển đúng vị trí đó, vừa bấm 1 nút là AI tối ưu hóa ngay lập tức.
2. **Trực quan hóa giá trị của AI Agent:** Người dùng thấy rõ sự biến chuyển dữ liệu: *CV cũ (82%) + JD mục tiêu $\rightarrow$ AI phân tích $\rightarrow$ CV mới (95%)*.
3. **Hiệu năng Frontend cực đỉnh:** Toàn bộ chạy trên **Vite SPA**, chuyển tab và update state trong **0 mili-giây** không cần reload trang.

---

👉 **Trạng thái:** Kế hoạch đã hoàn thành tại [`docs/PLAN-unified-cv-job-dashboard.md`](file:///c:/Users/dungv/AI-Career-Agent/docs/PLAN-unified-cv-job-dashboard.md). Bạn hãy xem qua bản kế hoạch ý tưởng này và cho tôi biết cảm nhận nhé!
