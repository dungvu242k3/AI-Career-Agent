import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const pathname = location.pathname;

  const navItems = [
    { label: "Phân tích & Tìm việc", href: "/workspace" },
    { label: "Phỏng vấn AI", href: "/interview" },
    { label: "Lộ trình kỹ năng", href: "/learning" },
    { label: "Quản lý ứng tuyển", href: "/applications" },
  ];

  return (
    <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 sm:px-8 md:px-12 h-16 bg-[#0f131c]/90 backdrop-blur-md border-b border-[#3c4a42]/40 font-['Inter',sans-serif]">
      {/* ──────────────── Logo bên trái ──────────────── */}
      <div className="flex items-center gap-3 shrink-0">
        <Link
          to="/"
          aria-label="CareerPilot AI Trang chủ"
          className="text-xl font-bold text-[#4edea3] tracking-tighter shrink-0 hover:opacity-90 transition-opacity font-['Plus_Jakarta_Sans',sans-serif] flex items-center gap-2"
        >
          <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] animate-pulse"></span>
          <span>CareerPilot AI</span>
        </Link>
        <span className="hidden sm:inline text-[11px] bg-[#181b25] text-[#94a3b8] px-2 py-0.5 rounded border border-[#1E293B] font-['JetBrains_Mono',monospace]">
          Studio v2.4
        </span>
      </div>

      {/* ──────────────── 4 Tính năng ở chính giữa ──────────────── */}
      <nav
        aria-label="Điều hướng chính"
        className="hidden md:flex items-center justify-center gap-1 xl:gap-2 whitespace-nowrap overflow-x-auto scrollbar-none absolute left-1/2 -translate-x-1/2"
      >
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              aria-label={`Tính năng ${item.label}`}
              className={`px-3 py-1.5 text-sm shrink-0 transition-all duration-150 rounded ${
                isActive
                  ? "text-[#4edea3] font-semibold border-b-2 border-[#4edea3]"
                  : "text-[#bbcabf] font-medium hover:text-[#4edea3] hover:bg-[#31353f]/50"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* ──────────────── CTA Actions bên phải ──────────────── */}
      <div className="flex items-center gap-3 md:gap-4 shrink-0">
        <Link
          to="/login"
          aria-label="Đăng nhập tài khoản"
          className="text-[#bbcabf] hover:text-[#4edea3] font-medium text-sm transition-colors px-2 py-1.5"
        >
          Đăng nhập
        </Link>
        <Link
          to="/workspace"
          aria-label="Mở Không Gian Làm Việc AI Studio"
          className="bg-[#10b981] hover:bg-[#4edea3] text-[#0f131c] font-bold px-4 py-2 rounded-lg text-xs sm:text-sm transition-colors shadow-sm font-['Plus_Jakarta_Sans',sans-serif]"
        >
          AI Studio
        </Link>
      </div>
    </header>
  );
}
