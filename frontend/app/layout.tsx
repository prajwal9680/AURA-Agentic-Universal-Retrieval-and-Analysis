import type { Metadata } from "next";
import { Inter, Newsreader, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import CommandPalette from "@/components/CommandPalette";
import TactileCursor from "@/components/TactileCursor";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const newsreader = Newsreader({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AURA — Agentic Universal Retrieval and Analysis",
  description:
    "AURA (Agentic Universal Retrieval and Analysis) — Don't search your screenshots. Ask your memory. Multimodal visual memory, pgvector hybrid search, and LangGraph knowledge graph intelligence.",
  keywords: ["AURA", "Agentic Universal Retrieval and Analysis", "multimodal RAG", "visual memory", "pgvector", "LangGraph", "knowledge graph"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${newsreader.variable} ${jetbrainsMono.variable}`}
    >
      <body>
        <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "var(--bg-canvas)" }}>
          <Sidebar />
          <main
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              background: "var(--bg-canvas)",
              position: "relative",
            }}
          >
            {children}
          </main>
        </div>
        <CommandPalette />
        <TactileCursor />
      </body>
    </html>
  );
}
