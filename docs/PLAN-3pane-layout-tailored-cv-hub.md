# 📐 KẾ HOẠCH TÁI CẤU TRÚC GIAO DIỆN 3 CỘT & TRUNG TÂM TẢI CV TỐI ƯU (TAILORED CV VAULT)

> **Mã kế hoạch:** `docs/PLAN-3pane-layout-tailored-cv-hub.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Không viết code)**  
> **Người lập kế hoạch:** `@[project-planner]`, `@[frontend-specialist]`, `@[ui-ux-pro-max]`  
> **Mục tiêu:** Tái cấu trúc bố cục 3 cột của Workspace Studio theo yêu cầu của người dùng:
> - **Cột 1:** Tách thành **2 Tầng (Trên / Dưới)**: Tầng trên = Hồ sơ CV người dùng; Tầng dưới = Nạp JD & Kết quả chấm điểm ATS.
> - **Cột 2:** Trung tâm Trợ lý AI Career Chat & Suy luận.
> - **Cột 3:** Kho Lưu Trữ & Xuất Bản CV Đã Tối Ưu (Tailored CV Hub / PDF Exporter) để người dùng xem trước và tải về.

---

## 🏛️ 1. BẢN ĐỒ KIẾN TRÚC GIAO DIỆN MỚI (NEW 3-COLUMN STUDIO LAYOUT)

```
┌──────────────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┐
│       CỘT 1: CV & ATS ENGINE         │      CỘT 2: AI CAREER COPILOT        │      CỘT 3: TAILORED CV VAULT        │
│          (Width: 32% - 35%)          │          (Width: 35% - 38%)          │          (Width: 27% - 30%)          │
├──────────────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────┤
│ 🔼 TẦNG TRÊN: HỒ SƠ CV CỦA TÔI        │ 💬 KHUNG CHAT AI HƯỚNG NGHIỆP        │ 📂 DANH SÁCH BẢN CV ĐÃ TỐI ƯU        │
│ • Họ tên, Title, Liên hệ, Avatar     │ • Chat trực tiếp với AI chuyên gia   │ • CV-Shopee-SeniorBackend.pdf        │
│ • 8 Nhóm kỹ năng (Thu gọn/Mở rộng)   │ • Hiểu sâu toàn bộ ngữ cảnh CV + JD  │ • CV-VNG-BackendLead.pdf             │
│ • Dòng thời gian kinh nghiệm         │ • Gợi ý câu hỏi phỏng vấn theo JD    │ • Điểm so sánh: 65đ ➔ 92đ (+27đ)     │
│ • Nút chỉnh sửa hồ sơ (Edit Modal)   │ • Streaming SSE phản hồi từng chữ    │                                      │
├──────────────────────────────────────┤                                      ├──────────────────────────────────────┤
│ 🔽 TẦNG DƯỚI: SO KHỚP JD & ĐIỂM ATS  │ 🧠 CHUỖI SUY LUẬN AI (REASONING)     │ 📄 TRÌNH XEM TRƯỚC (PREVIEW MODAL)   │
│ • Ô dán JD / Tải file JD (<2MB)      │ • Trace phân tích logic hồ sơ        │ • Xem định dạng PDF chuẩn ATS        │
│ • Đồng hồ điểm Radial SVG (50/30/20) │                                      │ • Tải file PDF 1-Click (Download)    │
│ • Thẻ kỹ năng 🟢🟡🔴⚪ & Nút STAR    │                                      │ • Sao chép văn bản Markdown/Text     │
└──────────────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🔍 2. CHI TIẾT THIẾT KẾ TỪNG CỘT

---

### 🔹 CỘT 1 (BÊN TRÁI): TRUNG TÂM NẠP HỒ SƠ & SO KHỚP ATS (SPLIT-PANE)
* **Kích thước:** Chiếm 4/12 cột (~33% màn hình Desktop).
* **Thiết kế phân tầng Trên / Dưới:**
  1. **Tầng Trên (My CV Profile Pane - Chiếm ~45% chiều cao hoặc Collapsible Accordion):**
     * Thẻ tệp CV đã tải lên, số lượng kỹ năng, độ tin cậy trích xuất.
     * Thông tin cá nhân & định vị nghề nghiệp (`detected_title`).
     * 8 nhóm kỹ năng chuẩn có thể bấm thu gọn/mở rộng để tiết kiệm không gian.
     * Nút **"Chỉnh Sửa CV"** và **"Tải Lên File Khác"**.
  2. **Tầng Dưới (JD & ATS Matching Studio Pane - Chiếm ~55% chiều cao):**
     * **Khi chưa nạp JD:** Hiển thị `JDInput` (Tab dán văn bản JD hoặc kéo thả file JD PDF/Word).
     * **Khi đã so khớp ATS:** Hiển thị `ATSResult` (Đồng hồ điểm Radial SVG, 3 cột điểm 50/30/20, Thẻ kỹ năng 4 màu có nút sinh câu STAR, và Lời khuyên cắt tỉa kỹ năng).
     * Có nút chuyển đổi linh hoạt: **"Đổi JD Khác"** để quay lại ô nhập.

