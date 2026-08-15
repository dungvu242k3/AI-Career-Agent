# Frontend Design System Specification: AI Career Agent

> **Phiên bản:** 1.0.0  
> **Triết lý Thiết kế:** Elite Technical Instrument — Đẳng cấp, Tối giản, Chuyên nghiệp, Tối ưu hóa cho Không gian làm việc AI (AI Workspace).  
> **Cam kết Thẩm mỹ:** Nghiêm cấm bảng màu tím/tím nhạt đại trà (Purple Ban), không dùng Bento Grid rập khuôn; tập trung vào độ tương phản cao, typography tinh tế và micro-interactions sắc nét.

---

## 1. Triết lý Thiết kế & Định danh Thị giác (Visual Identity & Philosophy)

AI Career Agent không phải là một landing page thông thường; đây là một **"Command Center" (Bàn làm việc thông minh)** dành cho ứng viên và kỹ sư phát triển sự nghiệp. Thiết kế phải mang lại cảm giác:
1. **Precision & Trust (Chính xác & Đáng tin cậy):** Đường nét thanh thoát, thông tin phân cấp rõ ràng, số liệu đánh giá (Match Score, Skill Gap) hiển thị trực quan và minh bạch.
2. **Dynamic & Alive (Sống động & Phản hồi liên tục):** Khi AI Agent suy luận và phân tích hồ sơ, giao diện phản hồi theo thời gian thực qua các tín hiệu streaming mượt mà, không giật cục.
3. **Ergonomic Workspace (Tối ưu công thái học):** Bố cục 3 cột (3-Pane) cho phép người dùng quan sát đồng thời Hồ sơ gốc (Source), Cuộc hội thoại điều hướng (AI Agent) và Kết quả phân tích (Insight).

---

## 2. Hệ thống Màu sắc & Semantic Tokens (Color Tokens)

> **Lưu ý nguyên tắc:** Bảng màu chủ đạo sử dụng **Deep Obsidian & Slate Gray** kết hợp với điểm nhấn **Emerald / Mint Green & Electric Cyan** tượng trưng cho sự phát triển nghề nghiệp, độ tin cậy và công nghệ hiện đại.

