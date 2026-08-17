import React, { useState, useRef } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, X, Sparkles, ShieldCheck } from "lucide-react";
import { uploadCv, ApiError } from "../services/cvApi";
import { UploadResponse } from "../types/candidate";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (data: UploadResponse) => void;
}

type UploadStep = "idle" | "uploading" | "parsing" | "completed" | "error";

export const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<UploadStep>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;

    const lowerName = selectedFile.name.toLowerCase();
    if (!lowerName.endsWith(".pdf") && !lowerName.endsWith(".docx")) {
      setErrorMessage("Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Microsoft Word (.docx).");
      setStep("error");
      return;
    }

    if (selectedFile.size > 2 * 1024 * 1024) {
      setErrorMessage("Kích thước tệp quá lớn. Giới hạn tối đa là 2MB.");
      setStep("error");
      return;
    }

    setFile(selectedFile);
    setErrorMessage(null);
    setStep("idle");
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleStartUpload = async () => {
    if (!file) return;

    setStep("uploading");
    setErrorMessage(null);

    try {
      // Step 1 -> Step 2 progress animation
      setTimeout(() => {
        setStep((curr) => (curr === "uploading" ? "parsing" : curr));
      }, 900);

      const result = await uploadCv(file);
      setUploadResult(result);
      setStep("completed");

      setTimeout(() => {
        onSuccess(result);
        onClose();
        // reset state
        setStep("idle");
        setFile(null);
      }, 1200);
    } catch (err) {
      setStep("error");
      if (err instanceof ApiError) {
        setErrorMessage(err.detail);
      } else {
        setErrorMessage((err as Error).message || "Đã xảy ra lỗi trong quá trình xử lý CV.");
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-[#0f1422] border border-[#1E293B] rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1E293B] bg-[#111827]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#10b981]/15 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                Tải Lên CV &amp; Bóc Tách Bằng AI
              </h3>
              <p className="text-[11px] text-[#94a3b8]">Hỗ trợ PDF tiếng Việt / tiếng Anh (Tối đa 2 trang)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#94a3b8] hover:text-[#f8fafc] hover:bg-[#181b25] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Dropzone */}
          {step === "idle" && (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
                dragOver
                  ? "border-[#10b981] bg-[#10b981]/10 scale-[1.01]"
                  : "border-[#1E293B] bg-[#0c101b] hover:border-[#10b981]/50 hover:bg-[#111827]"
              }`}
            >
              <label htmlFor="cv-file-upload" className="sr-only">Tải lên tệp CV PDF hoặc Word (.docx)</label>
              <input
                id="cv-file-upload"
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="hidden"
                onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              />

              <div className="w-14 h-14 mx-auto mb-3.5 rounded-full bg-[#181b25] border border-[#1E293B] flex items-center justify-center text-[#4edea3]">
                {file ? <FileText className="w-7 h-7" /> : <Upload className="w-7 h-7" />}
              </div>

              {file ? (
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-[#f8fafc]">{file.name}</p>
                  <p className="text-xs text-[#4edea3]">{(file.size / (1024 * 1024)).toFixed(2)} MB • Đã sẵn sàng</p>
                  <p className="text-[11px] text-[#94a3b8] pt-2">Click hoặc kéo file khác để thay đổi</p>
                </div>
              ) : (
                <div className="space-y-1.5">
                  <p className="text-sm font-semibold text-[#f8fafc]">Kéo &amp; thả file CV của bạn vào đây</p>
                  <p className="text-xs text-[#94a3b8]">hoặc <span className="text-[#4edea3] underline underline-offset-2">chọn tệp từ máy tính</span></p>
                  <p className="text-[11px] text-[#64748b] pt-1">Hỗ trợ PDF &amp; Word (.docx) • Tối đa 2 MB • 1-2 trang</p>
                </div>
              )}
            </div>
          )}

          {/* Processing States */}
          {(step === "uploading" || step === "parsing" || step === "completed") && (
            <div className="py-8 px-4 text-center space-y-4">
              <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
                {step === "completed" ? (
                  <CheckCircle2 className="w-14 h-14 text-[#4edea3] animate-in zoom-in duration-300" />
                ) : (
                  <>
                    <div className="absolute inset-0 rounded-full border-4 border-[#1E293B]"></div>
                    <div className="absolute inset-0 rounded-full border-4 border-[#10b981] border-t-transparent animate-spin"></div>
                    <Loader2 className="w-6 h-6 text-[#4edea3] animate-spin" />
                  </>
                )}
              </div>

              <div className="space-y-1.5">
                <h4 className="text-sm font-bold text-[#f8fafc]">
                  {step === "uploading" && "Đang tải lên và khử nhiễu tệp..."}
                  {step === "parsing" && "AI đang bóc tách & chuẩn hóa hồ sơ..."}
                  {step === "completed" && (
                    <span className="text-[#4edea3]">
                      {uploadResult?.is_cached ? "⚡ Lấy dữ liệu từ bộ nhớ đệm thành công!" : "✅ Bóc tách hồ sơ thành công!"}
                    </span>
                  )}
                </h4>
                <p className="text-xs text-[#94a3b8]">
                  {step === "uploading" && "Giải mã layout 2 cột & kiểm tra định dạng PDF"}
                  {step === "parsing" && "Bóc tách 8 nhóm kỹ năng, kinh nghiệm & học vấn"}
                  {step === "completed" && `Đã trích xuất ${uploadResult?.profile.personal_info.full_name}`}
                </p>
              </div>

              {/* Progress Stepper */}
              <div className="max-w-xs mx-auto pt-2 grid grid-cols-3 gap-2 text-[10px] font-['JetBrains_Mono',monospace]">
                <div className={`p-1.5 rounded border text-center ${step === "uploading" || step === "parsing" || step === "completed" ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/40" : "bg-[#181b25] text-[#64748b] border-[#1E293B]"}`}>
                  1. Tải lên
                </div>
                <div className={`p-1.5 rounded border text-center ${step === "parsing" || step === "completed" ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/40" : "bg-[#181b25] text-[#64748b] border-[#1E293B]"}`}>
                  2. Khử nhiễu
                </div>
                <div className={`p-1.5 rounded border text-center ${step === "completed" ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/40" : "bg-[#181b25] text-[#64748b] border-[#1E293B]"}`}>
                  3. Bóc tách AI
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {step === "error" && (
            <div className="p-4 bg-red-950/40 border border-red-800/60 rounded-xl space-y-2.5">
              <div className="flex items-start gap-2.5">
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h5 className="text-xs font-bold text-red-200">Không thể xử lý CV</h5>
                  <p className="text-xs text-red-300 leading-relaxed">{errorMessage}</p>
                </div>
              </div>

              <div className="pt-2 text-[11px] text-[#94a3b8] border-t border-red-900/40 space-y-1">
                <p className="font-semibold text-red-200/90">Gợi ý khắc phục:</p>
                <ul className="list-disc list-inside space-y-0.5 text-[#94a3b8]">
                  <li>Đảm bảo file PDF có chữ có thể copy (không phải file scan hoặc chụp ảnh).</li>
                  <li>File không vượt quá 2 trang và dung lượng dưới 10MB.</li>
                  <li>Nếu có mật khẩu mở file, vui lòng bỏ mật khẩu trước khi tải lên.</li>
                </ul>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setStep("idle");
                    setErrorMessage(null);
                  }}
                  className="px-3 py-1.5 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] text-xs font-medium rounded-lg transition-colors"
                >
                  Thử lại với tệp khác
                </button>
              </div>
            </div>
          )}

          {/* Security Guarantee */}
          <div className="flex items-center gap-2 text-[11px] text-[#64748b] bg-[#111827]/60 p-2.5 rounded-lg border border-[#1E293B]">
            <ShieldCheck className="w-4 h-4 text-[#4edea3] shrink-0" />
            <span>Thông tin cá nhân được bảo vệ &amp; chỉ dùng cho mục đích tối ưu hóa nghề nghiệp.</span>
          </div>
        </div>

        {/* Footer Actions */}
        {step === "idle" && (
          <div className="flex items-center justify-end gap-3 px-6 py-4 bg-[#111827] border-t border-[#1E293B]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-[#94a3b8] hover:text-[#f8fafc] transition-colors"
            >
              Hủy
            </button>
            <button
              type="button"
              disabled={!file}
              onClick={handleStartUpload}
              className={`px-5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
                file
                  ? "bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] shadow-sm cursor-pointer"
                  : "bg-[#181b25] text-[#64748b] border border-[#1E293B] cursor-not-allowed"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              Bắt đầu bóc tách CV
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
