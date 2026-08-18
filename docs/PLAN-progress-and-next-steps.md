# 📋 KẾ HOẠCH DỰ ÁN: TỔNG HỢP TIẾN ĐỘ & LỘ TRÌNH TRIỂN KHAI TIẾP THEO

> **Tài liệu:** `docs/PLAN-progress-and-next-steps.md`  
> **Chế độ:** PLANNING ONLY (Lập kế hoạch chi tiết, không sinh code)  
> **Trạng thái hệ thống:** Sẵn sàng cho Phase 3 (AI Chat & Tailored CV Generator)

---

## 📅 PHẦN 1: TỔNG HỢP TOÀN BỘ CÁC HẠNG MỤC ĐÃ HOÀN THÀNH

Cho đến thời điểm hiện tại, dự án **CareerPilot AI** đã hoàn thành xuất sắc 100% nền tảng cốt lõi từ **AI Engine**, **Backend API/Database/Storage** cho đến **Giao diện người dùng (Frontend Studio)**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                           KIẾN TRÚC HỆ THỐNG ĐÃ HOÀN THÀNH                                  │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ 1. AI & INGESTION PIPELINE   │ 2. ATS MATCHING & SCORING    │ 3. 3-COLUMN WORKSPACE STUDIO  │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • PyMuPDF (PDF 2 cột, bảng)  │ • Công thức ATS 50/30/20     │ • Cột 1: Hồ sơ CV & So khớp   │
│ • DocxParser (Word chuẩn hóa)│ • 4 Nhóm thẻ 🟢🟡🔴⚪        │   JD / Báo cáo ATS (Split)    │
│ • OpenAI GPT-4o-mini +       │ • Xác thực Contextual Proof  │ • Cột 2: Trợ lý AI Copilot &  │
│   Google Gemini Fallback     │ • Phạt nhồi từ khóa (>20 ks) │   Chuỗi suy luận Reasoning    │
│ • 8 Nhóm kỹ năng Taxonomy    │ • Tiêu chuẩn 10-15 Elite Ks  │ • Cột 3: Kho lưu & Tải CV     │
│ • Cơ chế Auto-Healing URL/Date│ • Trình viết STAR Rewriter  │   May đo (Tailored CV Vault)  │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

### Chi tiết các luồng đã hoàn thành:
1. **Pipeline Trích xuất CV Thông minh (Phase 1):**
   - Hỗ trợ tải PDF và DOCX (< 2MB).
   - Tự động phát hiện và chặn CV dạng ảnh scan không có text layer.
   - Bóc tách cấu trúc 2 cột, phân loại chuẩn hóa 8 nhóm kỹ năng chuyên ngành.
   - Cơ chế tự phục hồi dữ liệu (Auto-Healing) chống lỗi thời gian/URL/ký tự rác.

2. **Động cơ So Khớp JD & Chấm Điểm ATS Chuẩn Quốc Tế (Phase 2):**
   - Phân tích JD qua text dán hoặc tải file PDF/Word.
   - Công thức chấm điểm 3 trụ cột: **50% Kỹ năng (Hard/Soft)** + **30% Độ khớp kinh nghiệm/vị trí** + **20% Định dạng/Cấu trúc**.
   - Bộ lọc **Chống nhồi từ khóa (Anti-Keyword Stuffing)**: Ưu tiên chuẩn 10-15 kỹ năng cốt lõi có minh chứng trong lịch sử làm việc (`Contextual Proof Verification`).
   - Phân loại kỹ năng 4 màu trực quan: 🟢 Khớp chính xác | 🟡 Tương đương | 🔴 Thiếu | ⚪ Kỹ năng mở rộng.
   - Bộ sinh câu thành tựu định lượng theo chuẩn **STAR (Situation - Task - Action - Result)**.

3. **Bảo mật & Tối ưu Hạ tầng (Pre-Prod Security Hardening):**
   - Bộ trượt Sliding Window Rate Limiter ngăn chặn spam/DoS và cạn kiệt chi phí API token.
   - Hỗ trợ Object Storage MinIO (S3) kết hợp dự phòng Local Disk (Fast-fail trong 800ms).
   - Header bảo mật HTTP chuẩn OWASP (XSS, Clickjacking, MIME-sniffing protection).
   - Cơ sở dữ liệu Async PostgreSQL (với native JSONB + GIN Index) và SQLite Fallback.

