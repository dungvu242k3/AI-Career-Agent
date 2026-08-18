# 🗺️ LỘ TRÌNH KỸ THUẬT: NÂNG CẤP HỆ THỐNG AI NÂNG CAO (ADVANCED AI ROADMAP)

> **Mã kế hoạch:** `docs/PLAN-advanced-ai-upgrade-roadmap.md`  
> **Chế độ:** 📝 **PLANNING & ROADMAP ONLY (Lập kế hoạch chia nhỏ từng phần, KHÔNG viết code)**  
> **Kiến trúc sư:** `@[project-planner]`, `@[ai-agents-architect]`, `@[ai-engineering-toolkit]`  
> **Mục tiêu:** Nâng cấp toàn diện hệ thống từ Standard Prompting lên **3 Trụ Cột AI Nâng Cao (State-of-the-Art Applied AI)** theo từng Phase độc lập, dễ làm, dễ kiểm thử và theo dõi tiến độ.

---

## 📊 TỔNG QUAN 3 GIAI ĐOẠN NÂNG CẤP (3-PHASE ROADMAP)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       LỘ TRÌNH 3 TRỤ CỘT AI NÂNG CAO CHO CAREERPILOT                        │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ PHASE A: AGENTIC CRITIC LOOP │ PHASE B: HYBRID VECTOR SEARCH│ PHASE C: ADVERSARIAL ARENA    │
│ (May đo CV & Chống Ảo Giác)  │ (Tìm việc Ngữ nghĩa & Rerank)│ (Phòng Phỏng vấn Đa Tác tử)   │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • Actor Agent (Sinh nháp)    │ • Vector Embedding Pipeline  │ • Tech Lead Agent (Hỏi sâu)   │
│ • Critic Agent (Soi lỗi/ATS) │ • Dense + Sparse BM25 Search │ • HR Culture Agent (Hành vi)  │
│ • Reflector (Tự sửa đến 95đ) │ • Cross-Encoder Re-ranker    │ • Judge Agent (Chấm điểm E2E) │
│ • 0% Hallucination Guarantee │ • Semantic Match Score %     │ • Live Mock Interview Arena   │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

---

## 🚀 GIAI ĐOẠN 1 (PHASE A): AGENTIC SELF-REFLECTION & CRITIC-ACTOR PIPELINE
> **Trọng tâm:** Biến động cơ may đo CV và sinh câu STAR thành **Hệ thống AI Tự Phản Biện Khép Kín (Closed-Loop Reflection System)** để đảm bảo mọi câu chữ xuất ra đều đạt 95+ điểm và không bao giờ bịa đặt.

### 📌 Phần 1.1: Xây Dựng Critic Agent Core (`ai/analysis/critic_agent.py`)
- **Nhiệm vụ:** Tạo một Agent chuyên trách đóng vai **"Thanh Tra Tuyển Dụng Khó Tính"**, chấm điểm bản thảo theo 4 chiều:
  1. **Định lượng (Quantifiable Metrics):** Có số liệu cụ thể (%, $, giây, DAU, quy mô) hay không?
  2. **Chống ảo giác (Anti-Hallucination Grounding):** Đối chiếu với CV gốc để phát hiện kinh nghiệm bịa đặt.
  3. **Độ phủ từ khóa ATS (Keyword Density):** Đạt chuẩn 10-15 từ khóa cốt lõi của JD chưa?
  4. **Động từ hành động (Harvard Action Verbs):** Sử dụng các động từ mạnh mẽ (Architected, Engineered, Optimized...).
- **Đầu ra:** Bảng điểm chi tiết `CriticScoreReport` (Điểm tổng, Danh sách lỗi cần sửa, Gợi ý cải thiện).

### 📌 Phần 1.2: Vòng Lặp Tự Sửa Lỗi (`ai/analysis/reflective_synthesizer.py`)
- **Nhiệm vụ:**
  - `Actor Agent` sinh bản nháp CV / câu STAR.
  - `Critic Agent` đánh giá. Nếu điểm < 90/100 ➔ Chuyển sang `Reflector Agent` sửa lại dựa trên phản biện của Critic (Tối đa 3 vòng lặp).
  - Khi điểm đạt ≥ 90 ➔ Xuất bản bản CV hoàn hảo sang Cột 3.
- **Unit Test:** `ai/tests/test_reflective_synthesizer.py` kiểm tra vòng lặp tự sửa lỗi.

### 📌 Phần 1.3: Hiển Thị Minh Bạch Trên UI (Reflection Trace Visualizer)
- **Nhiệm vụ:** Cột 3 hiển thị huy hiệu: `✅ Đã qua thẩm định Critic Agent: 94/100 (Qua 2 vòng tự tối ưu)`.

---

## 🔎 GIAI ĐOẠN 2 (PHASE B): HYBRID DENSE-SPARSE EMBEDDINGS & CROSS-ENCODER RE-RANKING
> **Trọng tâm:** Nâng cấp bộ máy tìm kiếm việc làm từ lọc SQL cơ bản thành **Hệ thống Tìm kiếm Ngữ nghĩa Đa tầng (Semantic Search Engine)**.

