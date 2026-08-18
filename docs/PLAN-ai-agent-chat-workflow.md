# 🧠 KẾ HOẠCH THIẾT KẾ KIẾN TRÚC AI AGENT CHO CỘT 2 (WORKSPACE COPILOT)

> **Tài liệu:** `docs/PLAN-ai-agent-chat-workflow.md`  
> **Chế độ:** 📝 **PLANNING & DISCUSSION ONLY (Bàn bạc kiến trúc, KHÔNG viết code)**  
> **Phương pháp luận:** AI Agent Architecture (`ai-agent-development` workflow)  
> **Mục tiêu:** Định hình chính xác bản chất, vòng đời, trạng thái (State Machine) và cách AI Agent tương tác giữa Cột 1 (Dữ liệu đầu vào) và Cột 3 (Sản phẩm đầu ra).

---

## 🎯 1. VẤN ĐỀ CỦA LUỒNG CHAT TRUYỀN THỐNG & ĐỊNH NGHĨA LẠI AI AGENT

### ❌ Vấn đề nếu chỉ là "Chatbox thông thường":
- Người dùng không biết phải gõ gì (Cold Start problem).
- Chatbox hoạt động rời rạc, không tác động trực tiếp vào sản phẩm ở Cột 1 và Cột 3.
- Trả về thông tin chung chung, không có tính hành động (Actionable Output).

### ✅ Định nghĩa AI Agent Cột 2 theo chuẩn `ai-agent-development`:
AI Agent ở Cột 2 **không phải là chatbot thụ động**, mà là một **Autonomous Career Orchestrator (Trọng tài & Trợ lý hành động chủ động)**:
- **Nắm giữ State (Trạng thái toàn cục):** Biết ứng viên đang ở bước nào (Vừa tải CV? Đang chọn JD? Đã có điểm ATS? Hay đang chuẩn bị nộp đơn?).
- **Human-in-the-loop:** Hỏi ứng viên để lấy thêm dữ kiện còn thiếu ➔ Tạo ra Artifacts (Bản may đo CV, Cover Letter, Danh sách việc làm) ➔ Chờ ứng viên bấm xác nhận để cập nhật sang Cột 3.
- **Tool Calling (Tích hợp công cụ):** Tự động gọi các công cụ nội bộ: `job_scanner`, `ats_analyzer`, `star_generator`, `cv_patcher`.

---

## 🔄 2. SƠ ĐỒ LUỒNG HOẠT ĐỘNG TOÀN CẢNH (STATE MACHINE & AGENT LOOPS)

