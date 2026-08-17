# Few-Shot Golden Examples

The following are reference examples showing the expected input → output mapping. Use these to calibrate your extraction accuracy and JSON structure.

---

## Example 1: English Chronological CV (Mid-level Software Engineer)

### Input:
"""
David Park
Senior Backend Engineer | david.park@gmail.com | +84 912 345 678
Ho Chi Minh City, Vietnam
LinkedIn: linkedin.com/in/davidpark | GitHub: github.com/dpark

PROFESSIONAL SUMMARY
Results-driven Backend Engineer with 4+ years of experience building scalable microservices and distributed systems. Passionate about clean architecture and DevOps culture.

WORK EXPERIENCE

TechVN Corp — Senior Backend Developer
Jan 2023 – Present | Ho Chi Minh City
- Led migration from monolithic Django app to FastAPI microservices, reducing response time by 40%
- Designed event-driven architecture using Kafka and Redis pub/sub for real-time notifications
- Mentored 3 junior developers through code reviews and pair programming sessions

StartupXYZ — Backend Developer
Jun 2021 – Dec 2022 | Remote
- Built RESTful APIs serving 50K+ daily active users with 99.9% uptime
- Implemented CI/CD pipeline using GitHub Actions and Docker, cutting deployment time from 2hrs to 15min
- Integrated Stripe payment processing handling $200K+ monthly transactions

EDUCATION
Bach Khoa University (HCMUT) — B.Eng Computer Science
2017 – 2021 | GPA: 8.2/10

SKILLS
Python, TypeScript, Go, FastAPI, Django, React, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS (EC2, S3, Lambda), GitHub Actions, Terraform, Git, Linux, Jira, pytest, Agile/Scrum

CERTIFICATIONS
- AWS Certified Solutions Architect – Associate (2023)
- Kubernetes CKA (2024)

LANGUAGES
- English: Professional Working (IELTS 7.0)
- Vietnamese: Native
"""

### Expected Output:
```json
{
  "personal_info": {
    "full_name": "David Park",
    "email": "david.park@gmail.com",
    "phone": "+84 912 345 678",
    "location": "Ho Chi Minh City, Vietnam",
    "linkedin_url": "https://linkedin.com/in/davidpark",
    "github_url": "https://github.com/dpark",
    "portfolio_url": null,
    "date_of_birth": null
  },
  "summary": {
    "summary_text": "Results-driven Backend Engineer with 4+ years of experience building scalable microservices and distributed systems. Passionate about clean architecture and DevOps culture.",
    "detected_title": "Senior Backend Engineer"
  },
  "education": [
    {
      "institution": "Bach Khoa University (HCMUT)",
      "degree": "B.Eng",
      "field_of_study": "Computer Science",
      "start_year": 2017,
      "end_year": 2021,
      "gpa": "8.2/10"
    }
  ],
  "work_experience": [
    {
      "company": "TechVN Corp",
      "role": "Senior Backend Developer",
      "start_date": "2023-01",
      "end_date": null,
      "is_current": true,
      "location": "Ho Chi Minh City",
      "raw_bullets": [
        "Led migration from monolithic Django app to FastAPI microservices, reducing response time by 40%",
        "Designed event-driven architecture using Kafka and Redis pub/sub for real-time notifications",
        "Mentored 3 junior developers through code reviews and pair programming sessions"
      ]
    },
    {
      "company": "StartupXYZ",
      "role": "Backend Developer",
      "start_date": "2021-06",
      "end_date": "2022-12",
      "is_current": false,
      "location": "Remote",
      "raw_bullets": [
        "Built RESTful APIs serving 50K+ daily active users with 99.9% uptime",
        "Implemented CI/CD pipeline using GitHub Actions and Docker, cutting deployment time from 2hrs to 15min",
        "Integrated Stripe payment processing handling $200K+ monthly transactions"
      ]
    }
  ],
  "projects": [],
  "skills_taxonomy": {
    "programming_languages": ["Python", "TypeScript", "Go"],
    "frameworks": ["FastAPI", "Django", "React"],
    "databases": ["PostgreSQL", "MongoDB", "Redis"],
    "devops_and_cloud": ["Docker", "Kubernetes", "AWS", "GitHub Actions", "Terraform"],
    "ai_and_ml": [],
    "testing": ["pytest"],
    "tools": ["Git", "Linux", "Jira"],
    "soft_skills": ["Agile/Scrum"]
  },
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect – Associate",
      "issuer": "Amazon Web Services",
      "issue_date": "2023",
      "credential_url": null
    },
    {
      "name": "Kubernetes CKA",
      "issuer": "CNCF",
      "issue_date": "2024",
      "credential_url": null
    }
  ],
  "languages": [
    {"language": "English", "proficiency": "Professional Working (IELTS 7.0)"},
    {"language": "Vietnamese", "proficiency": "Native"}
  ],
  "additional_sections": [],
  "metadata": {
    "total_experience_years": 4.1,
    "cv_language": "en",
    "cv_format_type": "chronological",
    "has_clear_sections": true,
    "extraction_confidence": 98,
    "detected_sections": ["Personal Info", "Professional Summary", "Work Experience", "Education", "Skills", "Certifications", "Languages"]
  }
}
```

