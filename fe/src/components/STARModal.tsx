import React, { useState, useEffect } from "react";
import {
  Sparkles,
  X,
  Copy,
  Check,
  Zap,
  Flame,
  ArrowRight,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { STARResult } from "../types/ats";
import { rewriteBulletToStar } from "../services/atsApi";

interface STARModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialSkillOrBullet: string | null;
  targetRole: string;
}

export const STARModal: React.FC<STARModalProps> = ({
  isOpen,
  onClose,
  initialSkillOrBullet,
  targetRole,
}) => {
  const [inputText, setInputText] = useState(initialSkillOrBullet || "");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<STARResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<"v1" | "v2" | null>(null);

  useEffect(() => {
    if (isOpen && initialSkillOrBullet) {
      setInputText(initialSkillOrBullet);
      generateStar(initialSkillOrBullet);
    } else if (!isOpen) {
      setResult(null);
      setErrorMessage(null);
      setCopiedKey(null);
    }
  }, [isOpen, initialSkillOrBullet]);

  const generateStar = async (textToRewrite: string) => {
    if (!textToRewrite.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await rewriteBulletToStar({
        raw_input: textToRewrite.trim(),
        target_role: targetRole || "Software Engineer",
      });
      setResult(data);
    } catch (err: any) {
      setErrorMessage(err.detail || err.message || "Lỗi khi tạo câu STAR.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string, key: "v1" | "v2") => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-gradient-to-r from-cyan-950/40 via-slate-900 to-indigo-950/40">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                Trình Viết Lại Câu Chuẩn STAR
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  AI Generator
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Biến kỹ năng thiếu thành câu thành tựu định lượng ấn tượng cho CV
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          {/* Input Box */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
              <span>Kỹ năng hoặc câu văn cần tối ưu:</span>
              <span className="text-slate-400 normal-case">Vị trí target: {targetRole || "Software Engineer"}</span>
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && generateStar(inputText)}
                placeholder="VD: Redis, Kubernetes hoặc 'Làm backend bằng FastAPI'..."
                className="flex-1 px-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-slate-200 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <button
                onClick={() => generateStar(inputText)}
                disabled={isLoading || !inputText.trim()}
                className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl flex items-center gap-2 transition-all shadow-md shadow-cyan-600/20"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
                Tạo lại
              </button>
            </div>
          </div>

          {/* Error */}
          {errorMessage && (
            <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
              {errorMessage}
            </div>
          )}

          {/* Loading Skeleton */}
          {isLoading && !result && (
            <div className="space-y-4 py-6">
              <div className="h-24 bg-slate-800/50 rounded-xl animate-pulse" />
              <div className="h-24 bg-slate-800/50 rounded-xl animate-pulse" />
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4 animate-fadeIn">
              {/* Power verb badge */}
              {result.action_verb && (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span>Động từ hành động mạnh:</span>
                  <span className="px-2.5 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
                    ⚡ {result.action_verb}
                  </span>
                </div>
              )}

              {/* Version 1: Balanced */}
              <div className="group relative p-4 bg-gradient-to-br from-slate-950 to-slate-900 border border-cyan-800/40 hover:border-cyan-500/60 rounded-xl transition-all shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-md bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                      <Zap className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wide">
                      Phiên bản 1: Chuẩn STAR cân bằng
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(result.star_v1, "v1")}
                    className="flex items-center gap-1.5 px-3 py-1 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 text-xs font-medium rounded-lg transition-colors border border-cyan-500/30"
                  >
                    {copiedKey === "v1" ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Đã chép</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Sao chép</span>
                      </>
                    )}
                  </button>
                </div>
                <p className="text-slate-200 text-sm leading-relaxed pl-2 border-l-2 border-cyan-500">
                  {result.star_v1}
                </p>
              </div>

              {/* Version 2: Max Impact */}
              <div className="group relative p-4 bg-gradient-to-br from-slate-950 to-slate-900 border border-indigo-800/40 hover:border-indigo-500/60 rounded-xl transition-all shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-md bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                      <Flame className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide">
                      Phiên bản 2: Tối đa hóa Số liệu & Quy mô
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(result.star_v2, "v2")}
                    className="flex items-center gap-1.5 px-3 py-1 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 text-xs font-medium rounded-lg transition-colors border border-indigo-500/30"
                  >
                    {copiedKey === "v2" ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Đã chép</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Sao chép</span>
                      </>
                    )}
                  </button>
                </div>
                <p className="text-slate-200 text-sm leading-relaxed pl-2 border-l-2 border-indigo-500">
                  {result.star_v2}
                </p>
              </div>

              {/* Improvements Explanation */}
              {result.improvements && result.improvements.length > 0 && (
                <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1.5">
                  <span className="text-xs font-semibold text-slate-400">
                    💡 Điểm cải thiện nổi bật:
                  </span>
                  <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                    {result.improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span>💡 Bạn có thể dán trực tiếp câu này vào mục Kinh nghiệm làm việc hoặc Dự án của CV</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};
