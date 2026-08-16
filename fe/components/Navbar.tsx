"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Phân tích CV", href: "/workspace" },
    { label: "Tìm việc", href: "/jobs" },
    { label: "Phỏng vấn AI", href: "/interview" },
    { label: "Lộ trình kỹ năng", href: "/learning" },
    { label: "Quản lý ứng tuyển", href: "/applications" },
  ];

  return (
    <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 md:px-12 h-16 bg-[#0f131c]/90 backdrop-blur-md border-b border-[#3c4a42]/40 font-['Inter',sans-serif]">
      {/* ──────────────── Logo bên trái ──────────────── */}
      <div className="flex items-center shrink-0">
        <Link
          href="/"
          aria-label="CareerPilot AI Trang chủ"
          className="text-xl font-bold text-[#4edea3] tracking-tighter shrink-0 hover:opacity-90 transition-opacity font-['Plus_Jakarta_Sans',sans-serif]"
        >
          CareerPilot AI
        </Link>
      </div>

      {/* ──────────────── 5 Tính năng ở chính giữa (Cố định 1 hàng) ──────────────── */}
      <nav
        aria-label="Điều hướng chính"
        className="hidden lg:flex items-center justify-center gap-1 xl:gap-2 whitespace-nowrap overflow-x-auto scrollbar-none absolute left-1/2 -translate-x-1/2"
      >
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
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
          href="/login"
          aria-label="Đăng nhập tài khoản"
          className="text-[#bbcabf] hover:text-[#4edea3] font-medium text-sm transition-colors px-2 py-1.5"
        >
          Đăng nhập
        </Link>
        <Link
          href="/workspace"
          aria-label="Bắt đầu sử dụng miễn phí"
          className="bg-[#10b981] hover:bg-[#4edea3] text-[#0f131c] font-semibold px-4 py-2 rounded text-sm transition-colors shadow-sm"
        >
          Bắt đầu miễn phí
        </Link>
      </div>
    </header>
  );
}
