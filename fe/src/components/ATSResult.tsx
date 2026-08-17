import React, { useState } from "react";
import {
  Award,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  TrendingUp,
  Briefcase,
  Layers,
  ArrowRight,
  RefreshCw,
  Lightbulb,
  FileCheck,
  Zap,
  Info,
} from "lucide-react";
import { JDMatchReport, SkillMatchItem } from "../types/ats";
import { STARModal } from "./STARModal";

interface ATSResultProps {
  report: JDMatchReport;
  onReset: () => void;
  targetRole?: string;
}

export const ATSResult: React.FC<ATSResultProps> = ({
  report,
  onReset,
  targetRole,
}) => {
  const [selectedMissingSkill, setSelectedMissingSkill] = useState<string | null>(null);
  const [isStarModalOpen, setIsStarModalOpen] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-500/40 bg-emerald-500/10";
    if (score >= 60) return "text-amber-400 border-amber-500/40 bg-amber-500/10";
    return "text-rose-400 border-rose-500/40 bg-rose-500/10";
  };

  const getGaugeStrokeColor = (score: number) => {
    if (score >= 80) return "#10b981"; // emerald-500
    if (score >= 60) return "#f59e0b"; // amber-500
    return "#f43f5e"; // rose-500
  };

  const handleOpenStar = (skillName: string) => {
    setSelectedMissingSkill(skillName);
    setIsStarModalOpen(true);
  };

  // SVG Gauge calculations
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (report.overall_score / 100) * circumference;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 backdrop-blur-md shadow-xl flex flex-col gap-6 animate-fadeIn">
      {/* Header with Title & Reset Button */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-[11px] font-bold">
              BÁO CÁO ATS CHUẨN QUỐC TẾ
            </span>
            <span className="text-xs text-slate-400 font-medium">50/30/20 Weighting</span>
          </div>
          <h2 className="text-base font-bold text-white mt-1">
            Kết Quả So Khớp: {report.jd_title || "Vị trí tuyển dụng"}
          </h2>
        </div>

        <button
          onClick={onReset}
          className="text-xs px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 border border-slate-700 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Phân tích JD khác
        </button>
      </div>

      {/* Hero: Score Gauge & Verdict Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
        {/* Radial Gauge */}
        <div className="flex flex-col items-center justify-center">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="56"
                cy="56"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="8"
                fill="transparent"
              />
              <circle
                cx="56"
                cy="56"
                r={radius}
                stroke={getGaugeStrokeColor(report.overall_score)}
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-2xl font-black text-white font-mono leading-none">
                {report.overall_score}
              </span>
              <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                Điểm ATS
              </span>
            </div>
          </div>
          <div className="mt-2 text-center">
            <span
              className={`inline-block px-3 py-0.5 rounded-full text-xs font-bold border ${getScoreColor(
                report.overall_score
              )}`}
            >
              Hạng {report.overall_grade}
            </span>
          </div>
        </div>

        {/* Verdict & Summary Description */}
        <div className="md:col-span-2 space-y-2 text-left">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            {report.verdict}
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            {report.experience_gap_analysis ||
              "Hệ thống đã phân tích hồ sơ của bạn với các tiêu chí bắt buộc và ưu tiên của nhà tuyển dụng."}
          </p>
        </div>
      </div>

      {/* 3 Pillars Breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Pillar 1: Skills */}
        <div className="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              Kỹ năng (50%)
            </span>
            <span className="text-xs font-bold text-cyan-400 font-mono">
              {report.skill_match_score}/100
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-cyan-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.skill_match_score}%` }}
            />
          </div>
        </div>

        {/* Pillar 2: Experience */}
        <div className="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-indigo-400" />
              Kinh nghiệm (30%)
            </span>
            <span className="text-xs font-bold text-indigo-400 font-mono">
              {report.experience_fit_score}/100
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-indigo-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.experience_fit_score}%` }}
            />
          </div>
        </div>

        {/* Pillar 3: Format & Metrics */}
        <div className="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5 text-emerald-400" />
              Định dạng & STAR (20%)
            </span>
            <span className="text-xs font-bold text-emerald-400 font-mono">
              {report.format_quality_score}/100
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.format_quality_score}%` }}
            />
          </div>
        </div>
      </div>

      {/* Interactive Skill Chips Section */}
      <div className="space-y-4">
        {/* Missing Skills (Clickable for STAR generation) */}
        {report.missing_skills && report.missing_skills.length > 0 && (
          <div className="p-4 bg-rose-950/20 border border-rose-900/40 rounded-xl space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4" />
                Kỹ Năng Còn Thiếu ({report.missing_skills.length}) — Click để sinh câu chuẩn STAR
              </span>
              <span className="text-[10px] text-rose-400/80 uppercase tracking-wider font-semibold">
                Ưu tiên bổ sung
              </span>
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              {report.missing_skills.map((skill, idx) => (
                <button
                  key={idx}
                  onClick={() => handleOpenStar(skill.skill_name)}
                  className="group px-3 py-1.5 rounded-lg bg-rose-900/30 hover:bg-rose-800/50 border border-rose-700/50 hover:border-rose-500 text-rose-200 text-xs font-medium transition-all flex items-center gap-1.5 shadow-sm hover:shadow-rose-900/40 cursor-pointer"
                  title={`Nhấp để sinh câu STAR mẫu cho kỹ năng: ${skill.skill_name}`}
                >
                  <span>🔴 {skill.skill_name}</span>
                  {skill.importance === "required" && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 font-bold">
                      Bắt buộc
                    </span>
                  )}
                  <Zap className="w-3 h-3 text-rose-400 group-hover:scale-125 transition-transform" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Matched Skills (Exact + Semantic) */}
        {report.matched_skills && report.matched_skills.length > 0 && (
          <div className="p-4 bg-slate-950/40 border border-slate-800 rounded-xl space-y-2.5">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Kỹ Năng Đã Khớp ({report.matched_skills.length})
            </span>

            <div className="flex flex-wrap gap-2 pt-1">
              {report.matched_skills.map((skill, idx) => (
                <div
                  key={idx}
                  className={`px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 border ${
                    skill.match_type === "exact"
                      ? "bg-emerald-950/30 border-emerald-800/50 text-emerald-300"
                      : "bg-amber-950/30 border-amber-800/50 text-amber-300"
                  }`}
                  title={skill.cv_evidence || skill.jd_requirement}
                >
                  <span>{skill.match_type === "exact" ? "🟢" : "🟡"}</span>
                  <span>{skill.skill_name}</span>
                  {skill.match_type === "semantic" && (
                    <span className="text-[10px] text-amber-400 font-normal">
                      (Tương đương)
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Excess Skills */}
        {report.excess_skills && report.excess_skills.length > 0 && (
          <div className="p-3 bg-slate-950/20 border border-slate-800/60 rounded-xl space-y-2">
            <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
              <Info className="w-3.5 h-3.5 text-slate-500" />
              Kỹ năng khác trong CV (Ngoài phạm vi JD này):
            </span>
            <div className="flex flex-wrap gap-1.5">
              {report.excess_skills.slice(0, 10).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-slate-800/60 text-slate-400 text-[11px] border border-slate-700/40"
                >
                  ⚪ {skill}
                </span>
              ))}
              {report.excess_skills.length > 10 && (
                <span className="text-[11px] text-slate-500 self-center">
                  +{report.excess_skills.length - 10} kỹ năng khác
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Top 3 Actionable Recommendations */}
      {report.top_recommendations && report.top_recommendations.length > 0 && (
        <div className="p-4 bg-gradient-to-br from-cyan-950/30 via-slate-900 to-indigo-950/30 border border-cyan-800/40 rounded-xl space-y-3">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
              Top 3 Hành Động Tăng Điểm ATS (+15 - 30 điểm)
            </h4>
          </div>

          <div className="space-y-2">
            {report.top_recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-200">
                <span className="w-5 h-5 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 font-bold flex items-center justify-center flex-shrink-0 text-[11px]">
                  {idx + 1}
                </span>
                <p className="leading-relaxed pt-0.5">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* STAR Generator Modal */}
      <STARModal
        isOpen={isStarModalOpen}
        onClose={() => setIsStarModalOpen(false)}
        initialSkillOrBullet={selectedMissingSkill}
        targetRole={targetRole || report.jd_title || "Software Engineer"}
      />
    </div>
  );
};