```text
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│  Background      │  Surface / Card  │  Primary Brand   │  Accent / Active │
│  #090D16         │  #111827         │  #10B981         │  #06B6D4         │
│  (Deep Obsidian) │  (Slate Dark)    │  (Emerald Peak)  │  (Cyan Pulse)    │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

### 2.1. Bảng mã Semantic Tokens

| Token CSS Variable | Dark Mode (Mặc định) | Light Mode | Ý nghĩa sử dụng |
| :--- | :--- | :--- | :--- |
| `--background` | `hsl(222, 47%, 6%)` | `hsl(0, 0%, 98%)` | Màu nền tổng thể toàn bộ ứng dụng |
| `--surface` | `hsl(217, 33%, 11%)` | `hsl(0, 0%, 100%)` | Màu nền thẻ Card, Modal, Panel bên trong |
| `--surface-subtle` | `hsl(215, 28%, 16%)` | `hsl(210, 20%, 96%)` | Vùng nhập liệu, hover background, table row |
| `--border` | `hsl(217, 19%, 24%)` | `hsl(214, 15%, 88%)` | Đường viền ngăn cách các Panel và Component |
| `--border-focus` | `hsl(160, 84%, 39%)` | `hsl(160, 84%, 35%)` | Đường viền khi active / focus vào ô nhập liệu |
| `--foreground` | `hsl(210, 40%, 98%)` | `hsl(222, 47%, 11%)` | Màu chữ chính (Primary Text) |
| `--foreground-muted`| `hsl(215, 20%, 65%)` | `hsl(215, 16%, 47%)` | Màu chữ phụ, nhãn metadata, ghi chú thời gian |
| `--brand-primary` | `hsl(158, 64%, 52%)` | `hsl(158, 64%, 40%)` | Màu thương hiệu chủ đạo: nút CTA, score cao |
| `--brand-cyan` | `hsl(189, 94%, 43%)` | `hsl(189, 94%, 38%)` | Tín hiệu AI Agent đang xử lý, badge công nghệ |
| `--warning` | `hsl(38, 92%, 50%)` | `hsl(38, 92%, 45%)` | Cảnh báo Skill Gap cần bổ sung, hạn nộp hồ sơ |
| `--destructive` | `hsl(0, 84%, 60%)` | `hsl(0, 72%, 51%)` | Điểm không phù hợp, cảnh báo đỏ, nút hủy bỏ |

---

## 3. Hệ thống Typography (Typography Scale & Font Pairing)

- **Font chữ chính (Sans-serif):** `Inter` hoặc `Plus Jakarta Sans` — Đảm bảo tính trung tính, dễ đọc ở kích thước chữ nhỏ trong bảng biểu và danh sách kỹ năng.
- **Font chữ kỹ thuật (Monospace):** `JetBrains Mono` — Dùng cho điểm số phần trăm, terminal log của Agent, code block và diff view so sánh CV.

```text
Display-1:  36px / 44px (Bold - 700)      --> Tiêu đề Hero, Trang Dashboard
Heading-1:  28px / 36px (SemiBold - 600)  --> Tiêu đề Bounded Context (Career Workspace)
Heading-2:  20px / 28px (SemiBold - 600)  --> Tiêu đề Panel (Source, Insight, Job Detail)
Heading-3:  16px / 24px (Medium - 500)    --> Tên Module, Card Header
Body-Base:  14px / 22px (Regular - 400)   --> Nội dung đoạn văn bản, Chat message
Body-Small: 12px / 18px (Regular - 400)   --> Metadata, Thời gian, Badge nhãn
Mono-Data:  13px / 18px (Medium - 500)    --> Match Score (87%), ATS Score, Token stream
```

---

## 4. Kiến trúc Bố cục 3-Pane của Career Workspace (Responsive Layout)

Màn hình **Career Workspace (`fe/app/(app)/workspace`)** là tâm điểm của toàn bộ trải nghiệm người dùng, được phân bố linh hoạt theo thiết bị:

### 4.1. Desktop Layout (Màn hình $\ge 1280\text{px}$)
Cố định 3 cột làm việc đồng thời, không cần đóng mở modal:

```text
┌──────────────────────┬──────────────────────────────────────────┬────────────────────────┐
│  1. Source Panel     │  2. AI Agent Workspace (Main Panel)      │  3. Insight Panel      │
│  (Width: 260px)      │  (Flex-1, Scrollable)                    │  (Width: 340px)        │
├──────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ • CV Đã chọn         │ • Header: Chế độ làm việc (Match/Mock)   │ • Radar Skill Gap      │
│ • JD Mục tiêu        │ • Dòng thời gian hội thoại Agent         │ • Điểm tương thích ATS │
│ • Bộ lọc kỹ năng     │ • Stream bước suy luận (Real-time Steps) │ • Lộ trình đề xuất     │
│ • Nút tải thêm nguồn │ • Hộp nhập lệnh prompt điều hướng        │ • Nút Tối ưu hóa CV    │
└──────────────────────┴──────────────────────────────────────────┴────────────────────────┘
```

### 4.2. Tablet Layout ($768\text{px} \le \text{Width} < 1280\text{px}$)
- Cột **Source Panel** thu gọn thành thanh công cụ icon dọc (60px) hoặc Drawer trượt từ bên trái.
- Cột **Main Workspace** chiếm trọn diện tích trung tâm.
- Cột **Insight Panel** trượt ra từ bên phải dạng Sheet/Drawer khi người dùng bấm vào chỉ số Quick Score.

### 4.3. Mobile Layout ($\text{Width} < 768\text{px}$)
- Header cố định hiển thị Tên vị trí & Điểm số tóm tắt.
- Toàn màn hình ưu tiên cho **Main Agent Chat**.
- Bottom Navigation Bar cung cấp 3 Tab Switcher: `[Nguồn hồ sơ]`, `[AI Chat]`, `[Báo cáo phân tích]`.

---

## 5. Danh mục Thành phần Giao diện (Component Taxonomy)

### 5.1. UI Primitives (`fe/shared/components/ui/`)
- `Button`: Hỗ trợ các biến thể: `primary` (Emerald), `secondary` (Slate Surface), `outline` (Thin border), `ghost`, `destructive`. Có sẵn trạng thái `isLoading` kèm Spinner.
- `Card`: Bọc viền 1px (`border-slate-800`), hiệu ứng chuyển màu viền nhẹ khi hover.
- `Badge`: Thẻ hiển thị kỹ năng và mức độ phù hợp (`High Match`, `Missing Skill`, `Required`).
- `Drawer` & `Modal`: Dựa trên Radix Dialog, hỗ trợ trap focus và animation trượt mượt mà.
- `FileUploader`: Kéo thả file PDF/DOCX, hiển thị thanh tiến độ upload và validate dung lượng client-side.
- `Skeleton`: Hiệu ứng sóng mờ (shimmer effect) màu Slate để tải trước giao diện.

### 5.2. Domain Micro-Components (`fe/entities/*/components/`)
- `MatchScoreGauge`: Vòng tròn đo % tương thích kỹ năng với hiệu ứng quét sáng khi AI tính toán xong.
- `SkillGapMatrix`: Biểu đồ trực quan so sánh: *Kỹ năng ứng viên có* vs *Kỹ năng JD yêu cầu*.
- `JobCardMeta`: Khối tóm tắt thông tin công việc (Mức lương, Địa điểm, Remote, Hạn nộp).
- `DiffView`: Khối so sánh từng dòng văn bản CV trước và sau khi được Agent tối ưu hóa.

### 5.3. Agent Interactive Components (`fe/features/career-workspace/components/`)
- `AgentThinkingIndicator`: Hiển thị nhịp đập pulse và tên Agent đang kích hoạt (e.g. `⚡ JD Analyzer Agent is reading requirements...`).
- `StepExecutionList`: Danh sách các bước kiểm tra (Checklist) với icon trạng thái chuyển đổi từ `⟳ Pending` $\to$ `✓ Completed`.
- `StreamMessage`: Hiệu ứng Typewriter hiển thị câu trả lời từng token của AI kèm con trỏ nhấp nháy.

---

## 6. Tiêu chuẩn Animation & Micro-interactions (Motion Guidelines)

Tất cả chuyển động giao diện phải tinh tế, thời gian phản hồi ngắn để không gây cảm giác chậm trễ:

1. **Thời lượng chuẩn (Durations):**
   - Micro-hover (Button, Card border): `150ms ease-out`
   - Modal/Drawer trượt mở: `250ms cubic-bezier(0.16, 1, 0.3, 1)`
   - AI Typing Stream: `20ms` per token stream chunk
2. **Hiệu ứng AI Pulse:**
   - Sử dụng hiệu ứng `pulse` nhẹ với ánh sáng cyan `hsl(189, 94%, 43% / 0.15)` bao quanh avatar của Agent khi đang phân tích.
3. **Hiệu ứng Hoàn thành (Success Celebration):**
   - Khi tạo CV tối ưu hoặc hoàn thành bài Mock Interview, điểm số Match Score tăng dần dạng counter từ 0% đến điểm thực tế trong `800ms`.

---

## 7. Bảng Kiểm Tra Tuân Thủ Thiết Kế (Design Quality Checklist)

Trước khi nghiệm thu bất kỳ màn hình nào:
- [ ] **No Generic Purple:** Tuyệt đối không dùng gradient tím mặc định.
- [ ] **High Contrast Text:** Đảm bảo tỷ lệ tương phản chữ đạt tối thiểu WCAG AA (4.5:1 cho văn bản thường).
- [ ] **Responsive Tested:** Giao diện co giãn chuẩn xác trên cả 3 mốc (360px Mobile, 1024px Tablet, 1440px Desktop).
- [ ] **State Integrity:** Đã chuẩn bị đầy đủ 4 trạng thái: *Empty*, *Loading (Skeleton)*, *Streaming Active*, và *Error Fallback*.
- [ ] **No Layout Shifts (CLS):** Các khung hiển thị điểm số và chat luôn có `min-height` cố định để không bị giật trang khi dữ liệu đổ về.
