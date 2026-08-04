import type { Config } from "tailwindcss";
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        orange: { DEFAULT: "#ff6a00", dark: "#e85f00", soft: "#fff3ea" },
        brand: { orange: "#ff6a00", dark: "#101828", gray: "#344054", background: "#fafafa" },
        ink: "#101828",
        body: "#344054",
        muted: "#667085",
        line: "#eaecf0",
        paper: "#fafafa",
        success: "#12b76a",
      },
      fontFamily: {
        sans: ['Inter','-apple-system','BlinkMacSystemFont','Segoe UI','Roboto','Helvetica','Arial','sans-serif'],
        mono: ['ui-monospace','SF Mono','Menlo','Consolas','monospace'],
      },
      borderRadius: { xl2: "16px" },
      boxShadow: { card: "0 10px 34px rgba(16,24,40,.07)", pop: "0 18px 46px rgba(16,24,40,.12)" },
    },
  },
  plugins: [],
} satisfies Config;
