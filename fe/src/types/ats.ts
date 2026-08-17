/**
 * Canonical ATS and STAR Types
 * Strictly mirrors backend schemas in ai/models/jd.py, ai/models/star.py, and be/api/v1/schemas.py
 */

export interface SkillMatchItem {
  skill_name: string;
  match_type: "exact" | "semantic" | "missing";
  cv_evidence: string | null;
  jd_requirement: string;
  importance: "required" | "preferred";
}

export interface JDMatchReport {
  overall_score: number;
  overall_grade: string;
  verdict: string;

  skill_match_score: number;
  experience_fit_score: number;
  format_quality_score: number;

  matched_skills: SkillMatchItem[];
  missing_skills: SkillMatchItem[];
  excess_skills: string[];

  top_recommendations: string[];
  experience_gap_analysis: string;

  jd_title: string;
  analysis_language: string;
}

export interface STARResult {
  original: string;
  star_v1: string;
  star_v2: string;
  action_verb: string;
  improvements: string[];
}

export interface ATSHistoryItem {
  id: number;
  candidate_id: number;
  ats_score: number;
  ats_grade: string;
  report_json: string;
  created_at?: string;
}
