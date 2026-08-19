"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Clock,
  Calendar,
  Layers,
  Shield,
  Loader2,
  ChevronRight,
  Lock,
} from "lucide-react";
import { apiFetch, getThumbnailUrl, Memory } from "@/lib/api";

export default function TimelinePage() {
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchTimeline();
  }, []);

  const fetchTimeline = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/api/timeline");
      setTimelineData(data.groups || data.timeline || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "3.5rem 2rem 5rem" }}>
      {/* Editorial Header */}
      <div
        style={{
          marginBottom: "2.5rem",
          paddingBottom: "1.25rem",
          borderBottom: "1px solid var(--border-medium)",
        }}
      >
        <h1
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "2.4rem",
            fontWeight: 500,
            color: "var(--text-primary)",
            letterSpacing: "-0.025em",
          }}
        >
          Timeline Ledger
        </h1>
        <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginTop: 4 }}>
          Chronological visual record of captured screenshots and ingested documents
        </p>
      </div>

      {loading ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "6rem 0", color: "var(--text-secondary)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <Loader2 size={20} color="var(--accent-terracotta)" className="animate-spin" />
            <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.1rem" }}>Loading chronological ledger...</span>
          </div>
        </div>
      ) : timelineData.length === 0 ? (
        <div className="paper-card" style={{ padding: "3rem", textAlign: "center", color: "var(--text-secondary)" }}>
          <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.2rem", marginBottom: "0.5rem" }}>
            No visual memories recorded in the timeline
          </h3>
          <p style={{ fontSize: "0.85rem" }}>Ingest screenshots via the Ingest page or dropzone to populate your ledger.</p>
        </div>
      ) : (
        <div style={{ position: "relative", paddingLeft: "1.5rem" }}>
          {/* Vertical Spine Line */}
          <div
            style={{
              position: "absolute",
              top: 10,
              bottom: 10,
              left: 7,
              width: 1,
              background: "var(--border-strong)",
            }}
          />

          {timelineData.map((group: any, gIdx: number) => (
            <div key={gIdx} style={{ marginBottom: "3rem", position: "relative" }}>
              {/* Date Header Node */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1.25rem" }}>
                <div
                  style={{
                    width: 15,
                    height: 15,
                    borderRadius: "50%",
                    background: "var(--bg-canvas)",
                    border: "2.5px solid var(--accent-terracotta)",
                    marginLeft: -22,
                    zIndex: 2,
                  }}
                />
                <h2
                  style={{
                    fontFamily: "var(--font-serif)",
                    fontSize: "1.35rem",
                    fontWeight: 600,
                    color: "var(--text-primary)",
                  }}
                >
                  {group.date_label || group.date || "Past Session"}
                </h2>
                <span
                  className="tactile-pill"
                  style={{
                    fontSize: "0.7rem",
                    padding: "1px 7px",
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  {group.items?.length || group.memories?.length || 0} artifacts
                </span>
              </div>

              {/* Items List in this Date Group */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {(group.items || group.memories || []).map((item: any) => {
                  const isCritical =
                    item.sensitivity_level === "CRITICAL" || item.sensitivity_level === "SENSITIVE";

                  return (
                    <div
                      key={item.id}
                      onClick={() => router.push(`/memory/${item.id}`)}
                      className="paper-card"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "1.25rem",
                        padding: "1rem 1.25rem",
                        cursor: "pointer",
                      }}
                      data-interactive="true"
                    >
                      {/* Thumbnail Preview */}
                      <div
                        style={{
                          width: 80,
                          height: 56,
                          borderRadius: "var(--radius-xs)",
                          background: "var(--bg-subtle)",
                          border: "1px solid var(--border-medium)",
                          overflow: "hidden",
                          flexShrink: 0,
                          position: "relative",
                        }}
                      >
                        {isCritical ? (
                          <div
                            style={{
                              width: "100%",
                              height: "100%",
                              background: "rgba(184, 58, 46, 0.08)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            <Lock size={14} color="var(--severity-critical)" />
                          </div>
                        ) : (
                          <img
                            src={getThumbnailUrl(item.id)}
                            alt=""
                            style={{ width: "100%", height: "100%", objectFit: "cover" }}
                          />
                        )}
                      </div>

                      {/* Content Summary */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: 3 }}>
                          <span
                            className="tactile-pill"
                            style={{ fontSize: "0.68rem", padding: "1px 6px" }}
                          >
                            {item.category || "artifact"}
                          </span>
                          <span
                            style={{
                              fontSize: "0.68rem",
                              fontWeight: 600,
                              color: isCritical ? "var(--severity-critical)" : "var(--severity-public)",
                            }}
                          >
                            {item.sensitivity_level || "PUBLIC"}
                          </span>
                        </div>
                        <h3
                          style={{
                            fontFamily: "var(--font-serif)",
                            fontSize: "1.05rem",
                            fontWeight: 600,
                            color: "var(--text-primary)",
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                        >
                          {item.summary || item.original_filename}
                        </h3>
                        {item.ocr_text && (
                          <p
                            style={{
                              fontSize: "0.78rem",
                              color: "var(--text-secondary)",
                              whiteSpace: "nowrap",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              marginTop: 2,
                            }}
                          >
                            {isCritical ? "••••••••••••••••••••••••••••••••" : item.ocr_text}
                          </p>
                        )}
                      </div>

                      <ChevronRight size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
