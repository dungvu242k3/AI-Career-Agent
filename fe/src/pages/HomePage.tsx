import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, ArrowRight } from "lucide-react";
import { UploadModal } from "../components/UploadModal";
import { UploadResponse } from "../types/candidate";

export default function HomePage() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const navigate = useNavigate();

  const handleUploadSuccess = (_data: UploadResponse) => {
    navigate("/workspace");
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────
          MAIN CONTENT
      ──────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16">
        {/* HERO SECTION */}
        <section className="max-w-[1200px] mx-auto px-6 md:px-12 flex flex-col lg:flex-row items-center gap-12 py-12 md:py-20">
          {/* Left Column: Value Proposition */}
          <div className="flex-1 space-y-6">
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3.5 py-1.5 bg-[#181b25] text-xs font-semibold font-['Plus_Jakarta_Sans',sans-serif] text-[#4edea3] tracking-wide">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              TRỢ LÝ NGHỀ NGHIỆP AI TOÀN DIỆN
            </div>

            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[#f8fafc] leading-[1.18] tracking-tight">
              Từ CV chưa tối ưu đến Offer Letter — AI đồng hành cùng bạn.
            </h1>

            <p className="text-[#94a3b8] text-base sm:text-lg leading-relaxed max-w-xl font-['Inter',sans-serif]">
              Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến với độ chính xác kỹ thuật cao.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <button
                type="button"
                onClick={() => setIsUploadModalOpen(true)}
                aria-label="Phân tích CV miễn phí ngay"
                className="bg-[#10b981] text-[#090D16] font-semibold px-6 py-3 rounded-md border border-[#10b981] hover:bg-[#4edea3] transition-colors flex items-center gap-2 shadow-sm text-sm sm:text-base font-['Inter',sans-serif] cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                <span>Phân tích CV miễn phí</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <Link
                to="/workspace"
                aria-label="Khám phá không gian làm việc Workspace"
                className="bg-[#181b25] text-[#dfe2ef] font-medium px-6 py-3 rounded-md border border-[#1E293B] hover:bg-[#1f293d] hover:border-[#4edea3]/50 transition-colors flex items-center gap-2 text-sm sm:text-base font-['Inter',sans-serif]"
              >
                Trải nghiệm Workspace
              </Link>
            </div>
          </div>

          {/* Right Column: Live ATS Diagnostics Instrument Card */}
          <div className="flex-1 w-full max-w-md">
            <div className="bg-[#111827] border border-[#1E293B] rounded-lg p-6 relative shadow-2xl">
              <div className="absolute top-0 right-0 p-4 font-['JetBrains_Mono',monospace] text-[#4edea3]/80 text-xs font-medium">
                SCAN_ID: 0x8F9A2
              </div>

              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-xs font-bold uppercase tracking-wider text-[#94a3b8] mb-4 border-b border-[#1E293B] pb-2">
                Live ATS Diagnostics
              </h2>

              {/* Score Meter */}
              <div className="flex justify-between items-end mb-6">
                <div>
                  <div className="text-xs font-medium text-[#94a3b8] mb-1 font-['Inter',sans-serif]">
                    ATS Match Score
                  </div>
                  <div className="font-['JetBrains_Mono',monospace] text-4xl text-[#4edea3] font-extrabold tracking-tight">
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
                  <span className="font-['Plus_Jakarta_Sans',sans-serif] font-medium text-[#f8fafc]">
                    FastAPI
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[95%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs font-semibold">
                      95%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="font-['Plus_Jakarta_Sans',sans-serif] font-medium text-[#f8fafc]">
                    PostgreSQL
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[90%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs font-semibold">
                      90%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="font-['Plus_Jakarta_Sans',sans-serif] font-medium text-[#f8fafc]">
                    Docker
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#31353f] rounded-full overflow-hidden">
                      <div className="w-[88%] h-full bg-[#4edea3]"></div>
                    </div>
                    <span className="font-['JetBrains_Mono',monospace] text-[#4edea3] text-xs font-semibold">
                      88%
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="font-['Plus_Jakarta_Sans',sans-serif] font-medium text-[#94a3b8]">
                    Kubernetes
                  </span>
                  <span className="text-[#f59e0b] text-xs border border-[#f59e0b]/30 px-2 py-0.5 rounded bg-[#f59e0b]/10 font-medium font-['Inter',sans-serif]">
                    Thiếu kinh nghiệm
                  </span>
                </div>
              </div>

              {/* Action Button inside Card */}
              <Link
                to="/workspace"
                aria-label="Tối ưu hóa nội dung CV ngay"
                className="w-full bg-[#181b25] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981] hover:text-[#4edea3] py-2.5 rounded-md text-sm transition-colors flex justify-center items-center gap-2 font-medium font-['Inter',sans-serif]"
              >
                <span>Tối ưu hóa nội dung CV ngay</span>
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
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* ────────────────────────────────────────────────────────
          FOOTER
      ──────────────────────────────────────────────────────── */}
      <footer className="w-full pt-16 pb-12 px-6 md:px-12 border-t border-[#1E293B] bg-[#070A10]">
        <div className="max-w-[1200px] mx-auto">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-[#1E293B]">
            {/* Column 1 & 2: Brand Info */}
            <div className="lg:col-span-2 space-y-4">
              <span
                className="inline-block text-xl font-bold text-[#4edea3] tracking-tight font-['Plus_Jakarta_Sans',sans-serif]"
              >
                CareerPilot AI
              </span>
              <p className="text-sm text-[#94a3b8] leading-relaxed max-w-sm font-['Inter',sans-serif]">
                Nền tảng trợ lý nghề nghiệp AI toàn diện thiết kế chuyên biệt cho Kỹ sư phần mềm và người tìm việc ngành IT tại Việt Nam.
              </p>
            </div>

            {/* Column 3: Tính năng cốt lõi */}
            <div className="space-y-3">
              <div className="text-xs font-semibold text-[#f8fafc] uppercase tracking-wider font-['JetBrains_Mono',monospace]">
                Tính Năng
              </div>
              <ul className="space-y-2.5 text-sm text-[#94a3b8] font-['Inter',sans-serif]">
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Phân tích CV &amp; ATS
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Tìm việc
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Luyện phỏng vấn AI
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Lộ trình kỹ năng
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Quản lý ứng tuyển
                  </span>
                </li>
              </ul>
            </div>

            {/* Column 4: Tài nguyên */}
            <div className="space-y-3">
              <div className="text-xs font-semibold text-[#f8fafc] uppercase tracking-wider font-['JetBrains_Mono',monospace]">
                Tài Nguyên
              </div>
              <ul className="space-y-2.5 text-sm text-[#94a3b8] font-['Inter',sans-serif]">
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Tiêu chuẩn ATS 2026
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Phương pháp STAR
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Không gian AI Workspace
                  </span>
                </li>
                <li>
                  <span className="hover:text-[#4edea3] transition-colors cursor-default">
                    Dashboard ứng viên
                  </span>
                </li>
              </ul>
            </div>

            {/* Column 5: Thông tin */}
            <div className="space-y-3">
              <div className="text-xs font-semibold text-[#f8fafc] uppercase tracking-wider font-['JetBrains_Mono',monospace]">
                Thông Tin
              </div>
              <ul className="space-y-2.5 text-sm text-[#94a3b8] font-['Inter',sans-serif]">
                <li>
                  <span className="text-[#94a3b8] hover:text-[#dfe2ef] transition-colors cursor-default">
                    Bảo mật dữ liệu hồ sơ
                  </span>
                </li>
                <li>
                  <span className="text-[#94a3b8] hover:text-[#dfe2ef] transition-colors cursor-default">
                    Điều khoản sử dụng
                  </span>
                </li>
                <li>
                  <span className="text-[#94a3b8] hover:text-[#dfe2ef] transition-colors cursor-default">
                    Chính sách quyền riêng tư
                  </span>
                </li>
                <li>
                  <span className="text-[#64748b]">
                    Đồ án Tốt nghiệp CNTT
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-[#94a3b8] font-['Inter',sans-serif]">
            <div>
              © 2026 CareerPilot AI. Kỹ thuật chính xác từ Việt Nam.
            </div>
            <div className="flex items-center gap-4 font-['JetBrains_Mono',monospace] text-[#64748b]">
              <span>Bảo mật TLS 1.3</span>
              <span>•</span>
              <span className="text-[#4edea3]">careerpilot.vn</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Upload CV Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={handleUploadSuccess}
      />
    </div>
  );
}
