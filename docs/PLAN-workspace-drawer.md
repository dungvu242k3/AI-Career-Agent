# 📋 Kế Hoạch Triển Khai: AI Career Workspace — Mô Hình Drawer Slide-over (Hướng 3)

> **Mã kế hoạch:** `PLAN-workspace-drawer`  
> **Route chính:** `fe/app/(app)/workspace/page.tsx`  
> **Preview:** `fe/app/(app)/workspace/preview.html`  
> **Mô hình kiến trúc:** Trung tâm Hội thoại AI Toàn màn hình (Zen Focus Chat) kết hợp 2 Ngăn kéo Slide-over Drawer thông minh (Source Drawer & ATS Insight Drawer).

---

## 🎯 1. Mục Tiêu & Triết Lý Thiết Kế (Design Philosophy)

Mô hình **Hướng 3 (Drawer Slide-over & Zen Focus Workspace)** được thiết kế để giải quyết bài toán: **Tối đa hóa không gian tập trung cho việc trò chuyện & tinh chỉnh nội dung với AI Multi-Agent**, đồng thời vẫn truy cập tức thì vào CV gốc và báo cáo ATS chuyên sâu chỉ với 1 click hoặc phím tắt.

### 🌟 Nguyên tắc cốt lõi:
1. **Zen Focus (Tập trung tuyệt đối):** Không gian màn hình chính ưu tiên 100% cho dòng hội thoại thông minh, khối suy luận (Reasoning Stream), và khối so sánh trước/sau khi tối ưu CV (STAR Diff Component).
2. **Seamless Drawer Overlays:**
   - **Left Drawer (Source Panel):** Quản lý file CV tải lên, xem trước nội dung trích xuất và chọn JD mục tiêu.
   - **Right Drawer (ATS & Analytics Panel):** Bảng chẩn đoán ATS Match Score 94%, ma trận kỹ năng và nút áp dụng nhanh đề xuất.
3. **Responsive Nhất Quán (100% Responsive Parity):** Trải nghiệm đồng nhất từ Desktop màn hình lớn (1440px), Laptop (1024px) đến Tablet và Mobile (375px) mà không bị bó hẹp cột.
4. **Phím tắt Pro-Developer:** Hỗ trợ phím tắt nhanh (`Ctrl + [` mở Drawer trái, `Ctrl + ]` mở Drawer phải, `Esc` đóng ngăn kéo).

---

## 🎨 2. Hệ Thống Màu Sắc & Typography

- **Canvas nền:** `#090D16` (Deep Obsidian)
- **Khung Drawer & Cards:** `#111827` (Slate 900) kết hợp `#181b25` (Surface Level 2)
- **Viền cấu trúc:** `1px solid #1E293B`
- **Lớp phủ nền (Backdrop):** `bg-black/60 backdrop-blur-sm`
- **Màu chủ đạo (Primary Accent):** `#10b981` & `#4edea3` (Emerald Peak - Vượt qua ATS)
- **Màu cảnh báo (Warning / Skill Gap):** `#f59e0b` (Amber)
- **Màu nhấn phụ (Cyan Accent):** `#06b6d4` (Electric Cyan)
- **Typography:**
  - Tiêu đề & Nhãn: `Plus Jakarta Sans` (Weight 600 / 700)
  - Nội dung & Hội thoại: `Inter` (Weight 400 / 500)
  - Số liệu, Điểm số, Mã nguồn: `JetBrains Mono` (Weight 500 / 600)
- **Tuân thủ quy tắc cấm:** ❌ Không dùng màu tím (Purple Ban), ❌ Không dùng emoji làm biểu tượng icon.

---

## 🏗️ 3. Sơ Đồ Cấu Trúc Giao Diện (UI Architecture)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: [← Trang chủ] | [Session: Senior Backend CV] | [Chế độ: Phân tích CV ▾] | [📄 Hồ sơ] [📊 Điểm ATS]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│ ┌───────────────────────────┐    ┌──────────────────────────────────────────────┐    ┌────────────────────────┐
│ │   LEFT SLIDE-OVER DRAWER  │    │            CENTER ZEN FOCUS WORKSPACE        │    │  RIGHT SLIDE-OVER      │
│ │       (Source Drawer)     │    │                 (Multi-Agent Chat)           │    │        DRAWER          │
│ │      [Width: 380px]       │    │               [Max-width: 860px]             │    │    (ATS & Insights)    │
│ │                           │    │                                              │    │     [Width: 400px]     │
│ │ • Tải file PDF CV         │    │ • Agent Header: Resume Optimizer Agent       │    │ • Radial ATS Gauge 94% │
│ │ • Quản lý phiên bản CV    │ ◄──┤ • Reasoning Accordion (Thinking tokens...)   ├──► │ • Ma trận Kỹ năng      │
│ │ • Trích xuất Section:     │    │ • Tin nhắn phân tích định dạng Markdown      │    │   - Đạt yêu cầu (Xanh) │
│ │   - Kinh nghiệm           │    │ • Khối STAR Method Diff (So sánh Trước/Sau)  │    │   - Còn thiếu (Vàng)   │
│ │   - Kỹ năng cốt lõi       │    │ • Action Prompt Chips (Phỏng vấn, Sửa ATS...)│    │ • Nút 1-Click Apply    │
│ │ • Bộ chọn JD mục tiêu     │    │ • Multiline Input Bar + Đính kèm + Gửi       │    │ • Xuất báo cáo PDF     │
│ └───────────────────────────┘    └──────────────────────────────────────────────┘    └────────────────────────┘
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 4. Phân Rã Nhiệm Vụ Chi Tiết (Detailed Task Breakdown)

