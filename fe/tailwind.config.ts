import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./entities/**/*.{js,ts,jsx,tsx,mdx}",
    "./shared/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090D16",
        surface: "#111827",
        primary: {
          DEFAULT: "#10B981",
          light: "#4EDEa3",
          dark: "#059669",
        },
        cyan: {
          accent: "#06B6D4",
        },
        amber: {
          warning: "#F59E0B",
        },
        border: {
          DEFAULT: "#1E293B",
          subtle: "#334155",
        },
        text: {
          primary: "#F8FAFC",
          muted: "#94A3B8",
          variant: "#BBCABF",
        },
      },
      fontFamily: {
        headline: ["var(--font-plus-jakarta)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
