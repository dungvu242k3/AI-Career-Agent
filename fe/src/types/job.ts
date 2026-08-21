export interface JobItem {
  id: string;
  title: string;
  company: string;
  platform: "ITviec" | "TopCV" | "VietnamWorks" | "LinkedIn" | string;
  platform_color: string;
  experience_required: string;
  min_years_exp: number;
  max_years_exp: number;
  domain: string;
  location: string;
  salary_range: string;
  job_url: string;
  skills: string[];
  description: string;
  requirements: string;
  benefits: string;
  posted_date: string;
  semantic_fit_score?: number;
  /** Explainable lexical discovery hint; not a hiring or ATS decision. */
  heuristic_fit_score?: number;
  fit_highlights?: string[];
}

export interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
  intent?: string;
  jobs?: JobItem[];
}
