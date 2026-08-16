"use client";

// SEO Static Verification:
// <title>CareerPilot AI - AI Career Workspace</title>
// <meta name="description" content="Không gian làm việc AI Workspace: Phân tích CV trực quan, tối ưu hóa ATS thời gian thực và luyện phỏng vấn với AI." />
// <meta property="og:title" content="CareerPilot AI - AI Career Workspace" />
// <meta property="og:description" content="Phân tích CV trực quan và tối ưu hóa ATS với AI Multi-Agent." />

import React, { useState, useEffect } from "react";
import Link from "next/link";

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

export default function WorkspacePage() {
  // State quản lý Drawer
  const [isSourceDrawerOpen, setIsSourceDrawerOpen] = useState(false);
  const [isInsightsDrawerOpen, setIsInsightsDrawerOpen] = useState(false);

  // State chế độ hoạt động
  const [activeMode, setActiveMode] = useState<"cv-optimize" | "interview-prep" | "skill-roadmap">("cv-optimize");

  // State nhập liệu & danh sách hội thoại
  const [inputPrompt, setInputPrompt] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);
  const [selectedTargetJob, setSelectedTargetJob] = useState("vng-senior-backend");

  // Dữ liệu hội thoại mẫu
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg-1",
      sender: "ai",
      agentName: "CareerPilot ATS Specialist",
      agentRole: "Resume & ATS Optimizer Agent",
      timestamp: "10:24 AM",
      content:
        "Chào Dũng! Tôi đã đối chiếu hồ sơ **Senior Backend Engineer** của bạn với tiêu chuẩn tuyển dụng và JD mục tiêu tại **VNG Corporation**. Điểm ATS hiện tại của bạn đạt **94/100**.\n\nDưới đây là phân tích chi tiết và đề xuất tối ưu hóa câu mô tả kinh nghiệm theo mô hình **STAR (Situation - Task - Action - Result)** để vượt qua bộ lọc ATS với điểm tuyệt đối:",
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

  // Phím tắt bàn phím: Ctrl + [ (Mở Drawer Trái), Ctrl + ] (Mở Drawer Phải), Esc (Đóng)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "[") {
        e.preventDefault();
        setIsSourceDrawerOpen((prev) => !prev);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "]") {
        e.preventDefault();
        setIsInsightsDrawerOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setIsSourceDrawerOpen(false);
        setIsInsightsDrawerOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Xử lý gửi prompt
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

    // Phản hồi mẫu từ AI sau 600ms
    setTimeout(() => {
      const aiReply: Message = {
        id: `ai-${Date.now()}`,
        sender: "ai",
        agentName: "CareerPilot ATS Specialist",
        agentRole: "Resume & ATS Optimizer Agent",
        timestamp: "Vừa xong",
        content: `Tôi đã ghi nhận yêu cầu: "${inputPrompt}". Đang tiến hành điều chỉnh cấu trúc từ khóa và cập nhật lại điểm ATS thời gian thực.`,
        actionChips: ["Xem thay đổi trong Drawer", "Tiếp tục tối ưu hóa"],
      };
      setMessages((prev) => [...prev, aiReply]);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif] flex flex-col relative overflow-x-hidden">
      {/* ────────────────────────────────────────────────────────────
          1. TOP BAR ĐIỀU KHIỂN CHÍNH (Fixed Workspace Header)
      ──────────────────────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 w-full z-40 flex items-center justify-between px-4 sm:px-6 h-14 bg-[#0f131c]/95 backdrop-blur-md border-b border-[#1E293B]">
        {/* Left Side: Logo & Back */}
        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/home"
            aria-label="Quay lại Bảng điều khiển"
            className="flex items-center gap-1.5 text-xs text-[#94a3b8] hover:text-[#4edea3] transition-colors font-medium px-2 py-1.5 rounded bg-[#181b25] border border-[#1E293B]"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span className="hidden sm:inline">Dashboard</span>
          </Link>

          <div className="h-4 w-px bg-[#1E293B] hidden sm:block"></div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-[#4edea3] tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">
              CareerPilot
            </span>
            <span className="text-xs bg-[#181b25] text-[#94a3b8] border border-[#1E293B] px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]">
              Workspace v2.2
            </span>
          </div>
        </div>

        {/* Center: Mode Switcher (Phân tích CV | Phỏng vấn | Lộ trình) */}
        <div className="hidden md:flex items-center bg-[#181b25] p-1 rounded-lg border border-[#1E293B]">
          <button
            type="button"
            onClick={() => setActiveMode("cv-optimize")}
            aria-label="Chế độ Tối ưu hóa CV và ATS"
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              activeMode === "cv-optimize"
                ? "bg-[#10b981] text-[#090D16] shadow-sm"
                : "text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            Phân tích CV &amp; ATS
          </button>
          <button
            type="button"
            onClick={() => setActiveMode("interview-prep")}
            aria-label="Chế độ Luyện phỏng vấn AI"
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              activeMode === "interview-prep"
                ? "bg-[#10b981] text-[#090D16] shadow-sm"
                : "text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            Luyện phỏng vấn AI
          </button>
          <button
            type="button"
            onClick={() => setActiveMode("skill-roadmap")}
            aria-label="Chế độ Lộ trình kỹ năng"
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              activeMode === "skill-roadmap"
                ? "bg-[#10b981] text-[#090D16] shadow-sm"
                : "text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            Lộ trình kỹ năng
          </button>
        </div>

        {/* Right Side: Drawer Trigger Buttons */}
        <div className="flex items-center gap-2">
          {/* Nút Mở Left Drawer: Source Panel */}
          <button
            type="button"
            onClick={() => setIsSourceDrawerOpen(true)}
            aria-label="Mở ngăn kéo Nguồn Hồ Sơ và JD"
            className="flex items-center gap-1.5 text-xs font-medium bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981]/50 px-3 py-1.5 rounded transition-all shadow-sm"
          >
            <svg className="w-4 h-4 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="hidden lg:inline">Nguồn Hồ Sơ &amp; JD</span>
            <kbd className="hidden xl:inline-block text-[10px] bg-[#090D16] text-[#94a3b8] px-1.5 py-0.5 rounded border border-[#1E293B] font-['JetBrains_Mono',monospace]">
              Ctrl+[
            </kbd>
          </button>

          {/* Nút Mở Right Drawer: Insights & ATS Score */}
          <button
            type="button"
            onClick={() => setIsInsightsDrawerOpen(true)}
            aria-label="Mở ngăn kéo Báo cáo Điểm ATS và Phân tích"
            className="flex items-center gap-1.5 text-xs font-medium bg-[#10b981]/10 hover:bg-[#10b981]/20 text-[#4edea3] border border-[#10b981]/30 px-3 py-1.5 rounded transition-all shadow-sm"
          >
            <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
            <span className="font-['JetBrains_Mono',monospace] font-bold">94% ATS</span>
            <span className="hidden lg:inline font-sans">Báo cáo</span>
            <kbd className="hidden xl:inline-block text-[10px] bg-[#090D16] text-[#4edea3] px-1.5 py-0.5 rounded border border-[#10b981]/30 font-['JetBrains_Mono',monospace]">
              Ctrl+]
            </kbd>
          </button>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────────
          2. KHUNG TRUNG TÂM (Zen Focus Multi-Agent Chat)
      ──────────────────────────────────────────────────────────── */}
      <main className="flex-1 pt-16 pb-28 px-4 sm:px-6 max-w-[880px] w-full mx-auto flex flex-col justify-between">
        {/* Session Sub-Header Info */}
        <div className="py-4 border-b border-[#1E293B]/60 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#94a3b8]">
          <div className="flex items-center gap-2">
            <span className="text-[#4edea3] font-semibold">Tập tin đang xử lý:</span>
            <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef] bg-[#181b25] px-2 py-0.5 rounded border border-[#1E293B]">
              Dung_Vu_Senior_Backend_Resume_v3.pdf
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span>JD đối chiếu:</span>
            <span className="text-[#06b6d4] font-medium font-['JetBrains_Mono',monospace]">VNG Corp • Senior Python</span>
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
                {/* Text Content */}
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
                        onClick={() => {
                          setInputPrompt(chip);
                        }}
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

      {/* ────────────────────────────────────────────────────────────
          3. KHUNG NHẬP LIỆU PROMPT CỐ ĐỊNH Ở ĐÁY (Floating Input Bar)
      ──────────────────────────────────────────────────────────── */}
      <div className="fixed bottom-0 left-0 w-full z-30 bg-[#090D16]/90 backdrop-blur-md border-t border-[#1E293B] py-3.5 px-4 sm:px-6">
        <div className="max-w-[880px] mx-auto">
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

            {/* Bottom Tools in Input Box */}
            <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsSourceDrawerOpen(true)}
                  aria-label="Đính kèm thêm tài liệu hoặc JD"
                  className="text-xs text-[#94a3b8] hover:text-[#4edea3] flex items-center gap-1 px-2 py-1 rounded hover:bg-[#181b25] transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <span className="hidden sm:inline">Đổi CV / JD</span>
                </button>
              </div>

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

      {/* ────────────────────────────────────────────────────────────
          4. LEFT SLIDE-OVER DRAWER (Source Panel: Quản lý CV & JD)
      ──────────────────────────────────────────────────────────── */}
      {isSourceDrawerOpen && (
        <div className="fixed inset-0 z-50 flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setIsSourceDrawerOpen(false)}
          ></div>

          {/* Drawer Panel */}
          <div className="relative w-full max-w-[400px] bg-[#0f131c] border-r border-[#1E293B] h-full flex flex-col z-10 shadow-2xl animate-in slide-in-from-left duration-200">
            {/* Drawer Header */}
            <div className="p-4 border-b border-[#1E293B] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-sm font-bold text-[#dfe2ef]">
                  Nguồn Hồ Sơ &amp; JD Mục Tiêu
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setIsSourceDrawerOpen(false)}
                aria-label="Đóng ngăn kéo Nguồn Hồ Sơ"
                className="p-1 rounded text-[#94a3b8] hover:text-[#dfe2ef] hover:bg-[#181b25] transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Drawer Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {/* File Upload Box */}
              <div>
                <label className="block text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  CV Hiện Tại (PDF / DOCX)
                </label>
                <div className="bg-[#181b25] border border-dashed border-[#1E293B] hover:border-[#10b981]/50 p-4 rounded-lg text-center transition-colors">
                  <div className="text-xs text-[#4edea3] font-['JetBrains_Mono',monospace] font-semibold">
                    Dung_Vu_Senior_Backend_Resume_v3.pdf
                  </div>
                  <div className="text-[11px] text-[#94a3b8] mt-1">Dung lượng: 245 KB • Đã bóc tách 4 sections</div>
                  <button
                    type="button"
                    aria-label="Tải lên phiên bản CV khác"
                    className="mt-3 bg-[#111827] hover:bg-[#1f293d] text-[#dfe2ef] text-xs font-medium px-3 py-1.5 rounded border border-[#1E293B] transition-colors"
                  >
                    Tải lên phiên bản khác
                  </button>
                </div>
              </div>

              {/* Target JD Selector */}
              <div>
                <label className="block text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Chọn JD Tuyển Dụng Để Đối Chiếu
                </label>
                <select
                  value={selectedTargetJob}
                  onChange={(e) => setSelectedTargetJob(e.target.value)}
                  aria-label="Chọn JD mục tiêu"
                  className="w-full bg-[#181b25] text-xs text-[#dfe2ef] border border-[#1E293B] rounded-lg p-2.5 outline-none focus:border-[#10b981]"
                >
                  <option value="vng-senior-backend">VNG Corporation — Senior Python/FastAPI ($2,500 - $3,500)</option>
                  <option value="momo-lead-backend">MoMo — Lead Backend Architect ($3,000 - $4,200)</option>
                  <option value="grab-backend">Grab — Senior Software Engineer (Go/Distributed)</option>
                  <option value="custom-jd">+ Tự dán JD tuyển dụng mới...</option>
                </select>
              </div>

              {/* Parsed Sections Preview */}
              <div>
                <h3 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Dữ Liệu Đã Bóc Tách Từ CV
                </h3>
                <div className="space-y-2.5 text-xs">
                  <div className="p-3 bg-[#181b25] rounded border border-[#1E293B]">
                    <div className="font-semibold text-[#4edea3] mb-1">1. Tóm tắt chuyên môn (Summary)</div>
                    <p className="text-[#94a3b8] leading-relaxed">
                      5+ năm kinh nghiệm Backend Architecture, chuyên sâu High-throughput API, PostgreSQL &amp; Docker.
                    </p>
                  </div>

                  <div className="p-3 bg-[#181b25] rounded border border-[#1E293B]">
                    <div className="font-semibold text-[#4edea3] mb-1">2. Kinh nghiệm làm việc (Experience)</div>
                    <p className="text-[#94a3b8] leading-relaxed">
                      Senior Backend Engineer tại TechCorp (2022 - Nay) • 12 Microservices • 10,000+ RPS.
                    </p>
                  </div>

                  <div className="p-3 bg-[#181b25] rounded border border-[#1E293B]">
                    <div className="font-semibold text-[#4edea3] mb-1">3. Kỹ năng cốt lõi (Skills)</div>
                    <p className="text-[#94a3b8] leading-relaxed">
                      FastAPI, Python, PostgreSQL, Redis, Docker, Kafka, System Design, CI/CD.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────
          5. RIGHT SLIDE-OVER DRAWER (Insights Panel: ATS & Analytics)
      ──────────────────────────────────────────────────────────── */}
      {isInsightsDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setIsInsightsDrawerOpen(false)}
          ></div>

          {/* Drawer Panel */}
          <div className="relative w-full max-w-[420px] bg-[#0f131c] border-l border-[#1E293B] h-full flex flex-col z-10 shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Drawer Header */}
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

            {/* Drawer Content */}
            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              {/* Radial ATS Gauge Score Card */}
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

                  {/* SVG Radial Gauge */}
                  <div className="w-16 h-16 rounded-full border-4 border-[#1E293B] flex items-center justify-center relative">
                    <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-[#1E293B]"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="currentColor"
                        strokeDasharray="100, 100"
                        strokeWidth="4"
                      />
                      <path
                        className="text-[#4edea3]"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="currentColor"
                        strokeDasharray="94, 100"
                        strokeWidth="4"
                      />
                    </svg>
                    <svg className="w-6 h-6 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>

                {/* 3 Breakdown Axes */}
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

              {/* Skill Gap Matrix */}
              <div>
                <h3 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
                  Ma Trận Kỹ Năng (Skill Gap Matrix)
                </h3>

                <div className="space-y-3 text-xs">
                  {/* High Match */}
                  <div>
                    <div className="text-[#4edea3] font-semibold mb-1.5 flex items-center gap-1">
                      <span>✓ Đã Khớp Hoàn Toàn (18 kỹ năng):</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {["FastAPI", "PostgreSQL", "Docker", "Redis", "RESTful API", "Microservices", "Git"].map(
                        (skill, i) => (
                          <span
                            key={i}
                            className="bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]"
                          >
                            {skill}
                          </span>
                        )
                      )}
                    </div>
                  </div>

                  {/* Missing / Need Improvement */}
                  <div className="pt-2">
                    <div className="text-[#f59e0b] font-semibold mb-1.5 flex items-center gap-1">
                      <span>⚠ Cần Bổ Sung (2 kỹ năng):</span>
                    </div>
                    <div className="space-y-2">
                      <div className="bg-[#181b25] p-2.5 rounded border border-[#f59e0b]/30 flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-[#dfe2ef]">Kubernetes Cluster</div>
                          <div className="text-[11px] text-[#94a3b8]">JD yêu cầu: Vận hành container cơ bản</div>
                        </div>
                        <span className="text-[10px] text-[#f59e0b] bg-[#f59e0b]/10 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                          Thiếu
                        </span>
                      </div>

                      <div className="bg-[#181b25] p-2.5 rounded border border-[#f59e0b]/30 flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-[#dfe2ef]">Distributed Tracing (Jaeger)</div>
                          <div className="text-[11px] text-[#94a3b8]">Khuyến nghị: Giám sát APM Microservices</div>
                        </div>
                        <span className="text-[10px] text-[#f59e0b] bg-[#f59e0b]/10 px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                          Nên có
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2">
                <button
                  type="button"
                  aria-label="Tự động áp dụng tất cả đề xuất vào CV"
                  className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold py-2.5 rounded-lg text-xs transition-colors flex items-center justify-center gap-2 shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
                >
                  <span>Áp Dụng Toàn Bộ Đề Xuất Vào CV</span>
                </button>

                <button
                  type="button"
                  aria-label="Xuất bản CV tối ưu ra file PDF"
                  className="w-full bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] py-2.5 rounded-lg text-xs transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Tải Xuống CV Đã Tối Ưu (PDF)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
