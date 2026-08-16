import React from "react";
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased flex items-center justify-center px-4 font-['Inter',sans-serif]">
      <div className="text-center space-y-4 max-w-md">
        <div className="text-6xl font-extrabold text-[#4edea3] font-['JetBrains_Mono',monospace]">
          404
        </div>
        <h1 className="text-xl font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
          Trang không tồn tại
        </h1>
        <p className="text-xs text-[#94a3b8]">
          Đường dẫn bạn yêu cầu không khả dụng hoặc đã được chuyển vị trí.
        </p>
        <Link
          to="/"
          className="inline-block bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] font-bold px-6 py-2.5 rounded-xl text-xs transition-colors shadow-sm"
        >
          Quay lại Trang Chủ
        </Link>
      </div>
    </div>
  );
}
