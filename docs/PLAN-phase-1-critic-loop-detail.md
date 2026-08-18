# 🛡️ KẾ HOẠCH CHI TIẾT GIAI ĐOẠN 1: ĐỘNG CƠ CRITIC-ACTOR SELF-REFLECTION CHO MAY ĐO CV

> **Tài liệu:** `docs/PLAN-phase-1-critic-loop-detail.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Kế hoạch chi tiết, KHÔNG viết code)**  
> **Kiến trúc sư:** `@[project-planner]`, `@[ai-agents-architect]`  
> **Mục tiêu:** Xây dựng hệ thống tự phản biện khép kín (Closed-Loop Reflection) đảm bảo bản CV may đo luôn đạt 90-95+ điểm ATS và **0% bịa đặt kinh nghiệm**.

---

## 🎯 1. BÀI TOÁN CẦN GIẢI QUYẾT TRONG GIAI ĐOẠN 1

Khi dùng AI tạo hoặc viết lại CV, có **2 rủi ro chí mạng** mà các hệ thống AI thông thường mắc phải:
1. **Ảo giác / Bịa đặt (Hallucination):** AI tự ý thêm các công nghệ hoặc kinh nghiệm mà ứng viên chưa từng làm chỉ để "khớp" với JD.
2. **Hành văn sáo rỗng (Fluff & Passive):** Dùng các từ thụ động (*"Chịu trách nhiệm phát triển..."*, *"Tham gia vào dự án..."*) và thiếu số liệu định lượng (%, $, req/s, DAU).

👉 **Giải pháp Giai đoạn 1:** Áp dụng mô hình **Actor - Critic - Reflector**:
- **Actor Agent:** Sinh bản nháp CV.
- **Critic Agent (Thanh tra độc lập):** Soi xét từng câu chữ theo 4 tiêu chí khắt khe.
- **Reflector Loop:** Tự động sửa lỗi dựa trên phản biện của Critic cho đến khi đạt điểm ≥ 90/100 mới xuất bản sang Cột 3.

---

## 🔬 2. BỘ TIÊU CHÍ THẨM ĐỊNH 4 CHIỀU CỦA CRITIC AGENT (4-DIMENSION RUBRIC)

Critic Agent sẽ chấm điểm bản CV trên thang điểm **100 điểm** (mỗi tiêu chí 25 điểm):

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       THANG ĐIỂM THẨM ĐỊNH 4 CHIỀU (CRITIC RUBRIC)                          │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ CHIỀU 1: ĐỊNH LƯỢNG THÀNH TỰU│ CHIỀU 2: CHỐNG BỊA ĐẶT       │ CHIỀU 3: ĐỘ PHỦ TỪ KHÓA ATS   │
│ (Quantifiable Metrics - 25đ) │ (Anti-Hallucination - 25đ)   │ (ATS Keyword Alignment - 25đ) │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • Tỷ lệ câu có số liệu cụ    │ • Đối chiếu 100% kỹ năng     │ • Kiểm tra độ phủ 10-15 từ    │
│   thể: %, $, ms, DAU, scale. │   với hồ sơ CV gốc.          │   khóa trọng tâm từ JD.       │
│ • >= 80% số câu có số: 25đ.  │ • Phát hiện kỹ năng "ảo":    │ • Danh sách kỹ năng chuẩn 10- │
│ • 60% - 79%: 20đ.            │   Trừ 5đ/kỹ năng bịa đặt.    │   15 skills: 25đ.             │
│ • < 40%: 8đ (Bắt viết lại).  │ • 0% Hallucination: 25đ.     │ • Quá nhiều (>20 skills): 16đ │
├──────────────────────────────┴──────────────────────────────┴───────────────────────────────┤
│ CHIỀU 4: ĐỘNG TỪ HÀNH ĐỘNG HARVARD & TÍNH TINH GỌN (Action Verbs & Brevity - 25đ)           │
│ • 100% câu đạn bắt đầu bằng Action Verb mạnh mẽ (Thiết kế, Tối ưu, Xây dựng, Spearheaded...).│
│ • Phát hiện cụm từ thụ động ("chịu trách nhiệm", "tham gia vào"): Trừ 4đ/lỗi.              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. SƠ ĐỒ VÒNG LẶP PHẢN BIỆN KHÉP KÍN (CLOSED-LOOP REFLECTION WORKFLOW)

```
[1. NGƯỜI DÙNG BẤM 'MAY ĐO CV CHUẨN HARVARD' Ở CỘT 3]
                          │
                          ▼
