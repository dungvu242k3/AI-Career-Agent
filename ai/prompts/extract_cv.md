# CV Extraction — Task Instructions

Your task is to accurately extract and normalize **all information** from the provided CV text into the exact JSON structure defined by the `CandidateProfile` schema.

---

## 📑 STEP 1: CV FORMAT DETECTION

Before extracting, identify the CV's layout format:

| Format Type | How to Detect |
|:---|:---|
| `chronological` | Work experience listed in reverse date order with clear company → role → date → bullets structure |
| `functional` | Skills/competencies listed first, work history is brief or secondary (common for career changers, fresh graduates) |
| `academic` | Contains Publications, Research, Grants, Teaching Experience, or Conference sections |
| `creative` | Non-standard layout, columns, infographic-style, minimal section headers |
| `combination` | Mix of functional (skills-first) and chronological (detailed work history) |

Set `metadata.cv_format_type` accordingly. If the CV has clearly labeled section headers (e.g., "Work Experience", "Kỹ năng"), set `metadata.has_clear_sections = true`. Otherwise, set it to `false`.

---

## 📑 STEP 2: SECTION RECOGNITION & MAPPING

Identify sections using these synonymous titles (English & Vietnamese):

1. **Personal Info:** Header area content, "Thông tin cá nhân", "Contact", "Personal Details"
2. **Summary / Objective:** "Summary", "Professional Summary", "Executive Summary", "Objective", "Career Goal", "About Me", "Profile", "Tóm tắt", "Mục tiêu nghề nghiệp", "Giới thiệu bản thân", "Về tôi"
3. **Education:** "Education", "Academic Background", "Học vấn", "Trình độ học vấn", "Quá trình đào tạo", "Bằng cấp"
4. **Work Experience:** "Experience", "Work Experience", "Professional Experience", "Employment History", "Career History", "Kinh nghiệm làm việc", "Quá trình công tác", "Kinh nghiệm"
5. **Projects:** "Projects", "Personal Projects", "Side Projects", "Key Projects", "Academic Projects", "Portfolio", "Dự án", "Dự án cá nhân", "Đồ án", "Sản phẩm nổi bật"
6. **Skills:** "Skills", "Technical Skills", "Core Competencies", "Tech Stack", "Technologies", "Kỹ năng", "Kỹ năng chuyên môn", "Năng lực cốt lõi", "Công nghệ"
7. **Certifications:** "Certifications", "Certificates", "Licenses", "Chứng chỉ", "Chứng chỉ chuyên môn", "Bằng cấp bổ sung"
8. **Languages:** "Languages", "Language Proficiency", "Ngôn ngữ", "Ngoại ngữ"
9. **Additional:** "Awards", "Achievements", "Honors", "Giải thưởng", "Thành tích", "Activities", "Volunteering", "Hoạt động", "Publications", "Nghiên cứu", "Interests", "Sở thích", "References", "Người tham chiếu"

### Decision Tree for Ambiguous Sections

If a section does NOT have a clear header:
- **Name + contact info at the top** → Extract as `personal_info`
- **Title/headline directly below the name** (e.g., "Senior Backend Engineer") → Set `summary.detected_title`
- **Paragraphs before any dated entries** → Extract as `summary.summary_text`
- **Bullet lists with company names + dates** → Extract as `work_experience`
- **Bullet lists with technology keywords but NO dates** → Extract as `projects` or `skills_taxonomy`
- **Short comma-separated or tag-style items** → Extract as `skills_taxonomy` (categorize into 8 buckets)

### Vietnamese Abbreviation Handling

Recognize and expand common Vietnamese abbreviations in CV context:
- ĐH / ĐHBK / ĐHQG → Đại học / Đại học Bách Khoa / Đại học Quốc gia
- CNTT / KHMT → Công nghệ Thông tin / Khoa học Máy tính
- KN → Kinh nghiệm
- CN → Chủ nhật / Công nghệ (context-dependent)
- KS / ThS / TS / PGS → Kỹ sư / Thạc sĩ / Tiến sĩ / Phó Giáo sư

---

## 🎯 STEP 3: EXTRACTION & NORMALIZATION RULES

