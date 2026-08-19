"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Search,
  Grid3X3,
  Network,
  Clock,
  Upload,
  Shield,
  Lock,
  Sparkles,
  Command,
  ChevronRight,
  BookOpen,
} from "lucide-react";
import { getMemories, getThumbnailUrl, Memory, apiFetch } from "@/lib/api";
import DesktopCompanionModal from "./DesktopCompanionModal";
import DiagnosticsModal from "./DiagnosticsModal";

const NAV = [
  { href: "/", icon: Search, label: "Search & Memory" },
  { href: "/gallery", icon: Grid3X3, label: "Knowledge Gallery" },
  { href: "/constellation", icon: Network, label: "Memory Constellation" },
  { href: "/timeline", icon: Clock, label: "Timeline Ledger" },
  { href: "/upload", icon: Upload, label: "Ingest Screenshots" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [recents, setRecents] = useState<Memory[]>([]);
  const [showDesktopModal, setShowDesktopModal] = useState(false);
  const [showDiagnosticsModal, setShowDiagnosticsModal] = useState(false);
  const [stats, setStats] = useState<{ total: number; protected: number; relationships: number }>({
    total: 0,
    protected: 0,
    relationships: 0,
  });

  useEffect(() => {
    getMemories({ limit: 4 })
      .then((data) => setRecents(data.items || []))
      .catch(() => {});

    apiFetch<{ total_memories?: number; sensitive_count?: number; protected_secrets?: number; total_relationships?: number }>("/api/stats")
      .then((data) => {
        setStats({
          total: data.total_memories || 0,
          protected: data.sensitive_count ?? data.protected_secrets ?? 0,
          relationships: data.total_relationships || 0,
        });
      })
      .catch(() => {});
  }, [pathname]);

  return (
    <aside
      style={{
        width: 268,
        background: "var(--bg-subtle)",
        borderRight: "1px solid var(--border-medium)",
        display: "flex",
        flexDirection: "column",
        padding: "1.5rem 1.1rem",
        gap: "0.5rem",
        flexShrink: 0,
        userSelect: "none",
      }}
    >
      {/* Editorial Brand Header */}
      <Link
        href="/"
        style={{
          padding: "0.25rem 0.5rem 1.4rem",
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          textDecoration: "none",
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "var(--radius-sm)",
            background: "var(--bg-surface)",
            border: "1px solid var(--border-medium)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "var(--shadow-paper)",
          }}
        >
          <span style={{ fontSize: "1.1rem", fontFamily: "var(--font-serif)", fontWeight: 700, color: "var(--accent-terracotta)" }}>
            A
          </span>
        </div>
        <div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontWeight: 600,
              fontSize: "1.15rem",
              letterSpacing: "-0.02em",
              color: "var(--text-primary)",
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
            }}
          >
            AURA
            <span
              style={{
                fontSize: "0.62rem",
                fontFamily: "var(--font-sans)",
                padding: "1px 6px",
                borderRadius: 99,
                background: "var(--accent-light)",
                color: "var(--accent-dark)",
                fontWeight: 600,
                border: "1px solid var(--accent-border)",
              }}
            >
              2.0
            </span>
          </div>
          <div style={{ fontSize: "0.67rem", color: "var(--text-secondary)", fontWeight: 500, letterSpacing: "-0.01em" }}>
            Agentic Universal Retrieval & Analysis
          </div>
        </div>
      </Link>

      {/* Global Quick Command Bar Trigger */}
      <button
        onClick={() => {
          const event = new KeyboardEvent("keydown", {
            key: "k",
            metaKey: true,
            ctrlKey: true,
            bubbles: true,
          });
          window.dispatchEvent(event);
        }}
        className="tactile-pill"
        style={{
          width: "100%",
          justifyContent: "space-between",
          padding: "0.45rem 0.75rem",
          background: "var(--bg-surface)",
          marginBottom: "0.75rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Search size={14} color="var(--accent-terracotta)" />
          <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>Quick find...</span>
        </div>
        <kbd
          style={{
            fontSize: "0.68rem",
            color: "var(--text-muted)",
            background: "var(--bg-subtle)",
            padding: "2px 5px",
            borderRadius: 4,
            border: "1px solid var(--border-subtle)",
            fontFamily: "var(--font-mono)",
          }}
        >
          ⌘K
        </kbd>
      </button>

      {/* Navigation Ledger */}
      <div style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", padding: "0.2rem 0.5rem" }}>
        Navigation
      </div>
      <nav style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
        {NAV.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius-sm)",
                color: isActive ? "var(--accent-dark)" : "var(--text-secondary)",
                background: isActive ? "var(--accent-light)" : "transparent",
                border: isActive ? "1px solid var(--accent-border)" : "1px solid transparent",
                fontWeight: isActive ? 600 : 500,
                fontSize: "0.84rem",
                textDecoration: "none",
                transition: "all 0.15s ease",
              }}
            >
              <Icon size={16} color={isActive ? "var(--accent-terracotta)" : "var(--text-muted)"} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Recent Visual Memories Section */}
      <div style={{ marginTop: "1.25rem", flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
        <div style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", padding: "0.2rem 0.5rem 0.4rem" }}>
          Recent Ingestions
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem", overflowY: "auto" }}>
          {recents.map((mem) => {
            const isCritical = mem.sensitivity_level === "CRITICAL";
            return (
              <Link
                key={mem.id}
                href={`/memory/${mem.id}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.6rem",
                  padding: "0.4rem 0.5rem",
                  borderRadius: "var(--radius-xs)",
                  color: "var(--text-secondary)",
                  textDecoration: "none",
                  fontSize: "0.78rem",
                  transition: "background 0.12s ease",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.background = "var(--bg-hover)";
                  (e.currentTarget as HTMLElement).style.color = "var(--text-primary)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.background = "transparent";
                  (e.currentTarget as HTMLElement).style.color = "var(--text-secondary)";
                }}
              >
                <div
                  style={{
                    width: 26,
                    height: 20,
                    borderRadius: 3,
                    background: "var(--bg-muted)",
                    border: "1px solid var(--border-subtle)",
                    overflow: "hidden",
                    flexShrink: 0,
                  }}
                >
                  {isCritical ? (
                    <div style={{ width: "100%", height: "100%", background: "rgba(184, 58, 46, 0.1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Lock size={10} color="var(--severity-critical)" />
                    </div>
                  ) : (
                    <img
                      src={getThumbnailUrl(mem.id)}
                      alt=""
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  )}
                </div>
                <span
                  style={{
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    flex: 1,
                  }}
                >
                  {mem.summary || mem.original_filename}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Editorial System Status Footer */}
      <div
        style={{
          marginTop: "auto",
          padding: "0.85rem",
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-sm)",
          border: "1px solid var(--border-medium)",
          display: "flex",
          flexDirection: "column",
          gap: "0.4rem",
          boxShadow: "var(--shadow-paper)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.72rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Indexed Memory</span>
          <span style={{ color: "var(--text-primary)", fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--severity-public)" }} />
            {stats.total} artifacts
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.72rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Shield Protected</span>
          <span style={{ color: "var(--severity-critical)", fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
            <Shield size={11} color="var(--severity-critical)" />
            {stats.protected} secrets
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.72rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Graph Constellation</span>
          <span style={{ color: "var(--accent-dark)", fontWeight: 600, fontFamily: "var(--font-mono)" }}>
            {stats.relationships} edges
          </span>
        </div>

        {/* Desktop Companion OS Ingestion Trigger */}
        <button
          type="button"
          onClick={() => setShowDesktopModal(true)}
          style={{
            marginTop: "0.35rem",
            padding: "0.4rem 0.5rem",
            background: "var(--accent-light)",
            border: "1px solid var(--accent-border)",
            borderRadius: "var(--radius-xs)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            cursor: "pointer",
            fontSize: "0.72rem",
            color: "var(--accent-dark)",
            fontWeight: 600,
            transition: "all 0.15s ease",
          }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--severity-public)", boxShadow: "0 0 5px var(--severity-public)" }} />
            <span>OS Ingestion Active</span>
          </span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.68rem", opacity: 0.85 }}>Ctrl+Shift+A</span>
        </button>

        {/* Developer Diagnostics Panel Trigger */}
        <button
          type="button"
          onClick={() => setShowDiagnosticsModal(true)}
          style={{
            padding: "0.35rem 0.5rem",
            background: "var(--bg-subtle)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "var(--radius-xs)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            cursor: "pointer",
            fontSize: "0.7rem",
            color: "var(--text-secondary)",
            transition: "all 0.15s ease",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span>⚡ Vision Health & Telemetry</span>
          </span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.65rem", color: "#059669" }}>Live</span>
        </button>
      </div>

      <DesktopCompanionModal
        isOpen={showDesktopModal}
        onClose={() => setShowDesktopModal(false)}
      />

      <DiagnosticsModal
        isOpen={showDiagnosticsModal}
        onClose={() => setShowDiagnosticsModal(false)}
      />
    </aside>
  );
}