### 📌 Phần 2.1: Pipeline Vector Embeddings (`ai/analysis/job_embeddings.py`)
- **Nhiệm vụ:**
  - Tích hợp mô hình nhúng Vector (`text-embedding-3-small` hoặc local embedding).
  - Sinh Vector nhúng 1536 chiều cho toàn bộ hồ sơ ứng viên (Candidate Vector) và các bài đăng tuyển dụng (Job Vectors).

### 📌 Phần 2.2: Động Cơ Tìm Kiếm Lai (Hybrid Search: BM25 + Vector Cosine)
- **Nhiệm vụ:**
  - Kết hợp **Sparse Search (BM25)**: Bắt chính xác các từ khóa công nghệ (Docker, Kafka, Golang).
  - Kết hợp **Dense Search (Cosine Similarity)**: Bắt độ tương đồng ngữ nghĩa về vai trò, cấp bậc, định hướng.
  - Hợp nhất điểm số qua thuật toán RRF (Reciprocal Rank Fusion).

### 📌 Phần 2.3: Cross-Encoder Re-ranker (`ai/analysis/job_reranker.py`)
- **Nhiệm vụ:**
  - Lấy Top 15 kết quả từ Hybrid Search ➔ Đưa qua Cross-Encoder chấm điểm tương thích sâu (Semantic Fit Score 0 - 100%).
  - Trả về danh sách đã xếp hạng tối ưu nhất theo ngữ cảnh hồ sơ.

### 📌 Phần 2.4: Giao Diện Thẻ Công Việc Ngữ Nghĩa (Semantic Job Match UI)
- **Nhiệm vụ:** Hiển thị trên thẻ việc làm: `🎯 93% Phù hợp ngữ nghĩa (Khớp sâu về Kiến trúc Microservices & Văn hóa Fintech)`.

---

## 🎙️ GIAI ĐOẠN 3 (PHASE C): ADVERSARIAL MULTI-AGENT ARENA (PHÒNG PHỎNG VẤN ĐA TÁC TỬ)
> **Trọng tâm:** Nâng cấp tab Phỏng vấn AI (`/interview`) thành **Đấu trường Giả lập Đa Tác Tử Đối Kháng (Multi-Agent Mock Interview)**.

### 📌 Phần 3.1: Bộ Ba Nhân Vật Tác Tử AI (`ai/analysis/interview_agents.py`)
- **Nhiệm vụ:** Xây dựng 3 Persona AI hoạt động đồng bộ:
  1. **Tech Lead Agent (Mr. Alex - Chuyên gia Kỹ thuật):** Soi sâu vào System Design, Database Indexing, Concurrency, bảo mật và các lỗ hổng kỹ thuật trong CV.
  2. **HR Manager Agent (Ms. Sarah - Chuyên gia Văn hóa):** Đặt câu hỏi về tình huống xung đột nhóm, quản lý áp lực, phương pháp STAR.
  3. **Silent Judge Agent (Trọng tài AI):** Lặng lẽ theo dõi toàn bộ hội thoại, chấm điểm độ logic, tính tự tin, và tổng hợp Báo cáo Đánh giá Năng lực (Comprehensive Assessment Report).

### 📌 Phần 3.2: Cơ Chế Điều Phối Lượt Hỏi (Turn-Taking Orchestrator)
- **Nhiệm vụ:** Quản lý kịch bản phỏng vấn sống động: Tech Lead hỏi 2 câu kỹ thuật ➔ HR chen ngang hỏi 1 câu tình huống ➔ Trọng tài chấm điểm từng câu trả lời của ứng viên.

### 📌 Phần 3.3: Giao Diện Phòng Phỏng Vấn Giả Lập Mới (`fe/src/pages/InterviewPage.tsx`)
- **Nhiệm vụ:** Giao diện trực quan hiển thị 2 Người Phỏng Vấn AI, dòng phụ đề thời gian thực (Live Transcript), thanh đo độ tự tin và Báo cáo tổng kết sau buổi phỏng vấn.

---

## 📋 THỨ TỰ THỰC HIỆN TỪNG BƯỚC (STEP-BY-STEP EXECUTION ORDER)

| Bước | Giai đoạn | Hạng mục công việc cụ thể | Thời gian ước tính | Giá trị đạt được |
|:---:|:---:|:---|:---:|:---|
| **BƯỚC 1** | **Phase A** | Xây dựng **Critic Agent & Self-Reflection Loop** cho May đo CV | Giai đoạn 1 | CV đạt 95+ điểm chuẩn Harvard, 0% bịa đặt. |
| **BƯỚC 2** | **Phase B** | Xây dựng **Hybrid Search & Vector Re-Ranking** cho Tìm việc | Giai đoạn 2 | Tìm việc theo ngữ nghĩa sâu, khớp chuẩn xác văn hóa & tech stack. |
| **BƯỚC 3** | **Phase C** | Xây dựng **Adversarial Multi-Agent Mock Interview** | Giai đoạn 3 | Phòng phỏng vấn giả lập sống động với Tech Lead + HR. |

---

## ❓ XÁC NHẬN VỚI BẠN (SOCRATIC GATE)

Bạn có đồng ý bắt đầu triển khai **BƯỚC 1 (Giai đoạn 1: Xây dựng Critic Agent & Self-Reflection Loop cho May Đo CV & Viết STAR)** trước không? 

Khi bạn xác nhận, tôi sẽ tiến hành từng bước nhỏ của Bước 1 một cách mạch lạc và báo cáo chi tiết cho bạn!
