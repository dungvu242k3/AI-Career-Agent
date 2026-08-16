# 📋 Kế Hoạch Thiết Kế: Không Gian Làm Việc 3 Cột Theo Mô Hình NotebookLM

> **Mã kế hoạch:** `PLAN-notebooklm-3pane`  
> **Lấy cảm hứng:** Giao diện 3 phân vùng (3-Pane Layout) kinh điển của **Google NotebookLM**  
> **Route áp dụng:** `fe/app/(app)/workspace/page.tsx`  
> **Mục tiêu:** Xây dựng không gian làm việc chuyên nghiệp, liền mạch và tập trung: Cột 1 nạp nguồn (CV & JD), Cột 2 bảng Chat AI đối thoại, Cột 3 Studio chứa các file CV đã được AI tối ưu hóa và xuất bản.

---

## 🏛️ 1. Kiến Trúc Bố Cục 3 Phân Vùng (NotebookLM-Style Grid)

Toàn bộ màn hình Không gian làm việc sẽ chiếm trọn chiều cao trình duyệt `h-[calc(100vh-4rem)]` (nằm ngay dưới thanh Menu Navbar cố định), chia làm 3 cột cuộn độc lập:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PERSISTENT GLOBAL NAVBAR (h-16 cố định: Logo | 5 Tab tính năng | Đăng nhập & Bắt đầu miễn phí)            │
├───────────────────────────────┬───────────────────────────────────────────┬──────────────────────────────┤
│ 📂 CỘT 1: NGUỒN ĐẦU VÀO       │ 💬 CỘT 2: TRUNG TÂM HỘI THOẠI AI          │ 📑 CỘT 3: STUDIO & BẢN CV    │
│    (SOURCES PANEL - 26%)      │    (CHAT CONVERSATION - 44%)              │    (STUDIO ARTIFACTS - 30%)  │
├───────────────────────────────┼───────────────────────────────────────────┼──────────────────────────────┤
│ • Nút: [+ Thêm CV / Dán JD]   │ • Header: CareerPilot ATS Specialist Agent│ • ATS Score Widget (94%)     │
│ • Danh sách Nguồn (Sources):  │ • Tiến trình suy luận (Reasoning Stream)  │ • Danh mục File CV đã sửa:   │
│   [✓] File_CV_Goc.pdf (245KB) │ • Khối đề xuất tối ưu STAR Diff           │   - CV_v2_STAR_VNG.pdf (Mới) │
│   [✓] JD_Senior_Python_VNG.txt│ • Gợi ý câu lệnh nhanh (Action Chips)     │   - CV_v1_Ban_Dau.pdf        │
│ • Bật/Tắt checkbox nguồn      │ • Chat History cuộn mượt mà               │ • Khung Xem trước (Preview): │
│ • Vùng kéo thả upload nhanh   │ • Ô nhập Prompt cố định ở đáy cột giữa    │   Bản CV trực quan bôi xanh  │
│ • Xem trước dữ liệu bóc tách  │   (Hỗ trợ Enter / Shift+Enter)            │ • Nút: [📥 Tải PDF] [📋 Copy]│
└───────────────────────────────┴───────────────────────────────────────────┴──────────────────────────────┘
```

---

## 🎨 2. Chi Tiết Từng Phân Vùng (Component Deep-Dive)

### 📂 CỘT 1: NGUỒN TÀI LIỆU (Sources Panel - Chiếm ~26% chiều ngang)
- **Mục đích:** Quản lý tất cả tài liệu đầu vào để AI lấy ngữ cảnh phân tích.
- **Thành phần:**
  1. **Nút tác vụ đầu trang:** `+ Thêm Nguồn Tài Liệu` (Mở modal/khung nạp file hoặc dán JD).
  2. **Danh sách Nguồn (Source Cards):**
     - Thẻ File CV: Biểu tượng PDF, tên file, dung lượng, trạng thái đã bóc tách (`✓ 4 sections`). Checkbox chọn nguồn để AI sử dụng.
     - Thẻ JD Mục Tiêu: Biểu tượng JD, tên công ty & vị trí (VNG - Senior Python), checkbox kích hoạt.
  3. **Khu vực Kéo thả Upload nhanh:** Ô nhỏ viền đứt nét ở cuối cột để thả thêm file bất kỳ lúc nào.
  4. **Tóm tắt bóc tách (Extracted Snippets):** Xem nhanh các mục Học vấn, Kinh nghiệm, Kỹ năng đã nhận diện.

---

### 💬 CỘT 2: TRUNG TÂM HỘI THOẠI AI (Chat Center - Chiếm ~44% chiều ngang)
- **Mục đích:** Không gian trò chuyện, hướng dẫn và ra lệnh cho AI tối ưu hóa CV.
- **Thành phần:**
  1. **Header phiên làm việc:** Tên Agent (`CareerPilot ATS Specialist`), trạng thái kết nối nguồn.
  2. **Dòng thời gian tin nhắn (Message Stream):**
     - Khối phân tích của AI kèm **Reasoning Accordion** (cho thấy các bước suy luận ngầm).
     - Khối so sánh **STAR Method Diff** (Trước vs Sau khi tối ưu câu mô tả kinh nghiệm).
     - Các nút **Action Chips gợi ý** 1-click: `⚡ Áp dụng câu này vào Studio`, `⚡ Thêm kỹ năng còn thiếu`, `⚡ Viết thư ứng tuyển (Cover Letter)`.
  3. **Khung nhập Prompt ghim đáy (Docked Input Bar):**
     - Ô textarea đa dòng tự co giãn.
     - Phím tắt `Enter` để gửi, `Shift + Enter` để xuống dòng.

---

### 📑 CỘT 3: STUDIO & BẢN CV ĐÃ SỬA (Artifacts Studio - Chiếm ~30% chiều ngang)
- **Mục đích:** Nơi chứa kết quả sản phẩm đầu ra (Bản CV đã được AI hiệu chỉnh, điểm ATS, công cụ xuất file).
- **Thành phần:**
  1. **Bảng điểm ATS Thông minh (ATS Diagnostic Widget):**
     - Vòng tròn Radial Gauge 94% ATS Match.
     - Thanh phân tích 3 trục: Kỹ năng (95%) • Tác động (90%) • Định dạng (98%).
  2. **Trình quản lý Phiên bản File CV (Version Switcher):**
     - `📄 CV_v2_Chuan_STAR_VNG.pdf` *(Phiên bản tối ưu mới nhất)*
     - `📄 CV_v1_Ban_Goc_Chua_Sua.pdf`
  3. **Khung Xem Trước CV Tối Ưu (Live Resume Preview):**
     - Hiển thị văn bản CV đã được AI biên tập lại hoàn chỉnh.
     - Các từ khóa kỹ thuật và số liệu định lượng mới được bôi sáng màu ngọc bích (`#10b981`).
  4. **Thanh Công Cụ Xuất Bản (Export Actions):**
     - Nút `📥 Tải xuống PDF (Chuẩn ATS)`
     - Nút `📋 Sao chép nội dung Markdown`
     - Nút `🚀 Đưa vào danh sách Ứng tuyển`

