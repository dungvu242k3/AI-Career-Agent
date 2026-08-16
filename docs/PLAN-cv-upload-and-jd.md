# 📋 Kế Hoạch Thiết Kế: Trang Phân Tích CV — Tải File CV & Dán Mô Tả Công Việc (JD)

> **Mã kế hoạch:** `PLAN-cv-upload-and-jd`  
> **Route áp dụng:** `fe/app/(app)/workspace/page.tsx`  
> **Mục tiêu:** Xây dựng luồng trải nghiệm phân tích CV hoàn chỉnh và trực quan: Cho phép tải file CV kéo thả kết hợp khung dán văn bản JD mục tiêu, sau đó kích hoạt AI phân tích & đối chiếu ATS.

---

## 🎯 1. Triết Lý Trải Nghiệm Người Dùng (2-State UX Workflow)

Để người dùng không bị bỡ ngỡ, giao diện trang Phân tích CV (`/workspace`) sẽ được chia làm 2 trạng thái chuyển đổi mượt mà (Smooth State Transition):

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                TRẠNG THÁI 1: INPUT & SETUP (ĐẦU VÀO)                             │
├────────────────────────────────────────┬─────────────────────────────────────────────────────────┤
│ KHUNG 1: TẢI LÊN CV (UPLOAD CV)        │ KHUNG 2: MÔ TẢ CÔNG VIỆC MỤC TIÊU (JOB DESCRIPTION)     │
│ • Vùng kéo thả file PDF / DOCX         │ • Khung dán văn bản (Paste Text) JD chi tiết            │
│ • Xem trước thông tin file, dung lượng │ • Nút chọn nhanh JD mẫu (VNG, MoMo, Grab, Viettel...)   │
│ • Hoặc chuyển sang dán text CV trực tiếp│ • Bộ đếm ký tự & phát hiện từ khóa sơ bộ               │
├────────────────────────────────────────┴─────────────────────────────────────────────────────────┤
│ 🚀 NÚT CHÍNH: [ BẮT ĐẦU PHÂN TÍCH & ĐỐI CHIẾU ATS BẰNG AI ] (Pulse Animation)                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼ (Chuyển trạng thái khi bấm Phân tích)
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             TRẠNG THÁI 2: LIVE ANALYSIS & CHAT RESULTS                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Thanh thông tin: [File: Backend_Resume.pdf] • [JD: Senior Python VNG] • [Đổi CV/JD ↺]          │
│ • Khung Báo cáo Điểm ATS: Radial Gauge 94% + Ma trận kỹ năng (Đã khớp / Còn thiếu)               │
│ • Khung Hội thoại AI Multi-Agent: Reasoning Stream, Khối STAR Diff (Trước/Sau) & Action Chips    │
│ • Khung nhập Prompt hỏi đáp trực tiếp với AI                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 2. Bố Cục Giao Diện Chi Tiết (UI Components Specification)

### 🔹 A. Trạng Thái 1: Khung Tải CV & Dán JD (Input Screen)

1. **Khung Kéo Thả Upload CV (Left Card - 50% width):**
   - Vùng dropzone viền nét đứt `border-dashed border-[#1E293B] hover:border-[#10b981]`.
   - Biểu tượng tài liệu SVG và dòng hướng dẫn: *"Kéo & thả file PDF, DOCX vào đây hoặc click để chọn file"*.
   - Thông tin file đã chọn: Tên file (`Dung_Vu_Senior_Backend.pdf`), dung lượng, nút xóa / đổi file.
   - Tab phụ: *"Hoặc dán văn bản CV thô"*.

2. **Khung Dán Mô Tả Công Việc (Right Card - 50% width):**
   - Ô `textarea` lớn với placeholder gợi ý: *"Dán toàn bộ nội dung JD tuyển dụng của công ty bạn muốn ứng tuyển (Yêu cầu kỹ năng, trách nhiệm công việc...)"*.
   - Hàng gợi ý nút nhanh (Quick Presets):
     - `[+ Dán mẫu: Senior Python/FastAPI - VNG]`
     - `[+ Dán mẫu: Lead Backend - MoMo]`
     - `[+ Dán mẫu: Go / Cloud Engineer - Grab]`

3. **Thanh Kích Hoạt Phân Tích (Bottom CTA Bar):**
   - Nút lớn toàn chiều rộng: `⚡ Bắt đầu Phân tích & Tối ưu ATS ngay` (`bg-[#10b981] hover:bg-[#4edea3]`).
   - Tự động kiểm tra điều kiện (Validate): Nếu chưa có file CV hoặc chưa có JD thì hiển thị thông báo nhắc nhở nhẹ nhàng.

---

### 🔹 B. Trạng Thái 2: Khung Kết Quả Phân Tích & Đối Thoại AI (Results Screen)

1. **Thanh Tác Vụ Đầu Trang (Session Control Bar):**
   - Hiển thị tóm tắt: CV đang xử lý & Công ty đối chiếu.
   - Nút `↺ Đổi CV hoặc JD khác` để quay lại Trạng thái 1 bất kỳ lúc nào.
2. **Khối Chẩn Đoán Điểm ATS (Top Widget):**
   - Điểm số **94% ATS** với vòng tròn SVG xoay động.
   - Ma trận phân loại kỹ năng: 🟢 Đã khớp (18 kỹ năng) vs 🟡 Cần bổ sung (`Kubernetes`, `Distributed Tracing`).
3. **Khối Chat AI & Khối So Sánh STAR Diff (Center Chat Stream):**
   - Khối Reasoning của AI giải thích lý do số điểm và đề xuất cách sửa câu văn trong CV.
   - Khối so sánh Trước / Sau khi tối ưu theo phương pháp STAR (+4% ATS).
   - Khung nhập lệnh tương tác liên tục ở đáy màn hình.

---

## 📋 3. Phân Rã Nhiệm Vụ Triển Khai (Task Breakdown)

### Giai đoạn 1: Xây dựng State Machine & Input Form
- [ ] Thiết lập State quản lý trạng thái: `step: "input" | "analyzing" | "result"`.
- [ ] Xây dựng Component Dropzone Upload CV (xử lý kéo thả file & file input).
- [ ] Xây dựng Component Textarea Dán JD với danh sách mẫu preset 1-click.

### Giai đoạn 2: Xây dựng Hiệu ứng Loading & Chuyển Cảnh
- [ ] Hiệu ứng quét từ khóa (Scanning Animation): Hiển thị tiến trình *"Đang trích xuất dữ liệu CV... -> Đang đối chiếu từ khóa JD... -> Đang tính toán điểm ATS"*.

### Giai đoạn 3: Kết Nối Trực Quan Màn Hình Kết Quả
- [ ] Hiển thị báo cáo ATS tương thích trực tiếp theo JD vừa dán.
- [ ] Tích hợp nút *"Quay lại chỉnh sửa CV/JD"* mà không làm mất dữ liệu đã nhập.

---

## 🏁 4. Tiêu Chuẩn Nghiệm Thu (Verification Criteria)

| Tiêu chí | Mục tiêu |
| :--- | :--- |
| **Kéo thả File** | Nhận diện file PDF/DOCX, hiển thị tên file và dung lượng |
| **Dán JD & Presets** | Cho phép dán văn bản hoặc bấm nút điền nhanh JD mẫu |
| **Chuyển cảnh** | Chuyển đổi mượt mà giữa màn hình Nhập liệu và màn hình Kết quả Chat |
| **Kiểm tra tự động** | `checklist.py` đạt 6/6 PASSED, `npx tsc` 0 lỗi |