---

### 🔹 CỘT 2 (Ở GIỮA): TRỢ LÝ AI CAREER COPILOT
* **Kích thước:** Chiếm 5/12 cột (~42% màn hình).
* **Chức năng:**
  1. **Hộp Thoại Chat Chuyên Gia:**
     * Nạp sẵn toàn bộ bối cảnh của Ứng viên (từ Cột 1 Trên) và Yêu cầu tuyển dụng (từ Cột 1 Dưới).
     * Các phím tắt nhanh (Prompt Chips):
       * 💡 *"Tôi nên nhấn mạnh kinh nghiệm nào cho JD này?"*
       * 🎯 *"Dự đoán 5 câu hỏi phỏng vấn hóc búa nhất cho vị trí này"*
       * ✉️ *"Viết một email Cover Letter ngắn gửi Tech Lead"*
  2. **Nút "Tạo Bản CV Tối Ưu Cho JD Này":**
     * Khi người dùng hài lòng với các câu sửa STAR, bấm nút này để AI tự động tổng hợp thành một phiên bản CV mới và **đẩy sang Cột 3**.

---

### 🔹 CỘT 3 (BÊN PHẢI): KHO LƯU TRỮ & XUẤT BẢN CV TỐI ƯU (TAILORED CV VAULT)
* **Kích thước:** Chiếm 3/12 cột (~25% màn hình).
* **Chức năng:**
  1. **Quản Lý Các Phiên Bản CV Tối Ưu:**
     * Mỗi lần so khớp và tối ưu với 1 JD, hệ thống sinh ra một thẻ phiên bản (Card):
       * Tên vị trí & Công ty (VD: *Shopee — Senior Backend Engineer*).
       * Điểm ATS trước và sau tối ưu (VD: *62đ ➔ 94đ | Hạng A+*).
       * Thời gian tạo (VD: *Vừa xong*).
  2. **Các Thao Tác Xuất Bản (Export Actions):**
     * 👁️ **Xem Trước (Quick Preview):** Mở cửa sổ xem trước bố cục CV hoàn chỉnh.
     * 📥 **Tải Xuống PDF (1-Click Download):** Xuất file PDF định dạng chuẩn quốc tế (Single-column, Clean ATS typography, Không dính bảng biểu gây lỗi ATS).
     * 📋 **Copy Text / Markdown:** Sao chép toàn bộ nội dung CV đã tối ưu để dán vào các nền tảng tuyển dụng trực tuyến.

---

## 🛠️ 3. LỘ TRÌNH THỰC HIỆN KHI BẮT ĐẦU CODE

| Bước | Thành phần | Chi tiết thực hiện |
|:---|:---|:---|
| **Bước 1** | `fe/src/pages/WorkspacePage.tsx` | Tái cấu trúc Layout: Di chuyển `JDInput` và `ATSResult` sang nửa dưới của Cột 1. |
| **Bước 2** | `fe/src/components/TailoredCVHub.tsx` (Mới) | Xây dựng Component Cột 3 chuyên trách quản lý, xem trước và tải các bản CV đã tối ưu. |
| **Bước 3** | `fe/src/types/candidate.ts` | Bổ sung type `TailoredCVVersion` (Lưu lịch sử các bản CV được tạo theo từng JD). |
| **Bước 4** | `fe/src/components/AICopilotChat.tsx` | Tinh chỉnh Cột 2 với nút CTA kết nối trực tiếp: *"Áp dụng cải tiến & Xuất CV sang Cột 3"*. |
| **Bước 5** | Kiểm thử giao diện & Build | Đảm bảo hiển thị co giãn hoàn hảo trên các độ phân giải màn hình (Desktop, Tablet, Mobile). |

---

## ❓ CÂU HỎI XÁC NHẬN TRƯỚC KHI TIẾN HÀNH:

1. Bạn thấy bố cục: **Cột 1 (CV trên + JD/ATS dưới) | Cột 2 (Chat AI) | Cột 3 (Kho CV tối ưu & Tải PDF)** như trên đã đúng 100% với mong muốn của bạn chưa?
2. Bạn có muốn bắt đầu triển khai ngay không?
