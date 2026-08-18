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
  ChevronDown,
  ChevronUp,
  Target,
  FileCheck2,
} from "lucide-react";
import { UploadModal } from "../components/UploadModal";
import { ProfileEditModal } from "../components/ProfileEditModal";
import { JDInput } from "../components/JDInput";
import { ATSResult } from "../components/ATSResult";
import { STARModal } from "../components/STARModal";
import { TailoredCVHub } from "../components/TailoredCVHub";
import {
  CandidateProfile,
  UploadResponse,
  SKILL_CATEGORY_LABELS,
  SkillCategoryKey,
} from "../types/candidate";
import { JDMatchReport } from "../types/ats";
import { getActiveCandidateLocally } from "../services/cvApi";

export default function WorkspacePage() {
  // Navigation & View Toggles
  const [isSkillsAccordionOpen, setIsSkillsAccordionOpen] = useState(true);
  const [isExpAccordionOpen, setIsExpAccordionOpen] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);

  // ATS & STAR State
  const [atsReport, setAtsReport] = useState<JDMatchReport | null>(null);
  const [currentJdText, setCurrentJdText] = useState<string>("");
  const [isAtsLoading, setIsAtsLoading] = useState(false);
  const [isStandaloneStarOpen, setIsStandaloneStarOpen] = useState(false);

  // Dynamic Candidate State (100% from Upload or localStorage)
  const [candidateId, setCandidateId] = useState<string | null>(null);
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
          - Column 1 (4/12 ~ 33%): Split-Pane (Top: My CV, Bottom: JD & ATS Scorer)
          - Column 2 (5/12 ~ 42%): AI Career Copilot & Chat
          - Column 3 (3/12 ~ 25%): Tailored CV Vault (Download Hub)
      ──────────────────────────────────────────────────────────── */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 h-[calc(100vh-4rem)] overflow-hidden">
        
        {/* ════════════════════════════════════════════════════════════
            CỘT 1 (4/12 Col ~ 33%): SPLIT PANE (MY CV + JD & ATS)
        ════════════════════════════════════════════════════════════ */}
        <aside className="lg:col-span-4 border-r border-[#1E293B] bg-[#0c101b] flex flex-col h-full overflow-y-auto scrollbar-thin">
          <div className="p-4 sm:p-5 space-y-6">
            
            {/* ──────────────────────────────────────────
                TẦNG 1 (TRÊN): HỒ SƠ CV CỦA TÔI (MY CV)
            ────────────────────────────────────────── */}
            <section className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-[#1E293B]">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
                  <h2 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                    1. Hồ Sơ CV Của Tôi
                  </h2>
                </div>
                {profile && (
                  <button
                    type="button"
                    onClick={() => setIsEditModalOpen(true)}
                    className="text-[11px] text-[#4edea3] hover:underline flex items-center gap-1 font-medium"
                  >
                    <Edit3 className="w-3 h-3" />
                    <span>Sửa CV</span>
                  </button>
                )}
              </div>

              {!profile ? (
                /* EMPTY STATE WHEN NO CV UPLOADED YET */
                <div className="bg-[#111827] border border-[#1E293B] border-dashed rounded-2xl p-5 text-center space-y-3.5 shadow-sm">
                  <div className="w-12 h-12 mx-auto rounded-2xl bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                      Chưa Có Hồ Sơ CV
                    </h3>
                    <p className="text-[11px] text-[#94a3b8] mt-1 leading-relaxed">
                      Tải lên CV (PDF hoặc Word &lt; 2MB) để AI tự động trích xuất 8 nhóm kỹ năng và kinh nghiệm.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => setIsUploadModalOpen(true)}
                    className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold py-2 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    <span>Tải Lên CV Ngay</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* File Info Card */}
                  <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-3.5 shadow-sm flex items-center justify-between">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-[#10b981]/15 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center shrink-0 font-bold text-xs font-['JetBrains_Mono',monospace]">
                        CV
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-xs font-bold text-[#f8fafc] truncate font-['Plus_Jakarta_Sans',sans-serif]">
                          {fileName || "CV_Ung_Vien.pdf"}
                        </h3>
                        <p className="text-[10px] text-[#94a3b8] flex items-center gap-1.5 pt-0.5">
                          <span>{totalSkillsCount} kỹ năng</span>
                          <span>•</span>
                          <span className="text-[#4edea3] font-['JetBrains_Mono',monospace]">
                            {profile.metadata.extraction_confidence}% tin cậy
                          </span>
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => setIsUploadModalOpen(true)}
                      className="bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-slate-300 hover:text-white text-[10px] px-2.5 py-1.5 rounded-lg transition-colors shrink-0"
                    >
                      Đổi File
                    </button>
                  </div>

                  {/* Candidate Identity */}
                  <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-3.5 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                        {profile.personal_info.full_name || "Ứng viên"}
                      </h4>
                      {profile.metadata.total_experience_years > 0 && (
                        <span className="text-[10px] text-[#38bdf8] bg-[#0284c7]/10 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                          {profile.metadata.total_experience_years} năm KN
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-[#4edea3] font-medium">
                      {profile.summary.detected_title || "Chuyên gia công nghệ"}
                    </p>

                    <div className="flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-400 pt-1 border-t border-[#1E293B]">
                      {profile.personal_info.email && (
                        <span className="flex items-center gap-1 truncate max-w-[180px]">
                          <Mail className="w-3 h-3 text-slate-500 shrink-0" />
                          <span className="truncate">{profile.personal_info.email}</span>
                        </span>
                      )}
                      {profile.personal_info.phone && (
                        <span className="flex items-center gap-1">
                          <Phone className="w-3 h-3 text-slate-500 shrink-0" />
                          <span>{profile.personal_info.phone}</span>
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Collapsible 8-Groups Skills Taxonomy */}
                  <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-3.5 space-y-2.5">
                    <button
                      type="button"
                      onClick={() => setIsSkillsAccordionOpen(!isSkillsAccordionOpen)}
                      className="w-full flex items-center justify-between text-xs font-bold text-slate-200 uppercase tracking-wider"
                    >
                      <span className="flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-cyan-400" />
                        8 Nhóm Kỹ Năng ({totalSkillsCount})
                      </span>
                      {isSkillsAccordionOpen ? (
                        <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                      )}
                    </button>

                    {isSkillsAccordionOpen && (
                      <div className="space-y-2.5 pt-1">
                        {(Object.keys(SKILL_CATEGORY_LABELS) as SkillCategoryKey[]).map((key) => {
                          const items = profile.skills_taxonomy[key] || [];
                          if (items.length === 0) return null;
                          const meta = SKILL_CATEGORY_LABELS[key];

                          return (
                            <div key={key}>
                              <div className="text-[10px] text-[#94a3b8] mb-1 font-medium flex items-center justify-between">
                                <span>{meta.title}:</span>
                                <span className="font-['JetBrains_Mono',monospace] text-[9px] text-slate-500">
                                  {items.length}
                                </span>
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {items.map((skill) => (
                                  <span
                                    key={skill}
                                    className={`px-1.5 py-0.5 rounded text-[10px] font-['JetBrains_Mono',monospace] border ${meta.color}`}
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Collapsible Work Experience Timeline */}
                  {profile.work_experience && profile.work_experience.length > 0 && (
                    <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-3.5 space-y-2.5">
                      <button
                        type="button"
                        onClick={() => setIsExpAccordionOpen(!isExpAccordionOpen)}
                        className="w-full flex items-center justify-between text-xs font-bold text-slate-200 uppercase tracking-wider"
                      >
                        <span className="flex items-center gap-1.5">
                          <Briefcase className="w-3.5 h-3.5 text-indigo-400" />
                          Kinh Nghiệm ({profile.work_experience.length})
                        </span>
                        {isExpAccordionOpen ? (
                          <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                        )}
                      </button>

                      {isExpAccordionOpen && (
                        <div className="space-y-2.5 border-l border-[#1E293B] pl-2.5 ml-1 pt-1">
                          {profile.work_experience.map((exp, idx) => (
                            <div key={idx} className="space-y-0.5 text-xs">
                              <div className="font-bold text-white text-[11px]">{exp.role}</div>
                              <div className="text-[10px] text-[#4edea3]">
                                {exp.company} • {exp.start_date} - {exp.is_current ? "Hiện tại" : exp.end_date || "Nay"}
                              </div>
                              {exp.raw_bullets && exp.raw_bullets.length > 0 && (
                                <p className="text-[10px] text-slate-400 line-clamp-2 leading-relaxed pt-0.5">
                                  {exp.raw_bullets[0]}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </section>

            {/* ──────────────────────────────────────────
                TẦNG 2 (DƯỚI): SO KHỚP JD & ĐIỂM ATS
            ────────────────────────────────────────── */}
            <section className="space-y-4 pt-2 border-t border-[#1E293B]">
              <div className="flex items-center justify-between pb-2 border-b border-[#1E293B]">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <h2 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                    2. So Khớp JD & Điểm ATS (50/30/20)
                  </h2>
                </div>
                {atsReport && (
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-bold font-mono">
                    {atsReport.overall_score}đ ({atsReport.overall_grade})
                  </span>
                )}
              </div>

              {!candidateId ? (
                <div className="p-4 bg-[#111827] border border-[#1E293B] rounded-xl text-center space-y-2">
                  <Target className="w-6 h-6 text-cyan-400 mx-auto" />
                  <p className="text-xs text-slate-300 font-semibold">Cần Tải CV Trước</p>
                  <p className="text-[11px] text-slate-400">
                    Vui lòng tải lên CV ở Tầng 1 trước khi dán mô tả công việc (JD) để chấm điểm.
                  </p>
                </div>
              ) : !atsReport ? (
                <JDInput
                  candidateId={candidateId}
                  onAnalysisSuccess={(report, rawText) => {
                    setAtsReport(report);
                    if (rawText) setCurrentJdText(rawText);
                  }}
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
            </section>

          </div>
        </aside>

        {/* ════════════════════════════════════════════════════════════
            CỘT 2 (5/12 Col ~ 42%): AI CAREER COPILOT & CHAT
        ════════════════════════════════════════════════════════════ */}
        <main className="lg:col-span-5 flex flex-col h-full bg-[#090D16] border-r border-[#1E293B]">
          
          {/* Chat Header */}
          <div className="h-14 px-5 border-b border-[#1E293B] bg-[#0c101b] flex items-center justify-between shrink-0">
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

          {/* Chat Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 scrollbar-thin">
            
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
                  Xin chào! Tôi là Trợ lý AI Hướng nghiệp của bạn. Hãy nhấn nút <strong className="text-[#4edea3]">"Tải Lên CV Ngay"</strong> ở Cột 1 để tôi trích xuất hồ sơ và bắt đầu tính toán độ tương thích ATS với các mô tả công việc (JD) mục tiêu nhé.
                </p>
              ) : (
                <p className="text-xs sm:text-sm text-[#dfe2ef] leading-relaxed">
                  Chào <span className="text-[#4edea3] font-semibold">{profile.personal_info.full_name || "bạn"}</span>! Tôi đã bóc tách hồ sơ CV của bạn với độ tin cậy <strong className="text-[#4edea3]">{profile.metadata.extraction_confidence}%</strong> (tìm thấy {totalSkillsCount} kỹ năng). Bạn có thể dán JD mục tiêu ở Tầng Dưới Cột 1 để xem điểm ATS và tạo các bản CV may đo lưu tại Cột 3.
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
                    <span className="text-[#dfe2ef] font-semibold">2. Kỹ năng nhận diện:</span> Phân loại thành công {totalSkillsCount} kỹ năng qua chuẩn 8 nhóm chuyên ngành (Đạt chuẩn 10-15 kỹ năng cốt lõi).
                  </p>
                  <p>
                    <span className="text-[#dfe2ef] font-semibold">3. Kinh nghiệm làm việc:</span> Ghi nhận {profile.work_experience.length} vị trí công tác ({profile.metadata.total_experience_years} năm tích lũy).
                  </p>
                </div>
              </div>
            )}

            {/* Quick Prompt Chips */}
            {profile && (
              <div className="space-y-2 pt-2">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                  Gợi Ý Câu Hỏi Nhanh:
                </span>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Tôi nên nhấn mạnh kinh nghiệm nào cho JD này?",
                    "Dự đoán 5 câu hỏi phỏng vấn kỹ thuật cho vị trí này",
                    "Viết giúp tôi đoạn tóm tắt mở đầu CV (Summary) ấn tượng",
                  ].map((chip, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setChatInput(chip)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700 transition-colors text-left"
                    >
                      💡 {chip}
                    </button>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Chat Input Bar */}
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
            CỘT 3 (3/12 Col ~ 25%): TAILORED CV VAULT (KHO CV TỐI ƯU)
        ════════════════════════════════════════════════════════════ */}
        <aside className="lg:col-span-3 h-full overflow-hidden">
          <TailoredCVHub
            candidateId={candidateId}
            candidateProfile={profile}
            currentAtsReport={atsReport}
            currentJdText={currentJdText}
          />
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
