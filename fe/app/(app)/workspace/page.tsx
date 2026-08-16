"use client";

// SEO Static Verification:
// <title>CareerPilot AI - AI Career Studio Workspace</title>
// <meta name="description" content="Không gian làm việc 3 cột theo chuẩn NotebookLM: Nguồn tài liệu CV & JD, Trung tâm đối thoại AI, và Studio quản lý các bản CV đã tối ưu." />
// <meta property="og:title" content="CareerPilot AI - AI Career Studio Workspace" />
// <meta property="og:description" content="Không gian làm việc 3 cột chuẩn NotebookLM phân tích CV và tối ưu ATS." />

import React, { useState, useRef } from "react";

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
  vng: {
    name: "JD VNG Corporation — Senior Python / FastAPI",
    company: "VNG Corp",
    role: "Senior Python",
    content: `Công ty: VNG Corporation
Vị trí: Senior Python / FastAPI Engineer
Yêu cầu:
- 4+ năm kinh nghiệm phát triển backend với Python (FastAPI / Django).
- Thành thạo thiết kế RESTful API, Microservices architecture và gRPC.
- Kinh nghiệm thực tế với PostgreSQL, tối ưu query, caching với Redis.
- Hiểu biết sâu về Docker, CI/CD, hệ thống phân tán chịu tải cao (10,000+ RPS).
- Ưu tiên ứng viên có kinh nghiệm với Distributed Tracing (Jaeger) và Kafka.`,
  },
  momo: {
    name: "JD MoMo — Lead Backend Architect",
    company: "MoMo",
    role: "Lead Architect",
    content: `Công ty: MoMo (M-Service)
Vị trí: Lead Backend Architect
Yêu cầu:
- 6+ năm kinh nghiệm Backend Architecture & Distributed Systems.
- Thành thạo kiến trúc Microservices, Message Broker (Kafka / RabbitMQ).
- Chuyên sâu Database Sharding, High-concurrency và Payment Gateway Security.
- Kinh nghiệm quản trị container với Kubernetes Cluster.`,
  },
};

