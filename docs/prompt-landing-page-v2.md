# 🟢 Prompt Landing Page — CareerPilot AI (v2.1 — Pro Micro-Interactions & Real Feature Mega Menu)

> **Mục đích:** Nạp trực tiếp vào Google Stitch hoặc AI Designer để sinh giao diện Landing Page chuyên nghiệp đỉnh cao.
> **Ngôn ngữ hiển thị:** Toàn bộ bằng Tiếng Việt (trừ tên thuật ngữ kỹ thuật, code và tên chuẩn công nghệ).

---

## 📋 Full Prompt Copy-Paste (Dán vào Stitch)

```text
Design an elite, production-grade Vietnamese Landing Page for "CareerPilot AI" — an intelligent career co-pilot and AI workspace engineered for Vietnamese software engineers, IT students, and tech professionals.

All visible UI labels, copy, tooltips, and descriptions MUST be in Vietnamese. Technical terms (ATS, JD, API, Docker, React, etc.) remain in English.

═══════════════════════════════════════════════════════
1. DESIGN SYSTEM & VISUAL IDENTITY
═══════════════════════════════════════════════════════

Aesthetic Philosophy: "Modern Technical Precision" (inspired by Linear, Raycast, and Stripe).
A crisp, developer-tool instrument with mathematically balanced spacing, high contrast, zero clutter, and purposeful micro-interactions.

Color Palette (Dark Mode):
- Background: #090D16 (Deep Obsidian Base — NOT pure black #000000)
- Card / Panel Surface: #111827 (Slate 900)
- Structural Borders: 1px solid #1E293B (Slate 800)
- Active / Hover Border: 1px solid #10B981 (Emerald Glow transition)
- Primary Action CTA: #10B981 (Emerald Peak — career growth)
- AI Signal / Pulse: #06B6D4 (Electric Cyan — live agent reasoning state)
- Warning / Skill Gap: #F59E0B (Warm Amber — missing requirements)
- Primary Text: #F8FAFC (Slate 50 — high contrast)
- Secondary / Muted Text: #94A3B8 (Slate 400)

Typography Hierarchy:
- Headlines & Hero: "Plus Jakarta Sans" (Weight 700 / 600)
- Body & UI Controls: "Inter" (Weight 400 / 500)
- Data Metrics, Match Scores, Code & AI Traces: "JetBrains Mono" (Weight 500 / 600)

Strict Anti-Patterns (DO NOT USE):
- ❌ NO purple or violet gradient backgrounds of any kind
- ❌ NO floating blurry 3D blobs, mesh aurora, or noisy particles
- ❌ NO generic emoji icons (use crisp Lucide/Heroicons SVG style)
- ❌ NO generic 4-card equal bento grid clichés
- ❌ NO stock photos of generic people smiling at laptops
- ❌ NO marketing buzzwords without substance ("Magical", "Revolutionize")

═══════════════════════════════════════════════════════
2. PAGE ARCHITECTURE (10 STRATEGIC SECTIONS)
═══════════════════════════════════════════════════════

───────────────────────────────────────────────────────
SECTION 1: FIXED HEADER & MEGA FEATURE DROPDOWN
───────────────────────────────────────────────────────
- Position: Sticky top with 80% opacity backdrop blur (rgba(9, 13, 22, 0.85)) and 1px bottom border (#1E293B).
- Left: Logo mark with Emerald terminal icon + Text "CareerPilot AI" + Live Status Pill: A small Cyan pulsing dot (#06B6D4) with text "AI Engine Online".
- Center Navigation:
  1. "Tính năng ▾" (Triggers a rich Mega Menu Dropdown on hover/click with 5 actual platform modules):
     • [Icon: FileCheck] "Phân tích CV chuẩn ATS" — Quét lỗi định dạng, đo % từ khóa chuẩn ATS quốc tế
     • [Icon: Target] "So khớp việc làm (JD Matcher)" — Thuật toán AI đo độ tương thích giữa CV & JD mục tiêu
     • [Icon: Mic] "Phỏng vấn giả lập AI (Mock Arena)" — Luyện trả lời tình huống kỹ thuật với Agent theo thời gian thực
     • [Icon: Map] "Lộ trình bù kỹ năng (Roadmap)" — Kế hoạch bù đắp Skill Gap 2-4 tuần theo vị trí
     • [Icon: Terminal] "AI Workspace (Command Center)" — Bàn làm việc 3-Pane đa tác vụ cho lập trình viên
  2. "Cách hoạt động" (Smooth scroll to How it Works)
  3. "Bảng giá" (Smooth scroll to Pricing)
  4. "Về chúng tôi" (Link to About/Tech)
- Right Actions:
  • "Đăng nhập" (Ghost button with Slate-300 text)
  • "Bắt đầu miễn phí" (Solid Emerald button #10B981, text #090D16, rounded-md, 150ms hover scale)

───────────────────────────────────────────────────────
SECTION 2: HERO SECTION WITH LIVE DASHBOARD INSTRUMENT
───────────────────────────────────────────────────────
- Layout: 2-Column Desktop (Left 52% Value Proposition, Right 48% Live Interactive Instrument). Single column stacked on mobile.

Left Column:
- Top Badge: Emerald border pill with text "⚡ NỀN TẢNG AGENTIC AI ĐỒNG HÀNH NGHỀ NGHIỆP"
- Main Display Headline (Large & Punchy, max 2 lines):
  "Từ CV chưa tối ưu đến Offer Letter — AI đồng hành cùng bạn."
- Subtitle:
  "Tự động trích xuất kỹ năng, đo điểm chuẩn ATS, giả lập phỏng vấn kỹ thuật và kiến tạo lộ trình học tập cá nhân hóa — tất cả trong một nền tảng duy nhất."
- Action Bar:
  • Primary CTA: "Phân tích CV miễn phí →" (Large Emerald button, subtle glow on hover)
  • Secondary CTA: "Xem Demo tương tác" (Slate-800 button with 1px border)
- Trust Micro-copy: "✓ Miễn phí cho sinh viên • ✓ Không yêu cầu thẻ tín dụng • ✓ Kết quả trong 3 phút"

Right Column (Live Instrument Card):
- A rich dark panel (#111827) with 1px border (#1E293B) and subtle Cyan accent top-border.
- Top Header: File indicator "Senior_Backend_Engineer_CV.pdf (4.2 MB)" + Status "Đã phân tích xong ✓".
- Center Radial Gauge: Large circular progress meter displaying "94%" in Emerald (#10B981) with label "Điểm Tương Thích ATS".
- Skill Taxonomy Chips:
  • Matched Skills (Green pill + checkmark): "FastAPI (95%)", "PostgreSQL (90%)", "Docker (88%)"
  • Missing Skill Gap (Amber pill + warning): "Kubernetes (Cần bổ sung)", "Distributed Tracing"
- Simulated Agent Thought Stream:
  A terminal-style box showing typewriter text:
  "> Agent matching against Top 50 Tech JDs in Vietnam... Found 14 high-match positions."

───────────────────────────────────────────────────────
SECTION 3: TRUST METRICS & TECH STACK TICKER
───────────────────────────────────────────────────────
- Background: #0B1120 with subtle top/bottom borders.
- 4 Key Metrics (Numbers in JetBrains Mono, Emerald #10B981):
  • "500+" — CV và hồ sơ đã được chuẩn hóa
  • "94.2%" — Tỷ lệ tương thích định dạng ATS
  • "< 3 phút" — Thời gian bóc tách & phân tích toàn diện
  • "100%" — Miễn phí các tính năng cốt lõi cho sinh viên
- Tech Stack Recognition Bar: Icons showing support for (Python, React, Java, Go, NodeJS, Docker, AWS, PostgreSQL).

───────────────────────────────────────────────────────
SECTION 4: "DÀNH CHO AI?" — 3 PERSONA CARDS
───────────────────────────────────────────────────────
- Heading: "Được may đo cho từng chặng đường sự nghiệp"
- Subheading: "Dù bạn đang chuẩn bị ra trường hay hướng tới vị trí Tech Lead, CareerPilot AI có giải pháp tương ứng."
- 3 Interactive Cards with 1px borders and Emerald hover transition:
  1. Card "Sinh viên IT sắp tốt nghiệp":
     - Icon: Graduation SVG (Lucide)
     - Nỗi đau: "Chưa biết viết CV ra sao, thiếu dự án thực tế và sợ rớt vòng lọc hồ sơ."
     - Giải pháp: "Phân tích điểm yếu, chuẩn hóa định dạng ATS và gợi ý công việc Fresher phù hợp."
  2. Card "Fresher & Junior đang tìm việc":
     - Icon: Code2 SVG (Lucide)
     - Nỗi đau: "Rải hàng chục CV nhưng không có phản hồi, lúng túng khi phỏng vấn kỹ thuật."
     - Giải pháp: "Tối ưu hóa từ khóa theo từng JD, luyện phỏng vấn giả lập không giới hạn với AI."
  3. Card "Mid / Senior muốn nâng cấp vị thế":
     - Icon: TrendingUp SVG (Lucide)
     - Nỗi đau: "Muốn nhảy việc với mức lương cao hơn nhưng chưa rõ khoảng trống kiến trúc hệ thống."
     - Giải pháp: "Bản đồ Skill Gap chuyên sâu, chỉ ra chính xác công nghệ cần bổ sung trong 30 ngày."

───────────────────────────────────────────────────────
SECTION 5: CÁCH HOẠT ĐỘNG — 3 BƯỚC ĐƠN GIẢN
───────────────────────────────────────────────────────
- Heading: "Quy trình 3 bước khép kín"
- Subheading: "Từ tệp PDF thô đến sự chuẩn bị hoàn hảo trước nhà tuyển dụng."
- 3 Connected Steps with directional arrows:
  • Bước 01: [Upload CV] Kéo thả PDF/DOCX — AI Agent tự động bóc tách kỹ năng, kinh nghiệm và dự án trong 5 giây.
  • Bước 02: [AI Deep Scan & Match] Đối chiếu với ma trận yêu cầu tuyển dụng, tính điểm ATS và phát hiện lỗ hổng kỹ năng.
  • Bước 03: [Hành động & Phỏng vấn] Nhận bản CV tối ưu, luyện mock interview tình huống và bắt đầu học theo lộ trình đề xuất.

───────────────────────────────────────────────────────
SECTION 6: 4 TRỤ CỘT TÍNH NĂNG CỐT LÕI (ASYMMETRIC GRID)
───────────────────────────────────────────────────────
- Heading: "Hệ thống công cụ toàn diện cho Kỹ sư IT"
- 4 Feature Cards (Asymmetric layout):
  1. Feature 1 (Large Card - Phân tích & Tối ưu CV):
     - Tag: "CV OPTIMIZER" (Emerald)
     - Title: "Trình bóc tách CV thông minh chuẩn ATS"
     - Description: "Phân tích cấu trúc câu, định lượng thành tựu theo mô hình STAR, kiểm tra độ tương thích với hệ thống ATS của các tập đoàn công nghệ."
  2. Feature 2 (So khớp việc làm):
     - Tag: "JOB MATCHER" (Cyan)
     - Title: "Ma trận so khớp năng lực và JD mục tiêu"
     - Description: "Tính toán % match chính xác theo từng kỹ năng cứng, kỹ năng mềm và năm kinh nghiệm."
  3. Feature 3 (Phỏng vấn giả lập AI):
     - Tag: "MOCK INTERVIEW" (Emerald)
     - Title: "Đấu trường phỏng vấn kỹ thuật thời gian thực"
     - Description: "Mô phỏng câu hỏi System Design và Coding tình huống. Nhận phản hồi tức thì về từ khóa và độ mạch lạc."
  4. Feature 4 (Lộ trình kỹ năng):
     - Tag: "SKILL ROADMAP" (Amber)
     - Title: "Lộ trình học tập bù đắp khoảng trống kỹ năng"
     - Description: "Biến các kỹ năng còn thiếu thành kế hoạch học tập chi tiết 2-4 tuần kèm tài liệu chọn lọc."

───────────────────────────────────────────────────────
SECTION 7: PRODUCT SHOWCASE — BÀN LÀM VIỆC 3-PANE
───────────────────────────────────────────────────────
- Heading: "Không gian làm việc Career AI Workspace"
- Subheading: "Bàn làm việc 3 cột (3-Pane) chuẩn công thái học cho năng suất tối đa."
- Interactive Viewport Mockup showing:
  • Cột 1 (Left 260px): Cây thư mục nguồn (CV PDF, JD mục tiêu)
  • Cột 2 (Center Flex-1): Luồng trò chuyện đa Agent, gõ suy luận thời gian thực
  • Cột 3 (Right 340px): Radar chart kỹ năng, đồng hồ điểm ATS và nút hành động nhanh
- 3 Interactive Switcher Tabs below mockup:
  [● Chế độ Phân tích CV] | [○ Chế độ Phỏng vấn AI] | [○ Chế độ Lộ trình Kỹ năng]

───────────────────────────────────────────────────────
SECTION 8: SO SÁNH "TRƯỚC & SAU" KHI DÙNG CAREERPILOT
───────────────────────────────────────────────────────
- Heading: "Khác biệt rõ rệt trong kết quả ứng tuyển"
- Split Comparison Card:
  • Cột TRƯỚC (Dim Slate #181B25): Điểm CV 58%, Thiếu 5 từ khóa cốt lõi, Chưa chuẩn bị phỏng vấn, Tỷ lệ nhận phản hồi < 10%.
  • Cột SAU (Vibrant Emerald Border): Điểm CV 94%, Đã bù 4/5 kỹ năng trọng tâm, Hoàn thành 5 bài Mock Interview, Tỷ lệ phản hồi > 65%.

───────────────────────────────────────────────────────
SECTION 9: BẢNG GIÁ MINH BẠCH & FAQ ACCORDION
───────────────────────────────────────────────────────
- 2 Gói Giá rõ ràng:
  • Gói MIỄN PHÍ (0đ / Mãi mãi): 3 lần phân tích CV/tháng, 5 lần so khớp JD, 3 bài phỏng vấn cơ bản.
  • Gói PRO (99.000đ / Tháng): Không giới hạn phân tích CV, So khớp toàn bộ việc làm, Phỏng vấn AI nâng cao không giới hạn, Xuất báo cáo PDF, Lộ trình kỹ năng chuyên sâu.
- FAQ Accordion (5 câu hỏi thực tế về hỗ trợ tiếng Việt, bảo mật dữ liệu, độ chính xác phỏng vấn).

───────────────────────────────────────────────────────
SECTION 10: FINAL CALL-TO-ACTION & FOOTER
───────────────────────────────────────────────────────
- Large Action Banner: "Sẵn sàng chinh phục công việc tiếp theo của bạn?"
- Big Emerald Button: "Bắt đầu phân tích CV ngay — Hoàn toàn miễn phí →"
- Footer 4 Columns:
  1. Brand: CareerPilot AI + "Trợ lý nghề nghiệp AI thế hệ mới" + GitHub & LinkedIn links.
  2. Sản phẩm: Phân tích CV, So khớp JD, Phỏng vấn AI, Lộ trình học, Workspace.
  3. Tài nguyên: Hướng dẫn viết CV, Blog kỹ thuật, Changelog, API.
  4. Hỗ trợ & Bản quyền: © 2026 CareerPilot AI (Đồ án tốt nghiệp CNTT).
```
