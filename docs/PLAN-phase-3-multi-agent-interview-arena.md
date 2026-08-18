# 🎙️ KẾ HOẠCH CHI TIẾT GIAI ĐOẠN 3: ĐẤU TRƯỜNG PHỎNG VẤN ĐA TÁC TỬ ĐỐI KHÁNG (ADVERSARIAL MULTI-AGENT MOCK INTERVIEW ARENA)

> **Tài liệu:** `docs/PLAN-phase-3-multi-agent-interview-arena.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Kế hoạch chi tiết, KHÔNG viết code)**  
> **Kiến trúc sư:** `@[project-planner]`, `@[ai-agents-architect]`, `@[ai-engineering-toolkit]`  
> **Mục tiêu:** Nâng cấp màn hình `/interview` thành phòng phỏng vấn giả lập sống động với **3 Persona AI độc lập** (Tech Lead + HR Manager + Trọng Tài Judge).

---

## 🎭 1. BỘ BA NHÂN VẬT TÁC TỬ AI (3-AGENT PERSONA ARCHITECTURE)

Trong phòng phỏng vấn, 3 AI Agent phối hợp nhịp nhàng mô phỏng buổi phỏng vấn thực tế tại các tập đoàn công nghệ lớn:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          3 NHÂN VẬT TÁC TỬ AI TRONG PHÒNG PHỎNG VẤN                         │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ 👨‍💻 AGENT 1: TECH LEAD        │ 👩‍💼 AGENT 2: HR MANAGER      │ ⚖️ AGENT 3: SILENT JUDGE      │
│ (Mr. Alex - Kỹ Thuật Khó Tính)│ (Ms. Sarah - Văn Hóa & STAR) │ (Trọng Tài Độc Lập)           │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • Soi đúng lỗ hổng kỹ thuật  │ • Phỏng vấn về văn hóa nhóm, │ • Lặng lẽ chấm điểm từng câu  │
│   giữa CV và JD.             │   xung đột, áp lực deadline. │   trả lời thời gian thực.     │
│ • Đặt câu hỏi dồn ép về:     │ • Đánh giá phương pháp trả   │ • Đánh giá 4 trục:            │
│   System Design, Concurrency,│   lời theo cấu trúc STAR.    │   1. Technical Depth (30%)    │
│   Database Indexing, Caching,│ • Quan sát tính chủ động     │   2. STAR Structure (25%)     │
│   High-load Architecture.    │   (Ownership) và giao tiếp.  │   3. Confidence & Tone (25%)  │
│                              │                              │   4. Adaptability (20%)       │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

---

## 🔄 2. LUỒNG HOẠT ĐỘNG PHỎNG VẤN (TURN-TAKING ORCHESTRATION)

```
[1. ỨNG VIÊN BẤM 'BẮT ĐẦU PHỎNG VẤN' TẠI TAB /interview]
                          │
                          ▼
[2. AI ORCHESTRATOR: PHÂN TÍCH KHOẢNG TRỐNG GIỮA CV VÀ JD]
• Trích xuất 3 điểm mạnh nhất và 3 lỗ hổng kỹ thuật lớn nhất của ứng viên.
• Lập kịch bản phỏng vấn động gồm 5-6 câu hỏi tình huống thực chiến.
                          │
                          ▼
[3. VÒNG LẶP PHỎNG VẤN TƯƠNG TÁC (INTERACTION LOOP)]
  ├── Lượt 1 (Tech Lead Alex): Hỏi câu mở đầu kỹ thuật và System Design.
  │   └── Ứng viên trả lời ➔ Silent Judge chấm điểm ngầm lượt 1.
  ├── Lượt 2 (Tech Lead Alex): Hỏi xoáy sâu vào câu trả lời vừa rồi (Follow-up drill down).
  │   └── Ứng viên trả lời ➔ Silent Judge chấm điểm ngầm lượt 2.
  ├── Lượt 3 (HR Sarah chen ngang): "Cho tôi ngắt lời một chút, bạn đã từng gặp xung đột kỹ thuật với đồng nghiệp trong tình huống đó chưa?"
  │   └── Ứng viên trả lời theo STAR ➔ Silent Judge chấm điểm lượt 3.
  └── Lượt 4-5: Đan xen kỹ thuật nâng cao và bài toán áp lực thời gian.
                          │
                          ▼
