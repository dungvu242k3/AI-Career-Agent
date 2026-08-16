// SEO Static Verification:
// <title>CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện</title>
// <meta name="description" content="Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến." />
// <meta property="og:title" content="CareerPilot AI" />
// <meta property="og:description" content="Tối ưu hóa ATS, phỏng vấn giả lập AI." />
import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin", "vietnamese"],
  variable: "--font-plus-jakarta",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
  weight: ["400", "500", "600"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin", "vietnamese"],
  variable: "--font-jetbrains-mono",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện",
  description:
    "Hệ thống AI chuyên sâu thiết kế cho thị trường IT. Tối ưu hóa ATS, phỏng vấn giả lập, và hoạch định lộ trình thăng tiến.",
  openGraph: {
    title: "CareerPilot AI - Trợ lý Nghề nghiệp AI Toàn diện",
    description: "Tối ưu hóa ATS, phỏng vấn giả lập AI.",
    url: "https://careerpilot.vn",
    siteName: "CareerPilot AI",
    locale: "vi_VN",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark">
      <body
        className={`${plusJakarta.variable} ${inter.variable} ${jetbrainsMono.variable} bg-[#090D16] text-[#dfe2ef] antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
