import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { LenisProvider } from "@/components/lenis-provider";
import { Grain } from "@/components/grain";
import { CursorGlow } from "@/components/cursor-glow";
import { Nav } from "@/components/nav";

const sans = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Pit Wall AI, the race-engineer in the loop",
  description:
    "Real-time, explainable race engineering. Live telemetry, counterfactual strategy, FIA rulebook on demand. Built on FastAPI plus IBM Granite.",
  metadataBase: new URL("http://localhost:3000"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body className="min-h-[100dvh] antialiased">
        <LenisProvider>
          <CursorGlow />
          <Grain />
          {children}
          <Nav />
        </LenisProvider>
      </body>
    </html>
  );
}