---

## 🛠️ 3. Phân Rã Công Việc Triển Khai (Task Breakdown)

### Giai đoạn 1: Khung Bố Cục 3 Cột (Responsive 3-Pane CSS Grid)
- [ ] Thiết lập Container `h-[calc(100vh-4rem)] flex flex-col md:flex-row overflow-hidden`.
- [ ] Cấu hình Cột 1 (Left), Cột 2 (Center), Cột 3 (Right) với thanh cuộn độc lập `overflow-y-auto`.
- [ ] Hỗ trợ chuyển tab linh hoạt trên màn hình Tablet/Mobile (Sources | Chat | Studio).

### Giai đoạn 2: Phát Triển Cột 1 (Sources Panel)
- [ ] Xây dựng danh sách Nguồn kèm checkbox bật/tắt nguồn.
- [ ] Tích hợp kéo thả tải file CV và ô dán nhanh JD.

### Giai đoạn 3: Phát Triển Cột 2 (Chat & Action Triggers)
- [ ] Khung Chat AI Multi-Agent với Reasoning Stream và STAR Diff block.
- [ ] Tích hợp nút "Áp dụng vào Studio" để cập nhật thời gian thực sang Cột 3.

### Giai đoạn 4: Phát Triển Cột 3 (Artifacts Studio & Live CV Preview)
- [ ] Xây dựng widget điểm ATS và ma trận từ khóa.
- [ ] Xây dựng bộ chuyển đổi phiên bản file CV (v1, v2).
- [ ] Xây dựng khung Preview CV với các đoạn highlight từ khóa.
- [ ] Nút tải file PDF và copy text.

---

## 🏁 4. Tiêu Chuẩn Nghiệm Thu (Verification Criteria)

| Tiêu chí | Mục tiêu |
| :--- | :--- |
| **Bố cục 3 cột** | Hiển thị 3 cột chuẩn song song trên Desktop, cuộn độc lập từng cột |
| **Tương tác liền mạch** | Chat ở cột giữa $\rightarrow$ cập nhật bản CV ở cột phải thời gian thực |
| **Không xung đột Navbar** | Navbar trên cùng vẫn cố định đứng yên hoàn hảo |
| **Chất lượng mã nguồn** | `checklist.py` đạt 6/6 PASSED, `npx tsc` 0 lỗi |
