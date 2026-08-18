export interface InterviewerPersona {
  name: string;
  role: string;
  avatar_color: string;
  style: string;
}

export interface QuestionItem {
  id: string;
  interviewer: InterviewerPersona;
  question_text: string;
  context_hint: string;
  category: "system_design" | "deep_technical" | "behavioral_star" | "culture_fit" | "stress_handling";
  difficulty: "easy" | "medium" | "hard";
}

export interface TurnEvaluation {
  score: number;
  technical_depth_score: number;
  star_structure_score: number;
  confidence_score: number;
  adaptability_score: number;
  feedback: string;
  key_strengths: string[];
  improvement_areas: string[];
  ideal_star_answer: string;
}

export interface InterviewTurn {
  turn_index: number;
  question: QuestionItem;
  candidate_answer?: string | null;
  evaluation?: TurnEvaluation | null;
  generated_by?: "template" | "llm" | "hybrid";
  follow_up_of?: number | null;
  bonus_points?: number;
  is_llm_evaluated?: boolean;
}

export interface CandidateAssessmentReport {
  session_id: string;
  candidate_name: string;
  target_role: string;
  total_turns_completed: number;
  overall_score: number;
  overall_grade: "A+" | "A" | "B+" | "B" | "C";
  verdict: string;
  technical_average: number;
  star_structure_average: number;
  confidence_average: number;
  adaptability_average: number;
  top_strengths: string[];
  critical_growth_areas: string[];
  actionable_prep_tips: string[];
}

export interface InterviewSession {
  session_id: string;
  candidate_id: string;
  candidate_name: string;
  target_role: string;
  domain?: string;
  tier?: "free" | "pro";
  max_turns?: number;
  is_quota_reached?: boolean;
  turns: InterviewTurn[];
  current_turn_index: number;
  is_completed: boolean;
  final_report?: CandidateAssessmentReport | null;
}
