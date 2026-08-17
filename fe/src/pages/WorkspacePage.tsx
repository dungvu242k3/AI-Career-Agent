import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Upload,
  FileText,
  Edit3,
  CheckCircle2,
  Sparkles,
  MapPin,
  Mail,
  Phone,
  Briefcase,
  GraduationCap,
  Calendar,
  Layers,
  Award,
  Globe,
  ExternalLink,
} from "lucide-react";
import { UploadModal } from "../components/UploadModal";
import { ProfileEditModal } from "../components/ProfileEditModal";
import {
  CandidateProfile,
  UploadResponse,
  SKILL_CATEGORY_LABELS,
  SkillCategoryKey,
} from "../types/candidate";
import { getActiveCandidateLocally } from "../services/cvApi";

// Types
interface JobItem {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  matchScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  description: string;
  requirements: string[];
  benefits: string[];
}

const DEFAULT_PROFILE: CandidateProfile = {
  personal_info: {
    full_name: "Nguyễn Văn An",
    email: "an.nguyen@email.com",
    phone: "0912 345 678",
    location: "TP. Hồ Chí Minh",
    linkedin_url: "https://linkedin.com/in/annguyen",
    github_url: "https://github.com/annguyen",
    portfolio_url: null,
    date_of_birth: null,
  },
  summary: {
    summary_text:
      "Kỹ sư Backend & AI với 4+ năm kinh nghiệm xây dựng hệ thống phân tán, microservices hiệu năng cao và RAG Pipelines phục vụ hàng triệu người dùng.",
    detected_title: "Senior AI & Backend Engineer",
  },
  education: [
    {
      institution: "Đại học Bách Khoa TP.HCM (HCMUT)",
      degree: "Kỹ sư",
      field_of_study: "Khoa học Máy tính",
      start_year: 2017,
      end_year: 2021,
      gpa: "8.4 / 10",
    },
  ],
  work_experience: [
    {
      company: "VNG Cloud",
      role: "Senior AI / Backend Engineer",
      start_date: "2023-01",
      end_date: null,
      is_current: true,
      location: "TP. Hồ Chí Minh",
      raw_bullets: [
        "Kiến trúc nền tảng AI Core xử lý 30,000+ truy vấn RAG/ngày với độ trễ < 250ms.",
        "Xây dựng microservices FastAPI và Redis cache, giảm tải database 45%.",
      ],
    },
    {
      company: "MoMo Fintech",
      role: "Software Engineer (Python/Go)",
      start_date: "2021-06",
      end_date: "2022-12",
      is_current: false,
      location: "TP. Hồ Chí Minh",
      raw_bullets: [
        "Phát triển API thanh toán phân tán chịu tải cao, tích hợp Kafka event streaming.",
        "Thiết lập CI/CD pipeline tự động hóa kiểm thử với Docker và GitHub Actions.",
      ],
    },
  ],
  projects: [
    {
      name: "CareerPilot AI",
      description: "Hệ thống AI Agent tự động hóa bóc tách CV và tối ưu điểm ATS theo chuẩn STAR.",
      role: "Lead Creator",
      technologies: ["FastAPI", "React", "Gemini 2.0 Flash", "PyMuPDF", "PostgreSQL"],
      url: "https://github.com/careerpilot-ai",
      highlights: ["Hỗ trợ layout 2 cột, khử nhiễu tự động và Structured Output."],
    },
  ],
  skills_taxonomy: {
    programming_languages: ["Python", "Go", "TypeScript", "SQL"],
    frameworks: ["FastAPI", "React", "Next.js", "Django", "PyTorch"],
    databases: ["PostgreSQL", "MongoDB", "Redis", "Qdrant DB"],
    devops_and_cloud: ["Docker", "Kubernetes", "AWS", "GitHub Actions", "CI/CD"],
    ai_and_ml: ["RAG Pipelines", "LLMs", "Vector Search", "LangChain"],
    testing: ["pytest", "Postman", "Playwright"],
    tools: ["Git", "Linux", "Jira", "VS Code"],
    soft_skills: ["Agile/Scrum", "Problem Solving", "System Architecture"],
  },
  certifications: [
    {
      name: "AWS Certified Solutions Architect – Associate",
      issuer: "Amazon Web Services",
      issue_date: "2023",
      credential_url: null,
    },
  ],
  languages: [
    { language: "Tiếng Việt", proficiency: "Bản xứ" },
    { language: "Tiếng Anh", proficiency: "Chuyên nghiệp (IELTS 7.0)" },
  ],
  additional_sections: [],
  metadata: {
    total_experience_years: 4.2,
    cv_language: "vi",
    cv_format_type: "chronological",
    has_clear_sections: true,
    extraction_confidence: 98,
    detected_sections: [
      "Thông tin cá nhân",
      "Tóm tắt",
      "Kinh nghiệm làm việc",
      "Kỹ năng chuyên môn",
      "Học vấn",
      "Dự án",
    ],
  },
};