```
                     ┌─────────────────────────────────────────────────────────┐
                     │           ỨNG VIÊN TẢI CV LÊN (CỘT 1)                   │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        AGENT STATE 1: ONBOARDING & CAREER PROFILE AUDIT                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Agent chào hỏi, tóm tắt Profile (Domain, Số năm KN, Điểm mạnh nhất).                                │
│ • Chủ động đưa ra 2 hướng hành động lớn:                                                               │
│   ├── [A. Tôi đã có JD cụ thể, muốn tối ưu CV ngay] ➔ Chuyển sang STATE 2 (ATS Optimizer)             │
│   └── [B. Tôi muốn quét thị trường tìm việc phù hợp] ➔ Chuyển sang STATE 3 (Job Discovery)           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                       │                                                  │
         Chọn Hướng A  │                                    Chọn Hướng B  │
                       ▼                                                  ▼
┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────────────┐
│  AGENT STATE 2: ATS GAP SOLVER & CO-EDITOR   │  │    AGENT STATE 3: MARKET JOB DISCOVERY AGENT         │
├──────────────────────────────────────────────┤  ├──────────────────────────────────────────────────────┤
│ 1. Agent đọc điểm ATS & lỗ hổng (Kỹ năng đỏ) │  │ 1. Agent quét các kênh (ITviec, TopCV, LinkedIn)     │
│ 2. Agent chủ động phỏng vấn ngắn ứng viên:   │  │ 2. Lọc theo: Chuyên ngành + Số năm kinh nghiệm       │
│    "JD yêu cầu Kafka nhưng CV chưa có. Bạn   │  │ 3. Hiển thị Job Cards + Nút [Xem chi tiết JD]        │
│     từng dùng message queue bao giờ chưa?"   │  │ 4. Bấm [🎯 Chọn Job Này Để Ứng Tuyển]                │
│ 3. Ứng viên gõ trả lời ngắn                  │  │    ➔ Agent tự động chuyển sang STATE 2 với JD đó!    │
│ 4. Agent sinh câu STAR chuẩn & hỏi:          │  └──────────────────────────────────────────────────────┘
│    "Tôi đã soạn câu STAR này, chèn vào CV?"  │
│ 5. Bấm [Đồng ý] ➔ Cập nhật thẳng sang Cột 3! │
└──────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        AGENT STATE 4: APPLICATION PACK GENERATION (VŨ KHÍ ỨNG TUYỂN)                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Khi CV ở Cột 3 đã đạt 90+ điểm:                                                                      │
│ • Agent đề xuất tạo bộ tài liệu đi kèm:                                                                │
│   1. Thư ứng tuyển (Cover Letter) 150 chữ gửi Hiring Manager.                                          │
│   2. Tin nhắn kết nối ngắn trên LinkedIn (Cold Outreach).                                              │
│   3. Thẩm định mức lương (Salary Benchmark) nên deal cho vị trí này.                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. CHI TIẾT 4 CHẾ ĐỘ HOẠT ĐỘNG CỦA AGENT (AGENT CAPABILITIES)

### 📌 Chế độ 1: Cố Vấn Khởi Động & Định Vị Hồ Sơ (Profile Onboarding)
* **Kích hoạt:** Khi người dùng vừa mở trang hoặc vừa tải CV lên.
* **Hành vi Agent:**
  - Nhận diện: Chuyên ngành (Domain), Cấp bậc (Junior/Mid/Senior), Điểm mạnh nổi bật.
  - Đưa ra các gợi ý rõ ràng thay vì để khung chat trống.

### 📌 Chế độ 2: Trinh Sát & Săn Việc Đa Nền Tảng (Job Discovery & Exploration)
* **Kích hoạt:** Khi người dùng hỏi tìm việc hoặc bấm nút tìm việc.
* **Hành vi Agent:**
  - Lấy các việc làm từ ITviec, TopCV, VietnamWorks, LinkedIn tương ứng với chuyên ngành và số năm kinh nghiệm.
  - Hiển thị danh thiếp công việc với: Tên vị trí, Công ty, Mức lương, Địa điểm, Link gốc và Nút xem chi tiết bên trong.
  - **Hành động cốt lõi:** Khi người dùng chọn 1 công việc ➔ Agent tự động biến JD đó thành mục tiêu và dẫn dắt sang Chế độ 3 (Vá lỗi CV cho JD đó).

### 📌 Chế độ 3: Đồng Tác Giả Tối Ưu CV & Vá Lỗ Hổng Kỹ Năng (Interactive CV Co-Editor)
* **Kích hoạt:** Khi đã có JD (dán vào hoặc chọn từ tìm việc).
* **Hành vi Agent:**
  - Phân tích điểm yếu (Ví dụ: Thiếu số liệu định lượng, thiếu từ khóa công nghệ).
  - Đặt câu hỏi phỏng vấn gợi mở để khai thác kinh nghiệm ẩn của ứng viên.
  - Viết lại câu đạn STAR và cập nhật thẳng vào bản CV bên Cột 3 khi người dùng duyệt.

### 📌 Chế độ 4: Soạn Thảo Vũ Khí Ứng Tuyển (Application Pack Generator)
* **Kích hoạt:** Sau khi CV đã tối ưu hoàn chỉnh.
* **Hành vi Agent:**
  - Tự động sinh Cover Letter cá nhân hóa cho công ty đó.
  - Sinh tin nhắn mở lời LinkedIn / Email gửi HR.
  - Tư vấn dải lương thị trường và bí quyết phỏng vấn câu hỏi khó của vị trí đó.

---

## ❓ 4. CÁC CÂU HỎI THẢO LUẬN VỚI BẠN (SOCRATIC DISCUSSION)

Để chúng ta thống nhất 100% về mặt thiết kế trước khi bắt tay vào triển khai:

1. **Về luồng khởi đầu (Entry Point):** Bạn có muốn khi người dùng vừa vào Workspace, Agent sẽ **chủ động hỏi 1 câu ngắn gọn định hướng** (Ví dụ: *"Chào bạn! Hôm nay bạn muốn tìm việc mới hay tối ưu CV cho 1 JD có sẵn?"*) không?
2. **Về tính tương tác 2 chiều (Co-editing Loop):** Khi người dùng xem danh sách việc làm và bấm chọn 1 việc, bạn có muốn Agent **tự động phân tích ngay những điểm CV hiện tại đang thiếu so với việc đó và cùng người dùng sửa luôn** không?
3. **Về các nút bấm nhanh (Prompt Action Chips):** Bạn muốn các nút bấm nhanh hiển thị cố định theo từng giai đoạn (Contextual Buttons) hay người dùng chủ yếu gõ câu hỏi tự do?
