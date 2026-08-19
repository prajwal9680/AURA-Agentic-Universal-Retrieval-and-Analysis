"use client";
import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Grid3X3,
  Network,
  Clock,
  Upload,
  Lock,
  ArrowRight,
  Sparkles,
  Command,
} from "lucide-react";
import { getMemories, Memory } from "@/lib/api";

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Memory[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
      getMemories({ limit: 6 })
        .then((d) => setResults(d.items || []))
        .catch(() => {});
    } else {
      setQuery("");
      setSelectedIndex(0);
    }
  }, [open]);

  useEffect(() => {
    if (!query.trim()) {
      getMemories({ limit: 6 })
        .then((d) => setResults(d.items || []))
        .catch(() => {});
      return;
    }
    const timer = setTimeout(() => {
      getMemories({ search: query, limit: 6 })
        .then((d) => setResults(d.items || []))
        .catch(() => {});
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (path: string) => {
    setOpen(false);
    router.push(path);
  };

  const navActions = [
    { label: "Search & Memory", path: "/", icon: Search },
    { label: "Knowledge Gallery", path: "/gallery", icon: Grid3X3 },
    { label: "Memory Constellation", path: "/constellation", icon: Network },
    { label: "Timeline Ledger", path: "/timeline", icon: Clock },
    { label: "Ingest Screenshots", path: "/upload", icon: Upload },
  ];

  if (!open) return null;

  return (
    <div
      onClick={() => setOpen(false)}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(31, 29, 26, 0.28)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "12vh",
        zIndex: 9999,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="paper-surface"
        style={{
          width: "100%",
          maxWidth: 620,
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-lg)",
          overflow: "hidden",
          boxShadow: "var(--shadow-floating)",
          border: "1px solid var(--border-strong)",
        }}
      >
        {/* Search Bar Input */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "1rem 1.25rem",
            borderBottom: "1px solid var(--border-medium)",
            gap: "0.75rem",
          }}
        >
          <Search size={18} color="var(--accent-terracotta)" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setSelectedIndex((prev) => (results.length > 0 ? (prev + 1) % results.length : 0));
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setSelectedIndex((prev) => (results.length > 0 ? (prev - 1 + results.length) % results.length : 0));
              } else if (e.key === "Enter") {
                if (results[selectedIndex]) {
                  handleSelect(`/memory/${results[selectedIndex].id}`);
                } else if (query.trim()) {
                  handleSelect(`/?q=${encodeURIComponent(query.trim())}`);
                }
              }
            }}
            placeholder="Search memory ledger or jump to section..."
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              fontSize: "0.95rem",
              fontFamily: "var(--font-sans)",
              color: "var(--text-primary)",
            }}
          />
          <kbd
            style={{
              fontSize: "0.68rem",
              color: "var(--text-muted)",
              background: "var(--bg-subtle)",
              padding: "2px 6px",
              borderRadius: 4,
              border: "1px solid var(--border-subtle)",
              fontFamily: "var(--font-mono)",
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Quick Jump Navigation */}
        {!query && (
          <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.4rem", padding: "0 0.5rem" }}>
              Quick Jump
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.3rem" }}>
              {navActions.map((act) => {
                const Icon = act.icon;
                return (
                  <button
                    key={act.path}
                    onClick={() => handleSelect(act.path)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      padding: "0.45rem 0.6rem",
                      background: "transparent",
                      border: "none",
                      borderRadius: "var(--radius-xs)",
                      color: "var(--text-secondary)",
                      fontSize: "0.82rem",
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "var(--bg-subtle)";
                      (e.currentTarget as HTMLElement).style.color = "var(--accent-dark)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "transparent";
                      (e.currentTarget as HTMLElement).style.color = "var(--text-secondary)";
                    }}
                  >
                    <Icon size={14} color="var(--accent-terracotta)" />
                    <span>{act.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Search Results List */}
        <div style={{ padding: "0.75rem 1rem", maxHeight: 320, overflowY: "auto" }}>
          <div style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.4rem", padding: "0 0.5rem" }}>
            {query ? "Matching Visual Memories" : "Recent Visual Artifacts"}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            {results.map((item, idx) => (
              <div
                key={item.id}
                onClick={() => handleSelect(`/memory/${item.id}`)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.55rem 0.65rem",
                  borderRadius: "var(--radius-xs)",
                  cursor: "pointer",
                  background: idx === selectedIndex ? "var(--bg-subtle)" : "transparent",
                  border: idx === selectedIndex ? "1px solid var(--border-medium)" : "1px solid transparent",
                }}
                onMouseEnter={() => setSelectedIndex(idx)}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.background = "transparent";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", minWidth: 0 }}>
                  <span
                    className="tactile-pill"
                    style={{ fontSize: "0.66rem", padding: "1px 6px" }}
                  >
                    {item.category}
                  </span>
                  <span
                    style={{
                      fontSize: "0.84rem",
                      fontWeight: 500,
                      color: "var(--text-primary)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {item.summary || item.original_filename}
                  </span>
                </div>
                <ArrowRight size={13} color="var(--text-muted)" style={{ flexShrink: 0 }} />
              </div>
            ))}
          </div>
        </div>

        {/* Footer info bar */}
        <div
          style={{
            padding: "0.6rem 1.25rem",
            background: "var(--bg-subtle)",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.72rem",
            color: "var(--text-muted)",
          }}
        >
          <span>Use ↵ to execute or select</span>
          <span>AURA Visual Memory 2.0</span>
        </div>
      </div>
    </div>
  );
}
