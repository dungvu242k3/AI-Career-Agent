import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Upload,
  FileText,
  Edit3,
  Sparkles,
  MapPin,
  Mail,
  Phone,
  Briefcase,
  Layers,
  ArrowRight,
} from "lucide-react";
import { UploadModal } from "../components/UploadModal";
import { ProfileEditModal } from "../components/ProfileEditModal";
import { JDInput } from "../components/JDInput";
import { ATSResult } from "../components/ATSResult";
import { STARModal } from "../components/STARModal";
import {
  CandidateProfile,
  UploadResponse,
  SKILL_CATEGORY_LABELS,
  SkillCategoryKey,
} from "../types/candidate";
import { JDMatchReport } from "../types/ats";
import { getActiveCandidateLocally } from "../services/cvApi";

export default function WorkspacePage() {
  // Navigation & Tabs
  const [activeRightTab, setActiveRightTab] = useState<"ats" | "jobs" | "studio">("ats");
  const [chatInput, setChatInput] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);

  // ATS & STAR State
  const [atsReport, setAtsReport] = useState<JDMatchReport | null>(null);
  const [isAtsLoading, setIsAtsLoading] = useState(false);
  const [isStandaloneStarOpen, setIsStandaloneStarOpen] = useState(false);

  // Dynamic Candidate State (100% from Upload or localStorage)
  const [candidateId, setCandidateId] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);

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
    setAtsReport(null); // Reset previous analysis when new CV is uploaded
  };

  const handleProfileSaved = (updated: CandidateProfile) => {
    setProfile(updated);
  };

  // Compute total skills count across 8 buckets
  const totalSkillsCount = profile
    ? Object.values(profile.skills_taxonomy).reduce(
        (acc, list) => acc + (Array.isArray(list) ? list.length : 0),
        0
      )
    : 0;

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
            
            {/* EMPTY STATE WHEN NO CV UPLOADED YET */}
            {!profile ? (
              <div className="bg-[#111827] border border-[#1E293B] border-dashed rounded-2xl p-6 text-center space-y-4 shadow-sm">
                <div className="w-14 h-14 mx-auto rounded-2xl bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center">
                  <FileText className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    Chưa Có Hồ Sơ CV
                  </h3>
                  <p className="text-xs text-[#94a3b8] mt-1.5 leading-relaxed">
                    Tải lên CV (PDF hoặc Word &lt; 2MB) để AI tự động trích xuất kỹ năng, kinh nghiệm và chấm điểm ATS chuẩn quốc tế.
                  </p>
                </div>

                <div className="p-3 bg-[#090D16] border border-[#1E293B] rounded-xl text-left text-[11px] text-[#94a3b8] space-y-2">
                  <div className="flex items-center gap-2 text-[#4edea3]">
                    <Sparkles className="w-3.5 h-3.5 shrink-0" />
                    <span className="font-semibold">Bóc tách 8 nhóm kỹ năng tự động</span>
                  </div>
                  <div className="flex items-center gap-2 text-cyan-400">
                    <Layers className="w-3.5 h-3.5 shrink-0" />
                    <span className="font-semibold">Chấm điểm ATS 50/30/20 chuyên sâu</span>
                  </div>
                  <div className="flex items-center gap-2 text-indigo-400">
                    <Briefcase className="w-3.5 h-3.5 shrink-0" />
                    <span className="font-semibold">Viết lại câu thành tựu chuẩn STAR</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(true)}
                  className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold py-2.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]"
                >
                  <Upload className="w-4 h-4" />
                  <span>Tải Lên CV Ngay</span>
                </button>
              </div>
            ) : (
              <>
                {/* 1.1 Uploaded File Info Card */}
                <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-[#10b981]/15 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center shrink-0 font-bold text-xs font-['JetBrains_Mono',monospace]">
                        CV
                      </div>
                      <div className="min-w-0">
                        <h2 className="text-xs font-bold text-[#f8fafc] truncate font-['Plus_Jakarta_Sans',sans-serif]">
                          {fileName || "CV_Ung_Vien.pdf"}
                        </h2>
                        <p className="text-[10px] text-[#94a3b8] flex items-center gap-1.5 pt-0.5">
                          <span>{totalSkillsCount} kỹ năng</span>
                          <span>•</span>
                          <span className="text-[#4edea3] font-['JetBrains_Mono',monospace]">
                            {profile.metadata.extraction_confidence}% tin cậy
                          </span>
                        </p>
                      </div>
                    </div>
                    <span className="text-[10px] text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-2 py-0.5 rounded font-['JetBrains_Mono',monospace] shrink-0">
                      Đã bóc tách
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
                      Xem / Sửa
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
                      {profile.metadata.total_experience_years > 0 && (
                        <span className="text-[10px] text-[#38bdf8] bg-[#0284c7]/10 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                          {profile.metadata.total_experience_years} năm KN
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[#4edea3] font-medium pt-0.5">
                      {profile.summary.detected_title || "Chuyên gia công nghệ"}
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

                {/* 1.3 Dynamic 8-Groups Skills Taxonomy */}
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

                {/* 1.4 Work Experience Timeline */}
                {profile.work_experience && profile.work_experience.length > 0 && (
                  <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm space-y-3">
                    <div className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                      Kinh Nghiệm Làm Việc ({profile.work_experience.length})
                    </div>
                    <div className="space-y-3 border-l-2 border-[#1E293B] pl-3 ml-1">
                      {profile.work_experience.map((exp, idx) => (
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
                      ))}
                    </div>
                  </div>
                )}

                {/* 1.5 Education */}
                {profile.education && profile.education.length > 0 && (
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
              </>
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
                  {profile ? `Hồ sơ: ${profile.personal_info.full_name || "Đã nạp"}` : "Chờ nạp CV..."}
                </div>
              </div>
            </div>
            {profile && (
              <button
                type="button"
                onClick={() => setIsReasoningOpen(!isReasoningOpen)}
                className="text-[11px] text-[#94a3b8] hover:text-[#4edea3] border border-[#1E293B] px-2.5 py-1 rounded-lg bg-[#181b25] transition-colors"
              >
                {isReasoningOpen ? "Ẩn suy luận" : "Hiện suy luận AI"}
              </button>
            )}
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
                <span className="text-[10px] text-[#94a3b8] font-['JetBrains_Mono',monospace]">AI Ready</span>
              </div>
              
              {!profile ? (
                <p className="text-xs sm:text-sm text-[#dfe2ef] leading-relaxed">
                  Xin chào! Tôi là Trợ lý AI của bạn. Hãy nhấn nút <strong className="text-[#4edea3]">"Tải Lên CV Ngay"</strong> ở Cột 1 để tôi trích xuất hồ sơ và bắt đầu tính toán độ tương thích ATS với các mô tả công việc (JD) mục tiêu nhé.
                </p>
              ) : (
                <p className="text-xs sm:text-sm text-[#dfe2ef] leading-relaxed">
                  Chào <span className="text-[#4edea3] font-semibold">{profile.personal_info.full_name || "bạn"}</span>! Tôi đã bóc tách hồ sơ CV của bạn với độ tin cậy <strong className="text-[#4edea3]">{profile.metadata.extraction_confidence}%</strong> (tìm thấy {totalSkillsCount} kỹ năng). Hãy dán JD mục tiêu ở Cột 3 để tôi tiến hành chấm điểm ATS chuyên sâu và tối ưu hóa đạn STAR nhé.
                </p>
              )}
            </div>

            {/* AI Deep Reasoning Chain Block */}
            {profile && isReasoningOpen && (
              <div className="bg-[#0c101b] border border-[#10b981]/30 rounded-xl p-4 space-y-3 font-['JetBrains_Mono',monospace]">
                <div className="flex items-center justify-between text-xs text-[#4edea3] font-bold">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-ping"></span>
                    <span>AI REASONING TRACE (Chuỗi suy luận hồ sơ)</span>
                  </div>
                  <span className="text-[10px] bg-[#10b981]/10 px-2 py-0.5 rounded border border-[#10b981]/30">
                    Confidence: {profile.metadata.extraction_confidence}%
                  </span>
                </div>

                <div className="text-[11px] text-[#94a3b8] space-y-2 border-l-2 border-[#1E293B] pl-3">
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">1. Cấu trúc CV:</span> Định dạng <code className="text-[#4edea3]">{profile.metadata.cv_format_type}</code>, ngôn ngữ <code className="text-[#38bdf8]">{profile.metadata.cv_language}</code>.
                  </p>
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">2. Kỹ năng nhận diện:</span> Phân loại thành công {totalSkillsCount} kỹ năng qua chuẩn 8 nhóm chuyên ngành.
                  </p>
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">3. Kinh nghiệm làm việc:</span> Ghi nhận {profile.work_experience.length} vị trí công tác ({profile.metadata.total_experience_years} năm tích lũy).
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
            CỘT 3 (4/12 Col ~ 33%): ATS STUDIO & JOB MATCHING
        ════════════════════════════════════════════════════════════ */}
        <aside className="lg:col-span-4 bg-[#0c101b] flex flex-col h-full overflow-hidden">
          
          {/* 3.1 Right Column Tab Header */}
          <div className="h-14 px-3 sm:px-4 border-b border-[#1E293B] bg-[#0c101b] flex items-center justify-between shrink-0">
            <div className="flex gap-1.5 bg-[#111827] p-1 rounded-lg border border-[#1E293B] w-full overflow-x-auto">
              <button
                type="button"
                onClick={() => setActiveRightTab("ats")}
                className={`flex-1 min-w-[110px] px-2.5 py-1.5 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-1.5 ${
                  activeRightTab === "ats"
                    ? "bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md shadow-cyan-600/30"
                    : "text-[#94a3b8] hover:text-[#dfe2ef]"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                <span>So Khớp ATS</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveRightTab("jobs")}
                className={`flex-1 min-w-[110px] px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  activeRightTab === "jobs"
                    ? "bg-[#181b25] text-[#4edea3] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#dfe2ef]"
                }`}
              >
                Khám Phá JD
              </button>
              <button
                type="button"
                onClick={() => setActiveRightTab("studio")}
                className={`flex-1 min-w-[100px] px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  activeRightTab === "studio"
                    ? "bg-[#181b25] text-[#4edea3] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#dfe2ef]"
                }`}
              >
                Studio STAR
              </button>
            </div>
          </div>

          {/* 3.2 Right Tab Content */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 scrollbar-thin">
            
            {/* TAB 1: ATS STUDIO & JD MATCHING */}
            {activeRightTab === "ats" && (
              <div className="space-y-4">
                {!candidateId ? (
                  <div className="p-5 bg-[#111827] border border-[#1E293B] rounded-xl text-center space-y-3">
                    <div className="w-10 h-10 mx-auto rounded-full bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <h4 className="text-xs font-bold text-[#f8fafc]">Chưa Có CV Để So Khớp</h4>
                    <p className="text-xs text-[#94a3b8] leading-relaxed">
                      Vui lòng tải lên file CV của bạn ở Cột 1 trước khi tiến hành so khớp với JD.
                    </p>
                    <button
                      type="button"
                      onClick={() => setIsUploadModalOpen(true)}
                      className="px-4 py-2 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold rounded-lg transition-colors inline-flex items-center gap-1.5"
                    >
                      <Upload className="w-3.5 h-3.5" />
                      <span>Tải Lên CV</span>
                    </button>
                  </div>
                ) : !atsReport ? (
                  <JDInput
                    candidateId={candidateId}
                    onAnalysisSuccess={(report) => setAtsReport(report)}
                    isLoading={isAtsLoading}
                    setIsLoading={setIsAtsLoading}
                  />
                ) : (
                  <ATSResult
                    report={atsReport}
                    onReset={() => setAtsReport(null)}
                    targetRole={profile?.summary.detected_title}
                  />
                )}
              </div>
            )}

            {/* TAB 2: EXPLORE JD & CUSTOM MATCHING */}
            {activeRightTab === "jobs" && (
              <div className="p-6 bg-[#111827] border border-[#1E293B] rounded-xl text-center space-y-4">
                <div className="w-12 h-12 mx-auto rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
                  <Briefcase className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    So Khớp JD Bất Kỳ
                  </h4>
                  <p className="text-xs text-[#94a3b8] mt-1.5 leading-relaxed">
                    Bạn có thể dán mô tả công việc (JD) từ TopCV, LinkedIn, ITviec hoặc VietnamWorks để AI phân tích tỷ lệ trúng tuyển tức thì.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveRightTab("ats")}
                  className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl transition-all inline-flex items-center gap-1.5 shadow-md"
                >
                  <span>Chuyển Sang Tab So Khớp ATS</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* TAB 3: STAR STUDIO */}
            {activeRightTab === "studio" && (
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-br from-cyan-950/30 via-slate-900 to-indigo-950/30 border border-cyan-800/40 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-cyan-400" />
                      Trình Viết STAR Theo Yêu Cầu
                    </span>
                    <button
                      type="button"
                      onClick={() => setIsStandaloneStarOpen(true)}
                      className="px-2.5 py-1 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-semibold rounded-lg transition-colors border border-cyan-500/30"
                    >
                      Mở Cửa Sổ AI
                    </button>
                  </div>
                  <p className="text-xs text-slate-300">
                    Nhập kỹ năng còn thiếu hoặc đoạn mô tả sơ sài để AI tự động chuyển hóa thành câu chuẩn STAR với động từ hành động mạnh và số liệu đo lường.
                  </p>
                </div>
              </div>
            )}

          </div>
        </aside>

      </div>

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
      {profile && candidateId && (
        <ProfileEditModal
          isOpen={isEditModalOpen}
          candidateId={candidateId}
          profile={profile}
          onClose={() => setIsEditModalOpen(false)}
          onSaved={handleProfileSaved}
        />
      )}

      {/* ────────────────────────────────────────────────────────────
          STANDALONE STAR REWRITER MODAL
      ──────────────────────────────────────────────────────────── */}
      <STARModal
        isOpen={isStandaloneStarOpen}
        onClose={() => setIsStandaloneStarOpen(false)}
        initialSkillOrBullet=""
        targetRole={profile?.summary.detected_title || ""}
      />

    </div>
  );
}