export default function WorkspacePage() {
  // State variables
  const [activeRightTab, setActiveRightTab] = useState<"jobs" | "studio">("jobs");
  const [activeVersion, setActiveVersion] = useState<"v2" | "v1">("v2");
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);

  // Active Candidate State (Loaded from API or localStorage)
  const [candidateId, setCandidateId] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string>("Nguyen_Van_A_CV.pdf");
  const [profile, setProfile] = useState<CandidateProfile>(DEFAULT_PROFILE);

  // Modals state
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Load from LocalStorage on mount if present
  useEffect(() => {
    const local = getActiveCandidateLocally();
    if (local.profile) {
      setProfile(local.profile);
      if (local.candidateId) setCandidateId(local.candidateId);
      if (local.filename) setFileName(local.filename);
    }
  }, []);

  const handleUploadSuccess = (data: UploadResponse) => {
    setCandidateId(data.candidate_id);
    setFileName(data.filename);
    setProfile(data.profile);
  };

  const handleProfileSaved = (updated: CandidateProfile) => {
    setProfile(updated);
  };

  // Compute total skills count across 8 buckets
  const totalSkillsCount = Object.values(profile.skills_taxonomy).reduce(
    (acc, list) => acc + (Array.isArray(list) ? list.length : 0),
    0
  );

  // Sample matched jobs data
  const jobsList: JobItem[] = [
    {
      id: "vng-01",
      title: "Senior AI & Backend Systems Engineer",
      company: "VNG Corporation",
      location: "TP. Hồ Chí Minh (Hybrid)",
      salary: "50.000.000đ - 75.000.000đ",
      matchScore: 96,
      matchedSkills: ["Python", "FastAPI", "RAG Pipelines", "PostgreSQL", "Docker"],
      missingSkills: ["Kafka Cluster"],
      description:
        "Chịu trách nhiệm kiến trúc và phát triển nền tảng AI Core phục vụ hàng triệu người dùng. Tối ưu hóa độ trễ truy vấn RAG và xây dựng backend microservices hiệu năng cao.",
      requirements: [
        "Từ 3+ năm kinh nghiệm phát triển hệ thống Backend với Python (FastAPI/AsyncIO) hoặc Go.",
        "Kinh nghiệm thực chiến với Vector Database (Qdrant, Milvus, Pinecone) và RAG Frameworks.",
        "Thành thạo tối ưu hóa câu lệnh PostgreSQL, Caching Redis và kiến trúc Microservices.",
        "Có tư duy làm việc độc lập và kỹ năng giải quyết vấn đề hệ thống quy mô lớn.",
      ],
      benefits: [
        "Mức lương cạnh tranh bậc nhất thị trường + Thưởng hiệu suất hàng năm (14-16 tháng lương).",
        "Bảo hiểm sức khỏe cao cấp VNG Care cho nhân viên và người thân.",
        "Môi trường làm việc Hybrid linh hoạt, cung cấp Macbook Pro M3 Max.",
      ],
    },
    {
      id: "momo-02",
      title: "Lead Backend Architect",
      company: "MoMo (M_Service)",
      location: "Hà Nội / TP. HCM",
      salary: "60.000.000đ - 85.000.000đ",
      matchScore: 92,
      matchedSkills: ["Python", "Go", "PostgreSQL", "Redis", "Microservices"],
      missingSkills: ["Kubernetes Operator"],
      description:
        "Thiết kế kiến trúc hệ thống thanh toán và dịch vụ tài chính chịu tải 30,000+ RPS. Đảm bảo tính khả dụng 99.99% và an toàn bảo mật dữ liệu giao dịch.",
      requirements: [
        "4+ năm kinh nghiệm Backend quy mô lớn, thành thạo Go/Python.",
        "Hiểu sâu về Sharding DB, Distributed Transaction và Idempotency.",
        "Kinh nghiệm làm việc với Redis Cluster, Kafka Event Streaming.",
      ],
      benefits: [
        "Gói ESOP dành cho nhân sự nòng cốt.",
        "Thưởng hiệu suất 3-5 tháng lương mỗi năm.",
        "Lộ trình thăng tiến rõ ràng lên Principal Architect.",
      ],
    },
    {
      id: "techfin-03",
      title: "Machine Learning Systems Lead",
      company: "TechFin Global",
      location: "Remote (Toàn thời gian)",
      salary: "$3,000 - $4,500 / tháng",
      matchScore: 88,
      matchedSkills: ["PyTorch", "Python", "RAG", "Docker", "Qdrant"],
      missingSkills: ["Triton Inference Server"],
      description:
        "Xây dựng hạ tầng triển khai mô hình LLM và RAG quy mô doanh nghiệp cho các tổ chức tài chính tại Singapore và Đông Nam Á.",
      requirements: [
        "Kinh nghiệm tối ưu hóa mô hình LLM, Fine-tuning và Quantization.",
        "Xây dựng API serving với độ trễ thấp (< 200ms).",
      ],
      benefits: [
        "Làm việc 100% Remote, thanh toán theo USD.",
        "Ngân sách $2,000/năm cho học tập và thiết bị.",
      ],
    },
  ];

  // Handler for selecting job to view in drawer
  const handleOpenJobDetail = (job: JobItem) => {
    setSelectedJob(job);
    setIsDrawerOpen(true);
  };

  // Handler for tailoring CV for a specific job
  const handleTailorForJob = (job: JobItem) => {
    setSelectedJob(job);
    setActiveRightTab("studio");
    setActiveVersion("v2");
  };

  // Handler for asking AI about the selected job
  const handleAskAiAboutJob = (job: JobItem) => {
    setIsDrawerOpen(false);
    setChatInput(`Phân tích mức độ tương thích giữa CV của tôi và JD ${job.title} tại ${job.company}`);
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif] flex flex-col pt-16">
      {/* ────────────────────────────────────────────────────────────
          UNIFIED 3-COLUMN STUDIO LAYOUT
      ──────────────────────────────────────────────────────────── */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 h-[calc(100vh-4rem)] overflow-hidden">
        
        {/* ════════════════════════════════════════════════════════════
            CỘT 1 (3/12 Col ~ 25%): MY CV & PROFILE
        ════════════════════════════════════════════════════════════ */}
        <aside className="lg:col-span-3 border-r border-[#1E293B] bg-[#0c101b] flex flex-col h-full overflow-y-auto scrollbar-thin">
          <div className="p-4 sm:p-5 space-y-5">
            
            {/* 1.1 Uploaded File Info Card */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-[#10b981]/15 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center shrink-0 font-bold text-xs font-['JetBrains_Mono',monospace]">
                    PDF
                  </div>
                  <div className="min-w-0">
                    <h2 className="text-xs font-bold text-[#f8fafc] truncate font-['Plus_Jakarta_Sans',sans-serif]">
                      {fileName}
                    </h2>
                    <p className="text-[10px] text-[#94a3b8] flex items-center gap-1.5 pt-0.5">
                      <span>Đã bóc tách {totalSkillsCount} kỹ năng</span>
                      <span>•</span>
                      <span className="text-[#4edea3] font-['JetBrains_Mono',monospace]">
                        {profile.metadata.extraction_confidence}% tin cậy
                      </span>
                    </p>
                  </div>
                </div>
                <span className="text-[10px] text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-2 py-0.5 rounded font-['JetBrains_Mono',monospace] shrink-0">
                  Đã chuẩn hóa
                </span>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(true)}
                  className="bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] hover:border-[#10b981]/40 text-[#dfe2ef] text-[11px] font-medium py-1.5 rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <Upload className="w-3 h-3 text-[#4edea3]" />
                  Thay CV Khác
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(true)}
                  className="bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] hover:border-[#10b981]/40 text-[#dfe2ef] text-[11px] font-medium py-1.5 rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <Edit3 className="w-3 h-3 text-[#38bdf8]" />
                  Xem / Chỉnh Sửa
                </button>
              </div>
            </div>

            {/* 1.2 Candidate Identity Card */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    {profile.personal_info.full_name || "Ứng viên"}
                  </h3>
                  <span className="text-[10px] text-[#38bdf8] bg-[#0284c7]/10 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                    {profile.metadata.total_experience_years} năm KN
                  </span>
                </div>
                <p className="text-xs text-[#4edea3] font-medium pt-0.5">
                  {profile.summary.detected_title || "Software Engineer"}
                </p>
              </div>

              {/* Contact details */}
              <div className="space-y-1.5 text-[11px] text-[#94a3b8] pt-1 border-t border-[#1E293B]">
                {profile.personal_info.email && (
                  <div className="flex items-center gap-2 truncate">
                    <Mail className="w-3 h-3 text-[#64748b] shrink-0" />
                    <span className="truncate">{profile.personal_info.email}</span>
                  </div>
                )}
                {profile.personal_info.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3 h-3 text-[#64748b] shrink-0" />
                    <span>{profile.personal_info.phone}</span>
                  </div>
                )}
                {profile.personal_info.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3 h-3 text-[#64748b] shrink-0" />
                    <span>{profile.personal_info.location}</span>
                  </div>
                )}
              </div>
            </div>

            {/* 1.3 ATS Score Breakdown Gauge */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Điểm Đánh Giá ATS
                </span>
                <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">
                  82 / 100
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2 bg-[#181b25] rounded-full overflow-hidden border border-[#1E293B] mb-3.5">
                <div className="w-[82%] h-full bg-[#10b981] rounded-full"></div>
              </div>

              {/* 3 Metric Axes */}
              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8] text-[11px]">Kỹ năng công nghệ</span>
                  <span className="text-[#4edea3] font-semibold font-['JetBrains_Mono',monospace] text-[11px]">18/20 (90%)</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8] text-[11px]">Tác động định lượng</span>
                  <span className="text-[#f59e0b] font-semibold font-['JetBrains_Mono',monospace] text-[11px]">12/20 (60% ⚠)</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8] text-[11px]">Cấu trúc chuẩn ATS</span>
                  <span className="text-[#4edea3] font-semibold font-['JetBrains_Mono',monospace] text-[11px]">19/20 (95%)</span>
                </div>
              </div>
            </div>

            {/* 1.4 Dynamic 8-Groups Skills Taxonomy */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Kỹ Năng Đã Bóc Tách ({totalSkillsCount})
                </span>
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(true)}
                  className="text-[10px] text-[#4edea3] hover:underline"
                >
                  Sửa
                </button>
              </div>

              <div className="space-y-3">
                {(Object.keys(SKILL_CATEGORY_LABELS) as SkillCategoryKey[]).map((key) => {
                  const items = profile.skills_taxonomy[key] || [];
                  if (items.length === 0) return null;
                  const meta = SKILL_CATEGORY_LABELS[key];

                  return (
                    <div key={key}>
                      <div className="text-[10px] text-[#94a3b8] mb-1 font-medium flex items-center justify-between">
                        <span>{meta.title}:</span>
                        <span className="font-['JetBrains_Mono',monospace]">{items.length}</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {items.map((skill) => (
                          <span
                            key={skill}
                            className={`px-2 py-0.5 rounded text-[11px] font-['JetBrains_Mono',monospace] border ${meta.color}`}
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 1.5 Work Experience Timeline */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
              <div className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Kinh Nghiệm Làm Việc ({profile.work_experience.length})
              </div>
              <div className="space-y-3 border-l-2 border-[#1E293B] pl-3 ml-1">
                {profile.work_experience.length === 0 ? (
                  <p className="text-[11px] text-[#64748b] italic">Chưa có kinh nghiệm ghi nhận</p>
                ) : (
                  profile.work_experience.map((exp, idx) => (
                    <div key={idx} className="space-y-0.5">
                      <div className="text-xs font-bold text-[#f8fafc]">{exp.role}</div>
                      <div className="text-[11px] text-[#4edea3]">
                        {exp.company} • {exp.start_date} - {exp.is_current ? "Hiện tại" : exp.end_date || "Nay"}
                      </div>
                      {exp.raw_bullets && exp.raw_bullets.length > 0 && (
                        <p className="text-[11px] text-[#94a3b8] line-clamp-2 leading-relaxed pt-0.5">
                          {exp.raw_bullets[0]}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 1.6 Education & Certifications */}
            {profile.education.length > 0 && (
              <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-2">
                <div className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Học Vấn &amp; Bằng Cấp
                </div>
                {profile.education.map((edu, idx) => (
                  <div key={idx} className="text-xs">
                    <div className="font-semibold text-[#f8fafc]">{edu.institution}</div>
                    <div className="text-[11px] text-[#94a3b8]">
                      {edu.degree} {edu.field_of_study && `• ${edu.field_of_study}`}
                      {edu.end_year && ` (${edu.end_year})`}
                    </div>
                  </div>
                ))}
              </div>
            )}

          </div>
        </aside>

        {/* ════════════════════════════════════════════════════════════
            CỘT 2 (5/12 Col ~ 42%): AI ASSISTANT & STAR REASONING
        ════════════════════════════════════════════════════════════ */}
        <main className="lg:col-span-5 flex flex-col h-full bg-[#090D16] border-r border-[#1E293B]">
          
          {/* 2.1 Chat Header */}
          <div className="h-14 px-6 border-b border-[#1E293B] bg-[#0c101b] flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#10b981] text-[#090D16] flex items-center justify-center font-bold text-sm">
                AI
              </div>
              <div>
                <h1 className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                  Trợ Lý Tối Ưu Hóa Nghề Nghiệp AI
                </h1>
                <div className="flex items-center gap-1.5 text-[10px] text-[#4edea3]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse"></span>
                  Đang phân tích CV và so khớp {jobsList.length} việc làm
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsReasoningOpen(!isReasoningOpen)}
              className="text-[11px] text-[#94a3b8] hover:text-[#4edea3] border border-[#1E293B] px-2.5 py-1 rounded-lg bg-[#181b25] transition-colors"
            >
              {isReasoningOpen ? "Ẩn suy luận" : "Hiện suy luận AI"}
            </button>
          </div>

          {/* 2.2 Chat Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 scrollbar-thin">
            
            {/* AI Welcome Message */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-2xl p-4 sm:p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
                  <span className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    CareerPilot AI Analyzer
                  </span>
                </div>
                <span className="text-[10px] text-[#94a3b8] font-['JetBrains_Mono',monospace]">10:30 AM</span>
              </div>
              
              <p className="text-xs sm:text-sm text-[#dfe2ef] leading-relaxed">
                Chào <span className="text-[#4edea3] font-semibold">{profile.personal_info.full_name}</span>! Tôi đã bóc tách hồ sơ CV của bạn với độ tin cậy <strong className="text-[#4edea3]">{profile.metadata.extraction_confidence}%</strong>. Bạn có thể chọn bất kỳ công việc nào ở Cột 3 để tôi tiến hành chấm điểm ATS chuyên sâu và đề xuất cách viết lại đạn STAR.
              </p>
            </div>

            {/* AI Deep Reasoning Chain Block */}
            {isReasoningOpen && (
              <div className="bg-[#0c101b] border border-[#10b981]/30 rounded-xl p-4 space-y-3 font-['JetBrains_Mono',monospace]">
                <div className="flex items-center justify-between text-xs text-[#4edea3] font-bold">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-ping"></span>
                    <span>AI REASONING TRACE (Chuỗi suy luận ATS)</span>
                  </div>
                  <span className="text-[10px] bg-[#10b981]/10 px-2 py-0.5 rounded border border-[#10b981]/30">
                    Confidence: {profile.metadata.extraction_confidence}%
                  </span>
                </div>

                <div className="text-[11px] text-[#94a3b8] space-y-2 border-l-2 border-[#1E293B] pl-3">
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">1. Nhận diện cấu trúc:</span> Định dạng <code className="text-[#4edea3]">{profile.metadata.cv_format_type}</code>, ngôn ngữ <code className="text-[#38bdf8]">{profile.metadata.cv_language}</code>.
                  </p>
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">2. Phân nhóm kỹ năng:</span> Nhận diện thành công {totalSkillsCount} kỹ năng qua chuẩn 8 nhóm.
                  </p>
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">3. Khuyến nghị STAR:</span> Điểm số tác động định lượng cần bổ sung thêm số liệu % tăng trưởng hoặc doanh số.
                  </p>
                </div>
              </div>
            )}

          </div>

          {/* 2.3 Chat Input Bar */}
          <div className="p-4 border-t border-[#1E293B] bg-[#0c101b] shrink-0">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                setChatInput("");
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                placeholder="Hỏi AI về cách tối ưu CV, so khớp JD, hoặc viết lại đạn STAR..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                className="flex-1 bg-[#181b25] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-[#f8fafc] placeholder-[#64748b] focus:outline-none focus:border-[#10b981] transition-colors"
              />
              <button
                type="submit"
                className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] px-4 py-2.5 rounded-xl text-xs font-bold transition-colors shrink-0 flex items-center gap-1.5"
              >
                <span>Gửi</span>
              </button>
            </form>
          </div>
        </main>

        {/* ════════════════════════════════════════════════════════════
            CỘT 3 (4/12 Col ~ 33%): JOB MATCHING & ATS STUDIO
        ════════════════════════════════════════════════════════════ */}
        <aside className="lg:col-span-4 bg-[#0c101b] flex flex-col h-full overflow-hidden">
          
          {/* 3.1 Right Column Tab Header */}
          <div className="h-14 px-4 sm:px-6 border-b border-[#1E293B] bg-[#0c101b] flex items-center justify-between shrink-0">
            <div className="flex gap-2 bg-[#111827] p-1 rounded-lg border border-[#1E293B]">
              <button
                type="button"
                onClick={() => setActiveRightTab("jobs")}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  activeRightTab === "jobs"
                    ? "bg-[#181b25] text-[#4edea3] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#dfe2ef]"
                }`}
              >
                Việc Làm Phù Hợp ({jobsList.length})
              </button>
              <button
                type="button"
                onClick={() => setActiveRightTab("studio")}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  activeRightTab === "studio"
                    ? "bg-[#181b25] text-[#4edea3] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#dfe2ef]"
                }`}
              >
                Studio Tinh Chỉnh STAR
              </button>
            </div>
          </div>

          {/* 3.2 Right Tab Content */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 scrollbar-thin">
            
            {/* TAB: MATCHED JOBS LIST */}
            {activeRightTab === "jobs" && (
              <div className="space-y-4">
                <div className="text-[11px] text-[#94a3b8]">
                  So khớp tự động dựa trên hồ sơ của <strong className="text-[#f8fafc]">{profile.personal_info.full_name}</strong>:
                </div>

                {jobsList.map((job) => (
                  <div
                    key={job.id}
                    className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 rounded-xl p-4 transition-all duration-200 shadow-sm space-y-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                          {job.title}
                        </h4>
                        <p className="text-[11px] text-[#94a3b8] pt-0.5">
                          {job.company} • {job.location}
                        </p>
                      </div>
                      <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace] bg-[#10b981]/10 px-2 py-0.5 rounded border border-[#10b981]/30 shrink-0">
                        {job.matchScore}% Match
                      </span>
                    </div>

                    <div className="text-[11px] text-[#38bdf8] font-semibold font-['JetBrains_Mono',monospace]">
                      {job.salary}
                    </div>

                    {/* Matched skills tags */}
                    <div className="flex flex-wrap gap-1">
                      {job.matchedSkills.map((s) => (
                        <span
                          key={s}
                          className="px-1.5 py-0.5 bg-[#181b25] border border-[#1E293B] text-[#dfe2ef] rounded text-[10px] font-['JetBrains_Mono',monospace]"
                        >
                          {s}
                        </span>
                      ))}
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-2 pt-1 border-t border-[#1E293B]">
                      <button
                        type="button"
                        onClick={() => handleOpenJobDetail(job)}
                        className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] text-[11px] font-medium py-1.5 rounded-lg transition-colors text-center"
                      >
                        Chi Tiết JD
                      </button>
                      <button
                        type="button"
                        onClick={() => handleTailorForJob(job)}
                        className="flex-1 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-[11px] font-bold py-1.5 rounded-lg transition-colors text-center"
                      >
                        Tối Ưu Cho Job
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: STAR STUDIO */}
            {activeRightTab === "studio" && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#f8fafc]">So Sánh Phiên Bản</span>
                  <div className="flex gap-1 bg-[#111827] p-1 rounded-lg border border-[#1E293B]">
                    <button
                      type="button"
                      onClick={() => setActiveVersion("v1")}
                      className={`px-2.5 py-1 text-[11px] font-medium rounded ${
                        activeVersion === "v1" ? "bg-[#181b25] text-[#dfe2ef]" : "text-[#94a3b8]"
                      }`}
                    >
                      Bản Gốc (V1)
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveVersion("v2")}
                      className={`px-2.5 py-1 text-[11px] font-bold rounded ${
                        activeVersion === "v2" ? "bg-[#10b981] text-[#090D16]" : "text-[#94a3b8]"
                      }`}
                    >
                      AI Tối Ưu (V2)
                    </button>
                  </div>
                </div>

                {/* Diff Comparison Card */}
                <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 space-y-3">
                  <div className="text-[11px] font-bold text-[#f8fafc]">
                    {activeVersion === "v1" ? "Đoạn mô tả gốc từ CV:" : "Đoạn mô tả được AI viết lại chuẩn STAR:"}
                  </div>
                  
                  <div className="p-3 bg-[#0c101b] border border-[#1E293B] rounded-lg text-xs leading-relaxed text-[#dfe2ef] font-['JetBrains_Mono',monospace]">
                    {activeVersion === "v1" ? (
                      <p className="text-[#94a3b8]">
                        "Phát triển backend cho hệ thống AI và RAG Pipelines, sử dụng FastAPI và PostgreSQL."
                      </p>
                    ) : (
                      <p className="text-[#4edea3]">
                        "Kiến trúc nền tảng AI Core phục vụ 30,000+ RPS bằng FastAPI &amp; Qdrant DB; tối ưu truy vấn RAG giúp giảm 40% độ trễ và tiết kiệm 35% chi phí hạ tầng."
                      </p>
                    )}
                  </div>

                  <div className="flex justify-end pt-2">
                    <button
                      type="button"
                      onClick={() => alert("Đã sao chép nội dung STAR!")}
                      className="px-3 py-1.5 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#4edea3] text-xs font-semibold rounded-lg transition-colors"
                    >
                      📋 Sao Chép Bản V2
                    </button>
                  </div>
                </div>
              </div>
            )}

          </div>
        </aside>

      </div>

      {/* ────────────────────────────────────────────────────────────
          JOB DETAIL DRAWER
      ──────────────────────────────────────────────────────────── */}
      {isDrawerOpen && selectedJob && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-[#0f1422] border-l border-[#1E293B] h-full p-6 flex flex-col shadow-2xl overflow-y-auto">
            {/* Drawer Header */}
            <div className="flex items-start justify-between pb-4 border-b border-[#1E293B]">
              <div>
                <h2 className="text-base font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                  {selectedJob.title}
                </h2>
                <p className="text-xs text-[#4edea3] font-medium pt-1">
                  {selectedJob.company} • {selectedJob.location}
                </p>
              </div>
              <button
                onClick={() => setIsDrawerOpen(false)}
                className="p-1 rounded-lg text-[#94a3b8] hover:text-[#f8fafc] hover:bg-[#181b25] transition-colors"
              >
                &times;
              </button>
            </div>

            {/* Drawer Body */}
            <div className="py-5 space-y-5 text-xs text-[#dfe2ef] leading-relaxed">
              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Mô Tả Công Việc
                </h3>
                <p className="text-[#94a3b8]">{selectedJob.description}</p>
              </div>

              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Yêu Cầu Kỹ Thuật
                </h3>
                <ul className="space-y-1.5 text-[#94a3b8] list-disc pl-4">
                  {selectedJob.requirements.map((req, i) => (
                    <li key={i}>{req}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Quyền Lợi &amp; Đãi Ngộ
                </h3>
                <ul className="space-y-1.5 text-[#94a3b8] list-disc pl-4">
                  {selectedJob.benefits.map((ben, i) => (
                    <li key={i}>{ben}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Drawer Footer Actions */}
            <div className="pt-4 border-t border-[#1E293B] flex gap-3 mt-auto">
              <button
                type="button"
                onClick={() => handleAskAiAboutJob(selectedJob)}
                className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] font-semibold py-2.5 rounded-lg text-xs transition-colors"
              >
                💬 Hỏi AI Về Job Này
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsDrawerOpen(false);
                  handleTailorForJob(selectedJob);
                }}
                className="flex-1 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold py-2.5 rounded-lg text-xs transition-colors shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
              >
                ⚡ Tối Ưu CV Ngay
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────
          UPLOAD CV MODAL
      ──────────────────────────────────────────────────────────── */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={handleUploadSuccess}
      />

      {/* ────────────────────────────────────────────────────────────
          PROFILE EDIT MODAL
      ──────────────────────────────────────────────────────────── */}
      <ProfileEditModal
        isOpen={isEditModalOpen}
        candidateId={candidateId}
        profile={profile}
        onClose={() => setIsEditModalOpen(false)}
        onSaved={handleProfileSaved}
      />

    </div>
  );
}
