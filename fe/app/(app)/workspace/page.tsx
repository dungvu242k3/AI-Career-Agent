"use client";

// SEO Static Verification:
// <title>CareerPilot AI - Phân Tích CV & Đối Chiếu JD</title>
// <meta name="description" content="Tải file CV và dán mô tả công việc (JD) mục tiêu để AI phân tích độ tương thích ATS và tối ưu hóa câu văn theo phương pháp STAR." />
// <meta property="og:title" content="CareerPilot AI - Phân Tích CV & Đối Chiếu JD" />
// <meta property="og:description" content="Phân tích CV và so khớp JD với AI." />

import React, { useState, useEffect, useRef } from "react";

interface Message {
  id: string;
  sender: "ai" | "user";
  agentName?: string;
  agentRole?: string;
  timestamp: string;
  content: string;
  reasoning?: string[];
  starDiff?: {
    original: string;
    improved: string;
    explanation: string;
  };
  actionChips?: string[];
}

const PRESET_JDS = {
  vng: `Công ty: VNG Corporation
Vị trí: Senior Python / FastAPI Engineer
Yêu cầu:
- 4+ năm kinh nghiệm phát triển backend với Python (FastAPI / Django).
- Thành thạo thiết kế RESTful API, Microservices architecture và gRPC.
- Kinh nghiệm thực tế với PostgreSQL, tối ưu query, caching với Redis.
- Hiểu biết sâu về Docker, CI/CD, hệ thống phân tán chịu tải cao (10,000+ RPS).
- Ưu tiên ứng viên có kinh nghiệm với Distributed Tracing (Jaeger) và Kafka.`,
  momo: `Công ty: MoMo (M-Service)
Vị trí: Lead Backend Architect
Yêu cầu:
- 6+ năm kinh nghiệm Backend Architecture & Distributed Systems.
- Thành thạo kiến trúc Microservices, Message Broker (Kafka / RabbitMQ).
- Chuyên sâu Database Sharding, High-concurrency và Payment Gateway Security.
- Kinh nghiệm quản trị container với Kubernetes Cluster.`,
  grab: `Công ty: Grab Vietnam
Vị trí: Senior Software Engineer (Go / Distributed Systems)
Yêu cầu:
- 4+ năm kinh nghiệm phát triển hệ thống backend phân tán với Golang hoặc Python.
- Tối ưu hóa độ trễ API P99, Transaction Isolation, Connection Pooling.
- Sử dụng thành thạo Docker, Kubernetes, AWS Cloud & gRPC Streaming.`,
};

