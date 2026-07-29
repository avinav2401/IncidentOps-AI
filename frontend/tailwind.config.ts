import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(148, 163, 184, 0.08), 0 18px 48px rgba(2, 6, 23, 0.38)",
        "glow-blue": "0 0 32px rgba(56, 189, 248, 0.12)",
      },
      animation: {
        "pulse-soft": "pulse-soft 2.6s ease-in-out infinite",
        "enter": "enter 450ms cubic-bezier(0.22, 1, 0.36, 1) both",
      },
      keyframes: {
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: ".45" },
        },
        enter: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
