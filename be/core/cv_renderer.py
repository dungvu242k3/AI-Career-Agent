"""Harvard 1-Page CV PDF Rendering Engine using fpdf2.

Strict Harvard Resume Formatting Standards:
- Font: Times New Roman (Standard Serif) with UTF-8 Unicode support
- Single-column ATS-friendly layout
- Pure Black & White (No graphics, photos, or complex tables)
- Single page budget with calibrated line heights and compact margins
"""

import io
import logging
import os
from fpdf import FPDF
from ai.models.harvard_cv import HarvardCVData

logger = logging.getLogger(__name__)

# Standard Windows and Linux font locations for Times New Roman / Noto Serif
FONT_CANDIDATES = [
    # Windows standard paths
    ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf", "C:/Windows/Fonts/timesi.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/ariali.ttf"),
    # Linux standard paths
    (
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    ),
]


class HarvardPDF(FPDF):
    """Custom FPDF class tailored for single-page Harvard layout."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=13, top=12, right=13)
        self.set_auto_page_break(auto=False)  # Strict 1-page control
        self.font_family_name = "TimesNewRoman"
        self._init_fonts()

    def _init_fonts(self):
        """Initialize Unicode TTF fonts with multi-platform fallbacks."""
        registered = False
        for reg, bold, italic in FONT_CANDIDATES:
            if os.path.exists(reg) and os.path.exists(bold):
                try:
                    self.add_font("HarvardSerif", "", reg)
                    self.add_font("HarvardSerif", "B", bold)
                    if os.path.exists(italic):
                        self.add_font("HarvardSerif", "I", italic)
                    else:
                        self.add_font("HarvardSerif", "I", reg)
                    self.font_family_name = "HarvardSerif"
                    registered = True
                    break
                except Exception as font_err:
                    logger.debug("Failed to register font %s: %s", reg, font_err)

        if not registered:
            # Fallback to standard core font (Note: core fonts lack full Vietnamese diacritics)
            self.font_family_name = "Times"


class HarvardPDFRenderer:
    """Renders HarvardCVData into a clean, single-page, ATS-optimized PDF binary."""

    @staticmethod
    def render(cv: HarvardCVData) -> bytes:
        """Render complete Harvard CV into PDF bytes."""
        pdf = HarvardPDF()
        pdf.add_page()
        font = pdf.font_family_name
        is_vi = cv.target_language == "vi"

        page_width = 210  # A4 width in mm
        margin_left = 13
        margin_right = 13
        content_width = page_width - margin_left - margin_right

        # ── 1. HEADER (Candidate Name & Contact Line) ──
        pdf.set_font(font, "B", 13.5)
        pdf.cell(content_width, 6, cv.contact.full_name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")

        # Contact Info Line
        contact_parts = []
        if cv.contact.phone:
            contact_parts.append(cv.contact.phone)
        if cv.contact.email:
            contact_parts.append(cv.contact.email)
        if cv.contact.location:
            contact_parts.append(cv.contact.location)
        if cv.contact.linkedin_url:
            clean_linkedin = cv.contact.linkedin_url.replace("https://", "").replace("www.", "")
            contact_parts.append(clean_linkedin)
        if cv.contact.github_url:
            clean_github = cv.contact.github_url.replace("https://", "").replace("www.", "")
            contact_parts.append(clean_github)

        contact_line = "  |  ".join(contact_parts)
        pdf.set_font(font, "", 8.5)
        # Adaptively scale down font if contact info line exceeds page width (BUG-09)
        if pdf.get_string_width(contact_line) > content_width:
            pdf.set_font(font, "", 7.5)
            if pdf.get_string_width(contact_line) > content_width:
                pdf.set_font(font, "", 7.0)
        pdf.cell(content_width, 4.5, contact_line, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        # Helper for Section Headers & Overflow Guard (BUG-03)
        max_content_y = 285.0  # mm (A4 is 297mm with 12mm bottom margin)

        def check_overflow(section_name: str):
            if pdf.get_y() > max_content_y:
                logger.warning(
                    "Harvard CV 1-Page limit exceeded at section '%s': current_y=%.1fmm (max=%.1fmm)",
                    section_name,
                    pdf.get_y(),
                    max_content_y,
                )

        def render_section_header(title: str):
            pdf.ln(1.5)
            pdf.set_font(font, "B", 9.5)
            pdf.cell(content_width, 4.2, title.upper(), new_x="LMARGIN", new_y="NEXT")
            # Horizontal Rule
            y = pdf.get_y()
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.3)
            pdf.line(margin_left, y, margin_left + content_width, y)
            pdf.ln(1.2)

        # ── 2. PROFESSIONAL SUMMARY ──
        if cv.summary:
            render_section_header("Tóm tắt chuyên môn" if is_vi else "Professional Summary")
            pdf.set_font(font, "", 8.5)
            pdf.multi_cell(content_width, 3.8, cv.summary, align="J", new_x="LMARGIN", new_y="NEXT")
            check_overflow("Summary")

        # ── 3. EDUCATION ──
        if cv.education:
            render_section_header("Học vấn" if is_vi else "Education")
            for edu in cv.education:
                pdf.set_font(font, "B", 9.0)
                # Left: Institution, Right: Date
                pdf.cell(content_width * 0.75, 4.2, edu.institution, align="L")
                pdf.set_font(font, "", 8.5)
                pdf.cell(content_width * 0.25, 4.2, edu.graduation_year, align="R", new_x="LMARGIN", new_y="NEXT")

                # Degree Major + GPA
                pdf.set_font(font, "I", 8.5)
                degree_text = edu.degree_major
                if edu.gpa_honors:
                    degree_text += f" ({edu.gpa_honors})"
                pdf.cell(content_width, 3.8, degree_text, new_x="LMARGIN", new_y="NEXT")
            check_overflow("Education")

        # ── 4. WORK EXPERIENCE ──
        if cv.experience:
            render_section_header("Kinh nghiệm làm việc" if is_vi else "Work Experience")
            for exp in cv.experience:
                # Line 1: Company (Bold) + Dates (Right aligned)
                pdf.set_font(font, "B", 9.0)
                pdf.cell(content_width * 0.70, 4.2, exp.company, align="L")
                pdf.set_font(font, "", 8.5)
                pdf.cell(content_width * 0.30, 4.2, exp.date_range, align="R", new_x="LMARGIN", new_y="NEXT")

                # Line 2: Role (Italic) + Location (Right aligned)
                pdf.set_font(font, "I", 8.5)
                pdf.cell(content_width * 0.70, 3.8, exp.role, align="L")
                pdf.set_font(font, "", 8.0)
                pdf.cell(content_width * 0.30, 3.8, exp.location or "", align="R", new_x="LMARGIN", new_y="NEXT")

                # Bullets
                pdf.set_font(font, "", 8.5)
                for bullet in exp.bullets:
                    # Bullet point with hanging indent
                    x_start = margin_left
                    pdf.set_x(x_start)
                    pdf.cell(4, 3.7, chr(149) if font == "Times" else "\u2022", align="R")
                    pdf.set_x(x_start + 4.5)
                    pdf.multi_cell(content_width - 4.5, 3.7, bullet, align="L", new_x="LMARGIN", new_y="NEXT")
            check_overflow("Experience")

        # ── 5. KEY PROJECTS (Positioned before skills) ──
        if cv.projects:
            render_section_header("Dự án tiêu biểu" if is_vi else "Key Projects")
            for proj in cv.projects:
                pdf.set_font(font, "B", 9.0)
                pdf.cell(content_width * 0.70, 4.0, proj.name, align="L")
                pdf.set_font(font, "", 8.5)
                pdf.cell(content_width * 0.30, 4.0, proj.date_range or "", align="R", new_x="LMARGIN", new_y="NEXT")

                if proj.role_or_tech:
                    pdf.set_font(font, "I", 8.2)
                    pdf.cell(content_width, 3.6, proj.role_or_tech, new_x="LMARGIN", new_y="NEXT")

                pdf.set_font(font, "", 8.5)
                for bullet in proj.bullets:
                    x_start = margin_left
                    pdf.set_x(x_start)
                    pdf.cell(4, 3.6, chr(149) if font == "Times" else "\u2022", align="R")
                    pdf.set_x(x_start + 4.5)
                    pdf.multi_cell(content_width - 4.5, 3.6, bullet, align="L", new_x="LMARGIN", new_y="NEXT")
            check_overflow("Projects")

        # ── 6. TECHNICAL SKILLS (10-15 Core Skills) ──
        if cv.skills_categories:
            render_section_header("Kỹ năng chuyên môn" if is_vi else "Technical Skills")
            for cat in cv.skills_categories:
                pdf.set_font(font, "B", 8.5)
                cat_label = f"{cat.category_name}: "
                label_w = pdf.get_string_width(cat_label) + 1.5
                pdf.cell(label_w, 3.8, cat_label, align="L")

                pdf.set_font(font, "", 8.5)
                skills_str = ", ".join(cat.skills)
                pdf.multi_cell(content_width - label_w, 3.8, skills_str, align="L", new_x="LMARGIN", new_y="NEXT")
            check_overflow("Skills")

        # ── 7. CERTIFICATIONS & LANGUAGES (Merged Final Section) ──
        has_certs = bool(cv.certifications_and_languages.certifications)
        has_langs = bool(cv.certifications_and_languages.languages)
        if has_certs or has_langs:
            render_section_header("Chứng chỉ & Ngôn ngữ" if is_vi else "Certifications & Languages")

            if has_certs:
                pdf.set_font(font, "B", 8.5)
                label = "Chứng chỉ: " if is_vi else "Certifications: "
                label_w = pdf.get_string_width(label) + 1.5
                pdf.cell(label_w, 3.8, label, align="L")
                pdf.set_font(font, "", 8.5)
                pdf.multi_cell(
                    content_width - label_w,
                    3.8,
                    ", ".join(cv.certifications_and_languages.certifications),
                    align="L",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )

            if has_langs:
                pdf.set_font(font, "B", 8.5)
                label = "Ngoại ngữ: " if is_vi else "Languages: "
                label_w = pdf.get_string_width(label) + 1.5
                pdf.cell(label_w, 3.8, label, align="L")
                pdf.set_font(font, "", 8.5)
                pdf.multi_cell(
                    content_width - label_w,
                    3.8,
                    ", ".join(cv.certifications_and_languages.languages),
                    align="L",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
            check_overflow("CertificationsAndLanguages")

        # Output bytes
        buffer = io.BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()
