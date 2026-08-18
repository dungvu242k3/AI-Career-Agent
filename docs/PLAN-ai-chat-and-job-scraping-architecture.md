# 🏛️ BẢN THIẾT KẾ KỸ THUẬT: KIẾN TRÚC AI CHAT, RAG, AGENT & CƠ CHẾ LẤY DỮ LIỆU VIỆC LÀM

> **Tài liệu:** `docs/PLAN-ai-chat-and-job-scraping-architecture.md`  
> **Chế độ:** 📝 **PLANNING & ARCHITECTURE ONLY (Phân tích chuyên sâu, KHÔNG viết code)**  
> **Chủ đề thảo luận:**  
> 1. Luồng AI hoạt động dưới nền (Under the Hood) như thế nào?  
> 2. Có cần RAG (Vector Database) hay không? Khi nào cần?  
> 3. Có nhất thiết phải dùng Heavy Multi-Agent không?  
> 4. Cách lấy dữ liệu việc làm từ các kênh (TopCV, ITviec, VietnamWorks, LinkedIn) ra sao?

---

## 🔍 1. CÓ CẦN "AGENT" KHÔNG? VÀ NÊN DÙNG LOẠI AGENT NÀO?

### ❌ Sai lầm phổ biến: Heavy Multi-Agent Framework (CrewAI, AutoGen, LangGraph phức tạp)
Nếu dựng 3-4 agent tự do lặp vòng suy luận (ReAct Loop: Thought ➔ Action ➔ Observation ➔ Thought...):
* **Độ trễ rất cao (Latency 5 - 10 giây):** Người dùng bấm chat mà phải đợi quá lâu sẽ rời bỏ ứng dụng.
* **Tốn kém Token & Chi phí API:** Mỗi tin nhắn tốn gấp 4 - 6 lần số token.
* **Rủi ro ảo giác & Vòng lặp vô tận (Infinite Tool Calls):** Khó kiểm soát hành vi trả về của UI.

### ✅ Giải pháp tối ưu: "Single-Turn Directed Agent" (Intent Router + Function Calling)
Thay vì một Agent phức tạp tự chạy ngầm nhiều vòng, ta dùng mô hình **Kiến trúc Định hướng (Directed Function Calling)**:
1. **Bước 1 (Nhận diện Intent trong 50ms):** Nhận tin nhắn của người dùng.
2. **Bước 2 (Rẽ nhánh chính xác):**
   - **Nhánh A (Tìm việc):** Gọi trực tiếp hàm `fetch_jobs(domain, experience_years, location)` từ Database ➔ Trả về danh sách thẻ công việc kèm nút xem chi tiết.
   - **Nhánh B (Hỏi đáp CV / Hướng nghiệp):** Đưa ngữ cảnh CV vào LLM ➔ Sinh câu trả lời định dạng Markdown mượt mà.
3. **Ưu điểm:** Tốc độ phản hồi cực nhanh (< 1 giây), ổn định 100%, chi phí API cực thấp.

---

## 📚 2. CÓ CẦN "RAG" (VECTOR DATABASE / EMBEDDINGS) KHÔNG?

### 🚫 Đối với Hồ sơ CV & Mô tả JD: **HOÀN TOÀN KHÔNG CẦN RAG!**
* **Lý do kỹ thuật:**
  - CV thông thường dài khoảng 1 - 2 trang (~800 - 1,500 tokens).
  - JD thông thường dài 1 trang (~500 tokens).
  - Tổng context chỉ khoảng **1,500 - 2,000 tokens**.
  - Các mô hình hiện đại (GPT-4o-mini, Gemini 1.5/2.0) có cửa sổ ngữ cảnh từ **128,000 đến 1,000,000 tokens**.
  - ➔ Việc cắt nhỏ (chunking) rồi nhét vào Vector DB (Chroma/Pinecone) sẽ làm **vỡ vụn ngữ cảnh CV** và tăng độ phức tạp vô nghĩa.
* **Kỹ thuật chuẩn xác ở đây:** **Structured Context Injection (Bơm trực tiếp JSON Profile vào System Prompt)**.

### 💡 Khi nào thì CẦN RAG trong bài toán này?
Chỉ cần RAG khi:
* Hệ thống của bạn có **100,000+ bài tuyển dụng JD trong kho lưu trữ**, và người dùng tìm việc bằng câu hỏi ngữ nghĩa phức tạp:
  * *"Tìm cho tôi công việc nào ở công ty nước ngoài làm về thuật toán nén video mà không yêu cầu tiếng Nhật"*
  * Lúc này, RAG Vector Search sẽ quét qua hàng chục nghìn bài JD để tìm ra Top 5 bài có độ tương đồng ngữ nghĩa cao nhất.

---

## 🌐 3. CÁCH LẤY DỮ LIỆU VIỆC LÀM TỪ CÁC KÊNH (ITVIEC, TOPCV, LINKEDIN...)

