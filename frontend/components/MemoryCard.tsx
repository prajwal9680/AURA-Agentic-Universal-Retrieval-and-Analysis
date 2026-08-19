"use client";
import React, { useState } from "react";
import {
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  ArrowUpRight,
  Shield,
  FileText,
  Calendar,
  Layers,
} from "lucide-react";
import { getThumbnailUrl, Memory } from "@/lib/api";

interface MemoryCardProps {
  memory: Memory;
  showScore?: boolean;
  isRevealed?: boolean;
  onToggleReveal?: (id: string) => void;
  onClick?: () => void;
}

export default function MemoryCard({
  memory,
  showScore = false,
  isRevealed = false,
  onToggleReveal,
  onClick,
}: MemoryCardProps) {
  const [localRevealed, setLocalRevealed] = useState(false);
  const [imgError, setImgError] = useState(false);

  const isSensitive =
    memory.sensitivity_level === "CRITICAL" || memory.sensitivity_level === "SENSITIVE";

  const effectiveRevealed =
    onToggleReveal && isRevealed !== undefined ? isRevealed : localRevealed;

  const handleRevealClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleReveal) {
      onToggleReveal(memory.id);
    } else {
      setLocalRevealed((prev) => !prev);
    }
  };

  const getSeverityBadgeClass = (level?: string) => {
    switch (level) {
      case "CRITICAL":
        return "badge-critical";
      case "SENSITIVE":
        return "badge-sensitive";
      case "PERSONAL":
        return "badge-personal";
      default:
        return "badge-public";
    }
  };

  const parsedEntities: string[] = (() => {
    if (!memory.entities) return [];
    if (Array.isArray(memory.entities)) return memory.entities;
    try {
      return JSON.parse(memory.entities);
    } catch {
      return [];
    }
  })();

  const parsedTopics: string[] = (() => {
    if (!memory.topics) return [];
    if (Array.isArray(memory.topics)) return memory.topics;
    try {
      return JSON.parse(memory.topics);
    } catch {
      return [];
    }
  })();

  const formattedDate = memory.created_at
    ? new Date(memory.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : "";

  return (
    <div
      onClick={onClick}
      className="paper-card"
      style={{
        display: "flex",
        flexDirection: "column",
        cursor: onClick ? "pointer" : "default",
        overflow: "hidden",
        position: "relative",
      }}
      data-interactive="true"
    >
      {/* Thumbnail / Redacted Mask Container */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: 170,
          background: "var(--bg-subtle)",
          borderBottom: "1px solid var(--border-subtle)",
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {isSensitive && !effectiveRevealed ? (
          /* Redacted Zero-Trust Mask */
          <div style={{ position: "relative", width: "100%", height: "100%", overflow: "hidden" }}>
            {/* Blurred background silhouette */}
            {!imgError && (
              <img
                src={getThumbnailUrl(memory.id)}
                alt="Masked Thumbnail"
                onError={() => setImgError(true)}
                style={{
                  position: "absolute",
                  inset: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  filter: "blur(14px) brightness(0.4)",
                  transform: "scale(1.1)",
                }}
              />
            )}
            
            {/* Diagonal Caution Security Tape Banner */}
            <div className="tape-diagonal-strip">
              {memory.is_redacted ? "PERMANENTLY REDACTED" : "AURA ZERO-TRUST SHIELD"}
            </div>

            {/* Frosted Tape Center Panel */}
            <div
              className="redacted-tape"
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.45rem",
                padding: "0.85rem",
                textAlign: "center",
                zIndex: 2,
              }}
            >
              <div className="tape-glow-lock">
                <Lock size={16} color="#ffffff" />
              </div>
              <div style={{ zIndex: 3, marginTop: "0.2rem" }}>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#ffffff", letterSpacing: "0.02em" }}>
                  {memory.is_redacted ? "Sanitized Artifact" : "Zero-Trust Protected"}
                </div>
                <div style={{ fontSize: "0.68rem", color: "rgba(255, 255, 255, 0.7)", marginTop: 1 }}>
                  {memory.is_redacted ? "All secrets destroyed" : "Confidential credentials masked"}
                </div>
              </div>
              {!memory.is_redacted && (
                <button
                  type="button"
                  onClick={handleRevealClick}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.3rem",
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    padding: "0.28rem 0.75rem",
                    borderRadius: 99,
                    marginTop: "0.25rem",
                    background: "rgba(255, 255, 255, 0.15)",
                    border: "1px solid rgba(255, 255, 255, 0.4)",
                    color: "#ffffff",
                    backdropFilter: "blur(8px)",
                    cursor: "pointer",
                    zIndex: 4,
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.25)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.15)")}
                >
                  <Eye size={12} />
                  <span>Reveal</span>
                </button>
              )}
            </div>
          </div>
        ) : !imgError ? (
          <img
            src={getThumbnailUrl(memory.id)}
            alt={memory.summary || "Screenshot"}
            onError={() => setImgError(true)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transition: "transform 0.3s ease",
            }}
          />
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "0.4rem",
              color: "var(--text-muted)",
              fontSize: "0.75rem",
            }}
          >
            <FileText size={24} />
            <span>Document Preview</span>
          </div>
        )}

        {/* Top Floating Category & Date Badges */}
        <div
          style={{
            position: "absolute",
            top: 8,
            left: 8,
            display: "flex",
            gap: "0.35rem",
            alignItems: "center",
          }}
        >
          <span
            className="tactile-pill"
            style={{
              fontSize: "0.68rem",
              padding: "2px 8px",
              background: "rgba(255, 255, 255, 0.92)",
              backdropFilter: "blur(4px)",
              color: "var(--text-primary)",
              fontWeight: 500,
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05)",
            }}
          >
            {memory.category || "artifact"}
          </span>

          <span
            className={`tactile-pill ${getSeverityBadgeClass(memory.sensitivity_level)}`}
            style={{
              fontSize: "0.68rem",
              padding: "2px 7px",
              fontWeight: 600,
            }}
          >
            {memory.sensitivity_level || "PUBLIC"}
          </span>

          {memory.application && (
            <span
              className="tactile-pill"
              style={{
                fontSize: "0.68rem",
                padding: "2px 7px",
                background: "rgba(240, 244, 255, 0.92)",
                backdropFilter: "blur(4px)",
                color: "#1e3a8a",
                fontWeight: 600,
                border: "1px solid rgba(191, 219, 254, 0.8)",
              }}
            >
              {memory.application}
            </span>
          )}

          {memory.clipboard_context && (
            <span
              className="tactile-pill"
              title={`Clipboard context: ${memory.clipboard_context}`}
              style={{
                fontSize: "0.68rem",
                padding: "2px 6px",
                background: "rgba(254, 243, 199, 0.92)",
                color: "#92400e",
                fontWeight: 600,
                border: "1px solid rgba(252, 211, 77, 0.8)",
              }}
            >
              📋 Link
            </span>
          )}
        </div>

        {/* Unmask Toggle Button if revealed */}
        {isSensitive && effectiveRevealed && (
          <button
            type="button"
            onClick={handleRevealClick}
            className="btn-paper"
            style={{
              position: "absolute",
              bottom: 8,
              right: 8,
              fontSize: "0.7rem",
              padding: "2px 7px",
              borderRadius: 99,
              background: "rgba(255, 255, 255, 0.92)",
            }}
          >
            <EyeOff size={12} />
            <span>Mask</span>
          </button>
        )}
      </div>

      {/* Card Body */}
      <div style={{ padding: "1rem 1.1rem", display: "flex", flexDirection: "column", flex: 1, gap: "0.5rem" }}>
        {/* Title / Summary */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "0.5rem" }}>
          <h3
            style={{
              fontSize: "0.98rem",
              fontFamily: "var(--font-serif)",
              fontWeight: 600,
              color: "var(--text-primary)",
              lineHeight: 1.35,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {memory.summary || memory.original_filename}
          </h3>
          <ArrowUpRight size={14} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: 3 }} />
        </div>

        {/* Clean Snippet */}
        {memory.ocr_text && (
          <p
            style={{
              fontSize: "0.78rem",
              color: "var(--text-secondary)",
              lineHeight: 1.45,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {isSensitive && !effectiveRevealed
              ? "••••••••••••••••••••••••••••••••••••••••••••••••"
              : memory.ocr_text}
          </p>
        )}

        {/* Entity / Visual Objects / Topic Tags */}
        {(parsedEntities.length > 0 || parsedTopics.length > 0 || (memory.visual_objects && memory.visual_objects.length > 0)) && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginTop: "auto", paddingTop: "0.4rem" }}>
            {memory.document_type && (
              <span
                style={{
                  fontSize: "0.65rem",
                  padding: "1px 6px",
                  borderRadius: "var(--radius-xs)",
                  background: "rgba(99, 102, 241, 0.08)",
                  color: "#4f46e5",
                  border: "1px solid rgba(99, 102, 241, 0.2)",
                  fontWeight: 600,
                }}
              >
                {memory.document_type.replace(/_/g, " ")}
              </span>
            )}
            {parsedEntities.slice(0, 2).map((ent, idx) => (
              <span
                key={`ent-${idx}`}
                style={{
                  fontSize: "0.68rem",
                  padding: "1px 6px",
                  borderRadius: "var(--radius-xs)",
                  background: "var(--bg-subtle)",
                  color: "var(--text-secondary)",
                  border: "1px solid var(--border-subtle)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {ent}
              </span>
            ))}
            {memory.visual_objects && Array.isArray(memory.visual_objects) && memory.visual_objects.slice(0, 2).map((obj, idx) => (
              <span
                key={`obj-${idx}`}
                style={{
                  fontSize: "0.65rem",
                  padding: "1px 6px",
                  borderRadius: "var(--radius-xs)",
                  background: "rgba(16, 185, 129, 0.08)",
                  color: "#059669",
                  border: "1px solid rgba(16, 185, 129, 0.2)",
                }}
              >
                👁️ {obj}
              </span>
            ))}
            {parsedTopics.slice(0, 1).map((top, idx) => (
              <span
                key={`top-${idx}`}
                style={{
                  fontSize: "0.68rem",
                  padding: "1px 6px",
                  borderRadius: "var(--radius-xs)",
                  background: "var(--bg-subtle)",
                  color: "var(--text-muted)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                #{top}
              </span>
            ))}
          </div>
        )}

        {/* Match Score & Evidence Footer if showScore */}
        {showScore && memory.similarity_score !== undefined && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              paddingTop: "0.5rem",
              marginTop: "0.3rem",
              borderTop: "1px solid var(--border-subtle)",
              fontSize: "0.72rem",
              color: "var(--text-muted)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent-terracotta)" }} />
              <span style={{ fontFamily: "var(--font-mono)", color: "var(--accent-dark)", fontWeight: 600 }}>
                {Math.round(memory.similarity_score * 100)}% match
              </span>
            </div>
            {formattedDate && <span>{formattedDate}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
