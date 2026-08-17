# 🎯 Kế Hoạch Toàn Diện: Bộ Máy Phân Tích & So Khớp JD Tuyển Dụng (Đa Định Dạng: PDF, DOCX, Dán Văn Bản)

> **Mã kế hoạch:** `PLAN-jd-matching-engine`  
> **Người lập:** `project-planner` & `architect-review`  
> **Trạng thái:** 📋 BẢN THẢO THIẾT KẾ & KHẢO SÁT Ý KIẾN (PLANNING ONLY - NO CODE)  
> **Trọng tâm:** Tập trung tối đa vào **Luồng 1 (So khớp CV với JD đa kênh)** và hỗ trợ sẵn **Luồng 2 (Đánh giá CV độc lập)**.

---

## 1. 🧭 BẢN ĐỒ TRẢI NGHIỆM NGƯỜI DÙNG (USER JOURNEY)

### 🌟 LUỒNG 1 (TRỌNG TÂM): SO KHỚP VỚI JD DOANH NGHIỆP
```
[ NGƯỜI DÙNG CÓ JD TUYỂN DỤNG ]
  │
  ├── Cách A: Dán trực tiếp đoạn văn bản JD (Textarea Paste)
  ├── Cách B: Kéo thả file JD dạng PDF (.pdf)
  └── Cách C: Kéo thả file JD dạng Word (.docx)
          │
          ▼
[ BƯỚC 1: XỬ LÝ & BÓC TÁCH JD BẰNG AI ]
  ├── Đọc text (dùng chung bộ parser siêu tốc PyMuPDF / python-docx)
  └── Bóc tách ra Schema có cấu trúc `JobDescriptionProfile`:
      • Vị trí tuyển dụng & Cấp bậc (Senior, Mid, Junior, Lead)
      • Nhóm kỹ năng BẮT BUỘC (Must-have Tech Stack)
      • Nhóm kỹ năng ƯU TIÊN (Nice-to-have / Good-to-have)
      • Số năm kinh nghiệm & Yêu cầu học vấn tối thiểu
          │
          ▼
[ BƯỚC 2: SO KHỚP ĐA CHIỀU GIỮA CV VÀ JD (MATCHING ENGINE) ]
  ├── 1. Kỹ năng Bắt buộc: Đã có những gì? Thiếu từ khóa gì quan trọng?
  ├── 2. Kinh nghiệm & Cấp bậc: Có đáp ứng số năm và phạm vi công việc không?
  └── 3. Bằng chứng định lượng: Các bullet point có số liệu chứng minh năng lực này chưa?
          │
          ▼
[ BƯỚC 3: TRẢ VỀ BÁO CÁO ATS STUDIO TRÊN WORKSPACE (CỘT 3) ]
  ├── 🎯 Điểm khớp tổng thể (0 - 100%) dạng đồng hồ tròn
  ├── 🏷️ Danh sách Chip Tags: [🟢 Kỹ năng đã khớp] vs [🔴 Kỹ năng còn thiếu]
  └── 💡 3 Hành động cụ thể giúp tăng ngay 15-30 điểm ATS
```

---

### 🛡️ LUỒNG 2: ĐÁNH GIÁ ĐỘC LẬP KHI KHÔNG CÓ JD (STANDALONE CV HEALTH CHECK)
- Nếu người dùng bấm *"Chấm điểm CV chung"* mà không nhập JD:
  - Hệ thống tự động kích hoạt chế độ **"CV Market Readiness"**:
    - Đánh giá chất lượng định dạng (Action verbs, Power words).
    - Đánh giá mức độ định lượng (tỷ lệ các câu có số liệu %, $).
    - Đề xuất bổ sung các kỹ năng tiêu chuẩn của ngành theo `detected_title` (ví dụ: CV là "Backend Engineer" thì kiểm tra các kỹ năng cốt lõi: Docker, Redis, DB Indexing, CI/CD).

---

## 2. 🏗️ KIẾN TRÚC KỸ THUẬT & DỮ LIỆU