Trong thực tế phát triển phần mềm, việc thu thập dữ liệu việc làm từ nhiều nền tảng được chia thành **3 mô hình kỹ thuật**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          3 MÔ HÌNH THU THẬP DỮ LIỆU VIỆC LÀM                                │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│ MÔ HÌNH 1: SEED DATABASE     │ MÔ HÌNH 2: BACKGROUND CRAWLER│ MÔ HÌNH 3: AGGREGATOR APIS    │
│ (Phát triển & Prototype)     │ (Thực tế - Tự chủ dữ liệu)   │ (Quy mô thương mại/Toàn cầu)  │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • Dữ liệu việc làm thực tế   │ • Chạy Cronjob định kỳ ngầm  │ • Sử dụng các API có sẵn:     │
│   được cấu trúc hóa trong    │   (mỗi 6 hoặc 12 tiếng).     │   - SerpAPI (Google Jobs API) │
│   PostgreSQL / SQLite.       │ • Dùng Playwright / Scrapy   │   - RapidAPI (JSearch API)    │
│ • Truy vấn siêu tốc (< 5ms). │   quét các mục việc làm mới  │   - LinkedIn Jobs API         │
│ • Không phụ thuộc mạng ngoài.│   và lưu vào PostgreSQL.     │ • Có dữ liệu realtime tức thì │
│ • Chuẩn hóa sẵn dữ liệu.     │ • Ứng viên chat ➔ Tìm trong  │ • Chi phí theo lượt gọi API   │
│                              │   DB nội bộ đã index sẵn.    │   ($10 - $50 / tháng).        │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

### ⚠️ Quy tắc sống còn khi làm tính năng Tìm Việc trong Chat:
> **TUYỆT ĐỐI KHÔNG cào web (scrape) trực tiếp lúc người dùng đang gõ chat!**  
> Vì cào realtime sẽ mất 10 - 20 giây, trang tuyển dụng có thể chặn IP (Cloudflare/Captcha) làm sập luồng chat.  
> **Luồng chuẩn:** Web Crawler chạy ngầm độc lập lưu vào Database ➔ Khi người dùng chat tìm việc, Backend chỉ query trong Database local với tốc độ 5ms!

---

## 🔄 4. LUỒNG HOẠT ĐỘNG HOÀN CHỈNH (END-TO-END DATAFLOW)

```
[1. NGƯỜI DÙNG NHẬP TIN NHẮN TỰ NHIÊN]
"Tìm việc backend 3 năm kinh nghiệm ở Hà Nội" hoặc "Hỏi về cách viết CV"
                  │
                  ▼
[2. BACKEND INTENT CLASSIFIER & PARAM EXTRACTOR]
• Phân tích câu:
  - Intent: `job_search`
  - Domain: `backend`
  - Experience: `3.0` năm
  - Location: `Hà Nội`
                  │
       ┌──────────┴───────────────────────────┐
       ▼ (Nếu là Job Search)                  ▼ (Nếu là Career Advice)
[3A. QUERY LOCAL JOBS DB]             [3B. DIRECT CONTEXT LLM]
• SELECT * FROM jobs                  • System Prompt:
  WHERE domain = 'backend'              "Bạn là Career AI. Ứng viên có profile: {JSON}"
  AND min_exp <= 3.0                  • LLM sinh câu trả lời Markdown ngắn gọn.
  AND location ILIKE '%Hà Nội%'       • Trả về `{ reply: text, jobs: [] }`
• Trả về 4-8 Job Items
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
[4. FRONTEND STREAM RENDERING]
• Hiển thị tin nhắn trả lời.
• Nếu có `jobs`: Hiển thị danh sách thẻ việc làm:
  - Tên công việc & Công ty
  - Số năm kinh nghiệm
  - Link bài đăng gốc
  - Nút [👁️ Xem chi tiết bên trong JD] (Mở Modal xem Mô tả, Yêu cầu, Phúc lợi)
```

---

## ❓ 5. BÀN BẠC & THỐNG NHẤT VỚI BẠN

Từ phân tích kỹ thuật trên:

1. **Về luồng AI:** Bạn có đồng ý áp dụng mô hình **Directed Intent Classifier (Nhanh, Rẻ, Không giật lag)** thay vì cố gắng dùng Framework Multi-Agent cồng kềnh không?
2. **Về RAG:** Chúng ta thống nhất **không dùng Vector DB cho CV** (bơm trực tiếp JSON Profile), giữ hệ thống tinh gọn nhất?
3. **Về nguồn dữ liệu việc làm:** Bạn muốn triển khai trước với **Kho dữ liệu Jobs mẫu thực tế (Seed DB)** hay muốn xây dựng luôn **Worker Crawler cào ngầm định kỳ**?
