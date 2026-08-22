"use client";
import React, { useState, useEffect, useRef, useMemo, useCallback } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  Lock,
  X,
  ExternalLink,
  Shield,
  Loader2,
  Eye,
  Grid,
  Search,
  Compass,
  Layers,
  ChevronRight,
  Maximize2,
  FolderOpen,
  Sliders,
  Activity,
  Cpu,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Target,
  Share2,
  Info,
  Radio,
  Sun,
  Moon,
  LayoutGrid,
} from "lucide-react";
import { apiFetch, getThumbnailUrl, Memory } from "@/lib/api";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-secondary)", background: "var(--bg-canvas)" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.85rem" }}>
        <Loader2 size={28} color="var(--accent-terracotta)" className="animate-spin" />
        <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.1rem", fontWeight: 500, color: "var(--text-primary)" }}>
          Initializing Gravitational Force Graph & Multi-Signal Edges...
        </span>
      </div>
    </div>
  ),
});

interface ConstellationMeta {
  id: string;
  constellation_key: string;
  name: string;
  icon: string;
  color: string;
  description: string;
}

const EDGE_TYPE_CONFIG: Record<string, { label: string; colorLight: string; colorDark: string; borderLight: string; borderDark: string }> = {
  SAME_PROJECT: { label: "Same Project", colorLight: "#4F46E5", colorDark: "#818cf8", borderLight: "rgba(79, 70, 229, 0.4)", borderDark: "rgba(129, 140, 248, 0.4)" },
  SAME_ENTITY: { label: "Same Entity", colorLight: "#059669", colorDark: "#34d399", borderLight: "rgba(5, 150, 105, 0.4)", borderDark: "rgba(52, 211, 153, 0.4)" },
  SAME_TOPIC: { label: "Same Topic", colorLight: "#D97706", colorDark: "#fbbf24", borderLight: "rgba(217, 119, 6, 0.4)", borderDark: "rgba(251, 191, 36, 0.4)" },
  SEMANTICALLY_RELATED: { label: "Semantic Similarity", colorLight: "#0284C7", colorDark: "#38bdf8", borderLight: "rgba(2, 132, 199, 0.4)", borderDark: "rgba(56, 189, 248, 0.4)" },
  TEMPORALLY_RELATED: { label: "Temporal Proximity", colorLight: "#E11D48", colorDark: "#fb7185", borderLight: "rgba(225, 29, 72, 0.4)", borderDark: "rgba(251, 113, 133, 0.4)" },
  DERIVED_FROM: { label: "Causal Lineage", colorLight: "#7C3AED", colorDark: "#c084fc", borderLight: "rgba(124, 58, 237, 0.4)", borderDark: "rgba(192, 132, 252, 0.4)" },
  constellation_member: { label: "Galaxy Orbit", colorLight: "rgba(111, 106, 99, 0.25)", colorDark: "rgba(148, 163, 184, 0.25)", borderLight: "rgba(111, 106, 99, 0.15)", borderDark: "rgba(148, 163, 184, 0.15)" },
};

