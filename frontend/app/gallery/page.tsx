"use client";
import React, { useState, useEffect, useMemo, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Search,
  Filter,
  Layers,
  Shield,
  Loader2,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  LayoutGrid,
  Grid,
  List,
  ArrowUpDown,
  Download,
  Laptop,
  Upload,
  Lock,
  Sparkles,
  RefreshCw,
  FileCode,
  Receipt,
  FileText,
  PieChart,
  MapPin,
  MessageSquare,
  UtensilsCrossed,
  Cpu,
  TerminalSquare,
  KeyRound,
  Compass,
  X,
} from "lucide-react";
import { getMemories, Memory, apiFetch } from "@/lib/api";
import MemoryCard from "@/components/MemoryCard";

const CONSTELLATIONS_LIST = [
  { id: "vision", label: "🛰️ Project Cartosat & Vision AI", color: "#D97757" },
  { id: "commerce", label: "🧾 Commerce & Hardware", color: "#B87B28" },
  { id: "security", label: "🔒 Security Vault", color: "#B83A2E" },
  { id: "culinary", label: "🍄 Culinary & Gastronomy", color: "#387B58" },
  { id: "travel", label: "🗺️ Transit & Travel", color: "#4A7C59" },
  { id: "comms", label: "💬 Communications", color: "#6366F1" },
  { id: "automotive", label: "🏎️ Automotive & Supercars", color: "#8B5CF6" },
  { id: "runtime", label: "⚡ Terminal & Runtime", color: "#E06C75" },
];

const CATEGORIES = [
  { id: "", label: "All Artifacts", icon: Layers },
  { id: "code", label: "Code & Software", icon: FileCode },
  { id: "research", label: "Research & AI", icon: Sparkles },
  { id: "chart", label: "Charts & Accuracy", icon: PieChart },
  { id: "dashboard", label: "Dashboards & Infra", icon: SlidersHorizontal },
  { id: "receipt", label: "Receipts & Finance", icon: Receipt },
  { id: "recipe", label: "Recipes & Culinary", icon: UtensilsCrossed },
  { id: "travel", label: "Travel & Boarding", icon: MapPin },
  { id: "conversation", label: "Chat & War Rooms", icon: MessageSquare },
  { id: "settings", label: "Security & Credentials", icon: KeyRound },
  { id: "document", label: "Documents & Notes", icon: FileText },
  { id: "product", label: "Hardware & Tech", icon: Cpu },
  { id: "terminal", label: "Terminal & Logs", icon: TerminalSquare },
];

const SENSITIVITY_OPTIONS = [
  { id: "", label: "All Privacy Tiers" },
  { id: "CRITICAL", label: "🔴 Critical (Shield Protected)" },
  { id: "SENSITIVE", label: "🟠 Sensitive Records" },
  { id: "PERSONAL", label: "🟡 Personal Data" },
  { id: "PUBLIC", label: "🟢 Public Artifacts" },
];

const SOURCE_OPTIONS = [
  { id: "", label: "All Sources" },
  { id: "desktop_capture", label: "📸 OS Desktop Captures (Ctrl+Shift+A)" },
  { id: "upload", label: "📁 Manual Web Uploads" },
];

const SORT_OPTIONS = [
  { id: "newest", label: "Newest First" },
  { id: "oldest", label: "Oldest First" },
  { id: "importance", label: "Highest Importance" },
  { id: "name", label: "Alphabetical (A-Z)" },
];

function GalleryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCategory = searchParams?.get("category") || "";
  const initialConstellation = searchParams?.get("constellation") || "";
  const initialSearch = searchParams?.get("search") || "";

  const [memories, setMemories] = useState<Memory[]>([]);
  const [total, setTotal] = useState(0);
  const [systemTotal, setSystemTotal] = useState(342);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(18);
  const [category, setCategory] = useState(initialCategory);
  const [constellation, setConstellation] = useState(initialConstellation);
  const [sensitivity, setSensitivity] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [search, setSearch] = useState(initialSearch);
  const [viewMode, setViewMode] = useState<"grid" | "compact" | "list">("grid");
  const [loading, setLoading] = useState(true);
  const [revealedIds, setRevealedIds] = useState<Set<string>>(new Set());

  // Fetch system-wide total stats on mount
  useEffect(() => {
    apiFetch("/api/stats")
      .then((data) => {
        if (data?.total_memories) setSystemTotal(data.total_memories);
      })
      .catch(() => {});
  }, []);

  // Polling interval: Auto-fetch new screenshots in real time without requiring manual refresh
  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      // Background silent refresh for live new captures
      getMemories({
        page,
        limit: perPage,
        category: category || undefined,
        constellation: constellation || undefined,
        sensitivity: sensitivity || undefined,
        source_type: sourceType || undefined,
        sort_by: sortBy || undefined,
        search: search || undefined,
      }).then((data) => {
        setMemories(data.items || []);
        setTotal(data.total || 0);
      }).catch(() => {});

      apiFetch("/api/stats")
        .then((data) => {
          if (data?.total_memories) setSystemTotal(data.total_memories);
        })
        .catch(() => {});
    }, 3500);

    return () => clearInterval(interval);
  }, [page, perPage, category, constellation, sensitivity, sourceType, sortBy, search]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await getMemories({
        page,
        limit: perPage,
        category: category || undefined,
        constellation: constellation || undefined,
        sensitivity: sensitivity || undefined,
        source_type: sourceType || undefined,
        sort_by: sortBy || undefined,
        search: search || undefined,
      });
      setMemories(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to load gallery:", err);
    } finally {
      setLoading(false);
    }
  };

  const clearAllFilters = () => {
    setCategory("");
    setConstellation("");
    setSensitivity("");
    setSourceType("");
    setSearch("");
    setPage(1);
  };

  const activeConstellationObj = useMemo(() => {
    if (!constellation) return null;
    return CONSTELLATIONS_LIST.find((c) => c.id === constellation) || null;
  }, [constellation]);

  const toggleReveal = (id: string) => {
    setRevealedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(memories, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `aura_gallery_export_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const totalPages = Math.ceil(total / perPage);
  const isFiltered = Boolean(category || constellation || sensitivity || sourceType || search);

  return (
    <div style={{ maxWidth: 1360, margin: "0 auto", padding: "2.5rem 2rem 5rem" }}>
      {/* Editorial Header */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
          marginBottom: "2rem",
          paddingBottom: "1.5rem",
          borderBottom: "1px solid var(--border-medium)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <h1
                style={{
                  fontFamily: "var(--font-serif)",
                  fontSize: "2.5rem",
                  fontWeight: 500,
                  color: "var(--text-primary)",
                  letterSpacing: "-0.025em",
                }}
              >
                Knowledge Gallery
              </h1>
              <span className="badge badge-system" style={{ fontSize: "0.78rem", padding: "3px 8px" }}>
                {systemTotal} Total Artifacts
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: 4 }}>
              <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)" }}>
                {isFiltered ? (
                  <span>
                    Showing <strong style={{ color: "var(--text-primary)" }}>{total}</strong> of <strong style={{ color: "var(--text-primary)" }}>{systemTotal}</strong> indexed screenshots
                    {activeConstellationObj && (
                      <span style={{ marginLeft: 6 }}>
                        • Filtered by <strong style={{ color: activeConstellationObj.color }}>{activeConstellationObj.label}</strong>
                      </span>
                    )}
                    {category && (
                      <span style={{ marginLeft: 6 }}>
                        • Category: <strong style={{ color: "var(--accent-terracotta)" }}>{category.toUpperCase()}</strong>
                      </span>
                    )}
                  </span>
                ) : (
                  <span>Explore, filter, and inspect your unified visual memory index ({systemTotal} total indexed screenshots)</span>
                )}
              </p>

              {isFiltered && (
                <button
                  onClick={clearAllFilters}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.25rem",
                    fontSize: "0.76rem",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: "var(--accent-light)",
                    color: "var(--accent-dark)",
                    border: "1px solid var(--accent-border)",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  <X size={12} />
                  <span>Clear Filter (View All {systemTotal})</span>
                </button>
              )}
            </div>
          </div>

          {/* Top Actions: Export, Constellation Map, Upload */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <button
              onClick={() => router.push("/constellation")}
              className="btn-paper"
              title="Open Interactive Constellation Map"
              style={{ fontSize: "0.82rem", padding: "0.45rem 0.85rem", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
            >
              <Compass size={14} color="var(--accent-terracotta)" />
              <span>Constellation Map</span>
            </button>
            <button
              onClick={handleExportJSON}
              className="btn-paper"
              title="Export visible memory metadata as JSON"
              style={{ fontSize: "0.82rem", padding: "0.45rem 0.85rem" }}
            >
              <Download size={14} />
              <span>Export JSON</span>
            </button>
            <button
              onClick={() => router.push("/upload")}
              className="btn-paper"
              style={{
                fontSize: "0.82rem",
                padding: "0.45rem 0.85rem",
                background: "var(--accent-terracotta)",
                color: "#ffffff",
                borderColor: "var(--accent-terracotta)",
              }}
            >
              <Upload size={14} />
              <span>Upload Screenshots</span>
            </button>
          </div>
        </div>

        {/* Primary Row: 12 Category Filters */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", overflowX: "auto", paddingBottom: "0.25rem" }}>
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const active = (!category && !constellation && cat.id === "") || category === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => {
                  setCategory(cat.id);
                  setConstellation(""); // Clear constellation when picking a specific category
                  setPage(1);
                }}
                className={`tactile-pill ${active ? "tactile-pill-active" : ""}`}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.4rem",
                  fontSize: "0.82rem",
                  padding: "0.4rem 0.85rem",
                  whiteSpace: "nowrap",
                }}
              >
                <Icon size={14} />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Secondary Row: Deep Filtering Controls */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "0.85rem",
            padding: "0.75rem 1rem",
            background: "var(--bg-paper-subtle)",
            borderRadius: "12px",
            border: "1px solid var(--border-medium)",
          }}
        >
          {/* Left filters: Search, Constellation, Privacy Tier, Source */}
          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.75rem", flex: 1 }}>
            {/* Search Input */}
            <div style={{ position: "relative", width: 220, minWidth: 170 }}>
              <div style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                <Search size={14} />
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                placeholder="Filter by keyword / entity..."
                className="editorial-input"
                style={{
                  width: "100%",
                  padding: "0.4rem 0.75rem 0.4rem 2rem",
                  fontSize: "0.82rem",
                  background: "var(--bg-surface)",
                }}
              />
              {search && (
                <button
                  onClick={() => setSearch("")}
                  style={{ position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                >
                  <X size={12} />
                </button>
              )}
            </div>

            {/* Constellation Selector */}
            <select
              value={constellation}
              onChange={(e) => {
                setConstellation(e.target.value);
                setCategory("");
                setPage(1);
              }}
              className="editorial-select"
              style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem", background: "var(--bg-surface)" }}
            >
              <option value="">🌌 All 8 Constellations</option>
              {CONSTELLATIONS_LIST.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>

            {/* Privacy Tier Filter */}
            <select
              value={sensitivity}
              onChange={(e) => {
                setSensitivity(e.target.value);
                setPage(1);
              }}
              className="editorial-select"
              style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem", background: "var(--bg-surface)" }}
            >
              {SENSITIVITY_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* Source Type Filter */}
            <select
              value={sourceType}
              onChange={(e) => {
                setSourceType(e.target.value);
                setPage(1);
              }}
              className="editorial-select"
              style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem", background: "var(--bg-surface)" }}
            >
              {SOURCE_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Right controls: Sort By, View Mode Switcher */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            {/* Sort Order */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <ArrowUpDown size={13} color="var(--text-secondary)" />
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="editorial-select"
                style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem", background: "var(--bg-surface)" }}
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* View Mode Toggle: Grid, Compact, List */}
            <div style={{ display: "flex", background: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--border-medium)", padding: 2 }}>
              <button
                onClick={() => setViewMode("grid")}
                title="Comfortable Grid View"
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  background: viewMode === "grid" ? "var(--bg-subtle)" : "transparent",
                  color: viewMode === "grid" ? "var(--text-primary)" : "var(--text-muted)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <LayoutGrid size={15} />
              </button>
              <button
                onClick={() => setViewMode("compact")}
                title="Dense Compact Grid"
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  background: viewMode === "compact" ? "var(--bg-subtle)" : "transparent",
                  color: viewMode === "compact" ? "var(--text-primary)" : "var(--text-muted)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <Grid size={15} />
              </button>
              <button
                onClick={() => setViewMode("list")}
                title="List View"
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  background: viewMode === "list" ? "var(--bg-subtle)" : "transparent",
                  color: viewMode === "list" ? "var(--text-primary)" : "var(--text-muted)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <List size={15} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Gallery Content State ────────────────────────────────────────────── */}
      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 380, gap: "1rem" }}>
          <Loader2 size={32} color="var(--accent-terracotta)" className="animate-spin" />
          <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.15rem", color: "var(--text-secondary)" }}>
            Loading visual memories from system of record...
          </span>
        </div>
      ) : memories.length === 0 ? (
        <div
          className="paper-card"
          style={{
            padding: "4rem 2rem",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "1rem",
            maxWidth: 600,
            margin: "2rem auto",
          }}
        >
          <div style={{ width: 56, height: 56, borderRadius: "50%", background: "var(--bg-subtle)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Layers size={26} color="var(--text-muted)" />
          </div>
          <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.35rem", fontWeight: 600, color: "var(--text-primary)" }}>
            No visual memories match your filter
          </h3>
          <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: 1.5, maxWidth: 420 }}>
            {isFiltered ? "Try resetting your active category, constellation, or search filters." : "Your visual memory database is currently empty. Ingest screenshots to populate the index."}
          </p>
          {isFiltered && (
            <button
              onClick={clearAllFilters}
              className="btn-paper"
              style={{ fontSize: "0.85rem", padding: "0.5rem 1.25rem", background: "var(--accent-terracotta)", color: "#ffffff", borderColor: "var(--accent-terracotta)" }}
            >
              Clear All Filters (View All {systemTotal})
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Main Grid View */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                viewMode === "grid"
                  ? "repeat(auto-fill, minmax(290px, 1fr))"
                  : viewMode === "compact"
                  ? "repeat(auto-fill, minmax(210px, 1fr))"
                  : "1fr",
              gap: viewMode === "compact" ? "1rem" : "1.5rem",
              marginBottom: "3rem",
            }}
          >
            {memories.map((m) => (
              <MemoryCard
                key={m.id}
                memory={m}
                isRevealed={revealedIds.has(m.id)}
                onToggleReveal={() => toggleReveal(m.id)}
              />
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "1rem",
                padding: "1.25rem 0",
                borderTop: "1px solid var(--border-medium)",
              }}
            >
              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Showing {(page - 1) * perPage + 1}–{Math.min(page * perPage, total)} of {total} items
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-paper"
                  style={{ padding: "0.4rem 0.75rem", fontSize: "0.82rem", opacity: page === 1 ? 0.5 : 1 }}
                >
                  <ChevronLeft size={14} />
                  <span>Previous</span>
                </button>

                <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)", padding: "0 0.5rem" }}>
                  Page {page} of {totalPages}
                </span>

                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-paper"
                  style={{ padding: "0.4rem 0.75rem", fontSize: "0.82rem", opacity: page === totalPages ? 0.5 : 1 }}
                >
                  <span>Next</span>
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function GalleryPage() {
  return (
    <Suspense
      fallback={
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 400, color: "var(--text-secondary)" }}>
          <Loader2 size={28} color="var(--accent-terracotta)" className="animate-spin" />
        </div>
      }
    >
      <GalleryContent />
    </Suspense>
  );
}
