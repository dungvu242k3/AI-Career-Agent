# 🗺️ KẾ HOẠCH BƯỚC TIẾP THEO: LỘ TRÌNH TRIỂN KHAI PHASE 3, 4 & 5 (CAREERPILOT AI)

> **Mã kế hoạch:** `docs/PLAN-next-step-phase3-roadmap.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Không viết code)**  
> **Người lập kế hoạch:** `@[project-planner]`, `@[ai-engineer]`, `@[frontend-specialist]`  
> **Mục tiêu:** Định hình các bước tiếp theo sau khi đã hoàn thành 100% Phase 1 (Bóc tách CV) và Phase 2 (So khớp JD + ATS 50/30/20 + STAR Rewriter + Chống nhồi nhét từ khóa).

---

## 📊 TRẠNG THÁI HIỆN TẠI CỦA 3 CỘT WORKSPACE STUDIO

```
┌────────────────────────┬────────────────────────┬────────────────────────┐
│   CỘT 1: MY CV (30%)   │   CỘT 2: AI COPILOT    │  CỘT 3: ATS STUDIO     │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ ✅ Bóc tách PDF/Word   │ 🟡 Đang hiển thị Trace │ ✅ In-Memory JD Parser │
│ ✅ 8 Nhóm kỹ năng      │    suy luận tĩnh       │ ✅ ATS 50/30/20 Scorer │
│ ✅ Timeline kinh nghiệm│ 🚀 CẦN NÂNG CẤP THÀNH  │ ✅ Chuẩn 10-15 Skills  │
│ ✅ Chống scan ảnh      │    TRỢ LÝ CHAT AI      │ ✅ STAR Rewriter V1/V2 │
│ ✅ Modal chỉnh sửa CV  │    TƯƠNG TÁC ĐA CHIỀU  │ ✅ 1-Click Copy STAR   │
└────────────────────────┴────────────────────────┴────────────────────────┘
```

---

## 🎯 3 LỰA CHỌN PHÁT TRIỂN TIẾP THEO

---

### 🚀 LỰA CHỌN 1 (KHUYẾN NGHỊ ƯU TIÊN CAO NHẤT): PHASE 3 — TRỢ LÝ AI CAREER CHAT (CỘT 2) & BẢN ĐỒ NHIỆT TỪ KHÓA
* **Mục tiêu:** Kích hoạt Cột 2 (AI Assistant) thành một **Chuyên Gia Hướng Nghiệp AI Tương Tác Trực Tiếp (Conversational Career Copilot)**.
* **Các tính năng chính:**
  1. **Chat Thông Minh với Toàn Bộ Ngữ Cảnh (Full-Context Career Chat):**
     * Chatbot tự động nạp dữ liệu từ Cột 1 (`CandidateProfile`) và Cột 3 (`JDMatchReport`) vào bộ nhớ ngữ cảnh.
     * Người dùng có thể hỏi bất kỳ câu hỏi nào:
       * *"Dựa vào JD Shopee này, tôi nên tập trung vào kỹ năng nào nhất trong buổi phỏng vấn?"*
       * *"Làm sao để tôi giải thích khoảng trống 6 tháng (career gap) trong CV một cách chuyên nghiệp?"*
       * *"Viết giúp tôi một bức thư ứng tuyển (Cover Letter) ngắn 150 chữ gửi Tech Lead vị trí này."*
  2. **Streaming Phản Hồi Từng Chữ (SSE Realtime Stream):** Sử dụng Server-Sent Events để câu trả lời hiển thị mượt mà theo thời gian thực.
  3. **Bản Đồ Nhiệt Từ Khóa (Keyword Heatmap):** Bật công tắc highlight trực quan các từ khóa công nghệ xuất hiện trên cả CV và JD.

---

### 🎯 LỰA CHỌN 2: PHASE 4 — DỰ ĐOÁN CÂU HỎI PHỎNG VẤN (INTERVIEW PREDICTOR) & XUẤT CV TAILORED PDF
* **Mục tiêu:** Biến kết quả ATS thành công cụ chuẩn bị phỏng vấn và tạo ra file CV hoàn chỉnh để nộp ngay.
* **Các tính năng chính:**
  1. **Bộ Dự Đoán Câu Hỏi Phỏng Vấn (Interview Question Predictor):**
     * Dựa trên các kỹ năng thiếu (🔴) và kỹ năng cốt lõi (🟢), sinh ra bộ 5–10 câu hỏi kỹ thuật + tình huống thực tế mà Nhà tuyển dụng của JD đó chắc chắn sẽ hỏi.
     * Cung cấp gợi ý trả lời mẫu theo đúng trải nghiệm thực tế của ứng viên.
  2. **Trình Xuất CV Tối Ưu Hóa Chuẩn ATS (Tailored PDF CV Exporter):**
     * Cho phép chèn trực tiếp các câu đạn STAR vừa sinh vào hồ sơ và tải về file PDF định dạng chuẩn ATS (Single-column, Clean typography, Không lỗi parse).

---

### 💼 LỰA CHỌN 3: PHASE 5 — THẨM ĐỊNH MỨC LƯƠNG (SALARY FIT) & SO KHỚP ĐA JD HÀNG LOẠT
* **Mục tiêu:** Định giá năng lực ứng viên trên thị trường và mở rộng quy mô so khớp.
* **Các tính năng chính:**
  1. **Thẩm Định Mức Lương Thị Trường (Salary Benchmark):** Ước tính dải lương (VD: $1,500 - $2,200) dựa trên số năm kinh nghiệm, vị trí và tech stack.
  2. **So Khớp Đa JD (Batch Multi-JD Comparison):** Cho phép so sánh 1 CV với 3–5 JD khác nhau cùng lúc để tìm ra công ty có độ tương thích cao nhất.

---

## 📋 BẢNG SO SÁNH CÁC LỰA CHỌN

| Tiêu chí | Lựa chọn 1: AI Career Chat (Cột 2) | Lựa chọn 2: Interview Predictor & Xuất PDF | Lựa chọn 3: Salary Fit & Đa JD |
|:---|:---:|:---:|:---:|
| **Tầm quan trọng** | 🌟🌟🌟 **P0 (Lấp đầy Cột 2)** | 🌟🌟 **P1 (Hậu tuyển dụng)** | 🌟 **P2 (Nâng cao)** |
| **Trải nghiệm người dùng** | Tương tác 2 chiều mượt mà | Sinh tài liệu nộp việc | Khảo sát thị trường |
| **Độ phức tạp kỹ thuật** | Trung bình (FastAPI Streaming + Context Injection) | Trung bình (ReportLab PDF / WeasyPrint) | Thấp - Trung bình |

---

## ❓ CÂU HỎI ĐỊNH HƯỚNG DÀNH CHO BẠN (SOCRATIC CHECK):

Bạn muốn hệ thống tiếp tục triển khai theo hướng nào tiếp theo?
1. **Lựa chọn 1 (Khuyến nghị):** Xây dựng **Trợ lý AI Career Chat (Cột 2)** với tính năng chat streaming thời gian thực, hiểu sâu toàn bộ CV + JD và Bản đồ nhiệt từ khóa.
2. **Lựa chọn 2:** Xây dựng **Bộ Dự đoán câu hỏi phỏng vấn theo JD** & **Xuất file PDF CV chuẩn ATS**.
3. **Lựa chọn khác:** Bất kỳ ý tưởng hoặc điều chỉnh cụ thể nào mà bạn muốn ưu tiên trước.