4. **Tái cấu trúc Giao diện 3 Cột Workspace Studio (Bước Vừa Hoàn Thành):**
   - **Cột 1 (Bên Trái - Split Pane ~33%):** Tầng trên là Hồ sơ CV cá nhân (8 nhóm kỹ năng dạng Accordion thu gọn/mở rộng, dòng thời gian kinh nghiệm) + Tầng dưới là Khung nạp JD và Báo cáo điểm ATS.
   - **Cột 2 (Ở Giữa ~42%):** Trợ lý AI Career Copilot với chuỗi suy luận logic (`AI REASONING TRACE`) và thanh nhập liệu tương tác.
   - **Cột 3 (Bên Phải ~25%):** Kho lưu trữ và tải CV may đo (`TailoredCVHub.tsx`) với modal Xem trước và nút Tải File PDF chuẩn ATS 1-chạm.

5. **Chất lượng Kiểm thử (Test Suite):**
   - 41/41 AI Engine tests PASS ✅
   - 24/24 Backend API tests PASS ✅
   - Frontend Production Build: 1,592 modules trong 2.01s (0 errors) ✅

---

## 🎯 PHẦN 2: LỘ TRÌNH VÀ CÁC BƯỚC TIẾP THEO CHO HÔM NAY

Để nâng tầm hệ thống từ **"Chấm điểm & Phân tích"** thành **"Tự động may đo CV hoàn chỉnh và Đồng hành cùng ứng viên"**, các bước tiếp theo được chia thành 3 giai đoạn rõ ràng:

---

### 🚀 BƯỚC 1: XÂY DỰNG ĐỘNG CƠ SINH CV MAY ĐO TỰ ĐỘNG (TAILORED CV SYNTHESIS ENGINE)
> **Mục tiêu:** Khi người dùng có báo cáo ATS, bấm nút *"Tự động may đo CV cho JD này"*, AI sẽ biên tập lại toàn bộ nội dung CV (Summary, sắp xếp lại 10-15 kỹ năng trọng tâm của JD, nâng cấp các bullet points thành câu chuẩn STAR).

* **Công việc Backend & AI:**
  1. Tạo Prompt Engine `ai/prompts/tailored_cv.md` chuyên sâu: Nhận vào `CandidateProfile` + `JDMatchReport` ➔ Sinh ra `TailoredCVProfile` tối ưu (Điểm ATS tăng từ ~60-70 lên 90-95).
  2. Xây dựng API Endpoint: `POST /api/v1/ats/generate-tailored-cv`.
  3. Tạo bảng lưu trữ `tailored_cvs` trong database gắn với `candidate_id` và `job_title`.
* **Công việc Frontend:**
  1. Nối nút *"May Đo CV Ngay"* từ `ATSResult` sang gọi API.
  2. Đổ dữ liệu các bản CV đã sinh vào `TailoredCVHub` ở **Cột 3**.
  3. Hiển thị so sánh trực quan điểm số trước và sau (Ví dụ: `68đ ➔ 94đ (+26đ)`).

---

### 📄 BƯỚC 2: BỘ XUẤT FILE PDF & WORD CHUẨN ATS (1-CLICK ATS-FRIENDLY EXPORT)
> **Mục tiêu:** Biến bản CV đã tối ưu trong `TailoredCVHub` thành tệp PDF hoặc DOCX hoàn chỉnh, thiết kế tối giản, sạch đẹp, đạt chuẩn 100% ATS-friendly (không dùng bảng phức tạp hay đồ họa làm rối máy quét).

