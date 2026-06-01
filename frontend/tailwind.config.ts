import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Warm charcoal + cream + papaya-coral signal
        bg: {
          DEFAULT: "#141210",
          1: "#1A1714",
          2: "#211C18",
          3: "#2A231D",
        },
        ink: {
          DEFAULT: "#F2EBE0",
          dim: "#BDB3A4",
          mute: "#7A7367",
          faint: "#3F3A33",
        },
        coral: {
          DEFAULT: "#E26C45",
          hi: "#F08A66",
          lo: "#B5512F",
        },
        signal: {
          danger: "#E0492E",
          caution: "#E2A33B",
          ok: "#5FB079",
          info: "#7AB7C7",
        },
        line: {
          DEFAULT: "rgba(242,235,224,0.08)",
          strong: "rgba(242,235,224,0.16)",
        },
      },
      fontFamily: {
        display: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        "mega": ["clamp(96px, 18vw, 320px)", { lineHeight: "0.88", letterSpacing: "-0.04em" }],
        "hero": ["clamp(64px, 10vw, 180px)", { lineHeight: "0.92", letterSpacing: "-0.035em" }],
        "section": ["clamp(48px, 7vw, 120px)", { lineHeight: "0.95", letterSpacing: "-0.03em" }],
      },
      borderRadius: {
        "bezel-lg": "2rem",
        "bezel-md": "1.25rem",
        "bezel-sm": "0.75rem",
      },
      boxShadow: {
        "bezel-inset": "inset 0 1px 0 rgba(255,255,255,0.08), inset 0 0 0 1px rgba(255,255,255,0.04)",
        "glass-lift": "0 1px 0 rgba(255,255,255,0.08) inset, 0 30px 80px -20px rgba(0,0,0,0.6)",
        "coral-glow": "0 0 60px -10px rgba(226,108,69,0.35)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "grain": "grain 8s steps(10) infinite",
        "tick": "tick 1s steps(1, end) infinite",
      },
      keyframes: {
        grain: {
          "0%,100%": { transform: "translate(0,0)" },
          "10%": { transform: "translate(-5%,-10%)" },
          "30%": { transform: "translate(3%,-15%)" },
          "50%": { transform: "translate(12%,9%)" },
          "70%": { transform: "translate(9%,4%)" },
          "90%": { transform: "translate(-1%,7%)" },
        },
        tick: { "0%,49%": { opacity: "1" }, "50%,100%": { opacity: "0" } },
      },
      transitionTimingFunction: {
        "spring": "cubic-bezier(0.32, 0.72, 0, 1)",
        "swift": "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