export default function ConstellationPage() {
  const [constellations, setConstellations] = useState<ConstellationMeta[]>([]);
  const [rawNodes, setRawNodes] = useState<any[]>([]);
  const [rawLinks, setRawLinks] = useState<any[]>([]);
  const [selectedConstellationKey, setSelectedConstellationKey] = useState<string>("");
  const [selectedEdgeType, setSelectedEdgeType] = useState<string>("ALL");
  const [minConfidence, setMinConfidence] = useState<number>(0.60);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [drawerSearch, setDrawerSearch] = useState<string>("");
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [hoverNode, setHoverNode] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [revealedIds, setRevealedIds] = useState<Set<string>>(new Set());
  const [isDarkMode, setIsDarkMode] = useState(false); // Default to App's Warm Editorial Parchment Theme!
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const graphRef = useRef<any>(null);
  const router = useRouter();

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/api/constellation");
      setConstellations(data.constellations || []);

      const nodes = (data.nodes || []).map((n: any) => ({
        ...n,
        name: n.name || n.label || "Artifact",
        label: n.name || n.label || "Artifact",
        val: n.is_hub ? 16 : 5.0,
      }));

      const links = (data.edges || data.links || []).map((l: any) => ({
        id: l.id || `${l.source}-${l.target}`,
        source: typeof l.source === "object" ? l.source.id : l.source,
        target: typeof l.target === "object" ? l.target.id : l.target,
        type: l.type || "SEMANTICALLY_RELATED",
        confidence: l.confidence ?? 0.8,
        reason: l.reason || "Connected by multimodal similarity",
        is_hub_edge: Boolean(l.is_hub_edge),
      }));

      setRawNodes(nodes);
      setRawLinks(links);
    } catch (err) {
      console.error("Failed to load constellation:", err);
    } finally {
      setLoading(false);
    }
  };

  // Filtered graph data based on confidence threshold, edge type, and constellation selection
  const filteredGraphData = useMemo(() => {
    let nodes = [...rawNodes];
    let links = [...rawLinks];

    // Filter links by confidence and edge type
    links = links.filter((l) => {
      if (l.is_hub_edge) return true;
      if (l.confidence < minConfidence) return false;
      if (selectedEdgeType !== "ALL" && l.type !== selectedEdgeType) return false;
      return true;
    });

    // If specific constellation is selected, focus those nodes
    if (selectedConstellationKey) {
      const allowedHubId = `hub_${selectedConstellationKey}`;
      const relevantNodeIds = new Set<string>();
      relevantNodeIds.add(allowedHubId);

      nodes.forEach((n) => {
        if (n.constellation_key === selectedConstellationKey) {
          relevantNodeIds.add(n.id);
        }
      });

      links = links.filter(
        (l) =>
          relevantNodeIds.has(typeof l.source === "object" ? l.source.id : l.source) &&
          relevantNodeIds.has(typeof l.target === "object" ? l.target.id : l.target)
      );
    }

    return { nodes, links };
  }, [rawNodes, rawLinks, minConfidence, selectedEdgeType, selectedConstellationKey]);

  // Graph Telemetry Stats
  const graphStats = useMemo(() => {
    const N = filteredGraphData.nodes.length;
    const E = filteredGraphData.links.length;
    const avgDegree = N > 0 ? ((2 * E) / N).toFixed(1) : "0.0";
    return {
      nodesCount: N,
      edgesCount: E,
      avgDegree,
      clustersCount: constellations.length || 8,
      density: N > 1 ? ((2 * E) / (N * (N - 1))).toFixed(4) : "0.0000",
    };
  }, [filteredGraphData, constellations]);

  // Active Constellation Metadata (from selected constellation or selected node's constellation)
  const activeConstellation = useMemo(() => {
    if (selectedConstellationKey) {
      return constellations.find((c) => c.constellation_key === selectedConstellationKey) || null;
    }
    if (selectedNode) {
      const key = selectedNode.constellation_key;
      return constellations.find((c) => c.constellation_key === key) || null;
    }
    return null;
  }, [selectedNode, selectedConstellationKey, constellations]);

  // All memory artifacts belonging to the active constellation
  const constellationMemories = useMemo(() => {
    if (!activeConstellation) return [];
    let items = rawNodes.filter(
      (n) => !n.is_hub && n.constellation_key === activeConstellation.constellation_key
    );
    if (drawerSearch.trim()) {
      const q = drawerSearch.toLowerCase();
      items = items.filter(
        (n) =>
          n.name.toLowerCase().includes(q) ||
          n.summary?.toLowerCase().includes(q) ||
          n.category?.toLowerCase().includes(q)
      );
    }
    return items;
  }, [activeConstellation, rawNodes, drawerSearch]);

  // Directly connected neighbors for selected node (Neighbor Radar)
  const nodeNeighbors = useMemo(() => {
    if (!selectedNode || selectedNode.is_hub) return [];
    const nodeId = selectedNode.id;
    const neighbors: Array<{ node: any; edge: any }> = [];

    const seenIds = new Set<string>();
    rawLinks.forEach((l) => {
      const srcId = typeof l.source === "object" ? l.source.id : l.source;
      const tgtId = typeof l.target === "object" ? l.target.id : l.target;

      if (srcId === nodeId && tgtId !== nodeId && !seenIds.has(tgtId)) {
        const neighborNode = rawNodes.find((n) => n.id === tgtId);
        if (neighborNode && !neighborNode.is_hub) {
          seenIds.add(tgtId);
          neighbors.push({ node: neighborNode, edge: l });
        }
      } else if (tgtId === nodeId && srcId !== nodeId && !seenIds.has(srcId)) {
        const neighborNode = rawNodes.find((n) => n.id === srcId);
        if (neighborNode && !neighborNode.is_hub) {
          seenIds.add(srcId);
          neighbors.push({ node: neighborNode, edge: l });
        }
      }
    });

    return neighbors.sort((a, b) => (b.edge.confidence || 0) - (a.edge.confidence || 0));
  }, [selectedNode, rawLinks, rawNodes]);

  // Tapping a Constellation: Centers camera, sets active key, and opens its Gallery!
  const handleSelectConstellation = (key: string) => {
    setSelectedConstellationKey(key);
    setDrawerSearch("");
    if (!key) {
      setSelectedNode(null);
      if (graphRef.current) {
        graphRef.current.zoomToFit(700, 50);
      }
      return;
    }

    const hubNode = rawNodes.find((n) => n.is_hub && n.constellation_key === key);
    if (hubNode && graphRef.current) {
      setSelectedNode(hubNode);
      graphRef.current.centerAt(hubNode.x, hubNode.y, 700);
      graphRef.current.zoom(2.2, 700);
    }
  };

  const handleNodeClick = useCallback(
    (node: any) => {
      setSelectedNode(node);
      if (node.is_hub && node.constellation_key) {
        setSelectedConstellationKey(node.constellation_key);
      }
      if (graphRef.current && typeof node.x === "number" && typeof node.y === "number") {
        graphRef.current.centerAt(node.x, node.y, 600);
        graphRef.current.zoom(2.4, 600);
      }
    },
    []
  );

  const handleZoom = (factor: number) => {
    if (graphRef.current) {
      const currentZoom = graphRef.current.zoom();
      graphRef.current.zoom(currentZoom * factor, 400);
    }
  };

  const handleResetView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(700, 50);
      setSelectedNode(null);
      setSelectedConstellationKey("");
    }
  };

  const toggleReveal = (id: string) => {
    setRevealedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // Color Tokens based on active theme
  const theme = useMemo(() => {
    if (isDarkMode) {
      return {
        bgCanvas: "#070B14",
        bgSurface: "rgba(15, 23, 42, 0.92)",
        bgSubtle: "rgba(30, 41, 59, 0.7)",
        bgTopBar: "rgba(11, 15, 25, 0.95)",
        textPrimary: "#F8FAFC",
        textSecondary: "#94A3B8",
        textMuted: "#64748B",
        border: "rgba(51, 65, 85, 0.6)",
        cardBorder: "rgba(51, 65, 85, 0.7)",
        canvasBackground: "#070B14",
        badgeBg: "rgba(56, 189, 248, 0.15)",
        badgeText: "#38BDF8",
        accent: "#38BDF8",
      };
    }
    return {
      bgCanvas: "var(--bg-canvas)",
      bgSurface: "var(--bg-surface)",
      bgSubtle: "var(--bg-subtle)",
      bgTopBar: "var(--bg-surface)",
      textPrimary: "var(--text-primary)",
      textSecondary: "var(--text-secondary)",
      textMuted: "var(--text-muted)",
      border: "var(--border-medium)",
      cardBorder: "var(--border-medium)",
      canvasBackground: "#F7F4EE",
      badgeBg: "var(--accent-light)",
      badgeText: "var(--accent-terracotta)",
      accent: "var(--accent-terracotta)",
    };
  }, [isDarkMode]);

  return (
    <div style={{ height: "calc(100vh - 1px)", display: "flex", flexDirection: "column", background: theme.bgCanvas, color: theme.textPrimary, overflow: "hidden" }}>
      {/* ── Editorial Top Bar with Constellation Switchers & Theme Mode ────────── */}
      <div
        style={{
          padding: "1rem 2rem",
          background: theme.bgTopBar,
          borderBottom: `1px solid ${theme.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "1rem",
          zIndex: 20,
          boxShadow: isDarkMode ? "none" : "var(--shadow-paper)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: "10px",
              background: isDarkMode ? "linear-gradient(135deg, #38bdf8 0%, #818cf8 100%)" : "var(--accent-terracotta)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: isDarkMode ? "0 0 20px rgba(56, 189, 248, 0.35)" : "var(--shadow-card)",
            }}
          >
            <Compass size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <h1 style={{ fontFamily: "var(--font-serif)", fontSize: "1.5rem", fontWeight: 500, color: theme.textPrimary, letterSpacing: "-0.02em" }}>
                Memory Constellations
              </h1>
              <span
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: "9999px",
                  background: theme.badgeBg,
                  color: theme.badgeText,
                  border: `1px solid ${theme.badgeText}33`,
                }}
              >
                CELESTIAL TOPOLOGY
              </span>
            </div>
            <p style={{ fontSize: "0.82rem", color: theme.textSecondary, marginTop: 2 }}>
              Tap any constellation to open its dedicated visual memory gallery & associative connections
            </p>
          </div>
        </div>

        {/* 8 Constellation Switchers + Theme Toggle */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", alignItems: "center" }}>
          {/* Theme Mode Switcher */}
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            title={isDarkMode ? "Switch to Editorial Warm Paper" : "Switch to Celestial Night Sky"}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              padding: "5px 12px",
              borderRadius: "9999px",
              background: theme.bgSubtle,
              color: theme.textPrimary,
              border: `1px solid ${theme.border}`,
              cursor: "pointer",
              marginRight: 6,
            }}
          >
            {isDarkMode ? <Sun size={13} color="#facc15" /> : <Moon size={13} color="var(--accent-terracotta)" />}
            <span>{isDarkMode ? "Night Sky" : "Warm Paper"}</span>
          </button>

          <button
            onClick={() => handleSelectConstellation("")}
            className={`tactile-pill ${!selectedConstellationKey ? "tactile-pill-active" : ""}`}
            style={{
              fontSize: "0.74rem",
              padding: "5px 12px",
              background: !selectedConstellationKey ? (isDarkMode ? "#38bdf8" : "var(--accent-terracotta)") : undefined,
              color: !selectedConstellationKey ? "#ffffff" : undefined,
            }}
          >
            🌌 All 8 Constellations
          </button>
          {constellations.map((c) => {
            const active = selectedConstellationKey === c.constellation_key;
            return (
              <button
                key={c.id}
                onClick={() => handleSelectConstellation(c.constellation_key)}
                className={`tactile-pill ${active ? "tactile-pill-active" : ""}`}
                style={{
                  fontSize: "0.74rem",
                  padding: "5px 12px",
                  borderColor: active ? c.color : undefined,
                  color: active ? c.color : undefined,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  boxShadow: active ? `0 0 10px ${c.color}33` : "none",
                }}
              >
                <span>{c.icon}</span>
                <span>{c.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Sub-Header Controls & Relationship Filter Matrix ─────────────────── */}
      <div
        style={{
          padding: "0.65rem 2rem",
          background: isDarkMode ? "rgba(15, 23, 42, 0.85)" : "var(--bg-subtle)",
          borderBottom: `1px solid ${theme.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "0.75rem",
          zIndex: 15,
        }}
      >
        {/* Edge Relationship Type Filter Matrix */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.72rem", color: theme.textSecondary, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginRight: 4 }}>
            Edge Filter:
          </span>
          <button
            onClick={() => setSelectedEdgeType("ALL")}
            style={{
              fontSize: "0.7rem",
              fontWeight: 600,
              padding: "3px 9px",
              borderRadius: "6px",
              background: selectedEdgeType === "ALL" ? (isDarkMode ? "rgba(56, 189, 248, 0.2)" : "var(--accent-light)") : "transparent",
              color: selectedEdgeType === "ALL" ? (isDarkMode ? "#38bdf8" : "var(--accent-terracotta)") : theme.textSecondary,
              border: `1px solid ${selectedEdgeType === "ALL" ? (isDarkMode ? "#38bdf8" : "var(--accent-terracotta)") : theme.border}`,
              cursor: "pointer",
            }}
          >
            All Edges
          </button>
          {Object.entries(EDGE_TYPE_CONFIG).map(([typeKey, cfg]) => {
            if (typeKey === "constellation_member") return null;
            const isAct = selectedEdgeType === typeKey;
            const activeColor = isDarkMode ? cfg.colorDark : cfg.colorLight;
            return (
              <button
                key={typeKey}
                onClick={() => setSelectedEdgeType(typeKey)}
                style={{
                  fontSize: "0.7rem",
                  fontWeight: 600,
                  padding: "3px 9px",
                  borderRadius: "6px",
                  background: isAct ? `${activeColor}22` : "transparent",
                  color: isAct ? activeColor : theme.textSecondary,
                  border: `1px solid ${isAct ? activeColor : theme.border}`,
                  cursor: "pointer",
                }}
              >
                ● {cfg.label}
              </button>
            );
          })}
        </div>

        {/* Confidence Slider & Quick Graph Search */}
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          {/* Confidence Slider */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.72rem", color: theme.textSecondary, fontWeight: 600 }}>
              Min Confidence: <span style={{ color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)", fontFamily: "var(--font-mono)", fontWeight: 700 }}>{(minConfidence * 100).toFixed(0)}%</span>
            </span>
            <input
              type="range"
              min="0.50"
              max="0.95"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              style={{ width: 90, accentColor: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)", cursor: "pointer" }}
            />
          </div>

          {/* Quick Node Search */}
          <div style={{ position: "relative", width: 220 }}>
            <Search size={13} style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", color: theme.textMuted }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Highlight memory..."
              className="editorial-input"
              style={{
                width: "100%",
                padding: "3px 8px 3px 26px",
                fontSize: "0.75rem",
                background: theme.bgSurface,
                border: `1px solid ${theme.border}`,
                borderRadius: "6px",
                color: theme.textPrimary,
                outline: "none",
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                style={{ position: "absolute", right: 6, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", color: theme.textMuted, cursor: "pointer" }}
              >
                <X size={12} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Main Canvas Viewport ─────────────────────────────────────────────── */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden", background: theme.canvasBackground }}>
        {loading && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: isDarkMode ? "rgba(7, 11, 20, 0.85)" : "rgba(247, 244, 238, 0.85)",
              backdropFilter: "blur(8px)",
              zIndex: 30,
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.85rem" }}>
              <Loader2 size={32} color={isDarkMode ? "#38bdf8" : "var(--accent-terracotta)"} className="animate-spin" />
              <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.1rem", color: theme.textPrimary, fontWeight: 500 }}>
                Computing gravitational layout across 342 multimodal memories...
              </span>
            </div>
          </div>
        )}

        {/* ── Floating Navigation Controls HUD ── */}
        <div
          style={{
            position: "absolute",
            bottom: 20,
            left: 20,
            display: "flex",
            flexDirection: "column",
            gap: "0.4rem",
            background: theme.bgSurface,
            backdropFilter: "blur(12px)",
            padding: "0.4rem",
            borderRadius: "10px",
            border: `1px solid ${theme.border}`,
            zIndex: 10,
            boxShadow: isDarkMode ? "0 8px 32px rgba(0,0,0,0.5)" : "var(--shadow-card)",
          }}
        >
          <button
            onClick={() => handleZoom(1.3)}
            title="Zoom In"
            style={{ background: theme.bgSubtle, border: `1px solid ${theme.border}`, color: theme.textPrimary, padding: "6px", borderRadius: "6px", cursor: "pointer" }}
          >
            <ZoomIn size={16} />
          </button>
          <button
            onClick={() => handleZoom(0.7)}
            title="Zoom Out"
            style={{ background: theme.bgSubtle, border: `1px solid ${theme.border}`, color: theme.textPrimary, padding: "6px", borderRadius: "6px", cursor: "pointer" }}
          >
            <ZoomOut size={16} />
          </button>
          <button
            onClick={handleResetView}
            title="Reset View / Center"
            style={{ background: theme.bgSubtle, border: `1px solid ${theme.border}`, color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)", padding: "6px", borderRadius: "6px", cursor: "pointer" }}
          >
            <Target size={16} />
          </button>
        </div>

        {/* ── Engineering Telemetry HUD Box (Top Left) ── */}
        <div
          style={{
            position: "absolute",
            top: 16,
            left: 16,
            background: theme.bgSurface,
            backdropFilter: "blur(12px)",
            padding: "0.85rem 1.1rem",
            borderRadius: "12px",
            border: `1px solid ${theme.border}`,
            zIndex: 10,
            boxShadow: isDarkMode ? "0 8px 32px rgba(0,0,0,0.4)" : "var(--shadow-card)",
            minWidth: 210,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <Activity size={14} color={isDarkMode ? "#38bdf8" : "var(--accent-terracotta)"} />
              <span style={{ fontSize: "0.74rem", fontWeight: 700, color: theme.textPrimary, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Graph Telemetry
              </span>
            </div>
            <span style={{ fontSize: "0.68rem", color: "#10b981", fontWeight: 700 }}>● OPTIMAL</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.4rem 0.8rem", fontSize: "0.74rem" }}>
            <div>
              <span style={{ color: theme.textMuted }}>Nodes (N):</span>
              <span style={{ color: theme.textPrimary, fontWeight: 700, marginLeft: 4, fontFamily: "var(--font-mono)" }}>{graphStats.nodesCount}</span>
            </div>
            <div>
              <span style={{ color: theme.textMuted }}>Edges (E):</span>
              <span style={{ color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)", fontWeight: 700, marginLeft: 4, fontFamily: "var(--font-mono)" }}>{graphStats.edgesCount}</span>
            </div>
            <div>
              <span style={{ color: theme.textMuted }}>Avg Degree:</span>
              <span style={{ color: theme.textPrimary, fontWeight: 700, marginLeft: 4, fontFamily: "var(--font-mono)" }}>{graphStats.avgDegree}</span>
            </div>
            <div>
              <span style={{ color: theme.textMuted }}>Density:</span>
              <span style={{ color: "#818cf8", fontWeight: 700, marginLeft: 4, fontFamily: "var(--font-mono)" }}>{graphStats.density}</span>
            </div>
          </div>
        </div>

        {/* ── 2D Force Graph Component ──────────────────────────────────────── */}
        <ForceGraph2D
          ref={graphRef}
          graphData={filteredGraphData}
          backgroundColor={theme.canvasBackground}
          nodeVal={(n: any) => n.val || 5.0}
          nodeColor={(n: any) => n.color}
          linkColor={(l: any) => {
            if (l.is_hub_edge) return isDarkMode ? "rgba(148, 163, 184, 0.12)" : "rgba(111, 106, 99, 0.12)";
            const cfg = EDGE_TYPE_CONFIG[l.type];
            if (cfg) return isDarkMode ? cfg.borderDark : cfg.borderLight;
            return isDarkMode ? "rgba(56, 189, 248, 0.25)" : "rgba(217, 119, 87, 0.25)";
          }}
          linkWidth={(l: any) => (l.is_hub_edge ? 1.0 : Math.max(1, (l.confidence || 0.8) * 2.2))}
          linkDirectionalParticles={(l: any) => (l.is_hub_edge ? 0 : 2)}
          linkDirectionalParticleSpeed={0.005}
          linkDirectionalParticleWidth={2.2}
          linkDirectionalParticleColor={(l: any) => {
            const cfg = EDGE_TYPE_CONFIG[l.type];
            if (cfg) return isDarkMode ? cfg.colorDark : cfg.colorLight;
            return isDarkMode ? "#38bdf8" : "#D97757";
          }}
          onNodeClick={handleNodeClick}
          onNodeHover={(n: any) => setHoverNode(n)}
          cooldownTicks={120}
          d3AlphaDecay={0.015}
          d3VelocityDecay={0.22}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            if (!node || typeof node.x !== "number" || typeof node.y !== "number" || !isFinite(node.x) || !isFinite(node.y)) {
              return;
            }
            const isSelected = selectedNode && selectedNode.id === node.id;
            const isHovered = hoverNode && hoverNode.id === node.id;
            const isHub = node.is_hub;
            const label = node.name || node.label || "";
            const isQueryMatch = searchQuery && label.toLowerCase().includes(searchQuery.toLowerCase());

            const radius = (node.val || 5.0) + (isSelected ? 3.5 : isHovered ? 2 : 0);

            if (isHub) {
              // ── Hub Celestial Star ──
              const glowRadius = radius * 2.8;
              const grad = ctx.createRadialGradient(node.x, node.y, radius * 0.2, node.x, node.y, glowRadius);
              grad.addColorStop(0, node.color || "#D97757");
              grad.addColorStop(0.4, isDarkMode ? `${node.color}55` : "rgba(217, 119, 87, 0.25)");
              grad.addColorStop(1, "rgba(0,0,0,0)");

              ctx.beginPath();
              ctx.arc(node.x, node.y, glowRadius, 0, 2 * Math.PI, false);
              ctx.fillStyle = grad;
              ctx.fill();

              // Solid Inner Core
              ctx.beginPath();
              ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
              ctx.fillStyle = node.color || "#D97757";
              ctx.fill();

              // Shimmering Golden/White Border
              ctx.strokeStyle = "#ffffff";
              ctx.lineWidth = 2.5 / globalScale;
              ctx.stroke();

              // Hub Name Label Tag
              const fontSize = Math.max(13 / Math.pow(globalScale, 0.65), 5);
              ctx.font = `700 ${fontSize}px Inter, sans-serif`;
              const textWidth = ctx.measureText(label).width;
              const padX = 8 / globalScale;
              const padY = 4 / globalScale;
              const bckgW = textWidth + padX * 2;
              const bckgH = fontSize + padY * 2;

              ctx.fillStyle = isDarkMode ? "rgba(7, 11, 20, 0.95)" : "rgba(255, 255, 255, 0.98)";
              ctx.fillRect(node.x - bckgW / 2, node.y + radius + 4 / globalScale, bckgW, bckgH);
              ctx.strokeStyle = node.color || "var(--accent-terracotta)";
              ctx.lineWidth = 1.2 / globalScale;
              ctx.strokeRect(node.x - bckgW / 2, node.y + radius + 4 / globalScale, bckgW, bckgH);

              ctx.textAlign = "center";
              ctx.textBaseline = "middle";
              ctx.fillStyle = isDarkMode ? "#ffffff" : "#1F1D1A";
              ctx.fillText(label, node.x, node.y + radius + 4 / globalScale + bckgH / 2);
            } else {
              // ── Memory Satellite Star ──
              if (isQueryMatch) {
                // Bright pulsing search reticle
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius * 2.5, 0, 2 * Math.PI, false);
                ctx.fillStyle = isDarkMode ? "rgba(250, 204, 21, 0.35)" : "rgba(217, 119, 87, 0.3)";
                ctx.fill();
                ctx.strokeStyle = isDarkMode ? "#facc15" : "var(--accent-terracotta)";
                ctx.lineWidth = 2 / globalScale;
                ctx.stroke();
              }

              ctx.beginPath();
              ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
              ctx.fillStyle = node.color || "#9E988F";
              ctx.fill();

              if (isSelected || isHovered) {
                ctx.strokeStyle = isSelected ? (isDarkMode ? "#38bdf8" : "var(--accent-terracotta)") : "#ffffff";
                ctx.lineWidth = (isSelected ? 2.5 : 1.5) / globalScale;
                ctx.stroke();

                // Floating tooltip label
                const fontSize = Math.max(10 / Math.pow(globalScale, 0.65), 3.5);
                ctx.font = `600 ${fontSize}px Inter, sans-serif`;
                const textWidth = ctx.measureText(label).width;
                const padX = 6 / globalScale;
                const padY = 3 / globalScale;
                const bckgW = textWidth + padX * 2;
                const bckgH = fontSize + padY * 2;

                ctx.fillStyle = isSelected ? (isDarkMode ? "rgba(14, 165, 233, 0.95)" : "rgba(217, 119, 87, 0.95)") : (isDarkMode ? "rgba(15, 23, 42, 0.95)" : "rgba(255, 255, 255, 0.98)");
                ctx.fillRect(node.x - bckgW / 2, node.y + radius + 3 / globalScale, bckgW, bckgH);
                ctx.strokeStyle = isSelected ? (isDarkMode ? "#38bdf8" : "var(--accent-terracotta)") : (isDarkMode ? "rgba(148, 163, 184, 0.5)" : "var(--border-medium)");
                ctx.lineWidth = 1 / globalScale;
                ctx.strokeRect(node.x - bckgW / 2, node.y + radius + 3 / globalScale, bckgW, bckgH);

                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = isSelected ? "#ffffff" : (isDarkMode ? "#ffffff" : "#1F1D1A");
                ctx.fillText(label, node.x, node.y + radius + 3 / globalScale + bckgH / 2);
              }
            }
          }}
        />

        {/* ── Constellation Gallery Drawer / Inspector ───────────────────────── */}
        {activeConstellation && (
          <div
            className="paper-card"
            style={{
              position: "absolute",
              top: 16,
              right: 16,
              width: 480,
              maxHeight: "calc(100% - 32px)",
              overflowY: "auto",
              padding: "1.5rem",
              zIndex: 30,
              background: theme.bgSurface,
              borderRadius: "14px",
              border: `1.5px solid ${activeConstellation.color || theme.accent}`,
              boxShadow: isDarkMode ? "0 20px 50px rgba(0,0,0,0.6)" : "var(--shadow-floating)",
              display: "flex",
              flexDirection: "column",
              gap: "1.1rem",
            }}
          >
            {/* Constellation Header */}
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                <span style={{ fontSize: "1.8rem" }}>{activeConstellation.icon}</span>
                <div>
                  <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.35rem", fontWeight: 600, color: theme.textPrimary, letterSpacing: "-0.01em" }}>
                    {activeConstellation.name}
                  </h2>
                  <span style={{ fontSize: "0.75rem", color: activeConstellation.color, fontWeight: 700, textTransform: "uppercase" }}>
                    Constellation Cluster • {constellationMemories.length} Visual Artifacts
                  </span>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedNode(null);
                  setSelectedConstellationKey("");
                }}
                style={{ background: "none", border: "none", cursor: "pointer", color: theme.textMuted, padding: 4 }}
              >
                <X size={18} />
              </button>
            </div>

            <p style={{ fontSize: "0.84rem", color: theme.textSecondary, lineHeight: 1.45 }}>
              {activeConstellation.description}
            </p>

            {/* If a specific single memory is clicked, show its detailed inspector */}
            {selectedNode && !selectedNode.is_hub && (
              <div
                style={{
                  padding: "0.85rem",
                  background: theme.bgSubtle,
                  borderRadius: "10px",
                  border: `1px solid ${theme.border}`,
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.6rem",
                }}
              >
                <div style={{ display: "flex", gap: "0.85rem", alignItems: "center" }}>
                  <div style={{ width: 80, height: 60, borderRadius: "6px", overflow: "hidden", background: theme.bgCanvas, flexShrink: 0, position: "relative" }}>
                    <img
                      src={getThumbnailUrl(selectedNode.id)}
                      alt=""
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        filter: selectedNode.sensitivity_level === "CRITICAL" && !revealedIds.has(selectedNode.id) ? "blur(6px)" : "none",
                      }}
                    />
                    {selectedNode.sensitivity_level === "CRITICAL" && !revealedIds.has(selectedNode.id) && (
                      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.3)" }}>
                        <Lock size={12} color="#ffffff" />
                      </div>
                    )}
                  </div>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ fontSize: "0.88rem", fontWeight: 700, color: theme.textPrimary, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {selectedNode.name}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: theme.textSecondary, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {selectedNode.summary || "Visual memory artifact"}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem", marginTop: 4 }}>
                      <button
                        onClick={() => router.push(`/memory/${selectedNode.id}`)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                          fontSize: "0.74rem",
                          color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)",
                          fontWeight: 600,
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          padding: 0,
                        }}
                      >
                        <span>Inspect Artifact</span>
                        <ChevronRight size={12} />
                      </button>
                      <button
                        onClick={() => router.push(`/?investigate=${encodeURIComponent(selectedNode.name)}`)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                          fontSize: "0.74rem",
                          color: "#818cf8",
                          fontWeight: 600,
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          padding: 0,
                        }}
                      >
                        <Sparkles size={12} />
                        <span>AI Search</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Neighbor Radar preview if available */}
                {nodeNeighbors.length > 0 && (
                  <div style={{ borderTop: `1px solid ${theme.border}`, paddingTop: "0.5rem" }}>
                    <span style={{ fontSize: "0.7rem", fontWeight: 700, color: theme.textMuted, textTransform: "uppercase" }}>
                      Associated Neighbors ({nodeNeighbors.length}):
                    </span>
                    <div style={{ display: "flex", gap: "0.35rem", overflowX: "auto", marginTop: 4 }}>
                      {nodeNeighbors.slice(0, 4).map(({ node: n, edge: e }, idx) => (
                        <button
                          key={`${n.id}-${e.id || idx}`}
                          onClick={() => handleNodeClick(n)}
                          style={{
                            fontSize: "0.68rem",
                            padding: "3px 8px",
                            borderRadius: "6px",
                            background: theme.bgCanvas,
                            color: theme.textPrimary,
                            border: `1px solid ${theme.border}`,
                            cursor: "pointer",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {n.name} ({((e.confidence || 0.8) * 100).toFixed(0)}%)
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Search inside this constellation */}
            <div style={{ position: "relative" }}>
              <div style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: theme.textMuted }}>
                <Search size={14} />
              </div>
              <input
                type="text"
                value={drawerSearch}
                onChange={(e) => setDrawerSearch(e.target.value)}
                placeholder={`Search inside ${activeConstellation.name}...`}
                className="editorial-input"
                style={{ width: "100%", padding: "0.45rem 0.75rem 0.45rem 2rem", fontSize: "0.82rem", background: theme.bgSubtle, border: `1px solid ${theme.border}`, borderRadius: "8px", color: theme.textPrimary }}
              />
              {drawerSearch && (
                <button
                  onClick={() => setDrawerSearch("")}
                  style={{ position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", color: theme.textMuted, cursor: "pointer" }}
                >
                  <X size={12} />
                </button>
              )}
            </div>

            {/* ── Complete Constellation Gallery Grid ── */}
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 700, color: theme.textPrimary, textTransform: "uppercase", letterSpacing: "0.03em" }}>
                  Constellation Gallery Grid ({constellationMemories.length})
                </span>
                <button
                  onClick={() => router.push(`/gallery?constellation=${activeConstellation.constellation_key}`)}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.25rem",
                    fontSize: "0.74rem",
                    fontWeight: 600,
                    color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  <span>Open in Dedicated Gallery</span>
                  <ExternalLink size={12} />
                </button>
              </div>

              {constellationMemories.length === 0 ? (
                <div style={{ padding: "2rem 1rem", textAlign: "center", color: theme.textMuted, fontSize: "0.84rem" }}>
                  No memories matched your search in this constellation.
                </div>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", maxHeight: 360, overflowY: "auto" }}>
                  {constellationMemories.map((m) => {
                    const isSelected = selectedNode && selectedNode.id === m.id;
                    const isProtected = m.sensitivity_level === "CRITICAL" && !revealedIds.has(m.id);
                    return (
                      <div
                        key={m.id}
                        onClick={() => handleNodeClick(m)}
                        className="card-interactive"
                        style={{
                          padding: "0.6rem",
                          background: isSelected ? (isDarkMode ? "rgba(56, 189, 248, 0.2)" : "var(--accent-light)") : theme.bgSubtle,
                          borderRadius: "8px",
                          border: isSelected ? `1.5px solid ${isDarkMode ? "#38bdf8" : "var(--accent-terracotta)"}` : `1px solid ${theme.border}`,
                          cursor: "pointer",
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.4rem",
                          transition: "all 0.15s ease",
                        }}
                        title={m.name}
                      >
                        <div style={{ width: "100%", height: 85, borderRadius: "6px", overflow: "hidden", background: theme.bgCanvas, position: "relative" }}>
                          <img
                            src={getThumbnailUrl(m.id)}
                            alt={m.name}
                            style={{
                              width: "100%",
                              height: "100%",
                              objectFit: "cover",
                              filter: isProtected ? "blur(6px)" : "none",
                            }}
                          />
                          {isProtected && (
                            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.3)" }}>
                              <Lock size={14} color="#ffffff" />
                            </div>
                          )}
                        </div>
                        <div style={{ fontSize: "0.78rem", fontWeight: 600, color: theme.textPrimary, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {m.name}
                        </div>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                          <span className={`badge badge-${m.category || "other"}`} style={{ fontSize: "0.65rem", padding: "1px 5px" }}>
                            {m.category?.toUpperCase() || "ARTIFACT"}
                          </span>
                          <span style={{ fontSize: "0.68rem", color: isDarkMode ? "#38bdf8" : "var(--accent-terracotta)", fontWeight: 600 }}>
                            Focus Map
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
