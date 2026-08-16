// SEO Static Verification:
// <title>CareerPilot AI - Tìm Việc & So Khớp Năng Lực IT</title>
// <meta name="description" content="Hệ thống AI so khớp việc làm IT chính xác theo năng lực thực tế trong CV của bạn." />
// <meta property="og:title" content="CareerPilot AI - Tìm Việc & So Khớp Năng Lực IT" />
// <meta property="og:description" content="Tìm việc làm IT và so khớp ATS chính xác với AI." />

import React from "react";
import Link from "next/link";

export const metadata = {
  title: "CareerPilot AI - Tìm Việc & So Khớp Năng Lực IT",
  description:
    "Hệ thống AI so khớp việc làm IT chính xác theo năng lực thực tế trong CV của bạn.",
  openGraph: {
    title: "CareerPilot AI - Tìm Việc & So Khớp Năng Lực IT",
    description: "Tìm việc làm IT và so khớp ATS chính xác với AI.",
    url: "https://careerpilot.vn/jobs",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

const mockJobs = [
  {
    id: "job-1",
    title: "Senior Python / FastAPI Engineer",
    company: "VNG Corporation",
    location: "TP. Hồ Chí Minh (Hybrid)",
    salary: "$2,500 - $3,500",
    matchScore: 96,
    tags: ["FastAPI", "PostgreSQL", "Docker", "Redis"],
    matchingReasons: [
      "Khớp hoàn toàn 5 năm kinh nghiệm Backend với Python/FastAPI",
      "Kinh nghiệm xử lý 10,000+ RPS đáp ứng yêu cầu High-load",
    ],
    missingSkills: [],
  },
  {
    id: "job-2",
    title: "Lead Backend Architect",
    company: "MoMo (M-Service)",
    location: "TP. Hồ Chí Minh",
    salary: "$3,000 - $4,200",
    matchScore: 94,
    tags: ["Microservices", "System Design", "Kafka", "PostgreSQL"],
    matchingReasons: [
      "Khớp kiến trúc Microservices và cơ sở dữ liệu phân tán",
      "Có thế mạnh về Payment Gateway & Transaction",
    ],
    missingSkills: ["Kubernetes Cluster"],
  },
  {
    id: "job-3",
    title: "Senior Software Engineer (Go / Cloud)",
    company: "Grab Vietnam",
    location: "TP. Hồ Chí Minh & Remote",
    salary: "$2,800 - $3,800",
    matchScore: 89,
    tags: ["Golang", "Distributed Systems", "gRPC", "Docker"],
    matchingReasons: [
      "Thế mạnh về tối ưu hóa độ trễ API P99",
      "Kinh nghiệm làm việc với hệ thống phân tán lớn",
    ],
    missingSkills: ["Golang Production Experience"],
  },
];

export default function JobsPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* ────────────────────────────────────────────────────────────
          MAIN CONTENT (JOBS MATCHING ARENA)
      ──────────────────────────────────────────────────────────── */}
      <main className="pt-24 pb-16 max-w-[1200px] mx-auto px-6 md:px-12">
        {/* Banner */}
        <div className="mb-8 border-b border-[#1E293B] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-2">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
              AI MATCH ENGINE: 42 VIỆC LÀM PHÙ HỢP
            </div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
              Việc Làm IT So Khớp Năng Lực
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1 font-['Inter',sans-serif]">
              Hệ thống tự động đối chiếu hồ sơ của bạn với 500+ JD tuyển dụng thực tế và chấm điểm tương thích ATS.
            </p>
          </div>
        </div>

        {/* Job List Cards */}
        <div className="space-y-4">
          {mockJobs.map((job) => (
            <div
              key={job.id}
              className="bg-[#111827] border border-[#1E293B] hover:border-[#10b981]/50 p-6 rounded-xl transition-all shadow-lg"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-[#1E293B]/60">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="text-base sm:text-lg font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
                      {job.title}
                    </h2>
                    <span className="bg-[#10b981]/10 text-[#4edea3] border border-[#10b981]/30 text-xs px-2.5 py-0.5 rounded-full font-['JetBrains_Mono',monospace] font-bold">
                      {job.matchScore}% ATS Match
                    </span>
                  </div>
                  <div className="text-xs text-[#94a3b8] mt-1.5 font-['Inter',sans-serif]">
                    <span className="text-[#dfe2ef] font-semibold">{job.company}</span> • {job.location} •{" "}
                    <span className="text-[#4edea3] font-['JetBrains_Mono',monospace] font-medium">
                      {job.salary}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <Link
                    href="/workspace"
                    aria-label={`Tối ưu CV cho ${job.company}`}
                    className="bg-[#181b25] hover:bg-[#1f293d] text-[#dfe2ef] border border-[#1E293B] hover:border-[#10b981]/50 text-xs font-semibold px-4 py-2.5 rounded-lg transition-colors"
                  >
                    Tối ưu CV cho JD này
                  </Link>
                  <button
                    type="button"
                    aria-label={`Ứng tuyển vào ${job.company}`}
                    className="bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-semibold text-xs px-4 py-2.5 rounded-lg transition-colors shadow-sm"
                  >
                    Ứng tuyển ngay
                  </button>
                </div>
              </div>

              {/* Tags & Reasons */}
              <div className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <div className="text-[#4edea3] font-semibold mb-2 flex items-center gap-1 font-['JetBrains_Mono',monospace]">
                    <span>✓ Lý do phù hợp:</span>
                  </div>
                  <ul className="space-y-1 text-[#94a3b8] list-disc list-inside">
                    {job.matchingReasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-[#94a3b8] font-semibold mb-2 font-['JetBrains_Mono',monospace]">
                    Kỹ năng yêu cầu:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {job.tags.map((t, i) => (
                      <span
                        key={i}
                        className="bg-[#181b25] text-[#bbcabf] border border-[#1E293B] px-2 py-0.5 rounded font-['JetBrains_Mono',monospace]"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
