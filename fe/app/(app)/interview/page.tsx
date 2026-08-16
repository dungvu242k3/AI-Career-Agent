// SEO Static Verification:
// <title>CareerPilot AI - Luyện Phỏng Vấn AI Giả Lập</title>
// <meta name="description" content="Phòng luyện phỏng vấn kỹ thuật IT giả lập với AI Mock Interview Coach theo phương pháp STAR." />
// <meta property="og:title" content="CareerPilot AI - Luyện Phỏng Vấn AI Giả Lập" />
// <meta property="og:description" content="Luyện phỏng vấn IT với AI Voice & Chat." />

import Link from "next/link";

export const metadata = {
  title: "CareerPilot AI - Luyện Phỏng Vấn AI Giả Lập",
  description:
    "Phòng luyện phỏng vấn kỹ thuật IT giả lập với AI Mock Interview Coach theo phương pháp STAR.",
  openGraph: {
    title: "CareerPilot AI - Luyện Phỏng Vấn AI Giả Lập",
    description: "Luyện phỏng vấn IT với AI Voice & Chat.",
    url: "https://careerpilot.vn/interview",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

export default function InterviewPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────────
          HEADER CHUẨN 5 TÍNH NĂNG (Active: Phỏng vấn AI)
      ──────────────────────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 w-full z-40 flex justify-between items-center px-6 md:px-12 h-16 bg-[#0f131c]/90 backdrop-blur-md border-b border-[#1E293B]">
        <div className="flex items-center shrink-0">
          <Link
            href="/"
            aria-label="CareerPilot AI Trang chủ"
            className="text-xl font-bold text-[#4edea3] tracking-tighter shrink-0 hover:opacity-90 transition-opacity font-['Plus_Jakarta_Sans',sans-serif]"
          >
            CareerPilot AI
          </Link>
        </div>

        <nav
          aria-label="Điều hướng chính"
          className="hidden lg:flex items-center justify-center gap-1 xl:gap-2 whitespace-nowrap overflow-x-auto scrollbar-none absolute left-1/2 -translate-x-1/2"
        >
          <Link
            href="/workspace"
            aria-label="Tính năng Phân tích CV"
            className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1.5 text-sm shrink-0"
          >
            Phân tích CV
          </Link>
          <Link
            href="/jobs"
            aria-label="Tính năng Tìm việc và So khớp"
            className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1.5 text-sm shrink-0"
          >
            Tìm việc &amp; So khớp
          </Link>
          <Link
            href="/interview"
            aria-label="Tính năng Phỏng vấn AI"
            className="text-[#4edea3] font-semibold border-b-2 border-[#4edea3] px-3 py-1.5 text-sm shrink-0"
          >
            Phỏng vấn AI
          </Link>
          <Link
            href="/learning"
            aria-label="Tính năng Lộ trình kỹ năng"
            className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1.5 text-sm shrink-0"
          >
            Lộ trình kỹ năng
          </Link>
          <Link
            href="/applications"
            aria-label="Tính năng Quản lý ứng tuyển"
            className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1.5 text-sm shrink-0"
          >
            Quản lý ứng tuyển
          </Link>
        </nav>

        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/workspace"
            aria-label="Tối ưu CV trong Workspace"
            className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold px-4 py-2 rounded text-xs transition-colors shadow-sm"
          >
            Không gian Workspace
          </Link>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────────
          MAIN CONTENT (AI INTERVIEW ARENA)
      ──────────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16 max-w-[1200px] mx-auto px-6 md:px-12">
        <div className="mb-8 border-b border-[#1E293B] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-2">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              AI MOCK COACH: PHƯƠNG PHÁP STAR
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
              Phòng Luyện Phỏng Vấn Giả Lập AI
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1 font-['Inter',sans-serif]">
              Luyện tập các câu hỏi System Design, Coding và Tình huống hành vi (Behavioral) với phản hồi chấm điểm tức thì.
            </p>
          </div>
        </div>

        {/* 3 Categories Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold text-[#4edea3] font-['JetBrains_Mono',monospace] uppercase mb-2">
                Chủ Đề 01
              </div>
              <h2 className="text-lg font-bold text-[#f8fafc] mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                System Design &amp; Architecture
              </h2>
              <p className="text-xs text-[#94a3b8] leading-relaxed mb-4">
                Thiết kế kiến trúc chịu tải cao, Microservices, Sharding DB, Caching Redis, và Message Queue Kafka.
              </p>
            </div>
            <button
              type="button"
              aria-label="Bắt đầu luyện System Design"
              className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold py-2.5 rounded-lg text-xs transition-colors shadow-sm"
            >
              Bắt đầu phiên phỏng vấn
            </button>
          </div>

          <div className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold text-[#06b6d4] font-['JetBrains_Mono',monospace] uppercase mb-2">
                Chủ Đề 02
              </div>
              <h2 className="text-lg font-bold text-[#f8fafc] mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                Technical Deep-Dive (Python &amp; SQL)
              </h2>
              <p className="text-xs text-[#94a3b8] leading-relaxed mb-4">
                Các câu hỏi đào sâu về Asynchronous I/O, Concurrency, Indexing PostgreSQL và Query Optimization.
              </p>
            </div>
            <button
              type="button"
              aria-label="Bắt đầu luyện Technical Deep-Dive"
              className="w-full bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981]/50 font-semibold py-2.5 rounded-lg text-xs transition-colors"
            >
              Bắt đầu phiên phỏng vấn
            </button>
          </div>

          <div className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold text-[#f59e0b] font-['JetBrains_Mono',monospace] uppercase mb-2">
                Chủ Đề 03
              </div>
              <h2 className="text-lg font-bold text-[#f8fafc] mb-2 font-['Plus_Jakarta_Sans',sans-serif]">
                Behavioral &amp; STAR Questions
              </h2>
              <p className="text-xs text-[#94a3b8] leading-relaxed mb-4">
                Xử lý xung đột kỹ thuật, quản lý thời hạn gấp (Deadlines), và dẫn dắt đội ngũ kỹ sư.
              </p>
            </div>
            <button
              type="button"
              aria-label="Bắt đầu luyện Behavioral STAR"
              className="w-full bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981]/50 font-semibold py-2.5 rounded-lg text-xs transition-colors"
            >
              Bắt đầu phiên phỏng vấn
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