---

## Example 2: Vietnamese Functional CV (Fresh Graduate / Career Changer)

### Input:
"""
NGUYỄN THỊ MAI ANH
Sinh viên mới tốt nghiệp | Lập trình viên Web
Email: maianh.nguyen@email.com | SĐT: 0987 654 321
Hà Nội

MỤC TIÊU NGHỀ NGHIỆP
Sinh viên năm cuối ngành CNTT tại ĐH Bách Khoa Hà Nội, mong muốn ứng tuyển vị trí Frontend Developer để phát triển kỹ năng chuyên môn trong môi trường công nghệ hiện đại.

KỸ NĂNG CHUYÊN MÔN
- Ngôn ngữ: JavaScript, TypeScript, HTML/CSS, Python
- Framework: React, Next.js, TailwindCSS
- Công cụ: Git, VS Code, Figma, Notion
- Cơ sở dữ liệu: MySQL, Firebase
- Khác: Responsive Design, REST API, Agile/Scrum

DỰ ÁN CÁ NHÂN

E-Commerce Platform (Đồ án tốt nghiệp)
- Vai trò: Fullstack Developer
- Mô tả: Xây dựng website bán hàng trực tuyến với giỏ hàng, thanh toán VNPay
- Công nghệ: React, Node.js, MongoDB, TailwindCSS
- Link: github.com/maianh/ecommerce

Blog cá nhân
- Vai trò: Developer
- Mô tả: Blog chia sẻ kiến thức lập trình với markdown editor
- Công nghệ: Next.js, MDX, Vercel

HỌC VẤN
ĐH Bách Khoa Hà Nội — Kỹ sư CNTT
2020 – 2024 | GPA: 3.4/4.0

HOẠT ĐỘNG
- Thành viên CLB Lập trình BKHN (2021-2023)
- Tình nguyện viên FPT Edu Hackathon 2023

NGOẠI NGỮ
- Tiếng Anh: TOEIC 750
- Tiếng Nhật: N4
"""

### Expected Output:
```json
{
  "personal_info": {
    "full_name": "Nguyễn Thị Mai Anh",
    "email": "maianh.nguyen@email.com",
    "phone": "0987 654 321",
    "location": "Hà Nội",
    "linkedin_url": null,
    "github_url": null,
    "portfolio_url": null,
    "date_of_birth": null
  },
  "summary": {
    "summary_text": "Sinh viên năm cuối ngành CNTT tại ĐH Bách Khoa Hà Nội, mong muốn ứng tuyển vị trí Frontend Developer để phát triển kỹ năng chuyên môn trong môi trường công nghệ hiện đại.",
    "detected_title": "Lập trình viên Web"
  },
  "education": [
    {
      "institution": "Đại học Bách Khoa Hà Nội",
      "degree": "Kỹ sư",
      "field_of_study": "Công nghệ Thông tin",
      "start_year": 2020,
      "end_year": 2024,
      "gpa": "3.4/4.0"
    }
  ],
  "work_experience": [],
  "projects": [
    {
      "name": "E-Commerce Platform",
      "description": "Xây dựng website bán hàng trực tuyến với giỏ hàng, thanh toán VNPay",
      "role": "Fullstack Developer",
      "technologies": ["React", "Node.js", "MongoDB", "TailwindCSS"],
      "url": "https://github.com/maianh/ecommerce",
      "highlights": []
    },
    {
      "name": "Blog cá nhân",
      "description": "Blog chia sẻ kiến thức lập trình với markdown editor",
      "role": "Developer",
      "technologies": ["Next.js", "MDX", "Vercel"],
      "url": null,
      "highlights": []
    }
  ],
  "skills_taxonomy": {
    "programming_languages": ["JavaScript", "TypeScript", "HTML/CSS", "Python"],
    "frameworks": ["React", "Next.js", "TailwindCSS"],
    "databases": ["MySQL", "Firebase"],
    "devops_and_cloud": [],
    "ai_and_ml": [],
    "testing": [],
    "tools": ["Git", "VS Code", "Figma", "Notion"],
    "soft_skills": ["Responsive Design", "REST API", "Agile/Scrum"]
  },
  "certifications": [],
  "languages": [
    {"language": "Tiếng Anh", "proficiency": "TOEIC 750"},
    {"language": "Tiếng Nhật", "proficiency": "N4"}
  ],
  "additional_sections": [
    {
      "section_name": "Hoạt động",
      "section_type": "activities",
      "items": [
        "Thành viên CLB Lập trình BKHN (2021-2023)",
        "Tình nguyện viên FPT Edu Hackathon 2023"
      ]
    }
  ],
  "metadata": {
    "total_experience_years": 0.0,
    "cv_language": "vi",
    "cv_format_type": "functional",
    "has_clear_sections": true,
    "extraction_confidence": 96,
    "detected_sections": ["Thông tin cá nhân", "Mục tiêu nghề nghiệp", "Kỹ năng chuyên môn", "Dự án cá nhân", "Học vấn", "Hoạt động", "Ngoại ngữ"]
  }
}
```
