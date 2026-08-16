# 🟢 Prompt Landing Page — CareerPilot AI (v2.2 — Khớp 100% Tính Năng Dự Án & Menu Trực Quan)

> **Mục đích:** Nạp vào Google Stitch hoặc AI Designer để sinh giao diện Landing Page chuẩn chỉ, hiển thị trực tiếp các tính năng thực tế có trong codebase.
> **Ngôn ngữ hiển thị:** Toàn bộ bằng Tiếng Việt (trừ thuật ngữ kỹ thuật quốc tế).

---

## 📋 Full Prompt Copy-Paste (Dán vào Stitch)

```text
Design a world-class, production-grade Vietnamese Landing Page for "CareerPilot AI" — an all-in-one AI career assistant and workspace engineered for Vietnamese software engineers, IT students, and job seekers.

All visible UI text on the page MUST be in Vietnamese. Technical terms (ATS, JD, STAR, API, Docker, FastAPI, React, etc.) remain in standard English.

═══════════════════════════════════════════════════════
1. DESIGN SYSTEM & VISUAL IDENTITY
═══════════════════════════════════════════════════════

Aesthetic: "Modern Technical Precision" — inspired by Linear, Raycast, and Stripe.
A clean, focused developer-tool instrument with sharp 1px borders, high contrast, zero clutter, and mathematically balanced spacing.

Color Palette (Dark Mode):
- Background: #090D16 (Deep Obsidian Canvas — NOT pure black #000000)
- Card / Panel Surface: #111827 (Slate 900)
- Structural Borders: 1px solid #1E293B (Slate 800)
- Interactive Hover Border: 1px solid #10B981 (Emerald transition, 150ms ease)
- Primary Action CTA: #10B981 (Emerald Peak — career advancement)
- Secondary Accent: #06B6D4 (Electric Cyan — data highlights)
- Warning / Skill Gap: #F59E0B (Warm Amber — missing qualifications)
- Primary Text: #F8FAFC (Slate 50 — high contrast)
- Secondary / Muted Text: #94A3B8 (Slate 400)

Typography:
- Headlines & Titles: "Plus Jakarta Sans" (Weight 700 / 600)
- Body & Descriptions: "Inter" (Weight 400 / 500)
- Data Metrics, Scores, Code & Match Rates: "JetBrains Mono" (Weight 500 / 600)

Anti-Patterns (Strictly Avoid):
- ❌ NO "system online" / "engine online" pulsing dots or badges in the navbar or hero.
- ❌ NO purple or violet gradient backgrounds.
- ❌ NO floating blurry 3D blobs, mesh aurora, or noisy particles.
- ❌ NO generic emoji icons (use crisp Lucide SVG icons).
- ❌ NO generic 4-card equal bento grid clichés.
- ❌ NO stock photos of generic people smiling at laptops.

═══════════════════════════════════════════════════════
2. NAVBAR MENU (KHỚP CHÍNH XÁC CÁC MODULE TRONG PROJECT)
═══════════════════════════════════════════════════════

SECTION 1: FIXED HEADER & FEATURE NAVIGATION
- Sticky top with 85% opacity backdrop blur (rgba(9, 13, 22, 0.85)) and 1px bottom border (#1E293B).
- Left: Clean Logo mark with Emerald terminal accent + Bold text "CareerPilot AI" (NO online status indicator).
- Center Navigation Links (Directly reflecting the 6 core functional modules of the system):
  1. "Phân tích CV" (Scroll/Link to CV Analysis & Optimization)
  2. "Tìm việc & So khớp" (Scroll/Link to Job Search & Matcher)
  3. "Phỏng vấn AI" (Scroll/Link to Mock Interview Arena)
  4. "Lộ trình kỹ năng" (Scroll/Link to Skill Gap Roadmap)
  5. "Quản lý ứng tuyển" (Scroll/Link to Application Tracker)
  6. "Bảng giá" (Scroll/Link to Pricing)
- Right Actions:
  • "Đăng nhập" (Ghost text button, Slate-300)
  • "Bắt đầu miễn phí" (Solid Emerald button #10B981, text #090D16, rounded-md)

═══════════════════════════════════════════════════════
3. PAGE SECTIONS (DẪN DẮT TOÀN DIỆN CÁC TÍNH NĂNG)
═══════════════════════════════════════════════════════

───────────────────────────────────────────────────────
SECTION 2: HERO SECTION WITH LIVE CV ANALYSIS INSTRUMENT
───────────────────────────────────────────────────────
Layout: 2-Column Desktop (Left 52% Value Proposition, Right 48% Live Instrument Card).

Left Column:
- Top Badge: Emerald border pill "TRỢ LÝ NGHỀ NGHIỆP AI TOÀN DIỆN"
- Main Headline (Large, bold):
  "Từ CV chưa tối ưu đến Offer Letter — AI đồng hành cùng bạn."
- Subtitle:
  "Phân tích CV chuẩn ATS, so khớp việc làm theo thời gian thực, luyện phỏng vấn kỹ thuật và kiến tạo lộ trình học tập cá nhân hóa — tất cả trong một nền tảng."
- Dual CTA Buttons:
  • Primary: "Phân tích CV miễn phí →" (Large Emerald button)
  • Secondary: "Trải nghiệm Workspace" (Slate-800 button with 1px border)
- Trust line: "✓ Miễn phí cho sinh viên • ✓ Không yêu cầu thẻ tín dụng • ✓ Có kết quả sau 3 phút"

Right Column (Interactive Analysis Card):
- Dark panel (#111827) with 1px border (#1E293B) and subtle Cyan top-border.
- Top Header: "Senior_Backend_Engineer_CV.pdf" + Badge "Đã phân tích xong ✓"
- Center Gauge: Circular radial score displaying "94%" in Emerald (#10B981) with label "Độ tương thích ATS".
- Skill Taxonomy Badges:
  • Khớp yêu cầu (Green): "FastAPI (95%)", "PostgreSQL (90%)", "Docker (88%)"
  • Cần bổ sung (Amber): "Kubernetes (Thiếu kinh nghiệm)", "Distributed Tracing"
- Quick Action Button inside Card: "Tối ưu hóa nội dung CV ngay →"

───────────────────────────────────────────────────────
SECTION 3: TRUST METRICS & TECH STACK TICKER
───────────────────────────────────────────────────────
- Full-width dark bar (#0B1120) with 1px top/bottom borders.
- 4 Key Metrics (JetBrains Mono font, Emerald bold):
  • "500+" — CV và hồ sơ kỹ sư đã được chuẩn hóa
  • "94.2%" — Tỷ lệ vượt qua vòng lọc hồ sơ ATS
  • "< 3 phút" — Thời gian bóc tách & phân tích toàn diện
  • "100%" — Miễn phí các tính năng cốt lõi cho sinh viên
- Tech Stack Support Badges (Subtle grayscale): Python, React, Java, Go, NodeJS, Docker, AWS, PostgreSQL.

───────────────────────────────────────────────────────
SECTION 4: "DÀNH CHO AI?" — 3 PERSONA CARDS
───────────────────────────────────────────────────────
- Heading: "Được thiết kế cho từng giai đoạn sự nghiệp"
- Subheading: "Dù bạn đang chuẩn bị ra trường hay hướng tới vị trí Tech Lead, CareerPilot AI luôn có công cụ phù hợp."
- 3 Interactive Cards with Lucide SVG icons:
  1. Card "Sinh viên IT sắp tốt nghiệp":
     - Icon: Graduation SVG
     - Vấn đề: "Chưa biết viết CV ra sao, thiếu dự án thực tế và sợ rớt vòng lọc hồ sơ."
     - Giải pháp: "Bóc tách kỹ năng, chuẩn hóa định dạng ATS và gợi ý công việc Fresher phù hợp."
  2. Card "Fresher & Junior đang tìm việc":
     - Icon: Code2 SVG
     - Vấn đề: "Rải hàng chục CV không có phản hồi, lúng túng khi phỏng vấn kỹ thuật."
     - Giải pháp: "Tối ưu hóa từ khóa theo từng JD, luyện phỏng vấn giả lập không giới hạn với AI."
  3. Card "Mid & Senior muốn bứt phá":
     - Icon: TrendingUp SVG
     - Vấn đề: "Muốn nhảy việc với mức lương cao hơn nhưng chưa rõ khoảng trống kiến trúc."
     - Giải pháp: "Bản đồ Skill Gap chuyên sâu, chỉ ra chính xác công nghệ cần bổ sung trong 30 ngày."

───────────────────────────────────────────────────────
SECTION 5: QUY TRÌNH 3 BƯỚC KHÉP KÍN
───────────────────────────────────────────────────────
- Heading: "Cách thức hoạt động"
- Subheading: "3 bước đơn giản để biến hồ sơ của bạn thành ứng viên sáng giá nhất"
- 3 Steps connected with an emerald directional line:
  • Bước 01: [Upload CV] Kéo thả PDF/DOCX — AI tự động trích xuất kỹ năng, kinh nghiệm và dự án trong 5 giây.
  • Bước 02: [AI Deep Scan & Match] Đối chiếu với ma trận yêu cầu tuyển dụng, tính điểm ATS và phát hiện lỗ hổng kỹ năng.
  • Bước 03: [Hành động & Phỏng vấn] Nhận bản CV tối ưu, luyện mock interview tình huống và bắt đầu học theo lộ trình đề xuất.

───────────────────────────────────────────────────────
SECTION 6: CHI TIẾT 6 TÍNH NĂNG CỐT LÕI TRONG PROJECT
───────────────────────────────────────────────────────
- Heading: "Hệ sinh thái tính năng hoàn chỉnh"
- Subheading: "Mọi công cụ cần thiết để quản lý toàn diện hành trình nghề nghiệp IT của bạn"

- 6 Feature Cards (Grid 3x2 hoặc Asymmetric Grid):
  1. [cv-analysis & optimization] "Phân tích & Tối ưu CV chuẩn ATS":
     - Tag: "CV OPTIMIZER"
     - Description: "Phân tích câu chữ theo mô hình STAR, kiểm tra độ tương thích ATS, đề xuất sửa từng dòng với Diff View trực quan."
  2. [job-search & job-matching] "Tìm việc & So khớp JD thông minh":
     - Tag: "JOB MATCHER"
     - Description: "Thuật toán AI đối chiếu hồ sơ với hàng trăm tin tuyển dụng, hiển thị chính xác % Match Score và ma trận kỹ năng thiếu."
  3. [interview] "Đấu trường Phỏng vấn giả lập AI (Mock Arena)":
     - Tag: "MOCK INTERVIEW"
     - Description: "Luyện phỏng vấn System Design và Coding theo tình huống thực tế của JD, nhận phản hồi tức thì về từ khóa và độ mạch lạc."
  4. [learning] "Lộ trình bù đắp kỹ năng (Skill Gap Roadmap)":
     - Tag: "SKILL ROADMAP"
     - Description: "Tự động biến các kỹ năng còn thiếu thành kế hoạch học tập 2-4 tuần với tài liệu và bài tập thực hành được chọn lọc."
  5. [applications] "Quản lý & Theo dõi ứng tuyển (Kanban Tracker)":
     - Tag: "APPLICATION TRACKER"
     - Description: "Bảng Kanban theo dõi trạng thái từng hồ sơ (Đã nộp, Đang phỏng vấn, Đã nhận Offer), nhắc lịch và lưu trữ ghi chú phỏng vấn."
  6. [career-workspace] "Không gian làm việc tập trung (AI Workspace)":
     - Tag: "3-PANE WORKSPACE"
     - Description: "Bàn làm việc 3 cột chuẩn công thái học: Nguồn hồ sơ bên trái, Hội thoại Agent ở giữa, Dữ liệu phân tích bên phải."

───────────────────────────────────────────────────────
SECTION 7: PRODUCT SHOWCASE — TRẢI NGHIỆM AI WORKSPACE 3-PANE
───────────────────────────────────────────────────────
- Heading: "Không gian làm việc Career AI Workspace"
- Subheading: "Quan sát đồng thời Hồ sơ gốc, Luồng phân tích của Agent và Dữ liệu chuyên sâu."
- Large UI Mockup showing the 3-Pane interface:
  • Left Panel (260px): Active Resume PDF info + Target JD Selector
  • Center Panel (Flex-1): Multi-agent chat timeline with step-by-step reasoning tokens
  • Right Panel (340px): Skill Gap Matrix, Radar Chart, and Match Score Gauge
- 3 Interactive Switcher Tabs below mockup:
  [● Chế độ Phân tích CV] | [○ Chế độ Phỏng vấn AI] | [○ Chế độ Lộ trình Kỹ năng]

───────────────────────────────────────────────────────
SECTION 8: SO SÁNH "TRƯỚC & SAU" KHI DÙNG CAREERPILOT
───────────────────────────────────────────────────────
- Heading: "Khác biệt rõ rệt trong kết quả ứng tuyển"
- Split Comparison Card (Left vs Right):
  • Cột TRƯỚC (Dim Slate #181B25): Điểm CV 58%, Thiếu 5 từ khóa cốt lõi, Chưa chuẩn bị phỏng vấn, Tỷ lệ phản hồi < 10%.
  • Cột SAU (Vibrant Emerald Border): Điểm CV 94%, Đã bù 4/5 kỹ năng trọng tâm, Hoàn thành 5 bài Mock Interview, Tỷ lệ phản hồi > 65%.

───────────────────────────────────────────────────────
SECTION 9: BẢNG GIÁ MINH BẠCH & FAQ ACCORDION
───────────────────────────────────────────────────────
- 2 Pricing Cards:
  • Gói MIỄN PHÍ (0đ / Mãi mãi): 3 lần phân tích CV/tháng, 5 lần so khớp JD, 3 bài phỏng vấn cơ bản, quản lý 5 ứng tuyển.
  • Gói PRO (99.000đ / Tháng): Không giới hạn phân tích CV, So khớp toàn bộ việc làm, Phỏng vấn AI không giới hạn, Xuất báo cáo PDF, Lộ trình kỹ năng chuyên sâu.
- FAQ Accordion (5 items: hỗ trợ tiếng Việt, bảo mật hồ sơ, phỏng vấn AI sát thực tế, chính sách hủy gói).

───────────────────────────────────────────────────────
SECTION 10: FINAL CTA & FOOTER
───────────────────────────────────────────────────────
- Final Action Banner: "Sẵn sàng chinh phục công việc tiếp theo của bạn?"
- Primary Action Button: "Bắt đầu phân tích CV ngay — Hoàn toàn miễn phí →"
- Footer 4 Columns:
  1. Brand: CareerPilot AI + "Trợ lý nghề nghiệp AI toàn diện cho Kỹ sư IT" + GitHub & LinkedIn links.
  2. Sản phẩm (Khớp đúng 6 module): Phân tích CV, Tìm việc & So khớp, Phỏng vấn AI, Lộ trình kỹ năng, Quản lý ứng tuyển, Workspace.
  3. Tài nguyên: Hướng dẫn viết CV, Blog kỹ thuật, Changelog, API Docs.
  4. Hỗ trợ & Bản quyền: © 2026 CareerPilot AI (Đồ án tốt nghiệp CNTT).
```
