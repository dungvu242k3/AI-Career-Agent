import React, { useState, useRef } from "react";
import {
  FileText,
  Upload,
  Sparkles,
  Loader2,
  AlertCircle,
  FileCode2,
  X,
  CheckCircle2,
  HelpCircle,
} from "lucide-react";
import { matchJd } from "../services/atsApi";
import { JDMatchReport } from "../types/ats";

interface JDInputProps {
  candidateId: string;
  onAnalysisSuccess: (report: JDMatchReport, rawJdText?: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const JDInput: React.FC<JDInputProps> = ({
  candidateId,
  onAnalysisSuccess,
  isLoading,
  setIsLoading,
}) => {
  const [activeTab, setActiveTab] = useState<"text" | "file">("text");
  const [jdText, setJdText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    if (!file) return;

    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".pdf") && !lower.endsWith(".docx")) {
      setErrorMessage("Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Microsoft Word (.docx).");
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setErrorMessage("Kích thước tệp quá lớn. Giới hạn tối đa là 2MB.");
      return;
    }

    setSelectedFile(file);
    setErrorMessage(null);
  };

  const handleAnalyze = async () => {
    if (!candidateId) {
      setErrorMessage("Vui lòng tải lên hoặc chọn hồ sơ CV trước khi so khớp JD.");
      return;
    }

    if (activeTab === "text" && (!jdText.trim() || jdText.trim().length < 15)) {
      setErrorMessage("Nội dung mô tả công việc (JD) quá ngắn (tối thiểu 15 ký tự).");
      return;
    }

    if (activeTab === "file" && !selectedFile) {
      setErrorMessage("Vui lòng chọn tệp JD (PDF hoặc DOCX) để phân tích.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const report = await matchJd(candidateId, {
        jdText: activeTab === "text" ? jdText : undefined,
        jdFile: activeTab === "file" ? selectedFile || undefined : undefined,
      });
      onAnalysisSuccess(report, activeTab === "text" ? jdText : report.jd_title);
    } catch (err: any) {
      setErrorMessage(err.detail || err.message || "Lỗi khi so khớp JD.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 backdrop-blur-md shadow-xl flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Nạp Mô Tả Công Việc (Job Description)</h3>
            <p className="text-xs text-slate-400">So khớp độ phù hợp hồ sơ và tìm ra kỹ năng còn thiếu</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => {
            setActiveTab("text");
            setErrorMessage(null);
          }}
          className={`pb-2 text-xs font-semibold px-3 flex items-center gap-1.5 transition-colors border-b-2 ${
            activeTab === "text"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileCode2 className="w-3.5 h-3.5" />
          Dán văn bản JD
        </button>

        <button
          onClick={() => {
            setActiveTab("file");
            setErrorMessage(null);
          }}
          className={`pb-2 text-xs font-semibold px-3 flex items-center gap-1.5 transition-colors border-b-2 ${
            activeTab === "file"
              ? "border-cyan-500 text-cyan-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          Tải tệp PDF / DOCX
        </button>
      </div>

      {/* Tab Content: Text Area */}
      {activeTab === "text" && (
        <div className="space-y-2">
          <div className="relative">
            <textarea
              rows={8}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Dán toàn bộ nội dung JD tuyển dụng (Yêu cầu kỹ năng, mô tả công việc, quyền lợi...)"
              className="w-full p-3.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-slate-200 text-xs font-sans focus:outline-none focus:border-cyan-500 transition-colors resize-y"
              maxLength={10000}
            />
            <div className="absolute bottom-2 right-3 text-[11px] text-slate-500 font-mono">
              {jdText.length} / 10,000 ký tự
            </div>
          </div>
        </div>
      )}

      {/* Tab Content: File Upload */}
      {activeTab === "file" && (
        <div className="space-y-2">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              if (e.dataTransfer.files?.[0]) {
                handleFileChange(e.dataTransfer.files[0]);
              }
            }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
              isDragOver
                ? "border-cyan-500 bg-cyan-950/20"
                : selectedFile
                ? "border-emerald-500/50 bg-emerald-950/10"
                : "border-slate-700/80 hover:border-slate-600 bg-slate-950/40"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
            />

            {selectedFile ? (
              <div className="flex items-center justify-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <p className="text-xs font-bold text-white">{selectedFile.name}</p>
                  <p className="text-[11px] text-slate-400">
                    {(selectedFile.size / 1024).toFixed(0)} KB • Sẵn sàng phân tích
                  </p>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <Upload className="w-5 h-5" />
                </div>
                <p className="text-xs font-semibold text-slate-200">
                  Kéo thả tệp JD vào đây, hoặc <span className="text-cyan-400">duyệt tệp</span>
                </p>
                <p className="text-[11px] text-slate-500">
                  Hỗ trợ định dạng PDF (.pdf) hoặc Word (.docx) • Tối đa 2MB
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {errorMessage && (
        <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={handleAnalyze}
        disabled={isLoading || (activeTab === "text" ? !jdText.trim() : !selectedFile)}
        className="w-full py-3 px-4 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>AI Đang Phân Tích & So Khớp 3 Tầng...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4 text-cyan-200" />
            <span>⚡ Phân Tích & Chấm Điểm ATS Ngay</span>
          </>
        )}
      </button>
    </div>
  );
};