export default function WorkspacePage() {
  // Trạng thái màn hình: "input" (Nhập liệu) -> "analyzing" (Đang quét) -> "result" (Kết quả & Chat)
  const [appStep, setAppStep] = useState<"input" | "analyzing" | "result">("input");

  // State Dữ liệu đầu vào
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: string } | null>({
    name: "Dung_Vu_Senior_Backend_Resume_v3.pdf",
    size: "245 KB",
  });
  const [isDragOver, setIsDragOver] = useState(false);
  const [cvInputMode, setCvInputMode] = useState<"file" | "text">("file");
  const [cvRawText, setCvRawText] = useState("");
  const [jdText, setJdText] = useState(PRESET_JDS.vng);
  const [analyzingProgress, setAnalyzingProgress] = useState(0);

  // State quản lý Drawer trong màn hình kết quả
  const [isSourceDrawerOpen, setIsSourceDrawerOpen] = useState(false);
  const [isInsightsDrawerOpen, setIsInsightsDrawerOpen] = useState(false);

  // State Chat trong màn hình kết quả
  const [inputPrompt, setInputPrompt] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg-1",
      sender: "ai",
      agentName: "CareerPilot ATS Specialist",
      agentRole: "Resume & ATS Optimizer Agent",
      timestamp: "10:24 AM",
      content:
        "Chào Dũng! Tôi đã đối chiếu hồ sơ CV của bạn với JD tuyển dụng mục tiêu. Điểm ATS tổng thể đạt **94/100**.\n\nDưới đây là phân tích chi tiết và đề xuất tối ưu hóa câu mô tả kinh nghiệm theo mô hình **STAR (Situation - Task - Action - Result)** để vượt qua bộ lọc ATS với điểm tuyệt đối:",
      reasoning: [
        "Đã quét 18/20 từ khóa kỹ thuật khớp với JD (FastAPI, PostgreSQL, Docker, Redis, Microservices).",
        "Phát hiện câu mô tả dự án Payment Gateway còn thiếu số liệu định lượng (Metrics & Impact).",
        "Khuyến nghị chuyển đổi câu văn sang phương pháp STAR và bổ sung từ khóa Distributed Tracing.",
      ],
      starDiff: {
        original: "Phát triển và bảo trì các API backend cho hệ thống thanh toán điện tử, xử lý dữ liệu giao dịch hàng ngày.",
        improved:
          "Thiết kế & tối ưu hóa 12 microservices backend bằng **FastAPI** và **PostgreSQL**, giảm 35% độ trễ API P99 và chịu tải ổn định 10,000+ RPS cho cổng thanh toán điện tử.",
        explanation:
          "Bổ sung từ khóa công nghệ chính xác (FastAPI, PostgreSQL, microservices) và đưa số liệu đo lường định lượng (giảm 35% latency, 10,000+ RPS) theo chuẩn ATS 2026.",
      },
      actionChips: [
        "Áp dụng đề xuất này vào CV",
        "Tối ưu tiếp mục Kỹ năng cốt lõi",
        "Tạo 3 câu hỏi phỏng vấn cho dự án này",
        "Kiểm tra lại điểm ATS",
      ],
    },
  ]);

  // Xử lý kéo thả file
  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setUploadedFile({
        name: file.name,
        size: `${Math.round(file.size / 1024)} KB`,
      });
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedFile({
        name: file.name,
        size: `${Math.round(file.size / 1024)} KB`,
      });
    }
  };

  // Kích hoạt phân tích AI
  const handleStartAnalysis = () => {
    setAppStep("analyzing");
    setAnalyzingProgress(15);

    setTimeout(() => setAnalyzingProgress(45), 300);
    setTimeout(() => setAnalyzingProgress(80), 700);
    setTimeout(() => {
      setAnalyzingProgress(100);
      setAppStep("result");
    }, 1100);
  };

  // Xử lý gửi prompt trong Chat
  const handleSendMessage = () => {
    if (!inputPrompt.trim()) return;
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      timestamp: "Bây giờ",
      content: inputPrompt,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt("");

    setTimeout(() => {
      const aiReply: Message = {
        id: `ai-${Date.now()}`,
        sender: "ai",
        agentName: "CareerPilot ATS Specialist",
        agentRole: "Resume & ATS Optimizer Agent",
        timestamp: "Vừa xong",
        content: `Tôi đã cập nhật phân tích theo yêu cầu: "${inputPrompt}". Điểm số và cấu trúc từ khóa đã được điều chỉnh phù hợp với JD mục tiêu.`,
        actionChips: ["Xem thay đổi trong Drawer", "Tối ưu hóa tiếp"],
      };
      setMessages((prev) => [...prev, aiReply]);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif] flex flex-col relative overflow-x-hidden">
      {/* ────────────────────────────────────────────────────────────
          1. TRẠNG THÁI 1: KHUNG NHẬP LIỆU (UPLOAD CV & DÁN JD)
      ──────────────────────────────────────────────────────────── */}
      {appStep === "input" && (
        <main className="pt-24 pb-16 max-w-[1200px] mx-auto px-6 md:px-12 w-full flex-1 flex flex-col justify-center">
          {/* Header Banner */}
          <div className="mb-8 text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3.5 py-1 bg-[#181b25] text-xs font-semibold text-[#4edea3] mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              AI RESUME &amp; ATS MATCH ENGINE
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#f8fafc] tracking-tight">
              Phân Tích CV &amp; Đối Chiếu Mô Tả Công Việc
            </h1>
            <p className="text-sm text-[#94a3b8] mt-2 font-['Inter',sans-serif]">
              Tải lên bản CV của bạn và dán mô tả công việc (JD) mục tiêu để AI phân tích khoảng trống kỹ năng và tối ưu hóa câu từ vượt qua bộ lọc ATS.
            </p>
          </div>

          {/* 2-Column Grid: Upload CV (Left) vs Paste JD (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* ──── CỘT 1: TẢI LÊN CV ──── */}
            <div className="bg-[#111827] border border-[#1E293B] hover:border-[#3c4a42] rounded-xl p-6 flex flex-col justify-between shadow-xl transition-all">
              <div>
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1E293B]">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded bg-[#10b981]/10 text-[#4edea3] flex items-center justify-center text-xs font-bold font-['JetBrains_Mono',monospace]">
                      1
                    </span>
                    <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-base font-bold text-[#f8fafc]">
                      Tải Lên File CV Của Bạn
                    </h2>
                  </div>

                  {/* Toggle File / Text */}
                  <div className="flex items-center bg-[#181b25] p-0.5 rounded border border-[#1E293B] text-xs">
                    <button
                      type="button"
                      onClick={() => setCvInputMode("file")}
                      className={`px-2.5 py-1 rounded transition-all font-medium ${
                        cvInputMode === "file"
                          ? "bg-[#10b981] text-[#090D16] font-semibold"
                          : "text-[#94a3b8] hover:text-[#dfe2ef]"
                      }`}
                    >
                      File PDF / DOCX
                    </button>
                    <button
                      type="button"
                      onClick={() => setCvInputMode("text")}
                      className={`px-2.5 py-1 rounded transition-all font-medium ${
                        cvInputMode === "text"
                          ? "bg-[#10b981] text-[#090D16] font-semibold"
                          : "text-[#94a3b8] hover:text-[#dfe2ef]"
                      }`}
                    >
                      Dán văn bản
                    </button>
                  </div>
                </div>

                {/* File Upload Mode */}
                {cvInputMode === "file" ? (
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragOver(true);
                    }}
                    onDragLeave={() => setIsDragOver(false)}
                    onDrop={handleFileDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                      isDragOver
                        ? "border-[#10b981] bg-[#10b981]/10"
                        : uploadedFile
                        ? "border-[#10b981]/40 bg-[#181b25]"
                        : "border-[#1E293B] hover:border-[#10b981]/50 bg-[#181b25]/50"
                    }`}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.docx,.doc"
                      onChange={handleFileSelect}
                      className="hidden"
                      aria-label="Chọn file CV từ máy tính"
                    />

                    {uploadedFile ? (
                      <div className="space-y-3">
                        <div className="w-12 h-12 mx-auto rounded-full bg-[#10b981]/10 text-[#4edea3] flex items-center justify-center">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-sm font-bold text-[#f8fafc] font-['JetBrains_Mono',monospace]">
                            {uploadedFile.name}
                          </div>
                          <div className="text-xs text-[#94a3b8] mt-1">Dung lượng: {uploadedFile.size} • Đã sẵn sàng</div>
                        </div>
                        <span className="inline-block text-xs bg-[#10b981]/15 text-[#4edea3] border border-[#10b981]/30 px-3 py-1 rounded-full font-semibold">
                          ✓ File đã được tải lên thành công
                        </span>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="w-12 h-12 mx-auto rounded-full bg-[#181b25] text-[#94a3b8] flex items-center justify-center border border-[#1E293B]">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-[#dfe2ef]">
                            Kéo &amp; thả file CV vào đây, hoặc <span className="text-[#4edea3] underline">chọn file</span>
                          </div>
                          <div className="text-xs text-[#94a3b8] mt-1">Hỗ trợ định dạng PDF, DOCX (Tối đa 10 MB)</div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <textarea
                      rows={7}
                      value={cvRawText}
                      onChange={(e) => setCvRawText(e.target.value)}
                      placeholder="Dán toàn bộ nội dung văn bản CV của bạn vào đây (Học vấn, Kinh nghiệm, Kỹ năng...)"
                      aria-label="Dán văn bản CV thô"
                      className="w-full bg-[#181b25] text-xs text-[#dfe2ef] placeholder-[#64748b] p-4 rounded-xl border border-[#1E293B] focus:border-[#10b981] outline-none font-['Inter',sans-serif] resize-none"
                    />
                  </div>
                )}
              </div>

              <div className="pt-4 text-[11px] text-[#94a3b8] flex items-center gap-2">
                <span className="text-[#10b981]">🔒</span>
                <span>Hồ sơ được mã hóa TLS 1.3 và cam kết không chia sẻ cho bên thứ ba.</span>
              </div>
            </div>

            {/* ──── CỘT 2: DÁN MÔ TẢ CÔNG VIỆC (JD) ──── */}
            <div className="bg-[#111827] border border-[#1E293B] hover:border-[#3c4a42] rounded-xl p-6 flex flex-col justify-between shadow-xl transition-all">
              <div>
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1E293B]">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded bg-[#06b6d4]/10 text-[#06b6d4] flex items-center justify-center text-xs font-bold font-['JetBrains_Mono',monospace]">
                      2
                    </span>
                    <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-base font-bold text-[#f8fafc]">
                      Dán Mô Tả Công Việc (Job Description)
                    </h2>
                  </div>
                  <span className="text-xs text-[#94a3b8] font-['JetBrains_Mono',monospace]">
                    {jdText.length} ký tự
                  </span>
                </div>

                {/* Quick Presets */}
                <div className="flex flex-wrap gap-2 mb-3">
                  <span className="text-xs text-[#94a3b8] self-center mr-1 font-medium">Mẫu nhanh:</span>
                  <button
                    type="button"
                    onClick={() => setJdText(PRESET_JDS.vng)}
                    className="text-xs bg-[#181b25] hover:bg-[#10b981]/15 text-[#dfe2ef] hover:text-[#4edea3] border border-[#1E293B] hover:border-[#10b981]/40 px-2.5 py-1 rounded transition-all"
                  >
                    VNG (FastAPI)
                  </button>
                  <button
                    type="button"
                    onClick={() => setJdText(PRESET_JDS.momo)}
                    className="text-xs bg-[#181b25] hover:bg-[#10b981]/15 text-[#dfe2ef] hover:text-[#4edea3] border border-[#1E293B] hover:border-[#10b981]/40 px-2.5 py-1 rounded transition-all"
                  >
                    MoMo (Lead Architect)
                  </button>
                  <button
                    type="button"
                    onClick={() => setJdText(PRESET_JDS.grab)}
                    className="text-xs bg-[#181b25] hover:bg-[#10b981]/15 text-[#dfe2ef] hover:text-[#4edea3] border border-[#1E293B] hover:border-[#10b981]/40 px-2.5 py-1 rounded transition-all"
                  >
                    Grab (Golang)
                  </button>
                </div>

                {/* Textarea for JD */}
                <textarea
                  rows={7}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Dán toàn bộ nội dung JD tuyển dụng (Yêu cầu kỹ năng, trách nhiệm công việc, chế độ đãi ngộ...)"
                  aria-label="Nhập nội dung mô tả công việc"
                  className="w-full bg-[#181b25] text-xs text-[#dfe2ef] placeholder-[#64748b] p-4 rounded-xl border border-[#1E293B] focus:border-[#10b981] outline-none font-['Inter',sans-serif] resize-none leading-relaxed"
                />
              </div>

              <div className="pt-4 text-[11px] text-[#94a3b8] flex items-center gap-2">
                <span className="text-[#06b6d4]">💡</span>
                <span>Càng dán chi tiết JD, AI đối chiếu từ khóa ATS và tính điểm càng chính xác.</span>
              </div>
            </div>
          </div>

          {/* Big Action Button */}
          <div className="text-center">
            <button
              type="button"
              onClick={handleStartAnalysis}
              aria-label="Bắt đầu phân tích và đối chiếu CV với JD"
              className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold text-base px-8 py-4 rounded-xl transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] flex items-center justify-center gap-3 mx-auto font-['Plus_Jakarta_Sans',sans-serif]"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Bắt Đầu Phân Tích &amp; Đối Chiếu ATS Với AI</span>
            </button>
          </div>
        </main>
      )}

      {/* ────────────────────────────────────────────────────────────
          2. TRẠNG THÁI 2: ĐANG PHÂN TÍCH (SCANNING PROGRESS)
      ──────────────────────────────────────────────────────────── */}
      {appStep === "analyzing" && (
        <main className="pt-24 pb-16 max-w-lg mx-auto px-6 w-full flex-1 flex flex-col justify-center text-center">
          <div className="bg-[#111827] border border-[#1E293B] rounded-2xl p-8 shadow-2xl space-y-6">
            <div className="w-16 h-16 mx-auto rounded-full border-4 border-[#1E293B] border-t-[#10b981] animate-spin flex items-center justify-center">
              <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">
                {analyzingProgress}%
              </span>
            </div>

            <div>
              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-lg font-bold text-[#f8fafc]">
                AI Đang Phân Tích &amp; Bóc Tách Dữ Liệu
              </h2>
              <p className="text-xs text-[#94a3b8] mt-1 font-['Inter',sans-serif]">
                Đang đối chiếu các từ khóa kỹ thuật giữa file CV và JD mục tiêu...
              </p>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2 bg-[#181b25] rounded-full overflow-hidden border border-[#1E293B]">
              <div
                className="h-full bg-[#10b981] transition-all duration-300"
                style={{ width: `${analyzingProgress}%` }}
              ></div>
            </div>

            <div className="space-y-1.5 text-xs text-[#94a3b8] font-['JetBrains_Mono',monospace]">
              <div className="text-[#4edea3]">✓ Đã trích xuất các section từ CV</div>
              <div className={analyzingProgress > 40 ? "text-[#4edea3]" : "text-[#64748b]"}>
                {analyzingProgress > 40 ? "✓ Đã bóc tách 20 từ khóa từ JD" : "• Đang quét từ khóa JD..."}
              </div>
              <div className={analyzingProgress > 80 ? "text-[#4edea3]" : "text-[#64748b]"}>
                {analyzingProgress > 80 ? "✓ Hoàn tất tính toán ma trận ATS" : "• Đang tính toán điểm số..."}
              </div>
            </div>
          </div>
        </main>
      )}

      {/* ────────────────────────────────────────────────────────────
          3. TRẠNG THÁI 3: KẾT QUẢ PHÂN TÍCH & CHAT AI
      ──────────────────────────────────────────────────────────── */}
      {appStep === "result" && (
        <main className="flex-1 pt-24 pb-28 px-4 sm:px-6 max-w-[920px] w-full mx-auto flex flex-col justify-between">
          {/* Top Session Control Bar */}
          <div className="py-3 px-4 rounded-xl bg-[#111827] border border-[#1E293B] mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-[#4edea3] font-semibold">CV:</span>
                <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef] bg-[#181b25] px-2 py-0.5 rounded border border-[#1E293B]">
                  {uploadedFile?.name || "CV_Da_Tai_Len.pdf"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#94a3b8]">Đối chiếu:</span>
                <span className="text-[#06b6d4] font-medium font-['JetBrains_Mono',monospace]">
                  VNG Corp • Senior Python
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {/* Nút Quay Lại Đổi CV/JD */}
              <button
                type="button"
                onClick={() => setAppStep("input")}
                aria-label="Đổi CV hoặc dán JD khác"
                className="flex items-center gap-1.5 text-xs font-semibold bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981]/50 px-3 py-1.5 rounded transition-all"
              >
                <svg className="w-3.5 h-3.5 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Đổi CV / Dán lại JD</span>
              </button>

              {/* Nút Báo Cáo ATS */}
              <button
                type="button"
                onClick={() => setIsInsightsDrawerOpen(true)}
                aria-label="Mở ngăn kéo Báo cáo Điểm ATS và Phân tích"
                className="flex items-center gap-1.5 text-xs font-medium bg-[#10b981]/10 hover:bg-[#10b981]/20 text-[#4edea3] border border-[#10b981]/30 px-3 py-1.5 rounded transition-all shadow-sm"
              >
                <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
                <span className="font-['JetBrains_Mono',monospace] font-bold">94% ATS</span>
              </button>
            </div>
          </div>

          {/* Quick Score Overview Banner */}
          <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-5 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full border-4 border-[#1E293B] flex items-center justify-center relative shrink-0">
                <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <path className="text-[#1E293B]" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="100, 100" strokeWidth="4" />
                  <path className="text-[#4edea3]" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="94, 100" strokeWidth="4" />
                </svg>
                <span className="text-sm font-extrabold text-[#4edea3] font-['JetBrains_Mono',monospace]">94%</span>
              </div>
              <div>
                <div className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                  Độ Tương Thích Tuyệt Vời Với JD VNG Corporation
                </div>
                <div className="text-xs text-[#94a3b8] mt-0.5">
                  Khớp 18/20 kỹ năng • Đạt chuẩn lọc sơ loại ATS 2026
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-[#94a3b8]">Thiếu từ khóa:</span>
              <span className="text-xs font-['JetBrains_Mono',monospace] bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/30 px-2 py-0.5 rounded">
                Kubernetes
              </span>
              <span className="text-xs font-['JetBrains_Mono',monospace] bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/30 px-2 py-0.5 rounded">
                Distributed Tracing
              </span>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="space-y-6 flex-1">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                {/* Agent Header */}
                {msg.sender === "ai" && (
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-full bg-[#10b981] text-[#090D16] font-bold text-[11px] flex items-center justify-center font-['Plus_Jakarta_Sans',sans-serif]">
                      AI
                    </div>
                    <span className="text-xs font-semibold text-[#dfe2ef]">{msg.agentName}</span>
                    <span className="text-[10px] text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-1.5 py-0.2 rounded font-['JetBrains_Mono',monospace]">
                      {msg.agentRole}
                    </span>
                    <span className="text-[11px] text-[#64748b]">{msg.timestamp}</span>
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`p-5 rounded-lg text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-[#181b25] text-[#dfe2ef] border border-[#1E293B] max-w-xl"
                      : "bg-[#111827] text-[#dfe2ef] border border-[#1E293B] w-full shadow-lg"
                  }`}
                >
                  <p className="whitespace-pre-line mb-4 font-['Inter',sans-serif]">{msg.content}</p>

                  {/* AI Reasoning Accordion */}
                  {msg.reasoning && msg.reasoning.length > 0 && (
                    <div className="mb-4 bg-[#181b25] border border-[#1E293B] rounded-md overflow-hidden">
                      <button
                        type="button"
                        onClick={() => setIsReasoningOpen(!isReasoningOpen)}
                        aria-label="Mở rộng quá trình suy luận của AI"
                        className="w-full px-3.5 py-2 text-xs font-semibold flex items-center justify-between text-[#94a3b8] hover:text-[#4edea3] bg-[#141822] transition-colors"
                      >
                        <div className="flex items-center gap-2 font-['JetBrains_Mono',monospace]">
                          <span className="w-2 h-2 rounded-full bg-[#4edea3] animate-ping"></span>
                          Tiến trình phân tích &amp; Suy luận của AI ({msg.reasoning.length} bước)
                        </div>
                        <svg
                          className={`w-4 h-4 transform transition-transform duration-150 ${
                            isReasoningOpen ? "rotate-180" : ""
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {isReasoningOpen && (
                        <div className="p-3.5 space-y-2 border-t border-[#1E293B] text-xs text-[#bbcabf] font-['JetBrains_Mono',monospace]">
                          {msg.reasoning.map((step, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                              <span className="text-[#4edea3]">✓</span>
                              <span>{step}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* STAR Method Diff Comparison Block */}
                  {msg.starDiff && (
                    <div className="bg-[#181b25] border border-[#1E293B] rounded-md p-4 mb-4 space-y-3">
                      <div className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif] flex items-center justify-between">
                        <span>So sánh tối ưu câu mô tả (STAR Method)</span>
                        <span className="text-[#10b981] font-['JetBrains_Mono',monospace]">+4% ATS Impact</span>
                      </div>

                      {/* Original */}
                      <div className="bg-[#111827] p-3 rounded border border-red-900/40 text-xs">
                        <div className="text-red-400 font-semibold mb-1 flex items-center gap-1.5 font-['JetBrains_Mono',monospace]">
                          <span>- Bản gốc (Chưa định lượng):</span>
                        </div>
                        <p className="text-[#94a3b8] line-through">{msg.starDiff.original}</p>
                      </div>

                      {/* Improved */}
                      <div className="bg-[#111827] p-3 rounded border border-[#10b981]/50 text-xs">
                        <div className="text-[#4edea3] font-semibold mb-1 flex items-center gap-1.5 font-['JetBrains_Mono',monospace]">
                          <span>+ Bản đề xuất (Chuẩn ATS &amp; STAR):</span>
                        </div>
                        <p className="text-[#f8fafc] font-medium leading-relaxed">{msg.starDiff.improved}</p>
                      </div>

                      {/* Explanation */}
                      <div className="text-xs text-[#94a3b8] italic border-l-2 border-[#10b981] pl-2.5">
                        💡 {msg.starDiff.explanation}
                      </div>
                    </div>
                  )}

                  {/* Interactive Action Prompt Chips */}
                  {msg.actionChips && (
                    <div className="flex flex-wrap gap-2 pt-2">
                      {msg.actionChips.map((chip, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setInputPrompt(chip)}
                          aria-label={`Gợi ý: ${chip}`}
                          className="text-xs bg-[#181b25] hover:bg-[#10b981]/15 text-[#dfe2ef] hover:text-[#4edea3] border border-[#1E293B] hover:border-[#10b981]/50 px-3 py-1.5 rounded-full transition-all flex items-center gap-1.5 font-medium"
                        >
                          <span>⚡</span>
                          <span>{chip}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </main>
      )}

      {/* ────────────────────────────────────────────────────────────
          KHUNG NHẬP LIỆU PROMPT CỐ ĐỊNH Ở ĐÁY (Khi ở chế độ Kết quả)
      ──────────────────────────────────────────────────────────── */}
      {appStep === "result" && (
        <div className="fixed bottom-0 left-0 w-full z-30 bg-[#090D16]/90 backdrop-blur-md border-t border-[#1E293B] py-3.5 px-4 sm:px-6">
          <div className="max-w-[920px] mx-auto">
            <div className="relative bg-[#111827] border border-[#1E293B] focus-within:border-[#10b981] rounded-xl shadow-2xl transition-all">
              <textarea
                rows={2}
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Hỏi AI: Tối ưu mục tóm tắt bản thân, tìm từ khóa còn thiếu, hoặc tạo câu hỏi phỏng vấn... (Enter để gửi)"
                aria-label="Nhập câu lệnh hỏi AI Career Agent"
                className="w-full bg-transparent text-sm text-[#dfe2ef] placeholder-[#64748b] px-4 pt-3 pb-10 resize-none outline-none font-['Inter',sans-serif]"
              />

              <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setAppStep("input")}
                  aria-label="Đổi file CV hoặc dán JD mới"
                  className="text-xs text-[#94a3b8] hover:text-[#4edea3] flex items-center gap-1 px-2 py-1 rounded hover:bg-[#181b25] transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Đổi CV / JD</span>
                </button>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-[#64748b] hidden sm:inline font-['JetBrains_Mono',monospace]">
                    Shift + Enter để xuống dòng
                  </span>
                  <button
                    type="button"
                    onClick={handleSendMessage}
                    aria-label="Gửi yêu cầu tới AI"
                    className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold px-4 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <span>Gửi</span>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────
          RIGHT SLIDE-OVER DRAWER (Insights Panel: ATS & Analytics)
      ──────────────────────────────────────────────────────────── */}
      {isInsightsDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setIsInsightsDrawerOpen(false)}
          ></div>

          <div className="relative w-full max-w-[420px] bg-[#0f131c] border-l border-[#1E293B] h-full flex flex-col z-10 shadow-2xl">
            <div className="p-4 border-b border-[#1E293B] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] animate-pulse"></span>
                <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-sm font-bold text-[#dfe2ef]">
                  Báo Cáo Điểm ATS &amp; Phân Tích
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setIsInsightsDrawerOpen(false)}
                aria-label="Đóng ngăn kéo Báo cáo ATS"
                className="p-1 rounded text-[#94a3b8] hover:text-[#dfe2ef] hover:bg-[#181b25] transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              <div className="bg-[#111827] border border-[#1E293B] rounded-lg p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-[#94a3b8] font-['Plus_Jakarta_Sans',sans-serif] uppercase tracking-wider mb-1">
                      ATS Match Score
                    </div>
                    <div className="text-4xl font-extrabold text-[#4edea3] font-['JetBrains_Mono',monospace]">
                      94%
                    </div>
                    <div className="text-xs text-[#10b981] font-medium mt-1">Khả năng vượt qua lọc CV: Cực cao</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-5 pt-4 border-t border-[#1E293B] text-center">
                  <div>
                    <div className="text-[11px] text-[#94a3b8]">Kỹ Năng</div>
                    <div className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">95%</div>
                  </div>
                  <div>
                    <div className="text-[11px] text-[#94a3b8]">Tác Động</div>
                    <div className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">90%</div>
                  </div>
                  <div>
                    <div className="text-[11px] text-[#94a3b8]">Định Dạng</div>
                    <div className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">98%</div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
                  Ma Trận Kỹ Năng
                </h3>
                <div className="space-y-2 text-xs">
                  <div className="text-[#4edea3] font-semibold">✓ Đã khớp: FastAPI, PostgreSQL, Docker, Redis, Microservices</div>
                  <div className="text-[#f59e0b] font-semibold">⚠ Cần bổ sung: Kubernetes Cluster, Distributed Tracing</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
