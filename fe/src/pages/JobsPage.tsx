import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, Briefcase, Search, ArrowRight, UploadCloud, FileText } from "lucide-react";
import { getActiveCandidateLocally } from "../services/cvApi";

export default function JobsPage() {
  const navigate = useNavigate();
  const [customJd, setCustomJd] = useState("");
  const candidate = getActiveCandidateLocally();

  const handleStartMatching = (e: React.FormEvent) => {
    e.preventDefault();
    if (customJd.trim()) {
      // Navigate to workspace with tab ATS active
      navigate("/workspace");
    } else {
      navigate("/workspace");
    }
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────────
          MAIN CONTENT (JOBS ARENA)
      ──────────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16 max-w-[1000px] mx-auto px-6 md:px-12">
        {/* Banner */}
        <div className="mb-10 border-b border-[#1E293B] pb-8 text-center sm:text-left flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-3">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              AI ATS MATCHING ENGINE
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
              Trung Tâm So Khớp &amp; Thẩm Định JD
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1.5 font-['Inter',sans-serif]">
              Dán bất kỳ mô tả công việc (JD) nào để AI đối chiếu trực tiếp với CV của bạn theo tiêu chuẩn 50-30-20.
            </p>
          </div>

          <div className="shrink-0 flex items-center justify-center">
            {candidate.profile ? (
              <div className="bg-[#111827] border border-[#10b981]/40 rounded-xl p-3.5 text-xs text-left">
                <div className="text-[#94a3b8] text-[11px]">Hồ sơ đang kết nối:</div>
                <div className="font-bold text-[#f8fafc] pt-0.5">{candidate.profile.personal_info.full_name || "Ứng viên"}</div>
                <div className="text-[10px] text-[#4edea3] pt-0.5 font-['JetBrains_Mono',monospace]">
                  {candidate.profile.summary.detected_title || "Đã nạp CV"}
                </div>
              </div>
            ) : (
              <Link
                to="/workspace"
                className="bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-xs text-[#dfe2ef] px-4 py-2.5 rounded-xl font-semibold transition-colors inline-flex items-center gap-2"
              >
                <UploadCloud className="w-4 h-4 text-[#4edea3]" />
                <span>Nạp CV Để Bắt Đầu</span>
              </Link>
            )}
          </div>
        </div>

        {/* Quick JD Analyzer Box */}
        <div className="bg-[#111827] border border-[#1E293B] rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-600 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                Dán JD Mục Tiêu Để Phân Tích Độ Khớp
              </h2>
              <p className="text-xs text-[#94a3b8]">
                Hỗ trợ mô tả công việc từ TopCV, LinkedIn, ITviec, VietnamWorks, v.v.
              </p>
            </div>
          </div>

          <form onSubmit={handleStartMatching} className="space-y-4">
            <textarea
              rows={6}
              value={customJd}
              onChange={(e) => setCustomJd(e.target.value)}
              placeholder="Dán nội dung mô tả công việc (JD), yêu cầu kỹ năng, trách nhiệm vào đây..."
              className="w-full bg-[#0c101b] border border-[#1E293B] focus:border-[#10b981] rounded-xl p-4 text-xs text-[#dfe2ef] placeholder-[#64748b] font-['Inter',sans-serif] focus:outline-none transition-colors leading-relaxed resize-y"
            />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
              <div className="text-[11px] text-[#94a3b8] flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-[#4edea3]" />
                <span>Hoặc tải tệp JD định dạng PDF / Word trực tiếp trong Workspace</span>
              </div>

              <button
                type="submit"
                className="bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-bold px-6 py-3 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]"
              >
                <span>Chuyển Sang Workspace So Khớp</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>

        {/* 3 Value Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
          <div className="bg-[#111827]/60 border border-[#1E293B] p-5 rounded-xl space-y-2">
            <div className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">
              01. ĐỐI SOÁT 3 TẦNG
            </div>
            <h3 className="text-sm font-bold text-[#f8fafc]">Trọng Số 50 / 30 / 20</h3>
            <p className="text-xs text-[#94a3b8] leading-relaxed">
              Tính điểm chuẩn hóa: 50% Kỹ năng công nghệ, 30% Số năm &amp; chiều sâu kinh nghiệm, 20% Cấu trúc chuẩn STAR.
            </p>
          </div>

          <div className="bg-[#111827]/60 border border-[#1E293B] p-5 rounded-xl space-y-2">
            <div className="text-xs font-bold text-cyan-400 font-['JetBrains_Mono',monospace]">
              02. PHÂN LOẠI 4 MÀU
            </div>
            <h3 className="text-sm font-bold text-[#f8fafc]">Bản Đồ Kỹ Năng</h3>
            <p className="text-xs text-[#94a3b8] leading-relaxed">
              Nhận diện rõ ràng kỹ năng khớp 100% 🟢, khớp ngữ nghĩa 🟡, kỹ năng thiếu 🔴 và kỹ năng bổ trợ ⚪.
            </p>
          </div>

          <div className="bg-[#111827]/60 border border-[#1E293B] p-5 rounded-xl space-y-2">
            <div className="text-xs font-bold text-indigo-400 font-['JetBrains_Mono',monospace]">
              03. BIẾN HÓA STAR
            </div>
            <h3 className="text-sm font-bold text-[#f8fafc]">1-Click Tối Ưu Đạn CV</h3>
            <p className="text-xs text-[#94a3b8] leading-relaxed">
              Bấm vào kỹ năng thiếu để AI sinh ngay câu thành tựu định lượng đo lường bằng số liệu thực tế.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
