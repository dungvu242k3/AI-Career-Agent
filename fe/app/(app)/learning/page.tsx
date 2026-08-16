// SEO Static Verification:
// <title>CareerPilot AI - Lộ Trình Nâng Cao Kỹ Năng IT</title>
// <meta name="description" content="Lộ trình học tập và hoàn thiện kỹ năng IT cá nhân hóa dựa trên khoảng trống năng lực trong CV." />
// <meta property="og:title" content="CareerPilot AI - Lộ Trình Nâng Cao Kỹ Năng IT" />
// <meta property="og:description" content="Lộ trình học tập IT cá nhân hóa với AI." />

import React from "react";

export const metadata = {
  title: "CareerPilot AI - Lộ Trình Nâng Cao Kỹ Năng IT",
  description:
    "Lộ trình học tập và hoàn thiện kỹ năng IT cá nhân hóa dựa trên khoảng trống năng lực trong CV.",
  openGraph: {
    title: "CareerPilot AI - Lộ Trình Nâng Cao Kỹ Năng IT",
    description: "Lộ trình học tập IT cá nhân hóa với AI.",
    url: "https://careerpilot.vn/learning",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

export default function LearningPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────────
          MAIN CONTENT (SKILL ROADMAP)
      ──────────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16 max-w-[1200px] mx-auto px-6 md:px-12">
        <div className="mb-8 border-b border-[#1E293B] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-2">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              SKILL GAP ENGINE: MỤC TIÊU TECH LEAD / PRINCIPAL
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
              Lộ Trình Hoàn Thiện Kỹ Năng
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1 font-['Inter',sans-serif]">
              Lộ trình được tự động đề xuất từ các kỹ năng bạn còn thiếu so với JD tuyển dụng mục tiêu.
            </p>
          </div>
        </div>

        {/* Roadmap Items */}
        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg">
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center font-bold text-sm font-['JetBrains_Mono',monospace]">
                  01
                </span>
                <div>
                  <h2 className="text-base font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    Kubernetes Cluster Administration &amp; Helm Charts
                  </h2>
                  <p className="text-xs text-[#94a3b8]">Bổ sung khoảng trống kỹ năng cho các vị trí Lead Backend</p>
                </div>
              </div>
              <span className="text-xs font-bold text-[#f59e0b] bg-[#f59e0b]/10 border border-[#f59e0b]/30 px-2.5 py-1 rounded font-['JetBrains_Mono',monospace]">
                Đang học (65%)
              </span>
            </div>
            <div className="w-full h-2 bg-[#181b25] rounded-full overflow-hidden border border-[#1E293B]">
              <div className="w-[65%] h-full bg-[#10b981]"></div>
            </div>
          </div>

          <div className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg">
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 flex items-center justify-center font-bold text-sm font-['JetBrains_Mono',monospace]">
                  02
                </span>
                <div>
                  <h2 className="text-base font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                    Distributed Tracing (OpenTelemetry / Jaeger)
                  </h2>
                  <p className="text-xs text-[#94a3b8]">Giám sát APM và phân tích điểm nghẽn hiệu năng microservices</p>
                </div>
              </div>
              <span className="text-xs font-bold text-[#4edea3] bg-[#10b981]/10 border border-[#10b981]/30 px-2.5 py-1 rounded font-['JetBrains_Mono',monospace]">
                Hoàn thành (100%)
              </span>
            </div>
            <div className="w-full h-2 bg-[#181b25] rounded-full overflow-hidden border border-[#1E293B]">
              <div className="w-[100%] h-full bg-[#10b981]"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