[4. XUẤT BẢN BÁO CÁO THẨM ĐỊNH NĂNG LỰC TOÀN DIỆN (FINAL ASSESSMENT REPORT)]
• Tổng điểm phỏng vấn (Scale 0-100, Hạng A+/A/B/C).
• Bảng phân tích chi tiết từng câu: Điểm mạnh, Điểm yếu, Câu trả lời mẫu chuẩn Harvard.
• Đề xuất 3 hành động cần cải thiện trước ngày phỏng vấn thật.
```

---

## 📁 3. DANH SÁCH CÁC BƯỚC THỰC HIỆN TRONG GIAI ĐOẠN 3 (TASK BREAKDOWN)

### 🔹 Bước 3.1: Data Models Cho Phòng Phỏng Vấn
* **Tệp:** `ai/models/interview.py`
* **Nhiệm vụ:**
  - `InterviewTurn`: Lượt hỏi/đáp (Người hỏi: Tech Lead / HR, Nội dung câu hỏi, Câu trả lời, Điểm chấm lượt, Nhận xét nhanh).
  - `InterviewSession`: Phiên phỏng vấn (Danh sách lượt, Trạng thái, Điểm tích lũy).
  - `CandidateAssessmentReport`: Báo cáo đánh giá tổng kết sau buổi thi.

### 🔹 Bước 3.2: Động Cơ Điều Phối Đa Tác Tử `InterviewArenaEngine`
* **Tệp:** `ai/analysis/interview_arena.py`
* **Nhiệm vụ:**
  - Khởi tạo kịch bản câu hỏi dựa trên CV và JD của ứng viên.
  - Sinh câu hỏi tiếp theo linh hoạt: Tech Lead hỏi sâu 2 câu ➔ HR xen vào 1 câu tình huống.
  - Động cơ chấm điểm tức thì (Realtime Judge Evaluator).

### 🔹 Bước 3.3: API Router Backend Cho Phỏng Vấn
* **Tệp:** `be/api/v1/interview_router.py`
* **Nhiệm vụ:**
  - `POST /api/v1/interview/start`: Bắt đầu phiên phỏng vấn mới.
  - `POST /api/v1/interview/submit-answer`: Gửi câu trả lời và nhận phản hồi + câu hỏi tiếp theo.
  - `POST /api/v1/interview/finish`: Kết thúc và xuất báo cáo đánh giá.
  - Gắn vào `be/main.py`.

### 🔹 Bước 3.4: Nâng Cấp Giao Diện Đấu Trường Phỏng Vấn (`/interview`)
* **Tệp:** `fe/src/pages/InterviewPage.tsx`
* **Nhiệm vụ:**
  - Giao diện phòng thi trực quan với 2 Avatar AI (Mr. Alex - Tech Lead, Ms. Sarah - HR).
  - Khung hội thoại dạng kịch bản phỏng vấn trực tiếp kèm dòng phụ đề thời gian thực (Live Transcript).
  - Bộ đếm thời gian (Timer) và thanh đo độ tự tin.
  - Modal / Card hiển thị Báo cáo Thẩm định Năng Lực Toàn Diện khi hoàn thành.

### 🔹 Bước 3.5: Kiểm Thử Đầy Đủ (Unit & Integration Tests)
* **Tệp:** `ai/tests/test_interview_arena.py`, `be/tests/test_interview_api.py`.
* **Nhiệm vụ:** Đảm bảo 100% test pass.

---

## ❓ 4. XÁC NHẬN CÙNG BẠN (SOCRATIC CONFIRMATION)

1. Bạn thấy kế hoạch xây dựng **Đấu Trường Phỏng Vấn Đa Tác Tử (Tech Lead + HR + Judge Agent)** như trên có đúng với mong đợi của bạn cho Giai đoạn 3 không?
2. Bạn có muốn chúng ta bắt tay vào triển khai **Giai đoạn 3** ngay bây giờ không?
