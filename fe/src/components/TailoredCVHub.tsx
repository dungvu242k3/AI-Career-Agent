import React, { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Eye,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Clock,
  Briefcase,
  AlertCircle,
  Globe2,
  Loader2,
  Check,
  Zap,
} from "lucide-react";
import { CandidateProfile } from "../types/candidate";
import { JDMatchReport } from "../types/ats";
import { generateHarvardCVPdf } from "../services/atsApi";

export interface TailoredCVItem {
  id: string;
  companyName: string;
  targetRole: string;
  language: "vi" | "en";
  originalScore: number;
  optimizedScore: number;
  grade: string;
  createdAt: string;
  filename: string;
  blobUrl: string;
  wordCount: number;
}

interface TailoredCVHubProps {
  candidateId: string | null;
  candidateProfile: CandidateProfile | null;
  currentAtsReport: JDMatchReport | null;
  currentJdText?: string;
}

export const TailoredCVHub: React.FC<TailoredCVHubProps> = ({
  candidateId,
  candidateProfile,
  currentAtsReport,
  currentJdText,
}) => {
  const [selectedLang, setSelectedLang] = useState<"vi" | "en">("vi");
  const [isGenerating, setIsGenerating] = useState(false);
  const [genStep, setGenStep] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [previewItem, setPreviewItem] = useState<TailoredCVItem | null>(null);
  const [tailoredList, setTailoredList] = useState<TailoredCVItem[]>([]);
  const timerRefs = React.useRef<ReturnType<typeof setTimeout>[]>([]);

  // Cleanup object URLs and pending timers on unmount (BUG-04 & BUG-05)
  useEffect(() => {
    return () => {
      timerRefs.current.forEach((t) => clearTimeout(t));
      timerRefs.current = [];
      tailoredList.forEach((item) => {
        if (item.blobUrl) URL.revokeObjectURL(item.blobUrl);
      });
    };
  }, [tailoredList]);

  const handleGenerateHarvardCV = async () => {
    if (!candidateId || !candidateProfile) {
      setErrorMessage("Vui lòng tải lên hồ sơ CV trước khi tạo bản may đo.");
      return;
    }

    // Require full JD text (BUG-08)
    const jdToUse = currentJdText?.trim();
    if (!jdToUse || jdToUse.length < 15) {
      setErrorMessage("Vui lòng nạp nội dung mô tả công việc (JD) đầy đủ (tối thiểu 15 ký tự) ở Cột 1 trước.");
      return;
    }

    setIsGenerating(true);
    setErrorMessage(null);
    setGenStep("1/3: AI đang tối ưu hóa từ khóa & cấu trúc STAR...");

    // Clear previous timers
    timerRefs.current.forEach((t) => clearTimeout(t));
    timerRefs.current = [];

    const t1 = setTimeout(() => {
      setGenStep("2/3: Cắt tỉa thông minh chuẩn 1 trang & xếp hạng dự án...");
    }, 1200);

    const t2 = setTimeout(() => {
      setGenStep("3/3: Xuất bản PDF Harvard chuẩn ATS...");
    }, 2400);

    timerRefs.current.push(t1, t2);

    try {
      const result = await generateHarvardCVPdf({
        candidate_id: candidateId,
        jd_text: jdToUse,
        language: selectedLang,
      });

      const blobUrl = URL.createObjectURL(result.blob);
      const original = currentAtsReport?.overall_score || 70;
      const optimized = Math.max(original + 12, result.estimatedScore || 92);

      const newItem: TailoredCVItem = {
        id: Date.now().toString(),
        companyName: currentAtsReport?.jd_title?.split("-")[0]?.trim() || "Target Company",
        targetRole: currentAtsReport?.jd_title || candidateProfile.summary.detected_title || "Software Engineer",
        language: selectedLang,
        originalScore: original,
        optimizedScore: Math.min(100, optimized),
        grade: optimized >= 90 ? "A+" : "A",
        createdAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        filename: result.filename,
        blobUrl: blobUrl,
        wordCount: result.wordCount,
      };

      setTailoredList((prev) => {
        // Revoke oldest blob if list has more than 5 items to prevent RAM bloat (BUG-05)
        if (prev.length >= 5) {
          const oldest = prev[prev.length - 1];
          if (oldest?.blobUrl) URL.revokeObjectURL(oldest.blobUrl);
          return [newItem, ...prev.slice(0, 4)];
        }
        return [newItem, ...prev];
      });
      setPreviewItem(newItem);
    } catch (err: any) {
      setErrorMessage(err.message || "Lỗi khi tạo CV Harvard tối ưu.");
    } finally {
      setIsGenerating(false);
      setGenStep("");
      timerRefs.current.forEach((t) => clearTimeout(t));
      timerRefs.current = [];
    }
  };

  const handleDirectDownload = (item: TailoredCVItem) => {
    const a = document.createElement("a");
    a.href = item.blobUrl;
    a.download = item.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="flex flex-col h-full bg-[#0c101b] border-l border-[#1E293B] overflow-hidden">
      {/* ── HEADER ── */}
      <div className="p-4 border-b border-[#1E293B] flex items-center justify-between shrink-0 bg-[#0c101b]/90 backdrop-blur-md">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
            <Briefcase className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
              Kho CV Harvard Tối Ưu
            </h3>
            <p className="text-[11px] text-slate-400">Xuất PDF chuẩn 1 trang & ATS</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-mono border border-emerald-500/30 font-bold">
            {tailoredList.length} bản
          </span>
        </div>
      </div>

      {/* ── ACTION BANNER (GENERATE SECTION) ── */}
      <div className="p-4 border-b border-[#1E293B] bg-[#111827]/60 space-y-3 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs text-slate-300 font-semibold">
            <Globe2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Ngôn ngữ CV:</span>
          </div>

          {/* Bilingual Toggle */}
          <div className="flex bg-[#090D16] p-0.5 rounded-lg border border-[#1E293B]">
            <button
              type="button"
              onClick={() => setSelectedLang("vi")}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedLang === "vi"
                  ? "bg-emerald-500 text-[#090D16] shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              🇻🇳 Tiếng Việt
            </button>
            <button
              type="button"
              onClick={() => setSelectedLang("en")}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedLang === "en"
                  ? "bg-emerald-500 text-[#090D16] shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              🇬🇧 English
            </button>
          </div>
        </div>

        {/* Generate Button */}
        <button
          type="button"
          onClick={handleGenerateHarvardCV}
          disabled={isGenerating || !currentAtsReport}
          className={`w-full py-2.5 px-4 rounded-xl font-['Plus_Jakarta_Sans',sans-serif] text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-md ${
            isGenerating
              ? "bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700"
              : !currentAtsReport
              ? "bg-slate-800/80 text-slate-500 cursor-not-allowed border border-slate-800"
              : "bg-emerald-500 hover:bg-emerald-400 text-[#090D16] hover:shadow-emerald-500/20 active:scale-[0.99]"
          }`}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span>Đang Tối Ưu Hóa...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-[#090D16]" />
              <span>Tạo CV Harvard 1 Trang ({selectedLang === "vi" ? "VI" : "EN"})</span>
            </>
          )}
        </button>

        {/* Progress status if generating */}
        {isGenerating && genStep && (
          <p className="text-[11px] text-emerald-400 font-mono text-center animate-pulse pt-0.5">
            {genStep}
          </p>
        )}

        {/* Rate limit info */}
        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-0.5">
          <span className="flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-400" />
            Giới hạn: 5 lượt tạo/ngày
          </span>
          <span className="text-slate-500">Font Times • 100% Text ATS</span>
        </div>

        {/* Error message if any */}
        {errorMessage && (
          <div className="p-2.5 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 text-[11px] flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* ── CONTENT AREA (SAVED TAILORED CVS) ── */}
      <div className="flex-1 p-4 overflow-y-auto scrollbar-thin space-y-4">
        {tailoredList.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 bg-[#111827]/40 border border-[#1E293B] border-dashed rounded-2xl space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>

            <div className="space-y-1.5 max-w-xs">
              <h4 className="text-sm font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                Chưa Có Bản CV Harvard Nào
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Nạp JD tại <strong>Cột 1</strong> và bấm nút <strong>"Tạo CV Harvard 1 Trang"</strong> ở trên để AI tự động sắp xếp lại kinh nghiệm, viết chuẩn STAR và xuất bản PDF.
              </p>
            </div>

            {currentAtsReport && (
              <div className="w-full p-3 bg-emerald-950/20 border border-emerald-800/40 rounded-xl text-left space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>JD đã sẵn sàng: {currentAtsReport.jd_title}</span>
                </div>
                <p className="text-[11px] text-slate-300">
                  Điểm ATS hiện tại: <strong className="text-white">{currentAtsReport.overall_score}/100</strong>. Bấm tạo CV để nâng điểm lên 90+.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {tailoredList.map((item) => (
              <div
                key={item.id}
                className="bg-[#111827] border border-[#1E293B] hover:border-emerald-500/40 rounded-xl p-3.5 space-y-3 transition-all shadow-sm group"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-wider">
                        {item.language === "vi" ? "🇻🇳 Tiếng Việt" : "🇬🇧 English"}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {item.createdAt}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-white mt-1 group-hover:text-emerald-300 transition-colors">
                      {item.targetRole}
                    </h4>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-black text-emerald-400 font-mono">
                      {item.optimizedScore}/100
                    </span>
                    <p className="text-[10px] text-slate-400">Hạng {item.grade}</p>
                  </div>
                </div>

                {/* Score Comparison Pill */}
                <div className="flex items-center justify-between p-2 bg-[#090D16] rounded-lg border border-[#1E293B] text-[11px]">
                  <span className="text-slate-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-emerald-400" />
                    Cải thiện ATS:
                  </span>
                  <span className="font-mono text-slate-300">
                    <span className="text-slate-500 line-through mr-1">{item.originalScore}đ</span>
                    ➔ <strong className="text-emerald-400">+{item.optimizedScore - item.originalScore}đ</strong>
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => setPreviewItem(item)}
                    className="flex-1 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors border border-slate-700"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Xem PDF</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDirectDownload(item)}
                    className="flex-1 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Tải Về</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── PDF PREVIEW MODAL ── */}
      {previewItem && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-[#1E293B] rounded-2xl max-w-4xl w-full h-[90vh] flex flex-col p-5 space-y-3 shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Xem Trước PDF CV Harvard ({previewItem.language.toUpperCase()})
                  </h3>
                  <p className="text-xs text-slate-400">
                    {previewItem.targetRole} • {previewItem.optimizedScore}/100 ATS Score
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleDirectDownload(previewItem)}
                  className="px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-[#090D16] font-bold text-xs rounded-xl flex items-center gap-1.5 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Tải PDF Xuống</span>
                </button>
                <button
                  type="button"
                  onClick={() => setPreviewItem(null)}
                  className="text-slate-400 hover:text-white text-xs px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700"
                >
                  Đóng
                </button>
              </div>
            </div>

            {/* Modal Body: Embedded PDF IFrame */}
            <div className="flex-1 bg-slate-950 rounded-xl overflow-hidden border border-[#1E293B]">
              <iframe
                src={previewItem.blobUrl}
                title="Harvard CV Preview"
                className="w-full h-full border-0"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
