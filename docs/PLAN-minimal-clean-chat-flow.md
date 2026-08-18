# 📋 KẾ HOẠCH THIẾT KẾ: KHUNG CHAT AI TINH GỌN (MINIMAL & DIRECT CHAT FLOW)

> **Tài liệu:** `docs/PLAN-minimal-clean-chat-flow.md`  
> **Chế độ:** 📝 **PLANNING ONLY (Không viết code)**  
> **Kiến trúc sư:** `@[project-planner]`  
> **Mục tiêu:** Tinh giản tối đa Cột 2 thành một khung Chat tự nhiên, sạch sẽ, không có các nút gợi ý thừa thãi hay câu hỏi gượng ép.

---

## 🎯 1. NGUYÊN TẮC THIẾT KẾ TINH GỌN (DESIGN PRINCIPLES)

1. **Không Gợi Ý Thừa Thãi (No Cluttered Suggestion Chips):**
   - Loại bỏ hoàn toàn các nút chip gợi ý câu hỏi cố định, các banner gợi ý rườm rà.
   - Giữ giao diện sạch sẽ, tập trung hoàn toàn vào luồng hội thoại tự nhiên giữa người dùng và AI.

2. **Chủ Động Từ Phía Người Dùng (User-Driven Interaction):**
   - Người dùng toàn quyền quyết định khi nào cần chat và gõ nội dung gì.
   - Khi người dùng cần tìm việc: Họ chỉ cần gõ tự nhiên (ví dụ: *"Tìm việc backend"*, *"Tìm việc fullstack 3 năm KN"*...).
   - AI sẽ tự động phân tích câu lệnh, lấy dữ liệu việc làm theo đúng chuyên ngành/số năm kinh nghiệm từ các kênh tuyển dụng và trả về danh sách.

3. **Cấu Trúc Trả Về Rõ Ràng & Trực Quan Khi Tìm Việc:**
   - Mỗi công việc trả về trong chat hiển thị chuẩn xác 4 thông tin cốt lõi mà bạn đã yêu cầu:
     1. **Tên công việc & Công ty**
     2. **Số năm kinh nghiệm yêu cầu**
     3. **Link bài đăng gốc**
     4. **Nút bấm xem thông tin bên trong công việc (`[👁️ Xem chi tiết]` / Modal)**

---

## 🔄 2. LUỒNG TƯƠNG TÁC ĐƠN GIẢN HÓA (SIMPLIFIED USER FLOW)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             GIAO DIỆN CHAT CỘT 2 TINH GỌN                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  [KHUNG HỘI THOẠI TRẮNG / LỊCH SỬ TIN NHẮN SẠCH ĐẸP]                                        │
│                                                                                             │
│  • Người dùng gõ: "Tìm các việc làm backend 2 năm kinh nghiệm"                              │
│                                                                                             │
│  • AI Copilot phản hồi:                                                                     │
│    "Dưới đây là các cơ hội việc làm Backend phù hợp từ ITviec, TopCV, LinkedIn..."          │
│                                                                                             │
│    ┌─────────────────────────────────────────────────────────────────────────────────────┐  │
│    │ 🏢 Senior Backend Engineer (Python/FastAPI) — VNG Corporation                       │  │
│    │ 📅 Kinh nghiệm: 3 - 5 năm kinh nghiệm | 📍 TP. HCM                                   │  │
│    │                                                                                     │  │
│    │ [🔗 Mở bài đăng gốc trên ITviec ↗]            [👁️ Xem chi tiết bên trong JD]       │  │
│    └─────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  • Khi bấm [👁️ Xem chi tiết bên trong JD]:                                                 │
│    ➔ Mở Modal xem toàn bộ: Mô tả công việc, Yêu cầu, Phúc lợi.                              │
│    ➔ Có nút: [🎯 Nạp JD Này Vào Workspace] để chuyển sang Cột 1 khi muốn so khớp.           │
│                                                                                             │
│  [Ô NHẬP LIỆU CHAT DUY NHẤT Ở DƯỚI CÙNG]                                                    │
│  [ Nhập câu hỏi hoặc yêu cầu tìm việc...                                ] [ Gửi ]          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ❓ 3. XÁC NHẬN VỚI BẠN (SOCRATIC GATE)

Bạn có muốn luồng hoạt động chuẩn theo hướng:
1. **Loại bỏ toàn bộ các nút gợi ý, chip câu hỏi cố định và reasoning trace mặc định** để giữ khung chat hoàn toàn sạch sẽ, tối giản.
2. Khi bạn gõ bất kỳ yêu cầu tìm việc nào (hoặc câu hỏi về CV/hướng nghiệp), AI sẽ phản hồi trực tiếp và hiển thị thẻ công việc với: **Tên công việc, Số năm kinh nghiệm, Link gốc và Nút xem chi tiết bên trong**.

Nếu bạn thấy đúng với ý bạn, hãy phản hồi để chúng ta chốt phương án này nhé!
