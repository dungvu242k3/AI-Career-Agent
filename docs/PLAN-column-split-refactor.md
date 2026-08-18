# 📐 KẾ HOẠCH BƯỚC 1: TÁI CẤU TRÚC VÀ TÁCH CỘT WORKSPACE STUDIO (COLUMN SPLIT REFACTOR)

> **Mã kế hoạch:** `docs/PLAN-column-split-refactor.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Không viết code)**  
> **Người lập kế hoạch:** `@[project-planner]`, `@[frontend-specialist]`, `@[ui-ux-pro-max]`  
> **Mục tiêu trọng tâm:** Thực hiện **BƯỚC 1** — Tái cấu trúc layout 3 cột:
> 1. Di chuyển toàn bộ tính năng **Nạp JD & Báo Cáo Chấm Điểm ATS** từ Cột 3 sang **Nửa Dưới của Cột 1**.
> 2. Tách **Cột 1** thành **2 Tầng (Trên: Hồ sơ CV | Dưới: So khớp JD & Điểm ATS)** với thanh cuộn mượt mà độc lập.
> 3. Chuẩn bị không gian **Cột 3** thành **Trung Tâm Tải & Quản Lý CV Tối Ưu (Tailored CV Hub)**.

---

## 🏛️ 1. SƠ ĐỒ CẤU TRÚC BỐ CỤC MỚI (WORKSPACE 3-COLUMN LAYOUT)

```
┌───────────────────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
│      CỘT 1 (4/12 Col ~ 33% - SPLIT PANE)      │     CỘT 2 (5/12 Col ~ 42%)       │      CỘT 3 (3/12 Col ~ 25%)      │
├───────────────────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ 🔼 TẦNG TRÊN (TOP): HỒ SƠ CV CỦA TÔI          │ 💬 TRỢ LÝ AI CAREER COPILOT      │ 📂 KHO CV TỐI ƯU (TAILORED VAULT)│
│ • Thẻ thông tin file tải lên (Tên, %, Skills) │ • Giao diện Chat AI Hướng nghiệp │ • Danh sách các bản CV đã tối ưu │
│ • 8 Nhóm kỹ năng (Có nút Thu gọn / Mở rộng)   │ • Chuỗi suy luận AI Reasoning    │   cho từng công ty/JD            │
│ • Dòng thời gian kinh nghiệm làm việc         │ • Phím tắt gợi ý câu hỏi         │ • Nút Xem Trước (Preview Modal)  │
│ • Nút "Chỉnh Sửa CV"                          │                                  │ • Nút 📥 Tải File PDF Chuẩn ATS  │
├───────────────────────────────────────────────┤                                  │                                  │
│ 🔽 TẦNG DƯỚI (BOTTOM): SO KHỚP JD & ĐIỂM ATS  │                                  │                                  │
│ • Khi chưa nạp JD: Khung nhập JDInput         │                                  │                                  │
│ • Khi đã có kết quả: ATSResult (Đồng hồ       │                                  │                                  │
│   Radial SVG, Điểm 50/30/20, Thẻ kỹ năng 4 màu│                                  │                                  │
│   🟢🟡🔴⚪, Huy hiệu xác thực, Nút STAR)      │                                  │                                  │
│ • Nút "Đổi JD Khác" để quay lại nhập          │                                  │                                  │
└───────────────────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
```

---

## 🔍 2. CHI TIẾT TỪNG BƯỚC THAY ĐỔI TRONG MÃ NGUỒN

### 🔹 Bước 1.1: Tái cấu trúc Cột 1 trong `fe/src/pages/WorkspacePage.tsx`
* **Tầng 1 (Trên - Hồ Sơ CV):**
  * Đặt trong một `section` có tiêu đề rõ ràng: **"1. Hồ Sơ Ứng Viên (My Profile)"**.
  * Bổ sung tính năng thu gọn/mở rộng (Accordion Toggle) cho 8 nhóm kỹ năng để khi người dùng cuộn xuống phần JD không bị quá dài.
  * Giữ nguyên nút chỉnh sửa hồ sơ `ProfileEditModal` và nút đổi tệp CV `UploadModal`.
* **Tầng 2 (Dưới - So Khớp JD & Kết Quả ATS):**
  * Đặt trong một `section` ngăn cách bằng đường kẻ viền tinh tế (`border-t border-slate-800`): **"2. So Khớp Job Description & ATS"**.
  * Nhúng trực tiếp `<JDInput candidateId={candidateId} ... />` khi chưa có `atsReport`.
  * Hiển thị `<ATSResult report={atsReport} onReset={() => setAtsReport(null)} ... />` ngay tại đây khi đã có kết quả.

---

### 🔹 Bước 1.2: Dành không gian Cột 3 cho "Tailored CV Vault"
* **Tại Cột 3:**
  * Di chuyển các tab cũ (ATS Tab) sang Cột 1.
  * Xây dựng giao diện **Kho Lưu Trữ CV Đã Tối Ưu (Tailored CV Hub)**:
    * **Empty State:** Khi chưa có bản CV nào được tối ưu $\rightarrow$ Hiển thị hướng dẫn: *"So khớp JD ở Cột 1 và nhờ AI tối ưu để tạo bản CV may đo cho riêng bạn."*
    * **Active State:** Hiển thị thẻ các bản CV đã tối ưu (VD: *Shopee — Senior Backend Engineer (Điểm ATS: 94đ | A+)*) kèm nút **"👁️ Xem Trước"** và **"📥 Tải PDF Chuẩn ATS"**.

---

### 🔹 Bước 1.3: Đảm bảo khả năng Co giãn & Cuộn trang mượt mà (Responsive Scroll)
* Thiết lập `h-full overflow-y-auto scrollbar-thin` độc lập cho từng cột:
  * Người dùng có thể cuộn xem chi tiết CV và JD ở Cột 1 mà không ảnh hưởng đến khung chat ở Cột 2 hay danh sách CV ở Cột 3.
  * Đảm bảo giao diện hiển thị xuất sắc từ màn hình lớn (1920px), màn hình laptop (1366px), đến máy tính bảng và điện thoại.

---

## 🧪 3. KẾ HOẠCH KIỂM ĐỊNH SAU KHI SỬA LAYOUT

1. **Kiểm tra chức năng tải và bóc tách CV (Cột 1 Trên):** Tải file PDF/DOCX lên $\rightarrow$ Dữ liệu hiển thị chuẩn xác ở Tầng Trên.
2. **Kiểm tra chức năng dán JD & Chấm điểm ATS (Cột 1 Dưới):** Dán JD $\rightarrow$ Bấm Phân tích $\rightarrow$ Kết quả ATS hiển thị ngay tại Tầng Dưới với đầy đủ đồng hồ SVG và nút sinh câu STAR.
3. **Kiểm tra Cột 3 (Tailored CV Hub):** Hiển thị đúng giao diện kho thành phẩm sẵn sàng nhận bản CV tối ưu.
4. **Biên dịch Frontend:** Chạy `npm run build` đảm bảo 0 lỗi TypeScript và 0 xung đột CSS.

---

## ❓ XÁC NHẬN BẮT ĐẦU:
Kế hoạch tái cấu trúc và tách cột đã hoàn tất chi tiết. Bạn có muốn tôi bắt tay vào thực hiện mã hóa **Bước 1: Tách Cột 1 thành 2 Tầng & Đổi Cột 3 thành Kho CV** ngay bây giờ không?
