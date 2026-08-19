"use client";
import React, { useState, useCallback, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import {
  Upload,
  FileImage,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  Shield,
  Layers,
  ArrowRight,
  Eye,
  FileText,
  Clock,
  Lock,
} from "lucide-react";
import { apiUploadFile, apiGetMemory, Memory, CATEGORY_ICONS, SENSITIVITY_CONFIG } from "@/lib/api";

interface FileProgress {
  file: File;
  memoryId?: string;
  status: "staged" | "uploading" | "ocr" | "vision" | "shield" | "embedding" | "connecting" | "done" | "error";
  stepLabel: string;
  stepIndex: number; // 0 to 5
  memory?: Memory;
  error?: string;
}

const PIPELINE_STEPS = [
  { key: "upload", label: "Upload & Verify", desc: "Binary validation & deduplication" },
  { key: "ocr", label: "Optical Character OCR", desc: "Extract raw tokens & layout blocks" },
  { key: "vision", label: "Multimodal Vision", desc: "Category, entities & semantic context" },
  { key: "shield", label: "Zero-Trust Shield", desc: "Deterministic credential detection" },
  { key: "embed", label: "Neural Embedding", desc: "Vector indexing & graph relations" },
];

export default function UploadPage() {
  const [fileItems, setFileItems] = useState<FileProgress[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const pollingRefs = useRef<{ [filename: string]: boolean }>({});

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newItems: FileProgress[] = acceptedFiles.map((file) => ({
      file,
      status: "staged",
      stepLabel: "Ready to ingest",
      stepIndex: 0,
    }));
    setFileItems((prev) => [...prev, ...newItems]);
    setError("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".png", ".jpg", ".jpeg", ".webp"] },
  });

  const pollMemoryStatus = async (filename: string, memoryId: string) => {
    pollingRefs.current[filename] = true;
    const startTime = Date.now();
    const timeoutMs = 90000; // 90 seconds timeout

    while (pollingRefs.current[filename]) {
      if (Date.now() - startTime > timeoutMs) {
        setFileItems((prev) =>
          prev.map((item) =>
            item.file.name === filename
              ? { ...item, status: "error", error: "Processing timed out. Refresh to verify status." }
              : item
          )
        );
        break;
      }

      try {
        const mem = await apiGetMemory(memoryId);
        const pStatus = mem.processing_status || "pending";

        if (pStatus === "done") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? {
                    ...item,
                    status: "done",
                    stepLabel: `Classified as ${mem.category.toUpperCase()}`,
                    stepIndex: 5,
                    memory: mem,
                  }
                : item
            )
          );
          break;
        } else if (pStatus === "error") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? {
                    ...item,
                    status: "error",
                    error: "Pipeline error occurred during analysis.",
                    stepIndex: 0,
                  }
                : item
            )
          );
          break;
        } else if (pStatus === "ocr") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? { ...item, status: "ocr", stepLabel: "Extracting optical text...", stepIndex: 2 }
                : item
            )
          );
        } else if (pStatus === "vision") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? { ...item, status: "vision", stepLabel: "Analyzing multimodal visual layout...", stepIndex: 3 }
                : item
            )
          );
        } else if (pStatus === "shield") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? { ...item, status: "shield", stepLabel: "Scanning with AURA Zero-Trust Shield...", stepIndex: 4 }
                : item
            )
          );
        } else if (pStatus === "embedding" || pStatus === "connecting") {
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? { ...item, status: "embedding", stepLabel: "Indexing vectors & discovering graph relations...", stepIndex: 5 }
                : item
            )
          );
        } else {
          // pending/processing
          setFileItems((prev) =>
            prev.map((item) =>
              item.file.name === filename
                ? { ...item, status: "uploading", stepLabel: "Uploaded — analyzing multimodal memory...", stepIndex: 1 }
                : item
            )
          );
        }
      } catch (e: any) {
        console.warn(`Polling error for ${memoryId}:`, e);
      }

      await new Promise((r) => setTimeout(r, 1500));
    }
  };

  const handleUploadAll = async () => {
    if (fileItems.length === 0 || uploading) return;
    setUploading(true);
    setError("");

    const staged = fileItems.filter((f) => f.status === "staged");

    for (const item of staged) {
      setFileItems((prev) =>
        prev.map((it) =>
          it.file.name === item.file.name
            ? { ...it, status: "uploading", stepLabel: "Uploading binary payload...", stepIndex: 1 }
            : it
        )
      );

      try {
        const res = await apiUploadFile(item.file);
        const memId = res.id;

        setFileItems((prev) =>
          prev.map((it) =>
            it.file.name === item.file.name
              ? { ...it, memoryId: memId, stepLabel: "Queued for multimodal analysis...", stepIndex: 1 }
              : it
          )
        );

        // Start async polling for this memory
        pollMemoryStatus(item.file.name, memId);
      } catch (err: any) {
        setFileItems((prev) =>
          prev.map((it) =>
            it.file.name === item.file.name
              ? { ...it, status: "error", error: err.message || "Upload failed", stepIndex: 0 }
              : it
          )
        );
      }
    }

    setUploading(false);
  };

  const completedCount = fileItems.filter((f) => f.status === "done").length;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "3.5rem 2rem 5rem" }}>
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
          Ingest Visual Artifacts
        </h1>
        <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginTop: 4 }}>
          Upload screenshots, photos, and scans for adaptive OCR, multimodal vision, and zero-trust indexing
        </p>
      </div>

      {/* Dropzone Container */}
      <div
        {...getRootProps()}
        className="paper-card"
        style={{
          padding: "4rem 2rem",
          textAlign: "center",
          border: isDragActive ? "2px dashed var(--accent-terracotta)" : "2px dashed var(--border-strong)",
          background: isDragActive ? "var(--accent-light)" : "var(--bg-surface)",
          cursor: "pointer",
          marginBottom: "2rem",
          transition: "all 0.2s ease",
        }}
      >
        <input {...getInputProps()} />
        <div
          style={{
            width: 54,
            height: 54,
            borderRadius: "50%",
            background: "var(--bg-subtle)",
            border: "1px solid var(--border-medium)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 1.25rem",
          }}
        >
          <Upload size={24} color="var(--accent-terracotta)" />
        </div>
        <h3
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.25rem",
            fontWeight: 600,
            color: "var(--text-primary)",
            marginBottom: "0.5rem",
          }}
        >
          {isDragActive ? "Drop visual captures here..." : "Select or drag screenshots here"}
        </h3>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", maxWidth: 460, margin: "0 auto" }}>
          Supports PNG, JPG, WEBP formats. High-resolution captures are processed with optical character recognition and neural graph linking.
        </p>
      </div>

      {/* File Ingestion Queue */}
      {fileItems.length > 0 && (
        <div className="paper-card" style={{ padding: "1.75rem 2rem", marginBottom: "2.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
            <div>
              <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.2rem", fontWeight: 600, color: "var(--text-primary)" }}>
                Ingestion Queue ({fileItems.length})
              </span>
              <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: 2 }}>
                {completedCount} of {fileItems.length} indexed into memory ledger
              </div>
            </div>
            {fileItems.some((f) => f.status === "staged") && (
              <button
                onClick={handleUploadAll}
                disabled={uploading}
                className="btn-terracotta"
              >
                {uploading ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
                <span>{uploading ? "Ingesting Artifacts..." : "Start Ingestion Pipeline"}</span>
              </button>
            )}
          </div>

          {/* Files Progress Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {fileItems.map((item, idx) => {
              const isDone = item.status === "done";
              const isError = item.status === "error";
              const isRunning = !isDone && !isError && item.status !== "staged";

              return (
                <div
                  key={idx}
                  style={{
                    background: isDone ? "var(--bg-surface)" : "var(--bg-subtle)",
                    borderRadius: "var(--radius-sm)",
                    border: isDone
                      ? "1px solid var(--border-medium)"
                      : isError
                      ? "1px solid rgba(184, 58, 46, 0.4)"
                      : "1px solid var(--border-subtle)",
                    padding: "1rem 1.25rem",
                    transition: "all 0.2s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                      {isDone ? (
                        <div
                          style={{
                            width: 28,
                            height: 28,
                            borderRadius: "50%",
                            background: "rgba(46, 125, 50, 0.12)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <CheckCircle2 size={16} color="var(--severity-public)" />
                        </div>
                      ) : isRunning ? (
                        <div
                          style={{
                            width: 28,
                            height: 28,
                            borderRadius: "50%",
                            background: "var(--accent-light)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Loader2 size={16} className="animate-spin" color="var(--accent-terracotta)" />
                        </div>
                      ) : isError ? (
                        <div
                          style={{
                            width: 28,
                            height: 28,
                            borderRadius: "50%",
                            background: "rgba(184, 58, 46, 0.12)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <AlertCircle size={16} color="var(--severity-critical)" />
                        </div>
                      ) : (
                        <FileImage size={20} color="var(--text-secondary)" />
                      )}
                      <div>
                        <div style={{ fontWeight: 600, fontSize: "0.88rem", color: "var(--text-primary)" }}>
                          {item.file.name}
                        </div>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 1 }}>
                          {(item.file.size / 1024).toFixed(1)} KB • {item.stepLabel}
                        </div>
                      </div>
                    </div>

                    {isDone && item.memory && (
                      <button
                        onClick={() => router.push(`/memory/${item.memory?.id}`)}
                        className="btn-paper"
                        style={{ padding: "0.35rem 0.75rem", fontSize: "0.78rem" }}
                      >
                        <span>View Artifact</span>
                        <ArrowRight size={13} />
                      </button>
                    )}
                  </div>

                  {/* Step Indicators */}
                  {isRunning && (
                    <div style={{ marginTop: "0.85rem", paddingTop: "0.75rem", borderTop: "1px solid var(--border-subtle)" }}>
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(5, 1fr)",
                          gap: "0.4rem",
                          fontSize: "0.7rem",
                        }}
                      >
                        {PIPELINE_STEPS.map((step, sIdx) => {
                          const isPast = item.stepIndex > sIdx + 1;
                          const isCurrent = item.stepIndex === sIdx + 1;
                          return (
                            <div
                              key={sIdx}
                              style={{
                                padding: "0.35rem 0.45rem",
                                borderRadius: "var(--radius-xs)",
                                background: isPast
                                  ? "rgba(46, 125, 50, 0.08)"
                                  : isCurrent
                                  ? "var(--accent-light)"
                                  : "transparent",
                                border: isCurrent
                                  ? "1px solid var(--accent-border)"
                                  : "1px solid transparent",
                                color: isPast
                                  ? "var(--severity-public)"
                                  : isCurrent
                                  ? "var(--accent-dark)"
                                  : "var(--text-muted)",
                                fontWeight: isCurrent ? 600 : 400,
                              }}
                            >
                              <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                {isPast ? "✓ " : isCurrent ? "▶ " : ""}{step.label}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Completed Summary Preview */}
                  {isDone && item.memory && (
                    <div
                      style={{
                        marginTop: "0.75rem",
                        paddingTop: "0.75rem",
                        borderTop: "1px solid var(--border-subtle)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        fontSize: "0.8rem",
                      }}
                    >
                      <div style={{ color: "var(--text-secondary)", maxWidth: "80%" }}>
                        {item.memory.summary || "Visual memory indexed."}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        <span
                          className="tactile-pill"
                          style={{
                            fontSize: "0.72rem",
                            background: "var(--bg-subtle)",
                            border: "1px solid var(--border-medium)",
                          }}
                        >
                          {CATEGORY_ICONS[item.memory.category] || "📷"} {item.memory.category}
                        </span>
                        {item.memory.sensitivity_level !== "PUBLIC" && (
                          <span
                            className="tactile-pill"
                            style={{
                              fontSize: "0.72rem",
                              background: "rgba(184, 58, 46, 0.1)",
                              borderColor: "rgba(184, 58, 46, 0.25)",
                              color: "var(--severity-critical)",
                            }}
                          >
                            <Shield size={10} style={{ marginRight: 2 }} />
                            {item.memory.sensitivity_level}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Quick Navigation Footer */}
      {completedCount > 0 && (
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "1rem" }}>
          <button onClick={() => router.push("/gallery")} className="btn-paper">
            <span>Explore Knowledge Gallery</span>
            <ArrowRight size={14} />
          </button>
          <button onClick={() => router.push("/constellation")} className="btn-terracotta">
            <span>View Constellation Graph</span>
            <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
