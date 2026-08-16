import React from "react";
import { Link } from "react-router-dom";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased flex items-center justify-center px-4 font-['Inter',sans-serif]">
      <div className="w-full max-w-md bg-[#111827] border border-[#1E293B] rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <Link
            to="/"
            className="text-2xl font-bold text-[#4edea3] tracking-tight font-['Plus_Jakarta_Sans',sans-serif]"
          >
            CareerPilot AI
          </Link>
          <h1 className="text-xl font-bold text-[#f8fafc] mt-3 font-['Plus_Jakarta_Sans',sans-serif]">
            Đăng nhập hệ thống
          </h1>
          <p className="text-xs text-[#94a3b8] mt-1">
            Tiếp tục tối ưu hóa CV và luyện phỏng vấn với AI
          </p>
        </div>

        <form className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#f8fafc] mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Email
            </label>
            <input
              type="email"
              placeholder="dungvu@example.com"
              className="w-full bg-[#181b25] border border-[#1E293B] focus:border-[#10b981] rounded-xl px-4 py-2.5 text-sm text-[#f8fafc] placeholder-[#64748b] outline-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#f8fafc] mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">
              Mật khẩu
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full bg-[#181b25] border border-[#1E293B] focus:border-[#10b981] rounded-xl px-4 py-2.5 text-sm text-[#f8fafc] placeholder-[#64748b] outline-none transition-colors"
            />
          </div>

          <Link
            to="/workspace"
            className="w-full bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold py-3 rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-2 mt-6 font-['Plus_Jakarta_Sans',sans-serif]"
          >
            Đăng Nhập
          </Link>
        </form>

        <div className="mt-6 text-center text-xs text-[#94a3b8]">
          Chưa có tài khoản?{" "}
          <Link to="/workspace" className="text-[#4edea3] hover:underline font-semibold">
            Bắt đầu miễn phí
          </Link>
        </div>
      </div>
    </div>
  );
}