* **Công việc:**
  1. Xây dựng template HTML/CSS chuyên dụng cho CV chuẩn quốc tế (Font chữ chuẩn ATS: Arial/Calibri/Times New Roman, phân cấp Heading Rõ ràng, bullet point sạch).
  2. Tạo bộ xuất file:
     - **Tùy chọn 1 (Client-side):** Sử dụng `html2pdf.js` / `@react-pdf/renderer` để tải trực tiếp trên trình duyệt.
     - **Tùy chọn 2 (Server-side):** Sử dụng Weasyprint / python-docx để xuất bản in hoàn hảo.
  3. Nút *"Tải PDF"* và *"Tải Word (.docx)"* trong `TailoredCVHub` tải file về máy người dùng chỉ với 1 click.

---

### 💬 BƯỚC 3: TÍCH HỢP TRỢ LÝ AI CHAT TRỰC TIẾP Ở CỘT 2 (INTERACTIVE AI CAREER COPILOT)
> **Mục tiêu:** Kích hoạt khung Chat ở Cột 2 thành Trợ lý thông minh thời gian thực (hỗ trợ Streaming SSE).

* **Công việc:**
  1. Xây dựng Router: `POST /api/v1/chat/message` (hoặc WebSocket / Server-Sent Events SSE).
  2. Context Injection: Tự động đính kèm `CandidateProfile` hiện tại và `JDMatchReport` vào prompt ngữ cảnh của AI.
  3. Hỗ trợ các tác vụ nhanh:
     - *"Giải thích tại sao tôi bị trừ điểm ở phần kinh nghiệm?"*
     - *"Viết lại giúp tôi đoạn tóm tắt mở đầu cho vị trí này"*
     - *"Dự đoán 5 câu hỏi phỏng vấn hóc búa nhất dựa trên lỗ hổng trong CV của tôi"*

---

### 🎙️ BƯỚC 4: BỘ DỰ ĐOÁN CÂU HỎI PHỎNG VẤN & MOCK INTERVIEW (PHASE 5)
> **Mục tiêu:** Chuẩn bị cho ứng viên bước phỏng vấn thực tế sau khi đã có CV 90+ điểm.

* **Công việc:**
  1. Module `InterviewQuestionPredictor`: Dự đoán 5 câu hỏi kỹ thuật + 3 câu hỏi hành vi tình huống dựa trên các điểm thiếu trong JD.
  2. Tạo giao diện luyện tập phỏng vấn thử (Mock Interview Mode) tương tác từng câu với AI.

---

## 📊 BẢNG TỔNG KẾT THỨ TỰ ƯU TIÊN HÔM NAY (PRIORITY ROADMAP)

| Thứ tự | Hạng mục công việc | Độ ưu tiên | Giá trị mang lại |
|:---:|:---|:---:|:---|
| **1** | **Sinh CV May Đo (Tailored CV Generator)** | 🔴 **P0 (Cao nhất)** | Biến điểm số phân tích thành sản phẩm đầu ra hoàn chỉnh lưu tại Cột 3. |
| **2** | **Xuất File PDF/Word Chuẩn ATS 1-Chạm** | 🔴 **P0 (Cao nhất)** | Cho phép người dùng tải ngay CV đi ứng tuyển thực tế. |
| **3** | **Kích hoạt Chat AI Copilot Cột 2 (Streaming)** | 🟡 **P1 (Quan trọng)** | Tương tác tư vấn trực tiếp và trả lời thắc mắc về hồ sơ. |
| **4** | **Dự đoán Câu hỏi Phỏng vấn (Interview Prep)** | 🟢 **P2 (Nâng cao)** | Khép kín toàn bộ hành trình ứng tuyển của ứng viên. |

---

## ❓ CÂU HỎI THỐNG NHẤT VỚI BẠN TRƯỚC KHI TRIỂN KHAI

Để triển khai chuẩn xác theo ý bạn hôm nay, bạn muốn ưu tiên bắt đầu với bước nào trước:
1. **Lựa chọn A (Khuyến nghị):** Bắt đầu ngay với **Bước 1 & Bước 2** (Xây dựng động cơ sinh bản CV May Đo cho JD và bộ xuất tải PDF/Word chuẩn ATS ở Cột 3)?
2. **Lựa chọn B:** Bắt đầu với **Bước 3** (Hoàn thiện tính năng Chat AI Copilot tương tác trực tiếp ở Cột 2 trước)?
