# 📐 KẾ HOẠCH CHI TIẾT BƯỚC 1: CV INGESTION & STRUCTURED EXTRACTION PIPELINE
*(Step 1: Tiếp nhận, Xử lý tài liệu & Chuẩn hóa Dữ liệu Ứng viên — ĐÃ CHỐT THIẾT KẾ)*

> **Vai trò:** AI Systems Engineer  
> **Mục tiêu:** Biến file CV PDF bất kỳ (1-3 trang, tiếng Việt / tiếng Anh, layout 1 hoặc 2 cột) thành một đối tượng `CandidateProfile` JSON có cấu trúc chuẩn hóa, sạch sẽ và tin cậy 100% để cấp dữ liệu cho các bước AI tiếp theo (ATS Scoring, Match, Rewrite).  
> **Trạng thái:** ✅ ĐÃ CHỐT THIẾT KẾ (Chờ triển khai hoặc lên tiếp kế hoạch Bước 2).

---

## 🎯 CÁC QUYẾT ĐỊNH THIẾT KẾ ĐÃ ĐƯỢC CHỐT

1. **UX Flow:** Sau khi bóc tách xong, FE sẽ hiển thị **bảng thẻ Preview trực quan** (Họ tên, Title, Số năm KN, 8 nhóm Skills, Công ty gần nhất) cho phép người dùng click sửa nhanh nếu cần trước khi kích hoạt Bước 2 (Chấm điểm ATS).
2. **Quyền riêng tư:** Hiển thị đầy đủ Email và Số điện thoại (ứng dụng phục vụ cá nhân).
3. **Taxonomy Kỹ năng:** Giữ nguyên 8 nhóm chuẩn IT (`Programming`, `Frameworks`, `Databases`, `DevOps/Cloud`, `AI/ML`, `Testing`, `Tools`, `Soft Skills`).

---

## 🗺️ KIẾN TRÚC TỔNG THỂ BƯỚC 1

```
                    ┌─────────────────────────┐
                    │      File Upload        │
                    │ (PDF từ User trên FE)   │
                    └────────────┬────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1.1 INGESTION & SECURITY GATE (Tiền kiểm tra an toàn)           │
│  - Magic Bytes Check (%PDF-1.x) & MIME Validation               │
│  - File Size Limit (<= 10MB) & Page Count Limit (<= 5 trang)    │
│  - Filename Sanitization & SHA256 Checksum (chống trùng lặp)    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1.2 PDF DECONSTRUCTION & DE-NOISING (Giải mã & Khử nhiễu Text)  │
│  - PyMuPDF Block Extraction: Phân tích tọa độ (BBox) để đọc     │
│    đúng thứ tự cột (2-column layout vs 1-column layout)         │
│  - Text Stream Detection: Nhận diện PDF có chữ vs PDF Scan/Ảnh  │
│  - Normalization: UTF-8 Unicode NFC, chuẩn hóa bullet icons     │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Cleaned Raw Text
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1.3 LLM EXTRACTION ENGINE (Bóc tách cấu trúc với Gemini Flash)   │
│  - Model: Gemini 2.0 Flash (Latency ~0.8s, Cost: ~200đ)         │
│  - Structured Output Enforcement: `response_schema` (JSON Mode) │
│  - Multilingual Handling: Tiếng Việt (họ tên, địa chỉ) & En     │
│  - Timeline Calculation: Tự tính tổng năm KN từ dates          │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Raw JSON
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1.4 CANONICAL SCHEMA & AUTO-HEALING (Kiểm định & Tự sửa lỗi)    │
│  - Pydantic v2 Model Validation & Strict Type Coercion          │
│  - Date Normalizer (Chuyển đổi các định dạng ngày về YYYY-MM)   │
│  - Taxonomy Normalizer (Gán Skill vào 8 nhóm IT chuẩn)          │
│  - Fallback Handler: Tự động gán default nếu thiếu field phụ    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Validated CandidateProfile
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1.5 PERSISTENCE & USER REVIEW GATE (Lưu trữ & Thẻ Preview)      │
│  - Lưu DB: `candidates` (JSON) & `uploads` (Raw Text + File)    │
│  - UI: Hiện thẻ tóm tắt cho phép User chỉnh sửa trước khi       │
│    bấm "Phân tích ATS" (Bước 2)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 CHỈ SỐ CAM KẾT (SLAs & Benchmarks cho Bước 1)

| Tiêu chí | Mục tiêu cam kết (Target SLA) |
|---|---|
| **Thời gian phản hồi (Latency)** | $\le 1.8$ giây (từ lúc bấm upload đến khi hiển thị thẻ preview) |
| **Chi phí mỗi lượt parse** | $\le 250$ VNĐ (~$0.01) |
| **Độ chính xác trích xuất (Extraction Accuracy)** | $\ge 96\%$ các trường thông tin chính (Tên, Email, Skills, Công ty) |
| **Tỷ lệ lỗi vỡ layout (2-column layout)** | $< 2\%$ |
