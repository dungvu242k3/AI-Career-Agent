# 📋 KẾ HOẠCH CHI TIẾT TỪNG BƯỚC: LUỒNG HOẠT ĐỘNG & KIẾN TRÚC HỆ THỐNG (STEP-BY-STEP ARCHITECTURE PLAN)

> **Tài liệu:** `docs/PLAN-step-by-step-architecture-flow.md`  
> **Chế độ:** 📝 **PLANNING & DISCUSSION ONLY (Bàn bạc & Trình bày luồng, KHÔNG viết code)**  
> **Mục tiêu:** Trình bày chi tiết từng bước hoạt động của luồng dữ liệu, cách các thành phần AI phối hợp với nhau, để bạn xem xét và xác nhận trước khi thực hiện.

---

## 🏛️ 1. TỔNG QUAN MÔ HÌNH 3 CỘT (WORKSPACE STUDIO ARCHITECTURE)

```
┌──────────────────────────────┬──────────────────────────────┬───────────────────────────────┐
│     CỘT 1: ĐẦU VÀO           │    CỘT 2: ĐIỀU PHỐI AI       │    CỘT 3: SẢN PHẨM ĐẦU RA     │
│   (Context & Truth Source)   │    (Interactive Copilot)     │    (Artifacts & Verified CV)  │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ • Tải lên CV (PDF/Docx)      │ • Chat tự nhiên với Copilot  │ • Bản xem trước CV Harvard    │
│ • Bóc tách Canonical Profile │ • Tìm việc theo Domain & Exp │ • Báo cáo Thẩm định Critic    │
│ • Dán JD hoặc Nạp từ Cột 2   │ • Tư vấn chiến lược ứng tuyển│ • Xuất PDF chuẩn Harvard      │
│ • Chấm điểm ATS 50/30/20     │ • Đồng biên tập câu STAR     │ • May đo Cover Letter         │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

---

## 🔄 2. CHI TIẾT 4 BƯỚC TRONG LUỒNG HOẠT ĐỘNG (END-TO-END FLOW)

### 📍 BƯỚC 1: Nạp CV & Phân Tích Hồ Sơ (Ingestion & Extraction)
1. **Người dùng:** Kéo thả tệp CV (PDF/Docx) vào Cột 1.
2. **Hệ thống AI xử lý:**
   - Trích xuất văn bản và bóc tách cấu trúc 7 phần bằng Pydantic Schema (`CandidateProfile`).
   - Tự động nhận diện Chuyên ngành (`Backend`, `Frontend`, `Fullstack`, `DevOps`...) và tính Số năm kinh nghiệm thực tế.
3. **Hiển thị:** Cột 1 hiển thị thẻ tóm tắt hồ sơ ứng viên; Cột 2 sẵn sàng tiếp nhận câu hỏi.

---

### 📍 BƯỚC 2: Tìm Việc Đa Kênh Theo Chuyên Ngành & Kinh Nghiệm (Job Discovery)
1. **Người dùng:** Gõ vào ô chat ở Cột 2 (ví dụ: *"Tìm việc backend 3 năm kinh nghiệm"*).
2. **Backend xử lý:**
   - **Intent Classifier:** Nhận diện ý định `job_search`, trích xuất `domain='backend'`, `exp=3.0`.
   - **Query Database:** Lọc danh sách việc làm phù hợp từ các kênh (ITviec, TopCV, VietnamWorks, LinkedIn) với tốc độ < 5ms.
3. **Hiển thị trong Chat Cột 2:**
   - Danh sách thẻ việc làm hiển thị rõ:
     - 🏢 **Tên vị trí & Công ty**
     - 📅 **Số năm kinh nghiệm yêu cầu**
     - 🔗 **Link bài đăng tuyển dụng gốc**
     - 👁️ **Nút `[Xem chi tiết]`**: Bấm mở Modal xem toàn bộ Mô tả, Yêu cầu, Phúc lợi.
     - 🎯 **Nút `[Nạp JD này vào Workspace]`**: 1-chạm đẩy thẳng toàn bộ JD sang Cột 1 để so khớp.

---

### 📍 BƯỚC 3: So Khớp ATS & May Đo CV Chuẩn Harvard với Critic-Actor Loop (Tailoring & Verification)
1. **So khớp ATS (Cột 1):**
   - Khi có JD (dán vào hoặc nạp từ việc làm ở Bước 2), hệ thống tính điểm ATS theo công thức **50% Kỹ năng + 30% Kinh nghiệm + 20% Định dạng**.
   - Hiển thị danh sách kỹ năng: 🟢 Khớp chính xác, 🟡 Tương đương, 🔴 Còn thiếu.
2. **May đo CV chuẩn Harvard (Cột 3):**
   - Người dùng bấm nút **`[🎯 May Đo CV Chuẩn Harvard]`**.
   - **Luồng AI Nâng Cao (Critic-Actor Reflection Loop):**
     - **Vòng 1 (Actor Agent):** Tạo bản nháp CV Harvard tối ưu theo JD.
     - **Vòng Thẩm định (Critic Agent):** Soi xét 4 tiêu chí: Có đủ số liệu %/đo lường không? Có bịa đặt kỹ năng không? Đạt chuẩn từ khóa chưa? Có dùng Harvard Action Verbs không?
     - **Vòng Tự Sửa (Reflector Loop):** Tự động sửa chữa các điểm yếu cho đến khi đạt điểm ≥ 90/100.
   - **Hiển thị ở Cột 3:**
     - Bản CV Harvard xem trước sống động.
     - Huy hiệu bảo chứng: `🛡️ Critic Agent Verified: 94/100 (0% Hallucination)`.
     - Nút tải PDF chuẩn Harvard.

---

### 📍 BƯỚC 4: Luyện Phỏng Vấn Giả Lập Đa Tác Tử (Adversarial Mock Interview)
1. **Người dùng:** Chuyển sang tab **`/interview`** (Phỏng vấn AI).
2. **Hệ thống khởi tạo Phòng phỏng vấn với 2 AI:**
   - **Tech Lead AI:** Đặt các câu hỏi kỹ thuật hóc búa, đào sâu vào các điểm yếu giữa CV và JD.
   - **HR Manager AI:** Đặt câu hỏi về xử lý xung đột, văn hóa nhóm và phương pháp STAR.
   - **Trọng tài AI (Silent Judge):** Lắng nghe câu trả lời, chấm điểm logic, độ tự tin và xuất Báo cáo đánh giá năng lực toàn diện.

---

## 📋 3. BẢNG PHÂN CHIA KẾ HOẠCH THỰC HIỆN TỪNG PHẦN (EXECUTION BREAKDOWN)

| Giai đoạn | Nội dung công việc | Đầu ra mong đợi |
|---|---|---|
| **GIAI ĐOẠN 1** | **Xây dựng Động cơ Critic-Actor Reflection Loop**<br>• `critic_agent.py`: Bộ thẩm định 4 chiều (Metrics, Grounding, ATS, Verbs).<br>• `reflective_synthesizer.py`: Vòng lặp tự phản biện khép kín.<br>• Kiểm thử 100% tỷ lệ pass. | CV may đo tự động đạt 90-95+ điểm, loại bỏ 100% lỗi bịa đặt kinh nghiệm. |
| **GIAI ĐOẠN 2** | **Hoàn thiện Cột 2 Chat Copilot Tinh Gọn & Tìm Việc Đa Kênh**<br>• Chat UI sạch sẽ, không nút gợi ý rườm rà.<br>• Lọc việc làm theo domain và số năm KN.<br>• Modal xem chi tiết JD & Nút nạp JD vào Cột 1. | Khung chat mượt mà, trực quan, xem được đầy đủ chi tiết công việc từ các sàn tuyển dụng. |
| **GIAI ĐOẠN 3** | **Xây dựng Hybrid Vector Search & Re-ranking**<br>• Nhúng Vector Embeddings 1536 chiều cho Job & Profile.<br>• Kết hợp BM25 + Vector Cosine + Cross-Encoder Reranker. | Tìm việc theo ngữ nghĩa sâu, hiển thị % tương thích văn hóa & tech stack. |
| **GIAI ĐOẠN 4** | **Xây dựng Phòng Phỏng Vấn Đa Tác Tử (`/interview`)**<br>• Tech Lead Agent + HR Agent + Judge Agent.<br>• Live Transcript, tính thời gian, chấm điểm real-time. | Phòng phỏng vấn giả lập sống động, chuẩn bị kỹ lưỡng trước khi đi phỏng vấn thật. |

---

## ❓ 4. CÂU HỎI XÁC NHẬN HƯỚNG ĐI CÙNG BẠN (SOCRATIC CONFIRMATION)

1. **Về luồng tương tác:** Bạn thấy 4 bước từ **Nạp CV ➔ Tìm việc & Chat ➔ May đo CV có Critic kiểm định ➔ Phỏng vấn giả lập** như trên đã hoàn toàn mạch lạc và đúng ý bạn chưa?
2. **Về lộ trình chia nhỏ:** Bạn có muốn chúng ta chốt bản kế hoạch này và bắt đầu triển khai lần lượt từ **Giai đoạn 1** trước không?
