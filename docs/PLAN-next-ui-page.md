# 🗺️ Kế hoạch Phát triển Giao diện Tiếp theo: CareerPilot AI (UI Roadmap)

> **Mục tiêu:** Xác định thứ tự ưu tiên, kiến trúc giao diện và kế hoạch triển khai trang tiếp theo cho nền tảng **CareerPilot AI**.  
> **Trạng thái hiện tại:** Đã hoàn thành Landing Page (`(marketing)`) và Home Dashboard (`(app)/home`).

---

## 📊 1. Ma Trận Đánh Giá & Độ Ưu Tiên Các Trang (UI Priority Matrix)

| Màn hình (Page / Route) | Vai trò nghiệp vụ | Độ phức tạp UI | Giá trị cốt lõi (Core Value) | Đề xuất ưu tiên |
| :--- | :--- | :---: | :---: | :---: |
| **1. AI Career Workspace**<br>`/workspace` | **Trọng tâm hệ thống (3-Pane Interface)**: Bóc tách CV, tương tác hội thoại Agent đa tác vụ, hiển thị Ma trận Skill Gap thời gian thực. | Cao (5/5) | ⭐⭐⭐⭐⭐ (P0 - Cốt lõi) | **Khuyên dùng số 1** |
| **2. Tìm việc & So khớp JD**<br>`/jobs` & `[jobId]` | Tìm kiếm việc làm IT, lọc theo mức độ phù hợp ATS (% Match), xem chi tiết yêu cầu & khoảng trống kỹ năng theo từng vị trí. | Trung bình (3/5) | ⭐⭐⭐⭐ (P1 - Trải nghiệm) | **Lựa chọn số 2** |
| **3. Quản lý ứng tuyển (Kanban)**<br>`/applications` | Bảng Kanban kéo thả theo dõi tiến trình nộp hồ sơ (Đã lưu, Đã nộp, Phỏng vấn, Offer), nhắc lịch hẹn phỏng vấn. | Trung bình (3/5) | ⭐⭐⭐⭐ (P1 - Quản lý) | **Lựa chọn số 3** |
| **4. Lộ trình kỹ năng thích ứng**<br>`/learning` | Lộ trình bù đắp kỹ năng (Roadmap 2-4 tuần), sơ đồ nhánh kỹ năng bị hổng từ kết quả quét CV & JD. | Trung bình (3/5) | ⭐⭐⭐ (P2 - Nâng cao) | **Lựa chọn số 4** |
| **5. Nhóm trang Xác thực**<br>`/login`, `/register` | Màn hình đăng nhập, đăng ký tài khoản với thiết kế Dark Minimalist đồng bộ Design System. | Thấp (2/5) | ⭐⭐⭐ (P2 - Hạ tầng) | **Lựa chọn số 5** |

---

## 🎯 2. Phân Tích Chuyên Sâu Các Lựa Chọn

### 🥇 Lựa chọn 1 (Khuyên Dùng): `app/(app)/workspace/page.tsx` — AI Career Workspace
* **Vì sao nên làm ngay?**
  - Đây là **"Trái tim của CareerPilot AI"** — nơi toàn bộ giá trị khác biệt của sản phẩm được thể hiện (sức mạnh của Multi-agent, phân tích ATS trực tiếp).
  - Kết nối trực tiếp từ nút CTA chính của Landing Page (`/workspace`) và Home Dashboard.
* **Cấu trúc giao diện chuẩn 3-Pane Ergonomic Workspace:**
  1. **Pane Trái (`Source Panel` - 280px):**
     - Trình xem tài liệu CV dạng thẻ/tab + Công cụ tải lên PDF.
     - Bộ chọn Target Job Description (Paste JD hoặc chọn từ danh sách).
  2. **Pane Giữa (`Center Panel` - Flex-1):**
     - Dòng thời gian hội thoại thông minh với AI Agent.
     - Multi-agent reasoning stream (hiển thị từng bước suy luận của Resume Analyzer, Skill Matcher, Interview Coach).
     - Gợi ý câu hỏi/hành động nhanh (Quick Action Chips).
  3. **Pane Phải (`Insight Panel` - 340px):**
     - Đồng hồ đo điểm chuẩn ATS (% Match Radial Gauge).
     - Ma trận Skill Gap Matrix (Phân loại: Kỹ năng đã khớp, Kỹ năng thiếu sót, Điểm mạnh).
     - Đề xuất hành động sửa CV tức thì (Quick Fix Actions).

---

### 🥈 Lựa chọn 2: `app/(app)/jobs/page.tsx` — Tìm việc & So khớp JD
* **Mục tiêu:** Cung cấp thị trường việc làm IT với góc nhìn ATS Match cá nhân hóa.
* **Cấu trúc giao diện:**
  - Bộ lọc đa chiều: Tech Stack (FastAPI, React, Docker...), Cấp bậc (Junior/Senior), Mức lương, Hình thức (Remote/Hybrid/Onsite).
  - Thẻ công việc hiển thị chỉ số ATS Match Score cá nhân hóa cho từng user.
  - Drawer chi tiết công việc: Đối chiếu trực tiếp kỹ năng người dùng vs Yêu cầu tuyển dụng.

---

### 🥉 Lựa chọn 3: `app/(app)/applications/page.tsx` — Quản lý Ứng tuyển (Kanban Tracker)
* **Mục tiêu:** Quản lý toàn diện hành trình xin việc.
* **Cấu trúc giao diện:**
  - 5 Cột Kanban: `Đã lưu (Saved)` $\rightarrow$ `Đã nộp (Applied)` $\rightarrow$ `Phỏng vấn (Interviewing)` $\rightarrow$ `Nhận Offer` $\rightarrow$ `Từ chối (Archived)`.
  - Thẻ công ty (VNG, Grab, MoMo, FPT...) kèm lịch phỏng vấn, link phòng họp và ghi chú chuẩn bị.

---

## 🛠️ 3. Kế hoạch Triển khai Chi tiết (Nếu chọn Workspace)

### Giai đoạn 1: Chuẩn bị Component Primitives & Layout Shell
- [ ] Xây dựng Shell 3 cột phản hồi responsive (Hỗ trợ thu gọn Pane trái/phải trên màn hình nhỏ).
- [ ] Tạo Header điều hướng Workspace (Tên phiên làm việc, chuyển đổi chế độ Phân tích CV / Phỏng vấn / Lộ trình).

### Giai đoạn 2: Phát triển Source Panel (Trái) & Insight Panel (Phải)
- [ ] `SourcePanel`: Tabs xem CV Uploaded + Form nạp JD mục tiêu.
- [ ] `InsightPanel`: Radial Score Gauge, Skill Taxonomy List (Xanh: Đạt, Vàng: Thiếu).

### Giai đoạn 3: Phát triển Trung tâm Hội thoại AI (Center Panel)
- [ ] Chat Timeline với tin nhắn Markdown, Thinking tokens, Code snippets.
- [ ] Action Chips: *"Tối ưu hóa câu đạn STAR"*, *"Tạo câu hỏi phỏng vấn cho JD này"*, *"Tìm việc tương tự"*.

### Giai đoạn 4: Đánh giá & Hoàn thiện
- [ ] Kiểm thử responsive, accessibility, TypeScript compilation (`npx tsc --noEmit`).
- [ ] Tạo preview HTML và Next.js page đồng bộ.
