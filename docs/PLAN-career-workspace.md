# 📋 Kế Hoạch Triển Khai: AI Career Workspace (`/workspace`)

> **Mã kế hoạch:** `PLAN-career-workspace`  
> **Route:** `fe/app/(app)/workspace/page.tsx`  
> **Preview:** `fe/app/(app)/workspace/preview.html`  
> **Mục tiêu:** Xây dựng màn hình trọng tâm cốt lõi của CareerPilot AI — Không gian làm việc 3 cột công thái học (3-Pane Workspace) kết hợp phân tích CV trực quan, hội thoại thông minh với AI Multi-Agent, và ma trận khoảng trống kỹ năng thời gian thực.

---

## 🎨 1. Hệ Thống Thiết Kế & Nguyên Tắc UI/UX (Design System)

- **Aesthetic:** "Modern Technical Precision" — Lấy cảm hứng từ Linear, Raycast, Stripe.
- **Bảng màu (Dark Obsidian Canvas):**
  - Background tổng: `#090D16` (Deep Obsidian)
  - Khung Panel / Cards: `#111827` (Slate 900) & `#181b25` (Surface)
  - Viền cấu trúc: `1px solid #1E293B`
  - Viền Hover tương tác: `1px solid #10b981` (Emerald transition)
  - Primary Accent: `#10b981` & `#4edea3` (Emerald Peak)
  - Warning / Skill Gap: `#f59e0b` (Amber)
  - Secondary Accent: `#06b6d4` (Electric Cyan)
  - Text: `#f8fafc` (Primary), `#94a3b8` (Muted), `#bbcabf` (Secondary)
- **Typography:**
  - Tiêu đề & Nhãn: `Plus Jakarta Sans` (Weight 600 / 700)
  - Nội dung & Hội thoại: `Inter` (Weight 400 / 500)
  - Mã nguồn, Tokens & Điểm số: `JetBrains Mono` (Weight 500 / 600)
- **Quy tắc cấm (Anti-patterns):**
  - ❌ Không dùng màu tím (Purple Ban)
  - ❌ Không dùng Bento Grid nhàm chán hoặc Mesh Gradient mờ
  - ❌ Không dùng Monospace in hoa cho câu văn tiếng Việt dài

---

## 🏗️ 2. Cấu Trúc Giao Diện 3 Cột (3-Pane Workspace Architecture)

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Top Navigation Bar (Session Title, Mode Switcher: Phân tích CV | Phỏng vấn | Lộ trình, Action CTA)│
├──────────────────────┬────────────────────────────────────────────┬───────────────────────────────┤
│                      │                                            │                               │
│  PANE 1: NGUỒN HỒ SƠ │        PANE 2: TRUNG TÂM HỘI THOẠI         │      PANE 3: INSIGHT & ATS    │
│   (Source Panel)     │                (Agent Chat)                │        (Analytics Panel)      │
│     [Width: 280px]   │             [Flex-1 / Flexible]            │         [Width: 340px]        │
│                      │                                            │                               │
│ • Tabs: CV / Job JD  │ • Agent Reasoning Stream (Thinking tokens) │ • ATS Radial Match Gauge (94%)│
│ • File Uploader PDF  │ • Tin nhắn phân tích định dạng Markdown   │ • Ma trận Kỹ năng (Match/Gap) │
│ • Target JD Selector │ • Khối mã Code / Diff đề xuất sửa CV      │ • Hành động sửa nhanh CV      │
│ • Trích xuất Section │ • Action Chips (STAR, Phỏng vấn, Match JD) │ • Radar Chart / Skill Matrix  │
│                      │ • Input Prompt Bar đa năng                 │                               │
│                      │                                            │                               │
└──────────────────────┴────────────────────────────────────────────┴───────────────────────────────┘
```

---

## 📋 3. Phân Rã Công Việc (Task Breakdown)

### 🔹 Giai đoạn 1: Khởi tạo Shell & Routing
- [ ] Tạo thư mục `fe/app/(app)/workspace`
- [ ] Khởi tạo Workspace Top Header (Logo thu nhỏ, Bộ chuyển chế độ `CV Optimizer` / `Interview Prep` / `Skill Roadmap`, Nút Xuất Báo Cáo PDF, Nút Quay lại Home).
- [ ] Thiết kế Layout Container 3 cột hỗ trợ Toggle/Collapse Pane trái & phải trên màn hình nhỏ.

### 🔹 Giai đoạn 2: Xây dựng Pane 1 — Nguồn Hồ Sơ & JD (`SourcePanel`)
- [ ] Trình quản lý CV tải lên (PDF chip, Dung lượng, Trạng thái phân tích).
- [ ] Xem trước trích xuất văn bản CV theo từng mục (Kinh nghiệm, Kỹ năng, Dự án, Học vấn).
- [ ] Bộ chọn Target JD: Nạp JD từ việc làm có sẵn hoặc dán JD văn bản tùy biến.

### 🔹 Giai đoạn 3: Xây dựng Pane 2 — Trung tâm AI Multi-Agent (`CenterPanel`)
- [ ] Dòng thời gian hội thoại (Timeline Chat) với Agent Avatar & Badge chuyên môn (*Resume Analyzer Agent*, *JD Matcher Agent*).
- [ ] Khối hiển thị tiến trình suy luận (Reasoning Accordion: "Đang đối chiếu 18 từ khóa kỹ thuật...").
- [ ] Khối Diff so sánh trước/sau khi tối ưu câu đạn mô tả kinh nghiệm (STAR Method).
- [ ] Khung nhập liệu (Prompt Input Box) kèm các phím tắt gợi ý (Prompt Action Chips).

### 🔹 Giai đoạn 4: Xây dựng Pane 3 — Phân Tích Chuyên Sâu (`InsightPanel`)
- [ ] Đồng hồ đo điểm ATS Radial Gauge SVG tương tác động.
- [ ] Ma trận phân loại kỹ năng:
  - 🟢 Kỹ năng khớp cao (`FastAPI`, `PostgreSQL`, `Docker`)
  - 🟡 Kỹ năng còn thiếu / Cần cải thiện (`Kubernetes`, `Distributed Tracing`)
  - 🔵 Điểm mạnh định lượng (Metrics & Impact).
- [ ] Nút CTA hành động nhanh: *"Áp dụng tất cả đề xuất vào CV"*, *"Tạo 5 câu hỏi phỏng vấn cho JD này"*.

### 🔹 Giai đoạn 5: Hoàn thiện, Kiểm thử & Tài liệu
- [ ] Tạo file giao diện độc lập `fe/app/(app)/workspace/preview.html` để kiểm tra trực quan.
- [ ] Chạy kiểm thử TypeScript `npx tsc --noEmit`.
- [ ] Kiểm thử responsive (Desktop 1440px, Laptop 1024px, Tablet/Mobile).

---

## 🏁 4. Kế Hoạch Kiểm Tra (Verification Checklist)

| Hạng mục | Tiêu chí đánh giá | Trạng thái |
| :--- | :--- | :---: |
| **Bố cục 3-Pane** | Hiển thị chuẩn 3 cột trên Desktop, cuộn độc lập từng cột | ⏳ Chờ thực hiện |
| **Typography** | Sử dụng Plus Jakarta Sans, Inter và JetBrains Mono đúng phân cấp | ⏳ Chờ thực hiện |
| **TypeScript** | `npx tsc --noEmit` đạt 0 lỗi | ⏳ Chờ thực hiện |
| **Màu sắc & UI** | Không dùng màu tím, viền 1px slate-800, điểm nhấn Emerald sắc nét | ⏳ Chờ thực hiện |
