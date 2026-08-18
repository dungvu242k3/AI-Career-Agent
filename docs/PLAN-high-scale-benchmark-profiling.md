# 📊 KẾ HOẠCH CHI TIẾT GIAI ĐOẠN 4: ĐO LƯỜNG HIỆU NĂNG QUY MÔ LỚN, LOAD TESTING & PRODUCTION OPTIMIZATION

> **Tài liệu:** `docs/PLAN-high-scale-benchmark-profiling.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Kế hoạch chi tiết, KHÔNG viết code)**  
> **Kiến trúc sư:** `@[project-planner]`, `@[performance-profiling]`, `@[ai-engineering-toolkit]`  
> **Mục tiêu:** Xây dựng bộ công cụ đo lường tốc độ, kiểm thử tải đồng thời cao (High-Concurrency Load Testing) và tối ưu hóa tài nguyên (Memory/CPU Profiling) chuẩn kỹ thuật AI Engineering.

---

## 🎯 1. BỐI CẢNH & CÁC CHỈ SỐ SLA MỤC TIÊU (BENCHMARK SLA METRICS)

Để đảm bảo hệ thống phục vụ tốt hàng nghìn ứng viên cùng lúc mà không bị trễ hoặc tràn bộ nhớ, chúng ta cần thiết lập và kiểm chứng các ngưỡng SLA:

```
┌──────────────────────────────────────┬────────────────────────────┬────────────────────────────┐
│ THÀNH PHẦN AI ENGINE                 │ NGƯỠNG SLA ĐỘ TRỄ (P95)    │ THÔNG LƯỢNG (THROUGHPUT)   │
├──────────────────────────────────────┼────────────────────────────┼────────────────────────────┤
│ 1. Critic-Actor Reflection Engine    │ < 5 ms                     │ > 2,000 requests/giây      │
│ 2. Hybrid Vector Search + Reranker   │ < 15 ms                    │ > 800 requests/giây        │
│ 3. Interview Arena Judge Evaluator   │ < 10 ms                    │ > 1,000 requests/giây      │
│ 4. PDF/DOCX Parser & ATS Extractor   │ < 200 ms                   │ > 50 uploads/giây          │
│ 5. Toàn hệ thống chịu tải đồng thời  │ Error Rate = 0.00%         │ 100 - 500 Virtual Users    │
└──────────────────────────────────────┴────────────────────────────┴────────────────────────────┘
```

---

## 🛠️ 2. DANH SÁCH CÁC CÔNG CỤ & SCRIPT TRONG GIAI ĐOẠN 4 (TASK BREAKDOWN)

### 🔹 Bước 4.1: Benchmark CLI Suite (`.agent/scripts/benchmark_engine.py`)
* **Nhiệm vụ:**
  - Chạy đo lường 10,000 lượt xử lý độc lập cho từng module AI:
    1. `CriticAgent`: Đo thời gian kiểm tra AST/Regex chống bịa đặt 4 chiều.
    2. `HybridJobSearchEngine`: Đo tốc độ Sparse BM25 + Dense Cosine Similarity.
    3. `JobCrossEncoderReranker`: Đo tốc độ tính Semantic Fit Score.
    4. `InterviewArenaEngine`: Đo tốc độ chấm điểm của Silent Judge.
  - Tính toán chính xác: $P_{50}, P_{90}, P_{95}, P_{99}$, Min, Max, Average và Throughput (RPS).
  - Xuất bảng biểu báo cáo định dạng Markdown trực quan.

### 🔹 Bước 4.2: High-Concurrency Load Testing Suite (`.agent/scripts/load_test.py`)
* **Nhiệm vụ:**
  - Giả lập tải đa luồng bất đồng bộ (`asyncio` + `httpx`) với 50, 100, 200 và 500 Virtual Users (VUs).
  - Bắn request đồng thời vào các API endpoints quan trọng:
    - `POST /api/v1/chat/message` (Tìm việc đa kênh).
    - `GET /api/v1/jobs/by-domain` (Hybrid Search & Re-ranking).
    - `POST /api/v1/interview/submit-answer` (Judge chấm điểm phỏng vấn).
    - `POST /api/v1/ats/generate-cv` (May đo CV với Critic Agent).
  - Đo tỷ lệ phản hồi thành công (200 OK), Request Timeouts và Latency Percentiles dưới áp lực tải lớn.

### 🔹 Bước 4.3: Memory Leak & CPU Flame Profiler (`.agent/scripts/profile_memory.py`)
* **Nhiệm vụ:**
  - Sử dụng `tracemalloc` và `cProfile` tích hợp sẵn của Python.
  - Đo bộ nhớ RAM đỉnh (Peak Memory RSS) khi xử lý 1,000 CV và 10,000 Job descriptions.
  - Xác định các hàm tiêu tốn nhiều chu kỳ CPU nhất (Bottleneck detection) để tối ưu $O(1)$ hoặc vectorization.

### 🔹 Bước 4.4: One-Click Full Project Verifier (`.agent/scripts/verify_all.py`)
* **Nhiệm vụ:**
  - Tích hợp kiểm thử chuỗi khép kín trong 1 lệnh duy nhất:
    1. `python .agent/scripts/security_scanner.py` (Quét 0 lỗ hổng).
    2. `python .agent/scripts/benchmark_engine.py` (Đạt chuẩn P95 SLA).
    3. `pytest` (Toàn bộ 99+ tests pass).
    4. `npm run build` (Frontend build pass 100%).
  - Báo cáo tổng thể sẵn sàng bàn giao sản phẩm hoàn chỉnh (Production-Ready).

---

## ❓ 3. XÁC NHẬN CÙNG BẠN (SOCRATIC CONFIRMATION)

1. Bạn thấy kế hoạch **Giai đoạn 4: Đo lường hiệu năng, Load Testing quy mô lớn và Tối ưu hóa Production** như trên có đúng với mục tiêu chứng minh năng lực AI Engineering mà bạn muốn không?
2. Bạn có muốn chúng ta bắt đầu triển khai **Giai đoạn 4** ngay bây giờ không?