### 🔹 Giai đoạn 1: Thiết Kế Shell, State Quản Lý Drawer & Header
- [ ] Xây dựng khung giao diện `fe/app/(app)/workspace/page.tsx` với các state quản lý:
  - `isSourceDrawerOpen` (boolean)
  - `isInsightsDrawerOpen` (boolean)
  - `activeMode` (`"cv-optimize"` | `"interview-prep"` | `"skill-roadmap"`)
- [ ] Top Header điều khiển:
  - Nút quay lại Bảng điều khiển (`/home`).
  - Tiêu đề phiên làm việc có thể chỉnh sửa (`Dung_Vu_Senior_Backend_Resume_v3.pdf`).
  - Nút bấm nhanh trên Header kích hoạt Left Drawer (`📄 Xem CV & JD`) và Right Drawer (`📊 Báo cáo ATS 94%`).
  - Bắt sự kiện phím tắt bàn phím (`Ctrl + [`, `Ctrl + ]`, `Esc`).

### 🔹 Giai đoạn 2: Xây Dựng Khung Hội Thoại Trung Tâm (Zen Focus Chat)
- [ ] **Agent Identity Banner:** Hiển thị Agent đang đảm nhiệm (*Resume Optimizer & ATS Specialist*), trạng thái trực tuyến.
- [ ] **Reasoning Stream Accordion:** Hiển thị quá trình AI bóc tách dữ liệu (*"Đang đối chiếu 18 từ khóa kỹ thuật giữa CV và JD của VNG Corporation..."*).
- [ ] **STAR Method Diff Block:** Khối so sánh tương phản trực quan:
  - *Trước (Chưa tối ưu):* "Phát triển các API backend cho hệ thống thanh toán."
  - *Sau (Tối ưu hóa ATS & STAR):* "Thiết kế & tái cấu trúc 12 microservices backend bằng **FastAPI** & **PostgreSQL**, giảm 35% độ trễ API P99 và xử lý 10,000+ RPS."
- [ ] **Interactive Action Chips:** Các nút tác vụ nhanh gợi ý ngay dưới câu trả lời của AI:
  - `[Áp dụng vào CV ngay]`
  - `[Tạo 5 câu hỏi phỏng vấn cho phần này]`
  - `[Kiểm tra lại điểm ATS]`
- [ ] **Multiline Input Bar:** Khung nhập liệu hỗ trợ mở rộng tự động, nút đính kèm tài liệu và nút gửi tương tác mượt mà.

### 🔹 Giai đoạn 3: Xây Dựng Left Drawer — Quản Lý Nguồn Hồ Sơ (Source Drawer)
- [ ] Khung trượt từ bên trái với hiệu ứng trượt mượt mà `translate-x-0` và lớp phủ mờ `backdrop-blur-sm`.
- [ ] Bộ nạp file kéo thả PDF / DOCX với thanh tiến trình trích xuất.
- [ ] Trình xem trước các mục đã bóc tách (Parsed Sections: Summary, Work Experience, Tech Stack, Education).
- [ ] Bộ chuyển đổi mục tiêu: Chuyển đổi linh hoạt giữa các JD mẫu có sẵn (VNG, MoMo, Grab) hoặc dán JD tùy chỉnh.

### 🔹 Giai đoạn 4: Xây Dựng Right Drawer — Bảng Điểm ATS & Báo Cáo Chuyên Sâu (Insights Drawer)
- [ ] Khung trượt từ bên phải chứa toàn bộ công cụ đo lường chuyên sâu:
  - **ATS Radial Gauge 94%** với SVG animation sinh động.
  - **Điểm chi tiết 3 trục:** Kỹ năng chuyên môn (95%), Đo lường tác động (90%), Định dạng từ khóa (98%).
  - **Ma trận kỹ năng (Skill Gap Matrix):**
    - 🟢 Đã khớp: `FastAPI`, `PostgreSQL`, `Docker`, `Redis`
    - 🟡 Cần bổ sung: `Kubernetes Cluster`, `Distributed Tracing`
  - **Nút hành động:** *"Tự động chèn từ khóa còn thiếu vào CV"* & *"Tải xuống bản CV tối ưu (PDF)"*.

### 🔹 Giai đoạn 5: Hoàn Thiện File Preview Độc Lập & Kiểm Thử
- [ ] Tạo file xem nhanh độc lập `fe/app/(app)/workspace/preview.html` tích hợp sẵn JavaScript tương tác mở/đóng Drawer và hiệu ứng động.
- [ ] Chạy kiểm thử TypeScript `npx tsc --noEmit` đạt 0 lỗi.
- [ ] Chạy Master Checklist (`checklist.py`) đảm bảo 100% Pass (Security, Lint, Schema, Tests, UX Audit, SEO Check).

---

## 🏁 5. Bảng Kiểm Tra Hoàn Thành (Verification Criteria)

| Hạng mục | Tiêu chuẩn chất lượng | Trạng thái |
| :--- | :--- | :---: |
| **Drawer Tương Tác** | Đóng/mở mượt mà bằng nút bấm và phím tắt, không vỡ layout | ⏳ Chờ triển khai |
| **Zen Chat Experience** | Hiển thị trọn vẹn Markdown, khối so sánh STAR Diff và Reasoning | ⏳ Chờ triển khai |
| **Responsive Parity** | Hoạt động trơn tru trên Desktop (1440px), Laptop (1024px), Mobile (375px) | ⏳ Chờ triển khai |
| **Bộ Kiểm Tra Hệ Thống** | `checklist.py` đạt 6/6 PASSED | ⏳ Chờ triển khai |