### 3.1 Personal Information
- `full_name`: Extract full name. For Vietnamese names, keep natural sequence (Họ - Tên Đệm - Tên, e.g., "Nguyễn Văn An").
- `date_of_birth`: Extract if explicitly present (e.g., "15/05/1998", "1998-05-15"). Do NOT compute from graduation year.
- `phone`, `email`, `location`: Normalize to clean values. If not found, use `null`.
- `linkedin_url`, `github_url`, `portfolio_url`: Extract full URLs. If not found, use `null`.

### 3.2 Job Title / Headline
- `detected_title`: Extract the headline title explicitly placed under or near the name (e.g., "Senior Backend Engineer", "AI Researcher"). If embedded in a Summary paragraph, extract the role mentioned.

### 3.3 Work Experience
- List from **most recent to oldest** (reverse chronological).
- `raw_bullets`: Retain the candidate's **exact wording verbatim**. Do NOT summarize, rephrase, or alter bullet text.
- `start_date` / `end_date`: Normalize to **YYYY-MM** or **YYYY** format.
  - Recognize varied formats: "Mar 2022", "Tháng 3/2022", "03/2022", "Q1 2023" (→ "2023-01"), "2022 - nay"
  - If currently working ("Present", "Hiện tại", "Now", "Nay", "Đến nay"): set `is_current: true` and `end_date: null`.
- `location`: Include if mentioned (city, "Remote", "Hybrid").

### 3.4 Skills Taxonomy (8 Buckets — Flat Name Lists)

Categorize all identified skills into exactly these 8 groups:

| Bucket | Examples | DO NOT Include |
|:---|:---|:---|
| `programming_languages` | Python, TypeScript, Go, Java, C++, Rust, PHP, SQL | Frameworks, Libraries |
| `frameworks` | FastAPI, React, Next.js, Spring Boot, Django, PyTorch, LangChain | Languages themselves |
| `databases` | PostgreSQL, MongoDB, Redis, MySQL, Qdrant, Elasticsearch, DynamoDB | ORM libraries (→ frameworks) |
| `devops_and_cloud` | Docker, Kubernetes, AWS, GCP, Azure, GitHub Actions, Terraform, CI/CD | Cloud-specific databases (→ databases) |
| `ai_and_ml` | RAG, LLMs, Agentic AI, Computer Vision, NLP, Fine-tuning, Vector Search | ML frameworks like PyTorch (→ frameworks) |
| `testing` | pytest, Playwright, Jest, JUnit, Postman, Cypress, Selenium | CI/CD tools (→ devops_and_cloud) |
| `tools` | Git, Linux, Jira, VS Code, Figma, Notion, Slack | Testing frameworks (→ testing) |
| `soft_skills` | Leadership, Agile/Scrum, Problem Solving, Communication, Mentoring | Technical skills |

**Rules:**
- Write skill names ONLY (e.g., "Python"), NOT proficiency levels (e.g., ~~"Python (Advanced)"~~).
- If a skill appears in the CV under a different name, normalize it (e.g., "JS" → "JavaScript", "k8s" → "Kubernetes", "PG" → "PostgreSQL").
- Each skill belongs to exactly ONE bucket. Use the table above to resolve ambiguity.

### 3.5 Certifications & Languages
- **Certifications:** Professional credentials (e.g., "AWS SAA", "CKA", "Google Cloud Professional").
- **Languages:** Spoken/written human languages with proficiency (e.g., "English - IELTS 7.5", "Vietnamese - Native", "Japanese - N2"). Do NOT confuse with programming languages.

### 3.6 Additional Sections
- Any extra sections (Awards, Activities, Publications, Volunteering, Interests, References) → place in `additional_sections` with their original `section_name` and classified `section_type`.

### 3.7 Metadata Calculation

| Field | Rule |
|:---|:---|
| `total_experience_years` | Accurately compute total cumulative work experience in years. Merge overlapping date ranges. |
| `cv_language` | `"vi"` if predominantly Vietnamese, `"en"` if English, `"mixed"` if bilingual. |
| `cv_format_type` | Detected in Step 1. |
| `has_clear_sections` | `true` if CV has clearly labeled section headers, `false` otherwise. |
| `extraction_confidence` | **95-100**: All fields extracted completely. **85-94**: Some optional fields missing (e.g., no LinkedIn URL). **70-84**: Structural issues, ambiguous sections, or OCR artifacts. **<70**: Major extraction problems. |
| `detected_sections` | Array of all section names detected in the document. |

---

## OUTPUT

Return ONLY a valid JSON object strictly conforming to the `CandidateProfile` schema. No commentary, no explanation, no markdown code fences.