### 2.1 Cấu Trúc Dữ Liệu Pydantic (`ai/models/job_description.py`)
```python
class JobDescriptionProfile(BaseModel):
    job_title: str
    seniority_level: str  # intern, junior, mid, senior, lead, manager
    required_skills: list[str]       # Kỹ năng bắt buộc (Must-have)
    preferred_skills: list[str]      # Kỹ năng ưu tiên (Nice-to-have)
    min_experience_years: float | None
    core_responsibilities: list[str]
    raw_text: str

class JDMatchReport(BaseModel):
    overall_score: int               # 0 - 100
    skill_match_percentage: int      # 40% trọng số
    experience_match_score: int      # 30% trọng số
    impact_metrics_score: int        # 30% trọng số
    matched_skills: list[str]        # Kỹ năng CV đã có khớp với JD
    missing_critical_skills: list[str] # Kỹ năng bắt buộc nhưng CV CHƯA CÓ
    recommended_keywords: list[str]  # Từ khóa JD nên đưa vào CV để qua ATS
    fit_summary: str                 # Tóm tắt đánh giá ngắn gọn (2-3 câu)
    actionable_quick_fixes: list[str]# Top 3 hành động cụ thể để sửa CV
```

---

### 2.2 Thiết Kế REST API Backend (`be/api/v1/ats_router.py`)

1. **`POST /api/v1/ats/parse-jd`**:
   - Nhận file (PDF/DOCX) hoặc raw text string.
   - Bóc tách ra `JobDescriptionProfile`.
2. **`POST /api/v1/ats/match`**:
   - Body: `{ "candidate_id": 123, "jd_text": "...", "jd_file": Optional }`
   - Chạy thuật toán so khớp giữa `CandidateProfile` và `JobDescriptionProfile`.
   - Lưu báo cáo vào bảng `analyses` trong Database.
   - Trả về `JDMatchReport`.

---

### 2.3 Thiết Kế Giao Diện Cột 3 (ATS Studio & Job Matcher)

```
┌────────────────────────────────────────────────────────┐
│ 🎯 ATS JOB MATCHER STUDIO                              │
├────────────────────────────────────────────────────────┤
│ [ 📋 Dán Văn Bản JD ]      [ 📁 Tải File PDF / DOCX ]  │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Nhập yêu cầu tuyển dụng (JD) hoặc kéo file...      │ │
│ │                                                    │ │
│ └────────────────────────────────────────────────────┘ │
│ [ ⚡ So Khớp & Chấm Điểm ATS Với CV Của Bạn ]         │
├────────────────────────────────────────────────────────┤
│ 📊 KẾT QUẢ SO KHỚP ĐỘ PHÙ HỢP:                         │
│   [ Đồng hồ đo điểm: 78 / 100 (Khá Tốt) ]              │
│                                                        │
│ 🟢 Kỹ Năng Đã Khớp (8):                                │
│   [ Python ] [ FastAPI ] [ Docker ] [ PostgreSQL ] ... │
│                                                        │
│ 🔴 Kỹ Năng Bắt Buộc Còn Thiếu (3):                     │
│   [ Redis Cache ] [ Kubernetes ] [ CI/CD GitHub Action]│
│   *(Bấm vào từ khóa để nhận gợi ý thêm vào CV)*       │
│                                                        │
│ 💡 GỢI Ý NÂNG CẤP NHANH (QUICK FIXES):                 │
│   1. Thêm từ khóa "Redis" vào mục Công nghệ Dự án 1    │
│   2. Bổ sung số liệu định lượng cho kinh nghiệm VNG    │
└────────────────────────────────────────────────────────┘
```

---

## ❓ 3 CÂU HỎI THIẾT KẾ ĐỂ THỐNG NHẤT VỚI BẠN (SOCRATIC GATE)

Trước khi bắt tay vào triển khai chi tiết, tôi muốn làm rõ 3 điểm thiết kế trải nghiệm này cùng bạn:

1. **Về việc tải file JD:**
   - Người dùng có cần xem lại file JD đã tải lên không, hay chỉ cần bóc tách lấy nội dung văn bản JD để so khớp là xong?
2. **Về ngôn ngữ JD:**
   - JD có thể bằng tiếng Anh (chiếm đa số ngành IT) hoặc tiếng Việt. Bạn có muốn kết quả so khớp và nhận xét luôn hiển thị bằng **Tiếng Việt thân thiện** cho người dùng không?
3. **Về luồng tương tác khi phát hiện "Kỹ năng còn thiếu":**
   - Khi hệ thống chỉ ra 3 kỹ năng còn thiếu (ví dụ: *Redis, Kubernetes*), bạn có muốn người dùng bấm vào kỹ năng đó để **AI tự động sinh câu mô tả chuẩn STAR** gợi ý chèn vào CV không?
