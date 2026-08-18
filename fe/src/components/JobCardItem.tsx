import React from "react";
import { JobItem } from "../types/job";

interface JobCardItemProps {
  job: JobItem;
  onViewDetails: (job: JobItem) => void;
  onApplyJd: (job: JobItem) => void;
}

export default function JobCardItem({
  job,
  onViewDetails,
  onApplyJd,
}: JobCardItemProps) {
  return (
    <div className="bg-[#111827] border border-[#1e293b] hover:border-emerald-500/50 rounded-xl p-3.5 transition-all shadow-md space-y-3 group text-[#f8fafc]">
      {/* Header Info */}
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <span
              className="text-[10px] font-bold uppercase px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]"
              style={{
                backgroundColor: `${job.platform_color}20`,
                color: job.platform_color,
                border: `1px solid ${job.platform_color}50`,
              }}
            >
              {job.platform}
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
              {job.domain}
            </span>
            <span className="text-[10px] text-slate-400 font-['JetBrains_Mono',monospace]">
              • {job.posted_date}
            </span>
          </div>

          <h4 className="text-xs sm:text-sm font-bold text-white group-hover:text-emerald-400 transition-colors leading-snug font-['Plus_Jakarta_Sans',sans-serif]">
            {job.title}
          </h4>
          <p className="text-xs text-slate-300 font-medium">
            🏢 {job.company}
          </p>
        </div>
      </div>

      {/* Highlights Bar */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-300 bg-[#090d16] p-2 rounded-lg border border-slate-800/80">
        <div className="flex items-center gap-1 text-amber-300 font-medium">
          <span>📅</span>
          <span>{job.experience_required}</span>
        </div>
        <div className="flex items-center gap-1 text-emerald-400 font-semibold">
          <span>💰</span>
          <span>{job.salary_range}</span>
        </div>
        <div className="flex items-center gap-1 text-slate-400">
          <span>📍</span>
          <span className="truncate max-w-[140px]">{job.location}</span>
        </div>
      </div>

      {/* Semantic Match Score & AI Fit Highlights (Cross-Encoder) */}
      {job.semantic_fit_score !== undefined && job.semantic_fit_score !== null && (
        <div className="p-2 bg-emerald-950/30 border border-emerald-500/30 rounded-lg space-y-1">
          <div className="flex items-center justify-between text-[11px]">
            <span className="flex items-center gap-1 font-bold text-emerald-400">
              <span>🎯</span>
              <span>Độ khớp ngữ nghĩa:</span>
            </span>
            <span className="font-mono font-black text-emerald-300">
              {job.semantic_fit_score}% Fit
            </span>
          </div>
          {job.fit_highlights && job.fit_highlights.length > 0 && (
            <ul className="text-[10px] text-slate-300 space-y-0.5 list-disc list-inside">
              {job.fit_highlights.map((h, i) => (
                <li key={i} className="truncate">{h}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {job.skills.slice(0, 4).map((s, idx) => (
            <span
              key={idx}
              className="text-[10px] bg-slate-800/80 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700 font-['JetBrains_Mono',monospace]"
            >
              {s}
            </span>
          ))}
          {job.skills.length > 4 && (
            <span className="text-[10px] text-slate-400 px-1 py-0.5">
              +{job.skills.length - 4}
            </span>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-800/80">
        <a
          href={job.job_url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Mở bài đăng tuyển dụng ${job.title}`}
          className="text-[11px] text-sky-400 hover:text-sky-300 underline flex items-center gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <span>🔗 Link bài đăng</span>
          <span>↗</span>
        </a>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onViewDetails(job)}
            aria-label={`Xem chi tiết tin tuyển dụng ${job.title}`}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold transition-colors border border-slate-700 flex items-center gap-1"
          >
            <span>👁️ Xem chi tiết</span>
          </button>

          <button
            type="button"
            onClick={() => onApplyJd(job)}
            aria-label={`Nạp JD ${job.title} để so khớp ATS`}
            className="px-2.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-[11px] font-bold transition-all shadow-sm flex items-center gap-1"
          >
            <span>🎯 Nạp JD</span>
          </button>
        </div>
      </div>
    </div>
  );
}
