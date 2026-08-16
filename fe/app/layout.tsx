import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện",
  description:
    "Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#090D16] text-[#dfe2ef] antialiased">
        {children}
      </body>
    </html>
  );
}
