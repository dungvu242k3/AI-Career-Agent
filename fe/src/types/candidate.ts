/**
 * Canonical Candidate Profile (v3) TypeScript Types
 * Strictly mirrors backend schemas in ai/models/candidate.py and be/api/v1/schemas.py
 */

export interface PersonalInfo {
  full_name: string;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  date_of_birth: string | null;
}

export interface SummarySection {
  summary_text: string | null;
  detected_title: string;
}

export interface EducationItem {
  institution: string;
  degree: string;
  field_of_study: string;
  start_year: number | null;
  end_year: number | null;
  gpa: string | null;
}

export interface WorkExperienceItem {
  company: string;
  role: string;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  location: string | null;
  raw_bullets: string[];
}

export interface ProjectItem {
  name: string;
  description: string;
  role: string | null;
  technologies: string[];
  url: string | null;
  highlights: string[];
}

export interface SkillsTaxonomy {
  programming_languages: string[];
  frameworks: string[];
  databases: string[];
  devops_and_cloud: string[];
  ai_and_ml: string[];
  testing: string[];
  tools: string[];
  soft_skills: string[];
}

export interface CertificationItem {
  name: string;
  issuer: string | null;
  issue_date: string | null;
  credential_url: string | null;
}

export interface LanguageItem {
  language: string;
  proficiency: string;
}

export interface AdditionalSectionItem {
  section_name: string;
  section_type: "awards" | "activities" | "publications" | "interests" | "references" | "other";
  items: string[];
}

export interface CVMetadata {
  total_experience_years: number;
  cv_language: "en" | "vi" | "mixed";
  cv_format_type: "chronological" | "functional" | "academic" | "creative" | "combination";
  has_clear_sections: boolean;
  extraction_confidence: number;
  detected_sections: string[];
}

export interface CandidateProfile {
  personal_info: PersonalInfo;
  summary: SummarySection;
  education: EducationItem[];
  work_experience: WorkExperienceItem[];
  projects: ProjectItem[];
  skills_taxonomy: SkillsTaxonomy;
  certifications: CertificationItem[];
  languages: LanguageItem[];
  additional_sections: AdditionalSectionItem[];
  metadata: CVMetadata;
}

export interface UploadResponse {
  candidate_id: number;
  filename: string;
  text_length: number;
  profile: CandidateProfile;
  storage_key?: string | null;
  presigned_url?: string | null;
  is_cached: boolean;
}

export interface UpdateProfileRequest {
  profile: CandidateProfile;
}

export interface MessageResponse {
  message: string;
  candidate_id: number | null;
}

export type SkillCategoryKey = keyof SkillsTaxonomy;

export const SKILL_CATEGORY_LABELS: Record<SkillCategoryKey, { title: string; color: string }> = {
  programming_languages: { title: "Ngôn Ngữ Lập Trình", color: "text-[#4edea3] bg-[#10b981]/10 border-[#10b981]/30" },
  frameworks: { title: "Frameworks & Thư Viện", color: "text-[#38bdf8] bg-[#0284c7]/10 border-[#0284c7]/30" },
  databases: { title: "Cơ Sở Dữ Liệu & Cache", color: "text-[#a78bfa] bg-[#7c3aed]/10 border-[#7c3aed]/30" },
  devops_and_cloud: { title: "DevOps & Đám Mây", color: "text-[#fb923c] bg-[#ea580c]/10 border-[#ea580c]/30" },
  ai_and_ml: { title: "AI, ML & Data Engineering", color: "text-[#ec4899] bg-[#db2777]/10 border-[#db2777]/30" },
  testing: { title: "Kiểm Thử & QA", color: "text-[#34d399] bg-[#059669]/10 border-[#059669]/30" },
  tools: { title: "Công Cụ & Môi Trường", color: "text-[#94a3b8] bg-[#181b25] border-[#1E293B]" },
  soft_skills: { title: "Kỹ Năng Mềm & Quản Trị", color: "text-[#facc15] bg-[#ca8a04]/10 border-[#ca8a04]/30" },
};
