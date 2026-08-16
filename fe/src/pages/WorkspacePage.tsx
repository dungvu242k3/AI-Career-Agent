import React, { useState } from "react";
import { Link } from "react-router-dom";

// Types
interface JobItem {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  matchScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  description: string;
  requirements: string[];
  benefits: string[];
}

export default function WorkspacePage() {
  // State variables
  const [activeRightTab, setActiveRightTab] = useState<"jobs" | "studio">("jobs");
  const [activeVersion, setActiveVersion] = useState<"v2" | "v1">("v2");
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [isReasoningOpen, setIsReasoningOpen] = useState(true);

  // Sample matched jobs data
  const jobsList: JobItem[] = [
    {
      id: "vng-01",
      title: "Senior AI & Backend Systems Engineer",
      company: "VNG Corporation",
      location: "TP. Hồ Chí Minh (Hybrid)",
      salary: "50.000.000đ - 75.000.000đ",
      matchScore: 96,
      matchedSkills: ["Python", "FastAPI", "RAG Pipelines", "PostgreSQL", "Docker"],
      missingSkills: ["Kafka Cluster"],
      description:
        "Chịu trách nhiệm kiến trúc và phát triển nền tảng AI Core phục vụ hàng triệu người dùng. Tối ưu hóa độ trễ truy vấn RAG và xây dựng backend microservices hiệu năng cao.",
      requirements: [
        "Từ 3+ năm kinh nghiệm phát triển hệ thống Backend với Python (FastAPI/AsyncIO) hoặc Go.",
        "Kinh nghiệm thực chiến với Vector Database (Qdrant, Milvus, Pinecone) và RAG Frameworks.",
        "Thành thạo tối ưu hóa câu lệnh PostgreSQL, Caching Redis và kiến trúc Microservices.",
        "Có tư duy làm việc độc lập và kỹ năng giải quyết vấn đề hệ thống quy mô lớn.",
      ],
      benefits: [
        "Mức lương cạnh tranh bậc nhất thị trường + Thưởng hiệu suất hàng năm (14-16 tháng lương).",
        "Bảo hiểm sức khỏe cao cấp VNG Care cho nhân viên và người thân.",
        "Môi trường làm việc Hybrid linh hoạt, cung cấp Macbook Pro M3 Max.",
      ],
    },
    {
      id: "momo-02",
      title: "Lead Backend Architect",
      company: "MoMo (M_Service)",
      location: "Hà Nội / TP. HCM",
      salary: "60.000.000đ - 85.000.000đ",
      matchScore: 92,
      matchedSkills: ["Python", "Go", "PostgreSQL", "Redis", "Microservices"],
      missingSkills: ["Kubernetes Operator"],
      description:
        "Thiết kế kiến trúc hệ thống thanh toán và dịch vụ tài chính chịu tải 30,000+ RPS. Đảm bảo tính khả dụng 99.99% và an toàn bảo mật dữ liệu giao dịch.",
      requirements: [
        "4+ năm kinh nghiệm Backend quy mô lớn, thành thạo Go/Python.",
        "Hiểu sâu về Sharding DB, Distributed Transaction và Idempotency.",
        "Kinh nghiệm làm việc với Redis Cluster, Kafka Event Streaming.",
      ],
      benefits: [
        "Gói ESOP dành cho nhân sự nòng cốt.",
        "Thưởng hiệu suất 3-5 tháng lương mỗi năm.",
        "Lộ trình thăng tiến rõ ràng lên Principal Architect.",
      ],
    },
    {
      id: "techfin-03",
      title: "Machine Learning Systems Lead",
      company: "TechFin Global",
      location: "Remote (Toàn thời gian)",
      salary: "$3,000 - $4,500 / tháng",
      matchScore: 88,
      matchedSkills: ["PyTorch", "Python", "RAG", "Docker", "Qdrant"],
      missingSkills: ["Triton Inference Server"],
      description:
        "Xây dựng hạ tầng triển khai mô hình LLM và RAG quy mô doanh nghiệp cho các tổ chức tài chính tại Singapore và Đông Nam Á.",
      requirements: [
        "Kinh nghiệm tối ưu hóa mô hình LLM, Fine-tuning và Quantization.",
        "Xây dựng API serving với độ trễ thấp (< 200ms).",
      ],
      benefits: [
        "Làm việc 100% Remote, thanh toán theo USD.",
        "Ngân sách $2,000/năm cho học tập và thiết bị.",
      ],
    },
  ];

  // Handler for selecting job to view in drawer
  const handleOpenJobDetail = (job: JobItem) => {
    setSelectedJob(job);
    setIsDrawerOpen(true);
  };

  // Handler for tailoring CV for a specific job
  const handleTailorForJob = (job: JobItem) => {
    setSelectedJob(job);
    setActiveRightTab("studio");
    setActiveVersion("v2");
  };

  // Handler for asking AI about the selected job
  const handleAskAiAboutJob = (job: JobItem) => {
    setIsDrawerOpen(false);
    setChatInput(`Phân tích mức độ tương thích giữa CV của tôi và JD ${job.title} tại ${job.company}`);
  };

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
          <div className="p-4 sm:p-5 space-y-6">
            
            {/* 1.1 Uploaded File Info */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-8 h-8 rounded-lg bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center font-bold text-xs font-['JetBrains_Mono',monospace]">
                    PDF
                  </span>
                  <div>
                    <h2 className="text-xs font-bold text-[#f8fafc] truncate max-w-[150px] font-['Plus_Jakarta_Sans',sans-serif]">
                      Nguyen_Van_A_CV.pdf
                    </h2>
                    <p className="text-[10px] text-[#94a3b8]">1.4 MB • Đã quét 18 kỹ năng</p>
                  </div>
                </div>
                <span className="text-[10px] text-[#4edea3] bg-[#10b981]/10 px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                  Sẵn sàng
                </span>
              </div>

              <div className="mt-3 flex gap-2">
                <button
                  type="button"
                  className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] text-[11px] font-medium py-1.5 rounded-lg transition-colors text-center"
                >
                  Thay CV Khác
                </button>
                <button
                  type="button"
                  className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] text-[11px] font-medium py-1.5 rounded-lg transition-colors text-center"
                >
                  Xem Bản Gốc
                </button>
              </div>
            </div>

            {/* 1.2 ATS Score Breakdown Gauge */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Điểm Đánh Giá ATS
                </span>
                <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace]">
                  82 / 100
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2.5 bg-[#181b25] rounded-full overflow-hidden border border-[#1E293B] mb-4">
                <div className="w-[82%] h-full bg-[#10b981] rounded-full"></div>
              </div>

              {/* 3 Metric Axes */}
              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8]">Kỹ năng công nghệ</span>
                  <span className="text-[#4edea3] font-semibold font-['JetBrains_Mono',monospace]">18/20 (90%)</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8]">Tác động định lượng (Metrics)</span>
                  <span className="text-[#f59e0b] font-semibold font-['JetBrains_Mono',monospace]">12/20 (60% ⚠)</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[#94a3b8]">Cấu trúc chuẩn ATS</span>
                  <span className="text-[#4edea3] font-semibold font-['JetBrains_Mono',monospace]">19/20 (95%)</span>
                </div>
              </div>
            </div>

            {/* 1.3 Parsed Skills List */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                  Kỹ Năng Đã Bóc Tách (18)
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="text-[11px] text-[#94a3b8] mb-1.5 font-medium">Core Backend &amp; API:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {["Python", "FastAPI", "Go", "RESTful API", "AsyncIO"].map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 bg-[#181b25] border border-[#1E293B] text-[#dfe2ef] rounded text-[11px] font-['JetBrains_Mono',monospace]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-[11px] text-[#94a3b8] mb-1.5 font-medium">AI &amp; Data Engineering:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {["RAG Pipelines", "Qdrant DB", "PyTorch", "LangChain"].map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 bg-[#10b981]/10 border border-[#10b981]/30 text-[#4edea3] rounded text-[11px] font-['JetBrains_Mono',monospace]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-[11px] text-[#94a3b8] mb-1.5 font-medium">Database &amp; DevOps:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {["PostgreSQL", "Redis", "Docker", "Kafka"].map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 bg-[#181b25] border border-[#1E293B] text-[#dfe2ef] rounded text-[11px] font-['JetBrains_Mono',monospace]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* 1.4 Experience Timeline */}
            <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 shadow-sm">
              <div className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-3 font-['Plus_Jakarta_Sans',sans-serif]">
                Kinh Nghiệm Làm Việc
              </div>
              <div className="space-y-3 border-l-2 border-[#1E293B] pl-3 ml-1">
                <div>
                  <div className="text-xs font-bold text-[#f8fafc]">Senior AI / Backend Engineer</div>
                  <div className="text-[11px] text-[#4edea3]">VNG Cloud • 2023 - Hiện tại</div>
                </div>
                <div>
                  <div className="text-xs font-bold text-[#f8fafc]">Software Engineer (Python/Go)</div>
                  <div className="text-[11px] text-[#94a3b8]">MoMo Fintech • 2021 - 2023</div>
                </div>
              </div>
            </div>

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
                  Đang phân tích CV và so khớp 5 việc làm
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsReasoningOpen(!isReasoningOpen)}
              className="text-[11px] text-[#94a3b8] hover:text-[#4edea3] border border-[#1E293B] px-2.5 py-1 rounded-lg bg-[#181b25] transition-colors"
            >
              {isReasoningOpen ? "Ẩn suy luận" : "Hiện suy luận AI"}
            </button>
          </div>

          {/* 2.2 Chat Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 scrollbar-thin">
            
            {/* AI Welcome Message */}
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-lg bg-[#10b981] text-[#090D16] flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                AI
              </div>
              <div className="flex-1 bg-[#111827] border border-[#1E293B] rounded-2xl rounded-tl-sm p-4 text-xs text-[#dfe2ef] space-y-3 leading-relaxed shadow-sm">
                <p className="font-medium text-[#f8fafc]">
                  Xin chào Nguyễn Văn A! Tôi đã hoàn tất phân tích hồ sơ CV của bạn:
                </p>
                <div className="space-y-1.5 pl-2 border-l-2 border-[#10b981]">
                  <div><strong className="text-[#4edea3]">Điểm mạnh:</strong> Tech stack chuẩn hiện đại (Python, FastAPI, RAG, Qdrant).</div>
                  <div><strong className="text-[#f59e0b]">Điểm cần cải thiện:</strong> Mục kinh nghiệm dự án còn thiếu số liệu định lượng (Metrics &amp; Scale).</div>
                  <div><strong className="text-[#06b6d4]">Cơ hội việc làm:</strong> Có <span className="font-bold text-[#4edea3]">3 vị trí phù hợp trên 90%</span> ở cột bên phải!</div>
                </div>
                <p className="text-[#94a3b8] text-[11px]">
                  💡 Hãy chọn 1 Job ở Cột 3 hoặc bấm vào các câu lệnh gợi ý bên dưới để tôi bắt đầu tối ưu CV theo chuẩn STAR!
                </p>
              </div>
            </div>

            {/* AI Reasoning Box (Accordion) */}
            {isReasoningOpen && (
              <div className="ml-10 bg-[#181b25] border border-[#1E293B] rounded-xl p-3.5 text-xs text-[#94a3b8] space-y-2">
                <div className="flex items-center gap-2 text-[#4edea3] font-semibold font-['JetBrains_Mono',monospace] text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                  QUÁ TRÌNH SUY LUẬN CỦA AI (DEEP REASONING)
                </div>
                <p className="text-[11px] leading-relaxed">
                  1. Quét đối chiếu 18 kỹ năng với JD VNG Corp (Senior AI &amp; Backend Systems).<br />
                  2. Khớp 5/6 yêu cầu cốt lõi (Tỷ lệ tương thích đạt 96%).<br />
                  3. Phát hiện câu mô tả dự án RAG cũ chưa nêu rõ độ trễ (Latency) và lưu lượng truy vấn (QPS). Đã tiến hành tái cấu trúc theo mô hình STAR.
                </p>
              </div>
            )}

            {/* STAR Diff Comparison Box */}
            <div className="ml-10 bg-[#111827] border border-[#1E293B] rounded-xl p-4 space-y-3 shadow-md">
              <div className="flex items-center justify-between pb-2 border-b border-[#1E293B]">
                <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace] uppercase">
                  ⚡ Đề xuất tối ưu hóa STAR (Kinh nghiệm VNG Cloud)
                </span>
                <span className="text-[10px] bg-[#10b981]/10 text-[#4edea3] px-2 py-0.5 rounded font-semibold">
                  Tăng +13% ATS
                </span>
              </div>

              {/* Before */}
              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-[#f87171] flex items-center gap-1.5">
                  <span>❌</span> Bản gốc trước đây:
                </div>
                <p className="text-xs text-[#94a3b8] bg-[#181b25] p-2.5 rounded border border-[#1E293B] line-through">
                  "Xây dựng hệ thống RAG tìm kiếm tài liệu cho doanh nghiệp bằng Python và Qdrant."
                </p>
              </div>

              {/* After */}
              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-[#4edea3] flex items-center gap-1.5">
                  <span>✅</span> Bản đề xuất chuẩn STAR:
                </div>
                <p className="text-xs text-[#f8fafc] bg-[#10b981]/10 p-2.5 rounded border border-[#10b981]/30 leading-relaxed font-medium">
                  "Kiến trúc hệ thống RAG đa luồng với Python và Qdrant, <span className="text-[#4edea3] font-bold">giảm thời gian phản hồi từ 1.8s xuống 320ms (-82%)</span>, phục vụ <span className="text-[#4edea3] font-bold">50,000+ truy vấn/ngày</span> với độ chính xác 94.6%."
                </p>
              </div>

              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => {
                    setActiveRightTab("studio");
                    setActiveVersion("v2");
                  }}
                  className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold px-3 py-1.5 rounded-lg text-xs transition-colors shadow-sm"
                >
                  Áp Dụng Vào CV Đã Tối Ưu
                </button>
                <button
                  type="button"
                  onClick={() => setChatInput("Hãy đề xuất cho tôi một phương án viết khác nhấn mạnh vào tối ưu hóa chi phí")}
                  className="bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] font-medium px-3 py-1.5 rounded-lg text-xs transition-colors"
                >
                  Tạo Phương Án Khác
                </button>
              </div>
            </div>

          </div>

          {/* 2.3 Quick Action Chips & Input Dock */}
          <div className="p-4 border-t border-[#1E293B] bg-[#0c101b] space-y-3">
            {/* Quick Action Chips */}
            <div className="flex gap-2 overflow-x-auto scrollbar-none pb-1">
              <button
                type="button"
                onClick={() => setChatInput("Phân tích điểm yếu lớn nhất trong CV của tôi và cách khắc phục")}
                className="whitespace-nowrap bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] hover:border-[#10b981]/50 text-[#dfe2ef] text-[11px] px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
              >
                <span>⚡</span> Phân tích điểm yếu lớn nhất
              </button>
              <button
                type="button"
                onClick={() => setChatInput("So sánh CV của tôi với JD VNG Corporation 96% Match")}
                className="whitespace-nowrap bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] hover:border-[#10b981]/50 text-[#dfe2ef] text-[11px] px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
              >
                <span>⚡</span> So sánh với JD VNG Corp
              </button>
              <button
                type="button"
                onClick={() => setChatInput("Viết lại toàn bộ phần kinh nghiệm làm việc theo chuẩn STAR có số liệu")}
                className="whitespace-nowrap bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] hover:border-[#10b981]/50 text-[#dfe2ef] text-[11px] px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
              >
                <span>⚡</span> Viết lại theo chuẩn STAR
              </button>
            </div>

            {/* Prompt Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (chatInput.trim()) {
                  setChatInput("");
                }
              }}
              className="relative flex items-center"
            >
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Nhập câu hỏi hoặc yêu cầu AI tối ưu hóa CV... (Enter để gửi)"
                className="w-full bg-[#111827] border border-[#1E293B] focus:border-[#10b981] rounded-xl pl-4 pr-24 py-3 text-xs text-[#f8fafc] placeholder-[#64748b] outline-none transition-colors shadow-inner"
              />
              <button
                type="submit"
                aria-label="Gửi tin nhắn cho AI"
                className="absolute right-2 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold px-4 py-1.5 rounded-lg text-xs transition-colors shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
              >
                Gửi
              </button>
            </form>
          </div>

        </main>

        {/* ════════════════════════════════════════════════════════════
            CỘT 3 (4/12 Col ~ 33%): JOB MATCH FEED & TAILOR STUDIO
        ════════════════════════════════════════════════════════════ */}
        <section className="lg:col-span-4 flex flex-col h-full bg-[#0c101b]">
          
          {/* 3.1 Right Header Tabs */}
          <div className="h-14 px-4 border-b border-[#1E293B] flex items-center justify-between shrink-0 bg-[#0c101b]">
            <div className="flex gap-1 bg-[#181b25] p-1 rounded-lg border border-[#1E293B]">
              <button
                type="button"
                onClick={() => setActiveRightTab("jobs")}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  activeRightTab === "jobs"
                    ? "bg-[#10b981] text-[#090D16] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#f8fafc]"
                }`}
              >
                🎯 Việc Làm So Khớp (3)
              </button>
              <button
                type="button"
                onClick={() => setActiveRightTab("studio")}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  activeRightTab === "studio"
                    ? "bg-[#10b981] text-[#090D16] shadow-sm"
                    : "text-[#94a3b8] hover:text-[#f8fafc]"
                }`}
              >
                📑 CV Đã Tối Ưu
              </button>
            </div>

            {activeRightTab === "studio" && (
              <div className="flex items-center gap-1.5 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveVersion("v2")}
                  className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                    activeVersion === "v2"
                      ? "bg-[#10b981]/20 text-[#4edea3] border border-[#10b981]/40"
                      : "text-[#94a3b8] hover:text-[#f8fafc]"
                  }`}
                >
                  v2 (95%)
                </button>
                <button
                  type="button"
                  onClick={() => setActiveVersion("v1")}
                  className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                    activeVersion === "v1"
                      ? "bg-[#10b981]/20 text-[#4edea3] border border-[#10b981]/40"
                      : "text-[#94a3b8] hover:text-[#f8fafc]"
                  }`}
                >
                  v1 (82%)
                </button>
              </div>
            )}
          </div>

          {/* 3.2 Tab Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
            
            {/* ───── TAB 1: JOB MATCH LIST ───── */}
            {activeRightTab === "jobs" && (
              <div className="space-y-4">
                <div className="text-[11px] text-[#94a3b8] flex justify-between items-center">
                  <span>Sắp xếp theo độ tương thích cao nhất</span>
                  <span className="text-[#4edea3] font-['JetBrains_Mono',monospace]">3 Vị trí</span>
                </div>

                {jobsList.map((job) => (
                  <div
                    key={job.id}
                    className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-4 rounded-xl transition-all shadow-sm space-y-3"
                  >
                    {/* Job Title & Company */}
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <h2 className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                          {job.title}
                        </h2>
                        <p className="text-[11px] text-[#94a3b8] mt-0.5">
                          {job.company} • {job.location}
                        </p>
                      </div>
                      <span className="text-xs font-bold text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-2 py-0.5 rounded-full shrink-0 font-['JetBrains_Mono',monospace]">
                        {job.matchScore}% Match
                      </span>
                    </div>

                    <div className="text-xs font-semibold text-[#10b981] font-['JetBrains_Mono',monospace]">
                      {job.salary}
                    </div>

                    {/* Skill Match Breakdown */}
                    <div className="space-y-1.5 pt-1 border-t border-[#1E293B]/60 text-[11px]">
                      <div className="flex flex-wrap gap-1 items-center">
                        <span className="text-[#94a3b8] text-[10px]">Khớp:</span>
                        {job.matchedSkills.slice(0, 4).map((skill) => (
                          <span
                            key={skill}
                            className="bg-[#10b981]/10 text-[#4edea3] px-1.5 py-0.5 rounded text-[10px] font-['JetBrains_Mono',monospace]"
                          >
                            {skill} ✓
                          </span>
                        ))}
                      </div>
                      {job.missingSkills.length > 0 && (
                        <div className="flex flex-wrap gap-1 items-center">
                          <span className="text-[#94a3b8] text-[10px]">Thiếu:</span>
                          {job.missingSkills.map((skill) => (
                            <span
                              key={skill}
                              className="bg-[#f59e0b]/10 text-[#f59e0b] px-1.5 py-0.5 rounded text-[10px] font-['JetBrains_Mono',monospace]"
                            >
                              {skill} ⚠
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-2 pt-2">
                      <button
                        type="button"
                        onClick={() => handleOpenJobDetail(job)}
                        className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] text-xs font-medium py-1.5 rounded-lg transition-colors text-center"
                      >
                        Xem Chi Tiết JD
                      </button>
                      <button
                        type="button"
                        onClick={() => handleTailorForJob(job)}
                        className="flex-1 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold py-1.5 rounded-lg transition-colors text-center font-['Plus_Jakarta_Sans',sans-serif]"
                      >
                        Tailor CV Này
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* ───── TAB 2: TAILORED CV STUDIO ───── */}
            {activeRightTab === "studio" && (
              <div className="space-y-4">
                <div className="bg-[#111827] border border-[#1E293B] rounded-xl p-4 space-y-4 shadow-md">
                  <div className="flex justify-between items-center pb-3 border-b border-[#1E293B]">
                    <div>
                      <div className="text-xs font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                        Bản CV Chuẩn ATS 2026
                      </div>
                      <div className="text-[10px] text-[#4edea3]">
                        {activeVersion === "v2"
                          ? "⚡ Đã tối ưu theo JD VNG Corp (ATS 95%)"
                          : "📄 Bản gốc chưa tối ưu (ATS 82%)"}
                      </div>
                    </div>
                    <span className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace] bg-[#10b981]/10 px-2 py-1 rounded">
                      {activeVersion === "v2" ? "95 / 100" : "82 / 100"}
                    </span>
                  </div>

                  {/* CV Content Preview */}
                  <div className="space-y-3 text-xs leading-relaxed">
                    <div>
                      <h3 className="font-bold text-[#f8fafc] uppercase tracking-wider text-[11px] mb-1">
                        1. Tóm Tắt Chuyên Môn (Summary)
                      </h3>
                      {activeVersion === "v2" ? (
                        <p className="text-[#dfe2ef] bg-[#10b981]/10 p-3 rounded border border-[#10b981]/30">
                          Senior AI &amp; Backend Systems Engineer với hơn 4.5 năm kinh nghiệm chuyên sâu về kiến trúc Microservices (Python/FastAPI/Go) và hạ tầng RAG Pipelines. Đã triển khai thành công hệ thống phục vụ 50,000+ QPS, tối ưu hóa độ trễ truy vấn giảm 82%.
                        </p>
                      ) : (
                        <p className="text-[#94a3b8] bg-[#181b25] p-3 rounded border border-[#1E293B]">
                          Kỹ sư phần mềm có hơn 4 năm kinh nghiệm làm Backend với Python, Go và AI. Muốn tìm kiếm cơ hội làm việc trong môi trường thử thách.
                        </p>
                      )}
                    </div>

                    <div>
                      <h3 className="font-bold text-[#f8fafc] uppercase tracking-wider text-[11px] mb-1">
                        2. Kinh Nghiệm Trọng Tâm (STAR Highlights)
                      </h3>
                      {activeVersion === "v2" ? (
                        <ul className="space-y-2 text-[#dfe2ef]">
                          <li className="bg-[#10b981]/10 p-2.5 rounded border border-[#10b981]/30">
                            • Kiến trúc hệ thống RAG đa luồng với Python và Qdrant, giảm thời gian phản hồi từ 1.8s xuống 320ms (-82%), phục vụ 50,000+ truy vấn/ngày.
                          </li>
                          <li className="bg-[#10b981]/10 p-2.5 rounded border border-[#10b981]/30">
                            • Tối ưu hóa câu lệnh PostgreSQL và Redis Caching, giảm tải CPU Database 45% trong các đợt cao điểm khuyến mãi.
                          </li>
                        </ul>
                      ) : (
                        <ul className="space-y-2 text-[#94a3b8]">
                          <li className="bg-[#181b25] p-2.5 rounded border border-[#1E293B]">
                            • Xây dựng hệ thống RAG tìm kiếm tài liệu cho doanh nghiệp bằng Python và Qdrant.
                          </li>
                          <li className="bg-[#181b25] p-2.5 rounded border border-[#1E293B]">
                            • Viết API và tối ưu database cho hệ thống backend.
                          </li>
                        </ul>
                      )}
                    </div>
                  </div>

                  <button
                    type="button"
                    className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold py-2.5 rounded-lg text-xs transition-colors shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
                  >
                    Tải Xuống Bản PDF Chuẩn ATS
                  </button>
                </div>
              </div>
            )}

          </div>
        </section>

      </div>

      {/* ────────────────────────────────────────────────────────────
          JOB DETAIL DRAWER (SLIDE-OVER PANEL)
      ──────────────────────────────────────────────────────────── */}
      {isDrawerOpen && selectedJob && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
          <div className="w-full max-w-lg bg-[#0c101b] border-l border-[#1E293B] h-full flex flex-col shadow-2xl p-6 overflow-y-auto scrollbar-thin">
            
            {/* Drawer Header */}
            <div className="flex justify-between items-start pb-4 border-b border-[#1E293B]">
              <div>
                <span className="text-xs font-bold text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-2 py-0.5 rounded-full font-['JetBrains_Mono',monospace]">
                  {selectedJob.matchScore}% Match Với CV Của Bạn
                </span>
                <h2 className="text-lg font-bold text-[#f8fafc] mt-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  {selectedJob.title}
                </h2>
                <p className="text-xs text-[#94a3b8] mt-0.5">
                  {selectedJob.company} • {selectedJob.location}
                </p>
                <div className="text-sm font-bold text-[#10b981] font-['JetBrains_Mono',monospace] mt-1">
                  {selectedJob.salary}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsDrawerOpen(false)}
                className="w-8 h-8 rounded-lg bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#94a3b8] hover:text-[#f8fafc] flex items-center justify-center text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {/* Drawer Body */}
            <div className="py-5 space-y-5 text-xs text-[#dfe2ef] leading-relaxed">
              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Mô Tả Công Việc
                </h3>
                <p className="text-[#94a3b8]">{selectedJob.description}</p>
              </div>

              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Yêu Cầu Kỹ Thuật
                </h3>
                <ul className="space-y-1.5 text-[#94a3b8] list-disc pl-4">
                  {selectedJob.requirements.map((req, i) => (
                    <li key={i}>{req}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-bold text-[#f8fafc] uppercase tracking-wider mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                  Quyền Lợi &amp; Đãi Ngộ
                </h3>
                <ul className="space-y-1.5 text-[#94a3b8] list-disc pl-4">
                  {selectedJob.benefits.map((ben, i) => (
                    <li key={i}>{ben}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Drawer Footer Actions */}
            <div className="pt-4 border-t border-[#1E293B] flex gap-3 mt-auto">
              <button
                type="button"
                onClick={() => handleAskAiAboutJob(selectedJob)}
                className="flex-1 bg-[#181b25] hover:bg-[#1f293d] border border-[#1E293B] text-[#dfe2ef] font-semibold py-2.5 rounded-lg text-xs transition-colors"
              >
                💬 Hỏi AI Về Job Này
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsDrawerOpen(false);
                  handleTailorForJob(selectedJob);
                }}
                className="flex-1 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold py-2.5 rounded-lg text-xs transition-colors shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
              >
                ⚡ Tối Ưu CV Ngay
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