export default function WorkspacePage() {
  // Mobile Tab State (cho màn hình nhỏ): "sources" | "chat" | "studio"
  const [activeMobileTab, setActiveMobileTab] = useState<"sources" | "chat" | "studio">("chat");

  // State Nguồn tài liệu (Cột 1)
  const [sources, setSources] = useState([
    {
      id: "src-1",
      name: "Dung_Vu_Senior_Backend_Resume_v3.pdf",
      type: "resume",
      size: "245 KB",
      active: true,
      sections: ["Summary", "Experience (3)", "Skills (18)", "Education"],
    },
    {
      id: "src-2",
      name: "JD_VNG_Senior_Python_FastAPI.txt",
      type: "jd",
      size: "1.2 KB",
      active: true,
      company: "VNG Corporation",
    },
  ]);

  const [selectedJdKey, setSelectedJdKey] = useState<"vng" | "momo">("vng");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State Phiên bản CV trong Studio (Cột 3)
  const [selectedVersion, setSelectedVersion] = useState<"v2" | "v1">("v2");
  const [isCopied, setIsCopied] = useState(false);

  // State Hội thoại AI (Cột 2)
  const [inputPrompt, setInputPrompt] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg-1",
      sender: "ai",
      agentName: "CareerPilot ATS Specialist",
      agentRole: "Resume & ATS Optimizer Agent",
      timestamp: "10:24 AM",
      content:
        "Chào Dũng! Tôi đã nạp 2 nguồn tài liệu: **File CV gốc** và **JD Senior Python tại VNG Corp**. Điểm tương thích ATS đạt **94/100**.\n\nDưới đây là đề xuất tối ưu hóa câu mô tả kinh nghiệm dự án Cổng thanh toán theo mô hình **STAR (Situation - Task - Action - Result)** để vượt qua bộ lọc ATS với điểm tuyệt đối:",
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
        "Áp dụng câu này vào Studio bên phải",
        "Bổ sung kỹ năng Kubernetes còn thiếu",
        "Tạo 3 câu hỏi phỏng vấn cho dự án này",
        "Xuất file CV tối ưu",
      ],
    },
  ]);

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

    setTimeout(() => {
      const aiReply: Message = {
        id: `ai-${Date.now()}`,
        sender: "ai",
        agentName: "CareerPilot ATS Specialist",
        agentRole: "Resume & ATS Optimizer Agent",
        timestamp: "Vừa xong",
        content: `Tôi đã cập nhật phân tích theo yêu cầu: "${inputPrompt}". Phiên bản CV trong Studio bên phải đã được đồng bộ các từ khóa mới nhất.`,
        actionChips: ["Xem bản CV mới trong Studio", "Tối ưu hóa tiếp"],
      };
      setMessages((prev) => [...prev, aiReply]);
    }, 600);
  };

  // Toggle checkbox nguồn
  const toggleSource = (id: string) => {
    setSources((prev) =>
      prev.map((src) => (src.id === id ? { ...src, active: !src.active } : src))
    );
  };

  // Sao chép nội dung CV
  const handleCopyResume = () => {
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="pt-16 h-screen flex flex-col bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif] overflow-hidden">
      {/* ────────────────────────────────────────────────────────────
          MOBILE NAVIGATION BAR (Chỉ hiển thị trên Mobile / Tablet nhỏ)
      ──────────────────────────────────────────────────────────── */}
      <div className="lg:hidden flex items-center justify-around border-b border-[#1E293B] bg-[#0c101b] h-11 text-xs shrink-0 font-medium">
        <button
          type="button"
          onClick={() => setActiveMobileTab("sources")}
          className={`flex items-center gap-1.5 py-2 px-3 border-b-2 transition-all ${
            activeMobileTab === "sources"
              ? "border-[#10b981] text-[#4edea3] font-semibold"
              : "border-transparent text-[#94a3b8]"
          }`}
        >
          <span>📂 Nguồn (2)</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveMobileTab("chat")}
          className={`flex items-center gap-1.5 py-2 px-3 border-b-2 transition-all ${
            activeMobileTab === "chat"
              ? "border-[#10b981] text-[#4edea3] font-semibold"
              : "border-transparent text-[#94a3b8]"
          }`}
        >
          <span>💬 Chat AI</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveMobileTab("studio")}
          className={`flex items-center gap-1.5 py-2 px-3 border-b-2 transition-all ${
            activeMobileTab === "studio"
              ? "border-[#10b981] text-[#4edea3] font-semibold"
              : "border-transparent text-[#94a3b8]"
          }`}
        >
          <span>📑 Studio (94%)</span>
        </button>
      </div>

      {/* ────────────────────────────────────────────────────────────
          BỐ CỤC 3 PHÂN VÙNG NOTEBOOKLM (3-PANE STUDIO WORKSPACE)
      ──────────────────────────────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">
        {/* ══════════════════════════════════════════════════════════
            CỘT 1: NGUỒN TÀI LIỆU (SOURCES PANEL - 26% WIDTH)
        ══════════════════════════════════════════════════════════ */}
        <aside
          className={`w-full lg:w-[26%] xl:w-[25%] border-r border-[#1E293B] bg-[#0c101b] flex flex-col shrink-0 overflow-y-auto ${
            activeMobileTab === "sources" ? "flex" : "hidden lg:flex"
          }`}
        >
          {/* Header Cột 1 */}
          <div className="p-4 border-b border-[#1E293B] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-xs font-bold uppercase tracking-wider text-[#dfe2ef]">
                Nguồn Tài Liệu (2)
              </h2>
            </div>
          </div>

          {/* Danh sách Nguồn đã nạp */}
          <div className="p-4 space-y-3 flex-1">
            {sources.map((src) => (
              <div
                key={src.id}
                className={`p-3 rounded-lg border transition-all ${
                  src.active
                    ? "bg-[#111827] border-[#1E293B] hover:border-[#10b981]/40"
                    : "bg-[#090D16]/50 border-[#1E293B]/40 opacity-60"
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-start gap-2">
                    <input
                      type="checkbox"
                      checked={src.active}
                      onChange={() => toggleSource(src.id)}
                      aria-label={`Kích hoạt nguồn ${src.name}`}
                      className="mt-0.5 accent-[#10b981] rounded cursor-pointer"
                    />
                    <div>
                      <div className="text-xs font-bold text-[#f8fafc] font-['JetBrains_Mono',monospace] leading-tight break-all">
                        {src.name}
                      </div>
                      <div className="text-[11px] text-[#94a3b8] mt-0.5">
                        {src.type === "resume" ? "File Hồ Sơ • " + src.size : "JD Tuyển Dụng • " + src.company}
                      </div>
                    </div>
                  </div>

                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-semibold shrink-0 font-['JetBrains_Mono',monospace] ${
                      src.type === "resume"
                        ? "bg-[#10b981]/15 text-[#4edea3]"
                        : "bg-[#06b6d4]/15 text-[#06b6d4]"
                    }`}
                  >
                    {src.type === "resume" ? "CV Gốc" : "Target JD"}
                  </span>
                </div>

                {src.sections && (
                  <div className="text-[11px] text-[#64748b] bg-[#181b25] px-2 py-1 rounded border border-[#1E293B] mt-2">
                    ✓ Đã bóc tách: {src.sections.join(" • ")}
                  </div>
                )}
              </div>
            ))}

            {/* Quick Upload Dropzone at Bottom of Column 1 */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border border-dashed border-[#1E293B] hover:border-[#10b981]/50 bg-[#181b25]/40 rounded-lg p-3 text-center cursor-pointer transition-colors mt-4"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                className="hidden"
                aria-label="Tải file lên"
              />
              <div className="text-xs text-[#94a3b8] hover:text-[#dfe2ef] flex items-center justify-center gap-1.5">
                <svg className="w-4 h-4 text-[#4edea3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                </svg>
                <span>Thả file CV mới vào đây</span>
              </div>
            </div>
          </div>

          {/* Quick JD Presets in Column 1 */}
          <div className="p-4 border-t border-[#1E293B] bg-[#090D16]">
            <div className="text-[11px] text-[#94a3b8] font-bold uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
              Đổi JD Tuyển Dụng Nhanh
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSelectedJdKey("vng")}
                className={`text-xs p-2 rounded text-left border transition-all ${
                  selectedJdKey === "vng"
                    ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/40 font-semibold"
                    : "bg-[#181b25] text-[#dfe2ef] border-[#1E293B] hover:border-[#3c4a42]"
                }`}
              >
                <div className="truncate font-bold">VNG Corp</div>
                <div className="text-[10px] text-[#94a3b8]">Senior Python</div>
              </button>
              <button
                type="button"
                onClick={() => setSelectedJdKey("momo")}
                className={`text-xs p-2 rounded text-left border transition-all ${
                  selectedJdKey === "momo"
                    ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/40 font-semibold"
                    : "bg-[#181b25] text-[#dfe2ef] border-[#1E293B] hover:border-[#3c4a42]"
                }`}
              >
                <div className="truncate font-bold">MoMo</div>
                <div className="text-[10px] text-[#94a3b8]">Lead Architect</div>
              </button>
            </div>
          </div>
        </aside>

        {/* ══════════════════════════════════════════════════════════
            CỘT 2: TRUNG TÂM HỘI THOẠI AI (CHAT CENTER - 44% WIDTH)
        ══════════════════════════════════════════════════════════ */}
        <section
          className={`flex-1 flex flex-col bg-[#090D16] overflow-hidden ${
            activeMobileTab === "chat" ? "flex" : "hidden lg:flex"
          }`}
        >
          {/* Header Cột 2 */}
          <div className="px-6 py-3 border-b border-[#1E293B] bg-[#0c101b] flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-[#10b981] text-[#090D16] font-bold text-xs flex items-center justify-center font-['Plus_Jakarta_Sans',sans-serif]">
                AI
              </div>
              <div>
                <div className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                  CareerPilot ATS Specialist
                </div>
                <div className="text-[10px] text-[#4edea3] font-['JetBrains_Mono',monospace]">
                  ● Đang phân tích 2 nguồn tài liệu
                </div>
              </div>
            </div>

            <div className="hidden sm:flex items-center gap-2">
              <span className="text-xs text-[#94a3b8] font-['JetBrains_Mono',monospace]">
                Đối chiếu: VNG Corporation
              </span>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                {/* Agent Header */}
                {msg.sender === "ai" && (
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold text-[#dfe2ef]">{msg.agentName}</span>
                    <span className="text-[10px] text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-1.5 py-0.2 rounded font-['JetBrains_Mono',monospace]">
                      {msg.agentRole}
                    </span>
                    <span className="text-[11px] text-[#64748b]">{msg.timestamp}</span>
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`p-4 sm:p-5 rounded-xl text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-[#181b25] text-[#dfe2ef] border border-[#1E293B] max-w-xl"
                      : "bg-[#111827] text-[#dfe2ef] border border-[#1E293B] w-full shadow-lg"
                  }`}
                >
                  <p className="whitespace-pre-line mb-4 font-['Inter',sans-serif]">{msg.content}</p>

                  {/* AI Reasoning Accordion */}
                  {msg.reasoning && msg.reasoning.length > 0 && (
                    <div className="mb-4 bg-[#181b25] border border-[#1E293B] rounded-lg overflow-hidden">
                      <button
                        type="button"
                        onClick={() => setIsReasoningOpen(!isReasoningOpen)}
                        aria-label="Mở rộng quá trình suy luận của AI"
                        className="w-full px-3.5 py-2 text-xs font-semibold flex items-center justify-between text-[#94a3b8] hover:text-[#4edea3] bg-[#141822] transition-colors"
                      >
                        <div className="flex items-center gap-2 font-['JetBrains_Mono',monospace]">
                          <span className="w-2 h-2 rounded-full bg-[#4edea3] animate-ping"></span>
                          Tiến trình phân tích ({msg.reasoning.length} bước)
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
                    <div className="bg-[#181b25] border border-[#1E293B] rounded-lg p-4 mb-4 space-y-3">
                      <div className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif] flex items-center justify-between">
                        <span>Đề xuất tối ưu câu mô tả (STAR Method)</span>
                        <span className="text-[#10b981] font-['JetBrains_Mono',monospace] font-bold">+4% ATS Impact</span>
                      </div>

                      {/* Original */}
                      <div className="bg-[#111827] p-3 rounded border border-red-900/40 text-xs">
                        <div className="text-red-400 font-semibold mb-1 font-['JetBrains_Mono',monospace]">
                          - Bản gốc (Chưa định lượng):
                        </div>
                        <p className="text-[#94a3b8] line-through">{msg.starDiff.original}</p>
                      </div>

                      {/* Improved */}
                      <div className="bg-[#111827] p-3 rounded border border-[#10b981]/50 text-xs">
                        <div className="text-[#4edea3] font-semibold mb-1 font-['JetBrains_Mono',monospace]">
                          + Bản đề xuất (Chuẩn ATS &amp; STAR):
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

          {/* Docked Input Prompt at Bottom of Column 2 */}
          <div className="p-4 border-t border-[#1E293B] bg-[#0c101b] shrink-0">
            <div className="relative bg-[#111827] border border-[#1E293B] focus-within:border-[#10b981] rounded-xl shadow-lg transition-all">
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
                className="w-full bg-transparent text-xs sm:text-sm text-[#dfe2ef] placeholder-[#64748b] px-4 pt-3 pb-9 resize-none outline-none font-['Inter',sans-serif]"
              />

              <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between">
                <span className="text-[11px] text-[#64748b] hidden sm:inline font-['JetBrains_Mono',monospace]">
                  Shift + Enter để xuống dòng
                </span>

                <button
                  type="button"
                  onClick={handleSendMessage}
                  aria-label="Gửi yêu cầu tới AI"
                  className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold px-4 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-1.5 shadow-sm ml-auto"
                >
                  <span>Gửi</span>
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════════
            CỘT 3: STUDIO & BẢN CV ĐÃ SỬA (ARTIFACTS - 30% WIDTH)
        ══════════════════════════════════════════════════════════ */}
        <aside
          className={`w-full lg:w-[30%] xl:w-[31%] border-l border-[#1E293B] bg-[#0c101b] flex flex-col shrink-0 overflow-y-auto ${
            activeMobileTab === "studio" ? "flex" : "hidden lg:flex"
          }`}
        >
          {/* Header Cột 3 */}
          <div className="p-4 border-b border-[#1E293B] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] animate-pulse"></span>
              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-xs font-bold uppercase tracking-wider text-[#dfe2ef]">
                Studio &amp; Bản CV Đã Tối Ưu
              </h2>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handleCopyResume}
                aria-label="Sao chép toàn bộ văn bản CV"
                className="text-xs bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] px-2 py-1 rounded transition-colors"
              >
                {isCopied ? "✓ Đã copy" : "Copy text"}
              </button>
            </div>
          </div>

          <div className="p-4 space-y-4 flex-1">
            {/* ATS Score Gauge Card */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-[#94a3b8] uppercase tracking-wider font-bold">
                    ATS Match Score
                  </div>
                  <div className="text-3xl font-extrabold text-[#4edea3] font-['JetBrains_Mono',monospace]">
                    94%
                  </div>
                  <div className="text-[11px] text-[#10b981] font-medium mt-0.5">
                    Khả năng vượt bộ lọc: Cực cao
                  </div>
                </div>

                <div className="w-14 h-14 rounded-full border-4 border-[#1E293B] flex items-center justify-center relative">
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
                  <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">94%</span>
                </div>
              </div>

              {/* 3 Axes */}
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-[#1E293B] text-center text-xs">
                <div>
                  <div className="text-[10px] text-[#94a3b8]">Kỹ Năng</div>
                  <div className="font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">95%</div>
                </div>
                <div>
                  <div className="text-[10px] text-[#94a3b8]">Tác Động</div>
                  <div className="font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">90%</div>
                </div>
                <div>
                  <div className="text-[10px] text-[#94a3b8]">Định Dạng</div>
                  <div className="font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">98%</div>
                </div>
              </div>
            </div>

            {/* Version Switcher */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Phiên Bản CV
                </span>
                <span className="text-[11px] text-[#4edea3] font-['JetBrains_Mono',monospace]">2 versions</span>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedVersion("v2")}
                  className={`flex-1 py-1.5 px-2 text-xs rounded border transition-all text-center ${
                    selectedVersion === "v2"
                      ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/50 font-bold"
                      : "bg-[#181b25] text-[#94a3b8] border-[#1E293B] hover:text-[#dfe2ef]"
                  }`}
                >
                  v2 • Chuẩn STAR (94%)
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedVersion("v1")}
                  className={`flex-1 py-1.5 px-2 text-xs rounded border transition-all text-center ${
                    selectedVersion === "v1"
                      ? "bg-[#10b981]/15 text-[#4edea3] border-[#10b981]/50 font-bold"
                      : "bg-[#181b25] text-[#94a3b8] border-[#1E293B] hover:text-[#dfe2ef]"
                  }`}
                >
                  v1 • Bản gốc (82%)
                </button>
              </div>
            </div>

            {/* Live CV Document Preview */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 space-y-4 text-xs leading-relaxed font-['Inter',sans-serif]">
              <div className="border-b border-[#1E293B] pb-3">
                <h3 className="text-base font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                  VŨ VĂN DŨNG
                </h3>
                <div className="text-[11px] text-[#4edea3] font-['JetBrains_Mono',monospace] font-semibold mt-0.5">
                  Senior Backend Engineer • Python / FastAPI / Cloud Architecture
                </div>
                <div className="text-[10px] text-[#94a3b8] mt-1">
                  TP. Hồ Chí Minh • dungvu@email.com • github.com/dungvu
                </div>
              </div>

              {/* Summary */}
              <div>
                <div className="font-bold text-[#dfe2ef] uppercase tracking-wider text-[11px] mb-1 font-['Plus_Jakarta_Sans',sans-serif]">
                  Tóm Tắt Chuyên Môn
                </div>
                <p className="text-[#94a3b8] text-[11px]">
                  5+ năm kinh nghiệm phát triển hệ thống backend chịu tải cao (High-throughput APIs), kiến trúc microservices và cơ sở dữ liệu phân tán.
                </p>
              </div>

              {/* Experience */}
              <div>
                <div className="font-bold text-[#dfe2ef] uppercase tracking-wider text-[11px] mb-1 font-['Plus_Jakarta_Sans',sans-serif]">
                  Kinh Nghiệm Làm Việc
                </div>
                <div className="space-y-2">
                  <div>
                    <div className="font-semibold text-[#f8fafc]">TechCorp Global • Senior Backend Lead</div>
                    <div className="text-[10px] text-[#64748b]">2022 - Hiện tại</div>
                    <div className="text-[11px] mt-1 text-[#dfe2ef] bg-[#10b981]/10 p-2 rounded border border-[#10b981]/30">
                      <span className="text-[#4edea3] font-bold">✨ Đã tối ưu (STAR): </span>
                      Thiết kế &amp; tối ưu hóa 12 microservices backend bằng <span className="text-[#4edea3] font-semibold">FastAPI</span> và <span className="text-[#4edea3] font-semibold">PostgreSQL</span>, giảm <span className="text-[#4edea3] font-semibold">35% độ trễ API P99</span> và chịu tải ổn định <span className="text-[#4edea3] font-semibold">10,000+ RPS</span> cho cổng thanh toán điện tử.
                    </div>
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div>
                <div className="font-bold text-[#dfe2ef] uppercase tracking-wider text-[11px] mb-1 font-['Plus_Jakarta_Sans',sans-serif]">
                  Kỹ Năng Đã Khớp ATS
                </div>
                <div className="flex flex-wrap gap-1">
                  {["FastAPI", "PostgreSQL", "Docker", "Redis", "Kafka", "Microservices", "CI/CD", "Kubernetes"].map((s, i) => (
                    <span key={i} className="bg-[#181b25] text-[#4edea3] px-1.5 py-0.5 rounded border border-[#10b981]/30 text-[10px] font-['JetBrains_Mono',monospace]">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Export PDF Button */}
            <button
              type="button"
              aria-label="Tải xuống bản CV chuẩn ATS PDF"
              className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold py-3 rounded-xl text-xs transition-all shadow-md flex items-center justify-center gap-2 font-['Plus_Jakarta_Sans',sans-serif]"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Tải Xuống PDF (Chuẩn ATS 2026)</span>
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
