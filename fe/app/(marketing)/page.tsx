import React from "react";
import Link from "next/link";

export const metadata = {
  // SEO Static Verification:
  // <title>CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện</title>
  // <meta name="description" content="Hệ thống AI chuyên sâu thiết kế cho thị trường IT." />
  // <meta property="og:title" content="CareerPilot AI" />
  // <meta property="og:description" content="Tối ưu hóa ATS, phỏng vấn giả lập AI." />
  title: "CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện",
  description:
    "Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến với độ chính xác kỹ thuật cao.",
  openGraph: {
    title: "CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện",
    description: "Tối ưu hóa ATS, phỏng vấn giả lập AI và lộ trình kỹ năng IT.",
    url: "https://careerpilot.vn",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────
          FIXED HEADER (1 HÀNG DUY NHẤT - 5 MỤC TÍNH NĂNG)
      ──────────────────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-12 h-16 bg-[#0f131c]/80 backdrop-blur-md border-b border-[#3c4a42]/40">
        <div className="flex items-center gap-8 min-w-0">
          <Link
            href="/"
            aria-label="CareerPilot AI Trang chủ"
            className="text-xl font-bold text-[#4edea3] tracking-tighter shrink-0 hover:opacity-90 transition-opacity font-['Plus_Jakarta_Sans',sans-serif]"
          >
            CareerPilot AI
          </Link>

          {/* Menu 1 dòng duy nhất - Không wrap, đúng 5 tính năng cốt lõi */}
          <nav
            aria-label="Điều hướng chính"
            className="hidden lg:flex items-center gap-1 xl:gap-2 whitespace-nowrap overflow-x-auto scrollbar-none"
          >
            <Link
              href="/workspace"
              aria-label="Tính năng Phân tích CV"
              className="text-[#4edea3] font-semibold border-b-2 border-[#4edea3] px-3 py-1 text-sm shrink-0"
            >
              Phân tích CV
            </Link>
            <Link
              href="/jobs"
              aria-label="Tính năng Tìm việc và So khớp"
              className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1 text-sm shrink-0"
            >
              Tìm việc &amp; So khớp
            </Link>
            <Link
              href="/workspace"
              aria-label="Tính năng Phỏng vấn AI"
              className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1 text-sm shrink-0"
            >
              Phỏng vấn AI
            </Link>
            <Link
              href="/learning"
              aria-label="Tính năng Lộ trình kỹ năng"
              className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1 text-sm shrink-0"
            >
              Lộ trình kỹ năng
            </Link>
            <Link
              href="/applications"
              aria-label="Tính năng Quản lý ứng tuyển"
              className="text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50 transition-all duration-150 rounded px-3 py-1 text-sm shrink-0"
            >
              Quản lý ứng tuyển
            </Link>
          </nav>
        </div>

        {/* CTA Actions */}
        <div className="flex items-center gap-3 md:gap-4 shrink-0">
          <Link
            href="/login"
            aria-label="Đăng nhập tài khoản"
            className="text-[#bbcabf] hover:text-[#4edea3] font-medium text-sm transition-colors px-2 py-1"
          >
            Đăng nhập
          </Link>
          <button
            type="button"
            aria-label="Bắt đầu sử dụng miễn phí"
            className="bg-[#10b981] text-[#0f131c] font-semibold px-4 py-2 rounded text-sm hover:bg-[#4edea3] transition-colors shadow-sm"
          >
            Bắt đầu miễn phí
          </button>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────
          MAIN CONTENT
      ──────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16">
        {/* HERO SECTION */}
        <section className="max-w-[1200px] mx-auto px-6 md:px-12 flex flex-col lg:flex-row items-center gap-12 py-12 md:py-20">
          {/* Left Column: Value Proposition */}
          <div className="flex-1 space-y-6">
            <div className="inline-flex items-center gap-2 border border-[#3c4a42] rounded-full px-3 py-1 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-[#4edea3] animate-pulse"></span>
              TRỢ LÝ NGHỀ NGHIỆP AI TOÀN DIỆN
            </div>

            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-3xl sm:text-4xl lg:text-5xl font-bold text-[#dfe2ef] leading-[1.15] tracking-tight">
              Từ CV chưa tối ưu đến Offer Letter — AI đồng hành cùng bạn.
            </h1>

            <p className="text-[#bbcabf] text-base sm:text-lg leading-relaxed max-w-xl">
              Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến với độ chính xác kỹ thuật cao.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <button
                type="button"
                aria-label="Phân tích CV miễn phí ngay"
                className="bg-[#10b981] text-[#0f131c] font-semibold px-6 py-3 rounded border border-[#10b981] hover:bg-[#4edea3] transition-colors flex items-center gap-2 shadow-sm text-sm sm:text-base"
              >
                Phân tích CV miễn phí
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                  />
                </svg>
              </button>

              <button
                type="button"
                aria-label="Khám phá không gian làm việc Workspace"
                className="bg-transparent text-[#dfe2ef] font-medium px-6 py-3 rounded border border-[#3c4a42] hover:bg-[#31353f]/50 hover:border-[#4edea3]/50 transition-colors flex items-center gap-2 text-sm sm:text-base"
              >
                Trải nghiệm Workspace
              </button>
            </div>
          </div>

          {/* Right Column: Live ATS Diagnostics Instrument Card */}
          <div className="flex-1 w-full max-w-md">
            <div className="bg-[#111827] border border-[#1E293B] rounded-lg p-6 relative shadow-2xl">
              <div className="absolute top-0 right-0 p-4 font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs opacity-60">
                SCAN_ID: 0x8F9A2
              </div>

              <h2 className="font-['JetBrains_Mono',monospace] text-xs font-bold uppercase tracking-wider text-[#bbcabf] mb-4 border-b border-[#1E293B] pb-2">
                LIVE ATS DIAGNOSTICS
              </h2>

              {/* Score Meter */}
              <div className="flex justify-between items-end mb-6">
                <div>
                  <div className="text-sm text-[#bbcabf] mb-1">
                    ATS Match Score
                  </div>
                  <div className="font-['JetBrains_Mono',monospace] text-4xl text-[#4edea3] font-bold">
                    94%
                  </div>
                </div>

                <div className="w-16 h-16 rounded-full border-4 border-[#31353f] flex items-center justify-center relative">
                  <svg
                    className="absolute inset-0 w-full h-full -rotate-90"
                    viewBox="0 0 36 36"
                  >
                    <path
                      className="text-[#31353f]"
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
                  <svg
                    className="w-6 h-6 text-[#4edea3]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2.5"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              </div>

              {/* Skills Breakdown Bars */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef]">
                    FastAPI
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[95%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs">
                      95%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef]">
                    PostgreSQL
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[90%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs">
                      90%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef]">
                    Docker
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[88%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs">
                      88%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm opacity-75">
                  <span className="font-['JetBrains_Mono',monospace] text-[#dfe2ef]">
                    Kubernetes
                  </span>
                  <span className="text-[#ffb95f] text-xs border border-[#ffb95f]/30 px-1.5 py-0.5 rounded bg-[#ffb95f]/10 font-['JetBrains_Mono',monospace]">
                    Thiếu kinh nghiệm
                  </span>
                </div>
              </div>

              {/* Action Button inside Card */}
              <button
                type="button"
                aria-label="Tối ưu hóa nội dung CV ngay"
                className="w-full bg-[#181b25] text-[#dfe2ef] border border-[#3c4a42] py-2.5 rounded text-sm hover:border-[#4edea3] hover:text-[#4edea3] transition-colors flex justify-center items-center gap-2 font-medium"
              >
                Tối ưu hóa nội dung CV ngay
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                  />
                </svg>
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* ────────────────────────────────────────────────────────
          FOOTER
      ──────────────────────────────────────────────────────── */}
      <footer className="w-full py-12 px-6 md:px-12 border-t border-[#3c4a42]/40 bg-[#0a0e17]">
        <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
          <div>
            <div className="font-['Plus_Jakarta_Sans',sans-serif] text-xl font-bold text-[#4edea3] mb-2">
              CareerPilot AI
            </div>
            <div className="text-[#bbcabf] text-sm">
              © 2026 CareerPilot AI. Kỹ thuật chính xác từ Việt Nam.
            </div>
          </div>

          <div className="flex flex-wrap gap-4 md:gap-6 font-['JetBrains_Mono',monospace] text-xs uppercase tracking-wider text-[#bbcabf]">
            <span>Phân tích CV</span>
            <span>•</span>
            <span>Tìm việc &amp; So khớp</span>
            <span>•</span>
            <span>Phỏng vấn AI</span>
            <span>•</span>
            <span>Lộ trình kỹ năng</span>
            <span>•</span>
            <span>Quản lý ứng tuyển</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
