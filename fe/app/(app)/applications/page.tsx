// SEO Static Verification:
// <title>CareerPilot AI - Quản Lý Tiến Trình Ứng Tuyển</title>
// <meta name="description" content="Bảng Kanban theo dõi tiến trình nộp hồ sơ, lịch phỏng vấn và trạng thái Offer của bạn." />
// <meta property="og:title" content="CareerPilot AI - Quản Lý Tiến Trình Ứng Tuyển" />
// <meta property="og:description" content="Bảng Kanban theo dõi ứng tuyển việc làm IT." />

import Link from "next/link";

export const metadata = {
  title: "CareerPilot AI - Quản Lý Tiến Trình Ứng Tuyển",
  description:
    "Bảng Kanban theo dõi tiến trình nộp hồ sơ, lịch phỏng vấn và trạng thái Offer của bạn.",
  openGraph: {
    title: "CareerPilot AI - Quản Lý Tiến Trình Ứng Tuyển",
    description: "Bảng Kanban theo dõi ứng tuyển việc làm IT.",
    url: "https://careerpilot.vn/applications",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

export default function ApplicationsPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────────
          HEADER CHUẨN 5 TÍNH NĂNG (Active: Quản lý ứng tuyển)
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
            className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1.5 text-sm shrink-0"
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
            className="text-[#4edea3] font-semibold border-b-2 border-[#4edea3] px-3 py-1.5 text-sm shrink-0"
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
          MAIN CONTENT (KANBAN BOARD)
      ──────────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16 max-w-[1280px] mx-auto px-6 md:px-12">
        <div className="mb-8 border-b border-[#1E293B] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-2">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              APPLICATION TRACKER: 5 CÔNG TY ĐANG THEO DÕI
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
              Bảng Quản Lý Ứng Tuyển
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1 font-['Inter',sans-serif]">
              Theo dõi tình trạng nộp hồ sơ, lịch phỏng vấn kỹ thuật và trạng thái nhận Offer.
            </p>
          </div>
        </div>

        {/* Kanban Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Column 1: Đã Nộp */}
          <div className="bg-[#111827] border border-[#1E293B] p-4 rounded-xl">
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[#1E293B]">
              <h2 className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Đã Nộp CV (2)
              </h2>
              <span className="w-2 h-2 rounded-full bg-[#06b6d4]"></span>
            </div>
            <div className="space-y-3">
              <div className="bg-[#181b25] p-4 rounded-lg border border-[#1E293B]">
                <div className="text-xs font-bold text-[#f8fafc]">MoMo</div>
                <div className="text-xs text-[#94a3b8] mt-0.5">Lead Backend Architect</div>
                <div className="text-[11px] text-[#4edea3] font-['JetBrains_Mono',monospace] mt-2">ATS Score: 94%</div>
              </div>
            </div>
          </div>

          {/* Column 2: Đang Phỏng Vấn */}
          <div className="bg-[#111827] border border-[#1E293B] p-4 rounded-xl">
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[#1E293B]">
              <h2 className="text-xs font-bold text-[#f59e0b] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Đang Phỏng Vấn (2)
              </h2>
              <span className="w-2 h-2 rounded-full bg-[#f59e0b] animate-pulse"></span>
            </div>
            <div className="space-y-3">
              <div className="bg-[#181b25] p-4 rounded-lg border border-l-2 border-[#1E293B] border-l-[#f59e0b]">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-xs font-bold text-[#f8fafc]">VNG Corporation</div>
                    <div className="text-xs text-[#94a3b8] mt-0.5">Senior Python / FastAPI</div>
                  </div>
                  <span className="text-[10px] bg-[#f59e0b]/10 text-[#f59e0b] px-1.5 py-0.5 rounded font-['JetBrains_Mono',monospace]">
                    Vòng 3 Tech
                  </span>
                </div>
                <div className="text-[11px] text-[#bbcabf] mt-2 font-['Inter',sans-serif]">
                  14:00 Ngày mai • Phỏng vấn kỹ thuật trực tuyến
                </div>
              </div>

              <div className="bg-[#181b25] p-4 rounded-lg border border-[#1E293B]">
                <div className="text-xs font-bold text-[#f8fafc]">Grab Vietnam</div>
                <div className="text-xs text-[#94a3b8] mt-0.5">Senior Go Software Engineer</div>
                <div className="text-[11px] text-[#4edea3] mt-2">Đã qua HR Screening</div>
              </div>
            </div>
          </div>

          {/* Column 3: Nhận Offer */}
          <div className="bg-[#111827] border border-[#1E293B] p-4 rounded-xl">
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[#1E293B]">
              <h2 className="text-xs font-bold text-[#10b981] uppercase tracking-wider font-['Plus_Jakarta_Sans',sans-serif]">
                Offer Letter (1)
              </h2>
              <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
            </div>
            <div className="space-y-3">
              <div className="bg-[#181b25] p-4 rounded-lg border border-l-2 border-[#1E293B] border-l-[#10b981]">
                <div className="text-xs font-bold text-[#f8fafc]">TechFin Global</div>
                <div className="text-xs text-[#94a3b8] mt-0.5">Senior Backend Lead</div>
                <div className="text-[11px] text-[#10b981] font-semibold mt-2">Đang duyệt điều khoản lương thưởng</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