[2. ACTOR AGENT: SINH BẢN NHÁP CV VÒNG 1]
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│ [3. CRITIC AGENT: THẨM ĐỊNH 4 CHIỀU ĐỘC LẬP]                      │
│ • Chấm: Metrics (20/25) + Grounding (25/25) + ATS (25/25) +       │
│         Verbs (18/25) = 88/100.                                   │
│ • Feedback: "Câu kinh nghiệm 2 còn dùng từ thụ động 'tham gia vào'│
│   và chưa có số liệu % cải thiện hiệu năng."                      │
└───────────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼ (Nếu Điểm >= 90)          ▼ (Nếu Điểm < 90 & Vòng < 3)
   [XUẤT BẢN RA CỘT 3 NGAY]   [4. REFLECTOR LOOP: TỰ ĐỘNG SỬA LỖI]
                              • Tiêm số liệu định lượng theo ngữ cảnh.
                              • Đổi động từ thụ động thành Action Verb.
                              • Loại bỏ kỹ năng không có chứng cứ.
                                        │
                                        ▼
                              [5. CRITIC CHẤM LẠI VÒNG 2]
                              • Điểm mới: 94/100 ➔ ĐẠT CHUẨN!
                                        │
                                        ▼
                              [6. XUẤT BẢN RA CỘT 3 KÈM HUY HIỆU THẨM ĐỊNH]
                              🛡️ Critic Agent Verified: 94/100 (0% Hallucination)
```

---

## 📁 4. DANH SÁCH TỪNG BƯỚC THỰC HIỆN CỤ THỂ (TASK BREAKDOWN)

### 🔹 Bước 1.1: Định nghĩa Pydantic Models cho Thẩm định & Phản biện
* **Tệp:** `ai/models/critic.py`
* **Nhiệm vụ:**
  - Định nghĩa schema `CriticDimensionScore` (Tên tiêu chí, Điểm 0-25, Góp ý).
  - Định nghĩa schema `CriticEvaluationReport` (Tổng điểm, Trạng thái duyệt, Danh sách lỗi, Lời khuyên cho Reflector).
  - Định nghĩa schema `ReflectiveSynthesisResult` (Số vòng lặp thực hiện, Điểm Critic cuối cùng, Lịch sử cải thiện qua từng vòng).

### 🔹 Bước 1.2: Xây dựng Lõi Thẩm Định `CriticAgent`
* **Tệp:** `ai/analysis/critic_agent.py`
* **Nhiệm vụ:**
  - Thuật toán bóc tách Regex nhận diện số liệu định lượng (%, $, req/s, DAU, latency ms...).
  - Thuật toán so sánh đối chiếu kỹ năng với `raw_profile` để chặn đứng 100% kỹ năng bịa đặt.
  - Từ điển Action Verbs chuẩn Harvard (Tiếng Anh & Tiếng Việt) và danh sách lọc từ thụ động.

### 🔹 Bước 1.3: Xây dựng Động Cơ Tự Phản Biện `ReflectiveHarvardSynthesizer`
* **Tệp:** `ai/analysis/reflective_synthesizer.py`
* **Nhiệm vụ:**
  - Điều phối vòng lặp khép kín giữa `HarvardCVSynthesizer` (Actor) và `CriticAgent` (Critic).
  - Hàm `_refine_draft_with_feedback()` tự động sửa các câu yếu theo chỉ dẫn của Critic.
  - Kiểm soát tối đa 3 vòng lặp để đảm bảo tốc độ phản hồi nhanh.

### 🔹 Bước 1.4: Tích hợp API Backend & Cập Nhật Response Headers
* **Tệp:** `be/api/v1/ats_router.py`
* **Nhiệm vụ:**
  - Nâng cấp endpoint `POST /api/v1/ats/generate-cv` để chạy qua `ReflectiveHarvardSynthesizer`.
  - Trả về các Headers minh bạch: `X-Critic-Score`, `X-Critic-Approved`, `X-Reflection-Iterations`.

### 🔹 Bước 1.5: Giao Diện Hiển Thị Minh Bạch Trên Cột 3
* **Tệp:** `fe/src/components/TailoredCVHub.tsx`
* **Nhiệm vụ:**
  - Hiển thị Huy hiệu thẩm định: `🛡️ Đã Thẩm Định Bởi Critic Agent: 94/100 (Qua 2 vòng tự tối ưu)`.
  - Bảng chi tiết 4 điểm thành phần khi người dùng di chuột hoặc bấm xem chi tiết.

### 🔹 Bước 1.6: Bộ Kiểm Thử Tự Động (Automated Testing)
* **Tệp:** `ai/tests/test_critic_agent.py`, `ai/tests/test_reflective_synthesizer.py`, `be/tests/test_generate_cv_api.py`.
* **Nhiệm vụ:** Chạy toàn bộ test suite để bảo đảm đạt 100% test pass.

---

## ❓ 5. XÁC NHẬN VỚI BẠN (SOCRATIC CONFIRMATION)

Bạn xem bản kế hoạch chi tiết của **Giai đoạn 1** ở trên:
1. Bạn có muốn điều chỉnh thêm tiêu chí nào trong **Thang điểm 4 chiều của Critic Agent** không?
2. Khi bạn đã hoàn toàn hài lòng với kế hoạch này, bạn có muốn chúng ta bắt đầu tiến hành triển khai Giai đoạn 1 không?
