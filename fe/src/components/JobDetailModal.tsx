import React from "react";
import { JobItem } from "../types/job";

interface JobDetailModalProps {
  job: JobItem | null;
  isOpen: boolean;
  onClose: () => void;
  onApplyJdToWorkspace: (job: JobItem) => void;
}

export default function JobDetailModal({
  job,
  isOpen,
  onClose,
  onApplyJdToWorkspace,
}: JobDetailModalProps) {
  if (!isOpen || !job) return null;

  const handleApplyClick = () => {
    onApplyJdToWorkspace(job);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-[#0f172a] border border-[#334155] w-full max-w-3xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden text-[#f8fafc]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 sm:p-6 border-b border-[#1e293b] bg-[#111827] flex items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span
                className="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full font-['JetBrains_Mono',monospace]"
                style={{
                  backgroundColor: `${job.platform_color}25`,
                  color: job.platform_color,
                  border: `1px solid ${job.platform_color}60`,
                }}
              >
                {job.platform}
              </span>
              <span className="text-[10px] uppercase tracking-wider bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                {job.domain}
              </span>
              <span className="text-xs text-slate-400 font-['JetBrains_Mono',monospace]">
                {job.posted_date}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white font-['Plus_Jakarta_Sans',sans-serif] leading-tight">
              {job.title}
            </h2>
            <p className="text-sm font-semibold text-emerald-400 mt-1">
              🏢 {job.company}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Đóng"
            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors shrink-0"
          >
            ✕
          </button>
        </div>

        {/* Quick Highlights Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-[#090d16] border-b border-[#1e293b] text-xs">
          <div className="flex items-center gap-2 bg-[#1e293b]/50 p-2.5 rounded-xl border border-slate-800">
            <span className="text-base">📅</span>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-bold">Kinh Nghiệm</div>
              <div className="font-semibold text-slate-200">{job.experience_required}</div>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-[#1e293b]/50 p-2.5 rounded-xl border border-slate-800">
            <span className="text-base">💰</span>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-bold">Mức Lương</div>
              <div className="font-semibold text-emerald-300">{job.salary_range}</div>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-[#1e293b]/50 p-2.5 rounded-xl border border-slate-800">
            <span className="text-base">📍</span>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-bold">Địa Điểm</div>
              <div className="font-semibold text-slate-200 truncate">{job.location}</div>
            </div>
          </div>
        </div>

        {/* Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6 scrollbar-thin text-xs sm:text-sm text-slate-300 leading-relaxed">
          {/* AI Semantic Fit Analysis if available */}
          {job.semantic_fit_score !== undefined && job.semantic_fit_score !== null && (
            <div className="p-3.5 bg-emerald-950/30 border border-emerald-500/30 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 font-bold text-emerald-400 text-xs">
                  <span>🎯</span>
                  <span>Đánh Giá Khớp Ngữ Nghĩa (Cross-Encoder AI):</span>
                </div>
                <span className="font-mono font-black text-sm text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/30">
                  {job.semantic_fit_score}% Phù hợp
                </span>
              </div>
              {job.fit_highlights && job.fit_highlights.length > 0 && (
                <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                  {job.fit_highlights.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Tech Stack */}
          {job.skills && job.skills.length > 0 && (
            <div>
              <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2 font-['JetBrains_Mono',monospace]">
                🛠️ Kỹ Năng / Tech Stack Trọng Tâm:
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {job.skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {job.description && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase text-emerald-400 tracking-wider font-['JetBrains_Mono',monospace]">
                📋 Mô Tả Công Việc &amp; Trách Nhiệm:
              </h3>
              <div className="p-4 rounded-xl bg-[#111827] border border-slate-800 whitespace-pre-line text-slate-200">
                {job.description}
              </div>
            </div>
          )}

          {/* Requirements */}
          {job.requirements && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase text-amber-400 tracking-wider font-['JetBrains_Mono',monospace]">
                🎯 Yêu Cầu Ứng Viên:
              </h3>
              <div className="p-4 rounded-xl bg-[#111827] border border-slate-800 whitespace-pre-line text-slate-200">
                {job.requirements}
              </div>
            </div>
          )}

          {/* Benefits */}
          {job.benefits && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase text-sky-400 tracking-wider font-['JetBrains_Mono',monospace]">
                🎁 Quyền Lợi &amp; Chế Độ Đãi Ngộ:
              </h3>
              <div className="p-4 rounded-xl bg-[#111827] border border-slate-800 whitespace-pre-line text-slate-200">
                {job.benefits}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="p-4 sm:p-5 border-t border-[#1e293b] bg-[#111827] flex flex-col sm:flex-row items-center justify-between gap-3">
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-sky-400 hover:text-sky-300 underline font-medium flex items-center gap-1.5 order-2 sm:order-1"
          >
            <span>🔗 Xem bài đăng gốc trên {job.platform}</span>
            <span>↗</span>
          </a>

          <div className="flex items-center gap-2 w-full sm:w-auto order-1 sm:order-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Đóng
            </button>

            <button
              type="button"
              onClick={handleApplyClick}
              className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
            >
              <span>🎯 Nạp JD Này Vào Workspace Để So Khớp</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
