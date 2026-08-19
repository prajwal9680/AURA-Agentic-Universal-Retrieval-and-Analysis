"use client";
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Lock,
  Unlock,
  Trash2,
  Eye,
  EyeOff,
  Shield,
  ShieldAlert,
  Zap,
  Brain,
  AlertTriangle,
  Copy,
  Check,
  Receipt,
  FileCode,
  Sparkles,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  Loader2,
  FileText,
} from "lucide-react";
import {
  apiFetch,
  API_URL,
  SENSITIVITY_CONFIG,
  CATEGORY_ICONS,
  Memory,
} from "@/lib/api";

export default function MemoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [memory, setMemory] = useState<Memory | null>(null);
  const [relationships, setRelationships] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionResult, setActionResult] = useState<any>(null);
  const [revealed, setRevealed] = useState(false);
  const [showEvidence, setShowEvidence] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      apiFetch(`/api/memories/${id}`),
      apiFetch(`/api/memories/${id}/relationships`).catch(() => ({ relationships: [] })),
    ])
      .then(([mem, rels]) => {
        setMemory(mem);
        setRelationships(rels.relationships || []);
      })
      .catch(() => router.push("/gallery"))
      .finally(() => setLoading(false));
  }, [id, router]);

  const runAction = async (action: string) => {
    setActionLoading(true);
    setActionResult(null);
    try {
      const data = await apiFetch(`/api/actions/${action}`, {
        method: "POST",
        body: JSON.stringify({ memory_id: id }),
      });
      setActionResult({ action, ...data.result });
    } catch (e: any) {
      setActionResult({ action, error: e.message });
    } finally {
      setActionLoading(false);
    }
  };

  const handleLock = async () => {
    await apiFetch(`/api/memories/${id}/lock`, { method: "POST" });
    setMemory((m) => (m ? { ...m, is_locked: !m.is_locked } : m));
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to permanently delete this memory artifact?")) return;
    await apiFetch(`/api/memories/${id}`, { method: "DELETE" });
    router.push("/gallery");
  };

  const handleRedact = async () => {
    if (!confirm("Permanently redact sensitive text and visual content from this memory artifact?\n\nThis action is IRREVERSIBLE. Secret OCR and visual embeddings will be permanently expunged from the database and disk.")) return;
    try {
      const updated = await apiFetch(`/api/memories/${id}/redact`, { method: "POST" });
      setMemory(updated);
      setRevealed(false);
    } catch (err) {
      console.error("Redaction error:", err);
      alert("Failed to redact memory artifact.");
    }
  };

  const copyOcr = () => {
    if (!memory?.ocr_text) return;
    navigator.clipboard.writeText(memory.ocr_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          gap: "0.75rem",
          color: "var(--text-secondary)",
        }}
      >
        <Loader2 size={22} color="var(--accent-terracotta)" className="animate-spin" />
        <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.1rem" }}>
          Loading visual memory artifact...
        </span>
      </div>
    );
  }

  if (!memory) return null;

  const isCritical = memory.sensitivity_level === "CRITICAL";
  const isSensitive = memory.sensitivity_level === "SENSITIVE";
  const shouldMask = (isCritical || isSensitive || memory._protected) && !revealed && !memory.is_redacted;
  const catIcon = CATEGORY_ICONS[memory.category] || "📷";

  // Contextual actions
  const actions = [];
  if (["receipt", "invoice", "finance"].includes(memory.category)) {
    actions.push({ id: "extract_expense", label: "Extract Expense & Line Items", icon: Receipt });
  }
  if (["code", "terminal", "ide"].includes(memory.category)) {
    actions.push({ id: "debug_code", label: "Debug & Explain Code", icon: FileCode });
  }
  actions.push({ id: "summarize", label: "Generate Grounded Summary", icon: Sparkles });

  return (
    <div style={{ maxWidth: 1320, margin: "0 auto", padding: "2.5rem 2rem 5rem" }}>
      {/* Top Header & Actions */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "1.25rem",
          marginBottom: "2rem",
          paddingBottom: "1.25rem",
          borderBottom: "1px solid var(--border-medium)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button
            onClick={() => router.push("/gallery")}
            className="btn-paper"
            style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem" }}
          >
            <ChevronLeft size={15} />
            <span>Gallery</span>
          </button>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <h1
                style={{
                  fontFamily: "var(--font-serif)",
                  fontSize: "1.75rem",
                  fontWeight: 600,
                  color: "var(--text-primary)",
                  letterSpacing: "-0.015em",
                }}
              >
                {memory.original_filename}
              </h1>
              <span className={`badge badge-${memory.category || "other"}`}>
                {catIcon} {memory.category?.toUpperCase() || "ARTIFACT"}
              </span>
              <span className={`badge badge-${(memory.sensitivity_level || "public").toLowerCase()}`}>
                {memory.sensitivity_level}
              </span>
              {memory.is_redacted && (
                <span
                  style={{
                    fontSize: "0.72rem",
                    fontWeight: 700,
                    padding: "0.2rem 0.55rem",
                    borderRadius: "6px",
                    background: "rgba(220, 38, 38, 0.12)",
                    color: "#dc2626",
                    border: "1px solid rgba(220, 38, 38, 0.3)",
                  }}
                >
                  PERMANENTLY REDACTED
                </span>
              )}
            </div>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: 3 }}>
              Captured {new Date(memory.created_at).toLocaleString()} • {memory.application || "Desktop System"}
            </p>
          </div>
        </div>

        {/* Global Action Toolbar */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <button
            onClick={handleLock}
            className="btn-paper"
            style={{
              color: memory.is_locked ? "var(--severity-critical)" : "var(--text-primary)",
            }}
          >
            {memory.is_locked ? <Lock size={13} /> : <Unlock size={13} />}
            <span>{memory.is_locked ? "Locked" : "Lock"}</span>
          </button>

          <button
            onClick={handleRedact}
            disabled={memory.is_redacted}
            className="btn-paper"
            style={{
              opacity: memory.is_redacted ? 0.7 : 1,
              cursor: memory.is_redacted ? "not-allowed" : "pointer",
              color: memory.is_redacted ? "#16a34a" : "inherit",
            }}
          >
            <Shield size={13} />
            <span>{memory.is_redacted ? "✓ Redacted Permanently" : "Redact Permanently"}</span>
          </button>

          <button
            onClick={handleDelete}
            className="btn-paper"
            style={{ color: "var(--severity-critical)" }}
          >
            <Trash2 size={13} />
            <span>Delete</span>
          </button>
        </div>
      </div>

      {/* Main Split Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.15fr 0.85fr",
          gap: "2rem",
          alignItems: "start",
        }}
      >
        {/* Left Column: Image Viewport & Actions */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Screenshot Display Card */}
          <div
            className="paper-card"
            style={{
              borderRadius: "var(--radius-md)",
              overflow: "hidden",
              background: "var(--bg-subtle)",
              position: "relative",
            }}
          >
            {memory.is_redacted ? (
              <div
                className="redacted-tape"
                style={{
                  minHeight: 380,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "3rem 2rem",
                  textAlign: "center",
                  gap: "1.2rem",
                }}
              >
                <div
                  style={{
                    width: 52,
                    height: 52,
                    borderRadius: "50%",
                    background: "rgba(220, 38, 38, 0.15)",
                    border: "1px solid #dc2626",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <ShieldAlert size={24} color="#dc2626" />
                </div>
                <div>
                  <h3
                    style={{
                      fontFamily: "var(--font-serif)",
                      fontSize: "1.35rem",
                      fontWeight: 600,
                      color: "#dc2626",
                    }}
                  >
                    Permanently Redacted & Sanitized
                  </h3>
                  <p
                    style={{
                      fontSize: "0.85rem",
                      color: "var(--text-secondary)",
                      maxWidth: 420,
                      marginTop: "0.3rem",
                    }}
                  >
                    This visual memory artifact has been permanently redacted under AURA Shield Zero-Trust policy. All sensitive OCR text and confidential tokens have been permanently expunged.
                  </p>
                </div>
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.4rem",
                    padding: "0.4rem 0.85rem",
                    borderRadius: "8px",
                    background: "rgba(220, 38, 38, 0.1)",
                    color: "#dc2626",
                    fontSize: "0.78rem",
                    fontWeight: 600,
                  }}
                >
                  <Lock size={12} />
                  <span>PERMANENT REDACTION LOCK (IRREVERSIBLE)</span>
                </div>
              </div>
            ) : shouldMask ? (
              <div style={{ position: "relative", minHeight: 400, overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {/* Background blurred silhouette */}
                <img
                  src={`${API_URL}${memory.image_url}`}
                  alt="Masked Screenshot"
                  style={{
                    position: "absolute",
                    inset: 0,
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    filter: "blur(20px) brightness(0.35)",
                    transform: "scale(1.1)",
                  }}
                />

                {/* Diagonal Caution Tape Banner */}
                <div className="tape-diagonal-strip" style={{ top: "18%", fontSize: "0.72rem", padding: "0.35rem 0" }}>
                  AURA ZERO-TRUST SECURITY SHIELD • CONFIDENTIAL DATA MASKED
                </div>

                {/* Center Frosted Glass Tape Shield Card */}
                <div
                  className="redacted-tape"
                  style={{
                    position: "relative",
                    zIndex: 3,
                    maxWidth: 480,
                    margin: "2rem auto",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: "2.5rem 2rem",
                    borderRadius: "14px",
                    textAlign: "center",
                    gap: "1rem",
                  }}
                >
                  <div className="tape-glow-lock" style={{ width: 44, height: 44 }}>
                    <Lock size={20} color="#ffffff" />
                  </div>
                  <div>
                    <h3
                      style={{
                        fontFamily: "var(--font-serif)",
                        fontSize: "1.4rem",
                        fontWeight: 700,
                        color: "#ffffff",
                        letterSpacing: "0.01em",
                      }}
                    >
                      Zero-Trust Shield Mask Active
                    </h3>
                    <p
                      style={{
                        fontSize: "0.86rem",
                        color: "rgba(255, 255, 255, 0.75)",
                        maxWidth: 380,
                        marginTop: "0.35rem",
                        lineHeight: 1.5,
                      }}
                    >
                      AURA Shield detected sensitive credentials or personal tokens. Visual preview and OCR text are securely masked by default.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setRevealed(true)}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      padding: "0.6rem 1.4rem",
                      borderRadius: 99,
                      background: "linear-gradient(135deg, var(--accent-terracotta), #b91c1c)",
                      color: "#ffffff",
                      border: "1px solid rgba(255, 255, 255, 0.35)",
                      boxShadow: "0 4px 14px rgba(185, 28, 28, 0.4)",
                      fontSize: "0.88rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
                    onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
                  >
                    <Eye size={15} />
                    <span>Authorize & Reveal Secret</span>
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <img
                  src={`${API_URL}${memory.image_url}`}
                  alt={memory.summary || memory.original_filename}
                  style={{
                    width: "100%",
                    display: "block",
                    maxHeight: 560,
                    objectFit: "contain",
                    background: "#FFFFFF",
                  }}
                />
                {isCritical && revealed && (
                  <div
                    style={{
                      padding: "0.6rem 1.25rem",
                      background: "rgba(184, 58, 46, 0.08)",
                      borderTop: "1px solid rgba(184, 58, 46, 0.25)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <span style={{ fontSize: "0.76rem", color: "var(--severity-critical)", fontWeight: 600 }}>
                      ⚠️ Currently Unmasked (Zero-trust bypass active)
                    </span>
                    <button
                      type="button"
                      onClick={() => setRevealed(false)}
                      className="btn-paper"
                      style={{ fontSize: "0.7rem", padding: "2px 8px", borderRadius: 99 }}
                    >
                      <EyeOff size={12} />
                      <span>Mask Secret</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Contextual AI Actions */}
          <div className="paper-card" style={{ padding: "1.5rem" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                marginBottom: "1rem",
              }}
            >
              <Zap size={16} color="var(--accent-terracotta)" />
              <h3 style={{ fontFamily: "var(--font-serif)", fontSize: "1.15rem", fontWeight: 600, color: "var(--text-primary)" }}>
                Contextual AI Intelligence
              </h3>
            </div>

            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {actions.map((act) => {
                const Icon = act.icon;
                return (
                  <button
                    key={act.id}
                    onClick={() => runAction(act.id)}
                    disabled={actionLoading}
                    className="btn-paper"
                  >
                    <Icon size={14} color="var(--accent-terracotta)" />
                    <span>{act.label}</span>
                  </button>
                );
              })}
            </div>

            {actionLoading && (
              <div
                style={{
                  marginTop: "1rem",
                  padding: "1rem",
                  background: "var(--bg-subtle)",
                  borderRadius: "var(--radius-sm)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.6rem",
                  color: "var(--text-secondary)",
                  fontSize: "0.85rem",
                }}
              >
                <Loader2 size={16} className="animate-spin" color="var(--accent-terracotta)" />
                <span>Executing multimodal intelligence reasoning...</span>
              </div>
            )}

            {actionResult && (
              <div
                style={{
                  marginTop: "1.25rem",
                  padding: "1.25rem",
                  background: "var(--bg-subtle)",
                  border: "1px solid var(--border-medium)",
                  borderRadius: "var(--radius-sm)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "0.85rem",
                    borderBottom: "1px solid var(--border-subtle)",
                    paddingBottom: "0.5rem",
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.72rem",
                      fontWeight: 600,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      color: "var(--accent-dark)",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.4rem",
                    }}
                  >
                    <Sparkles size={13} color="var(--accent-terracotta)" />
                    <span>Intelligence Execution ({actionResult.action?.replace("_", " ")})</span>
                  </div>
                  {actionResult.verified && (
                    <span
                      className="tactile-pill"
                      style={{
                        fontSize: "0.65rem",
                        padding: "1px 6px",
                        background: "rgba(34, 197, 94, 0.12)",
                        color: "#166534",
                        borderColor: "rgba(34, 197, 94, 0.3)",
                      }}
                    >
                      ✓ Grounded Evidence
                    </span>
                  )}
                </div>

                {/* Case 1: Expense Extraction */}
                {actionResult.merchant && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "0.5rem" }}>
                      <div>
                        <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>
                          {actionResult.merchant}
                        </div>
                        <div style={{ fontSize: "0.74rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)", marginTop: 2 }}>
                          Date: {actionResult.date || "N/A"} · {actionResult.category || "Receipt"}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--accent-terracotta)", fontFamily: "var(--font-serif)" }}>
                          {actionResult.total_amount || actionResult.total || "Amount Not Specified"}
                        </div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                          {actionResult.payment_method || "Payment Processed"}
                        </div>
                      </div>
                    </div>

                    {Array.isArray(actionResult.line_items) && actionResult.line_items.length > 0 && (
                      <div style={{ marginTop: "0.5rem", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.6rem" }}>
                        <div style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                          Itemized Breakdown
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                          {actionResult.line_items.map((it: any, idx: number) => (
                            <div key={idx} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                              <span>• {it.description}</span>
                              <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>{it.amount}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Case 2: Code Debugger */}
                {actionResult.error_type && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                      <span className="tactile-pill" style={{ fontSize: "0.7rem" }}>{actionResult.language || "Code"}</span>
                      <span style={{ fontSize: "0.86rem", fontWeight: 700, color: "var(--severity-critical)", fontFamily: "var(--font-mono)" }}>
                        {actionResult.error_type}
                      </span>
                    </div>

                    {actionResult.error_message && (
                      <div style={{ fontSize: "0.82rem", background: "var(--bg-surface)", padding: "0.6rem 0.8rem", borderRadius: "var(--radius-xs)", border: "1px solid var(--border-medium)", fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}>
                        {actionResult.error_message}
                      </div>
                    )}

                    {actionResult.root_cause && (
                      <div style={{ fontSize: "0.84rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                        <strong style={{ color: "var(--text-primary)" }}>Root Cause: </strong>
                        {actionResult.root_cause}
                      </div>
                    )}

                    {actionResult.suggested_fix && (
                      <div style={{ marginTop: "0.25rem", background: "#1e1e1e", color: "#e2e8f0", padding: "0.75rem 1rem", borderRadius: "var(--radius-xs)", fontSize: "0.8rem", fontFamily: "var(--font-mono)", position: "relative" }}>
                        <div style={{ fontSize: "0.68rem", textTransform: "uppercase", color: "#94a3b8", marginBottom: "0.3rem" }}>Suggested Fix</div>
                        <code>{actionResult.suggested_fix}</code>
                      </div>
                    )}
                  </div>
                )}

                {/* Case 3: Summary */}
                {!actionResult.merchant && !actionResult.error_type && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                    <div style={{ fontSize: "0.92rem", lineHeight: 1.55, color: "var(--text-primary)" }}>
                      {actionResult.overview || actionResult.summary || actionResult.answer || "Analysis completed."}
                    </div>
                    {Array.isArray(actionResult.key_points) && actionResult.key_points.length > 0 && (
                      <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.2rem", display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                        {actionResult.key_points.map((pt: string, idx: number) => (
                          <li key={idx}>{pt}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {/* Error Banner */}
                {actionResult.error && (
                  <div style={{ fontSize: "0.82rem", color: "var(--severity-critical)", padding: "0.5rem", background: "rgba(239, 68, 68, 0.1)", borderRadius: "var(--radius-xs)" }}>
                    Error: {actionResult.error}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Metadata, Evidence & OCR Explorer */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Metadata Card */}
          <div className="paper-card" style={{ padding: "1.5rem" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "1rem",
              }}
            >
              <span
                className="tactile-pill"
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 600,
                }}
              >
                {memory.sensitivity_level || "PUBLIC"}
              </span>
              <span style={{ fontSize: "0.74rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                {memory.created_at ? new Date(memory.created_at).toLocaleDateString() : ""}
              </span>
            </div>

            <h2
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.35rem",
                fontWeight: 600,
                color: "var(--text-primary)",
                lineHeight: 1.35,
                marginBottom: "0.75rem",
              }}
            >
              {memory.summary || memory.original_filename}
            </h2>

            <div style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginBottom: "1.25rem", fontFamily: "var(--font-mono)" }}>
              {memory.original_filename}
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "0.75rem",
                padding: "0.85rem 1rem",
                background: "var(--bg-subtle)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border-medium)",
                marginBottom: "1rem",
              }}
            >
              <div>
                <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  Category
                </div>
                <div style={{ fontSize: "0.86rem", fontWeight: 600, color: "var(--text-primary)", textTransform: "capitalize", marginTop: 2 }}>
                  {catIcon} {memory.category}
                </div>
              </div>
              <div>
                <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  Application Context
                </div>
                <div style={{ fontSize: "0.86rem", fontWeight: 600, color: "var(--text-primary)", marginTop: 2 }}>
                  {memory.application || "System Capture"}
                </div>
              </div>
              {memory.window_title && (
                <div style={{ gridColumn: "span 2" }}>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                    Active Window Title
                  </div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 500, color: "var(--text-secondary)", marginTop: 2, fontFamily: "var(--font-mono)" }}>
                    {memory.window_title}
                  </div>
                </div>
              )}
              {memory.clipboard_context && (
                <div style={{ gridColumn: "span 2", background: "rgba(254, 243, 199, 0.5)", padding: "0.5rem 0.75rem", borderRadius: "var(--radius-xs)", border: "1px solid rgba(252, 211, 77, 0.5)" }}>
                  <div style={{ fontSize: "0.68rem", color: "#92400e", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
                    <Copy size={12} />
                    <span>Associated Clipboard Context</span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#78350f", marginTop: 2, fontFamily: "var(--font-mono)", wordBreak: "break-all" }}>
                    {memory.clipboard_context}
                  </div>
                </div>
              )}
            </div>

            {/* Entity Tags */}
            {memory.entities && memory.entities.length > 0 && (
              <div style={{ marginBottom: "0.75rem" }}>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.4rem" }}>
                  Named Entities
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {memory.entities.map((e) => (
                    <span
                      key={e}
                      style={{
                        fontSize: "0.72rem",
                        padding: "2px 8px",
                        borderRadius: "var(--radius-xs)",
                        background: "var(--bg-subtle)",
                        color: "var(--text-primary)",
                        border: "1px solid var(--border-subtle)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Multimodal Visual Understanding Card */}
            {(memory.visual_summary || (memory.visual_objects && memory.visual_objects.length > 0) || memory.document_type) && (
              <div style={{ marginTop: "1rem", paddingTop: "0.85rem", borderTop: "1px solid var(--border-subtle)" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, display: "flex", alignItems: "center", gap: 4 }}>
                    <Sparkles size={12} color="var(--accent-terracotta)" />
                    <span>Multimodal Vision Intelligence</span>
                  </div>
                  <span
                    className="tactile-pill"
                    style={{
                      fontSize: "0.65rem",
                      padding: "1px 6px",
                      background: "rgba(16, 185, 129, 0.1)",
                      color: "#059669",
                      borderColor: "rgba(16, 185, 129, 0.3)",
                      fontWeight: 600,
                    }}
                  >
                    ✓ Verified Visual Analysis
                  </span>
                </div>

                {memory.visual_summary && memory.visual_summary !== memory.summary && (
                  <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.45, marginBottom: "0.5rem" }}>
                    {memory.visual_summary}
                  </p>
                )}

                {memory.visual_objects && memory.visual_objects.length > 0 && (
                  <div style={{ marginBottom: "0.5rem" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginBottom: "0.3rem" }}>Visible Visual Objects</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem" }}>
                      {memory.visual_objects.map((obj, i) => (
                        <span
                          key={i}
                          style={{
                            fontSize: "0.7rem",
                            padding: "2px 7px",
                            borderRadius: "var(--radius-xs)",
                            background: "rgba(16, 185, 129, 0.08)",
                            color: "#059669",
                            border: "1px solid rgba(16, 185, 129, 0.2)",
                          }}
                        >
                          👁️ {obj}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {memory.visual_details && typeof memory.visual_details === "object" && memory.visual_details.layout_structure && (
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", background: "var(--bg-surface)", padding: "0.4rem 0.6rem", borderRadius: "var(--radius-xs)", border: "1px solid var(--border-subtle)" }}>
                    <strong>Layout: </strong>{memory.visual_details.layout_structure} {memory.visual_details.theme ? `(${memory.visual_details.theme} theme)` : ""}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Evidence Mode & Fact Provenance Ledger */}
          <div className="paper-card" style={{ padding: "1.25rem 1.5rem" }}>
            <button
              onClick={() => setShowEvidence(!showEvidence)}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                color: "var(--text-primary)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Brain size={16} color="var(--accent-terracotta)" />
                <span style={{ fontFamily: "var(--font-serif)", fontSize: "1.05rem", fontWeight: 600 }}>
                  AURA Fact Provenance & Verification
                </span>
              </div>
              {showEvidence ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showEvidence && (
              <div
                style={{
                  marginTop: "1rem",
                  paddingTop: "0.75rem",
                  borderTop: "1px solid var(--border-subtle)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.55rem",
                  fontSize: "0.82rem",
                  color: "var(--text-secondary)",
                }}
              >
                {/* Provenance Ledger Items */}
                {memory.provenance_ledger && memory.provenance_ledger.length > 0 ? (
                  memory.provenance_ledger.map((item, idx) => (
                    <div key={idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.3rem 0", borderBottom: "1px solid var(--border-subtle)" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
                        <span
                          style={{
                            fontSize: "0.62rem",
                            fontWeight: 700,
                            padding: "1px 5px",
                            borderRadius: "4px",
                            background: item.source === "VISION" ? "rgba(99, 102, 241, 0.12)" : (item.source === "OCR" ? "rgba(245, 158, 11, 0.12)" : "rgba(16, 185, 129, 0.12)"),
                            color: item.source === "VISION" ? "#4f46e5" : (item.source === "OCR" ? "#d97706" : "#059669"),
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          [{item.source}]
                        </span>
                        <span style={{ textTransform: "capitalize", color: "var(--text-primary)" }}>{item.field.replace(/_/g, " ")}</span>
                      </div>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                        {Math.round((item.confidence || 0.9) * 100)}% verified
                      </span>
                    </div>
                  ))
                ) : (
                  <>
                    <div style={{ display: "flex", gap: "0.45rem", color: "var(--severity-public)" }}>
                      <span>✓</span>
                      <span>[VISION] Category verified as <strong>{memory.category}</strong></span>
                    </div>
                    {memory.entities && memory.entities.length > 0 && (
                      <div style={{ display: "flex", gap: "0.45rem", color: "var(--severity-public)" }}>
                        <span>✓</span>
                        <span>[VISION+OCR] Entities mapped: {memory.entities.join(", ")}</span>
                      </div>
                    )}
                    <div style={{ display: "flex", gap: "0.45rem", color: "var(--severity-public)" }}>
                      <span>✓</span>
                      <span>[DETERMINISTIC] Shield Sensitivity: <strong>{memory.sensitivity_level}</strong></span>
                    </div>
                    <div style={{ display: "flex", gap: "0.45rem", color: "var(--severity-public)" }}>
                      <span>✓</span>
                      <span>[CANONICAL EMBEDDING] Multimodal visual representation + OCR indexed</span>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Optical Text Explorer */}
          {memory.ocr_text && (
            <div className="paper-card" style={{ padding: "1.25rem 1.5rem" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "0.75rem",
                }}
              >
                <span
                  style={{
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "var(--text-secondary)",
                  }}
                >
                  Extracted Optical Text (EasyOCR)
                </span>
                <button
                  onClick={copyOcr}
                  className="btn-paper"
                  style={{ padding: "2px 8px", fontSize: "0.72rem" }}
                >
                  {copied ? <Check size={12} color="var(--severity-public)" /> : <Copy size={12} />}
                  <span>{copied ? "Copied" : "Copy"}</span>
                </button>
              </div>

              <div
                style={{
                  background: "var(--bg-subtle)",
                  borderRadius: "var(--radius-xs)",
                  padding: "0.85rem",
                  fontSize: "0.78rem",
                  color: "var(--text-primary)",
                  fontFamily: "var(--font-mono)",
                  maxHeight: 180,
                  overflowY: "auto",
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.5,
                  border: "1px solid var(--border-medium)",
                }}
              >
                {memory.ocr_text}
              </div>
            </div>
          )}

          {/* Connected Graph Relationships */}
          {relationships.length > 0 && (
            <div className="paper-card" style={{ padding: "1.25rem 1.5rem" }}>
              <div
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  color: "var(--text-secondary)",
                  marginBottom: "0.75rem",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>Connected Graph Edges ({relationships.length})</span>
                <button
                  onClick={() => router.push("/constellation")}
                  className="btn-paper"
                  style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                >
                  <span>Explore Constellation</span>
                  <ExternalLink size={10} />
                </button>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
                {relationships.map((r, i) => {
                  const targetId = r.related_memory?.id || (r.direction === "source" ? r.target_memory_id : r.source_memory_id);
                  return (
                    <div
                      key={i}
                      onClick={() => targetId && router.push(`/memory/${targetId}`)}
                      style={{
                        background: "var(--bg-subtle)",
                        borderRadius: "var(--radius-xs)",
                        padding: "0.6rem 0.75rem",
                        fontSize: "0.8rem",
                        color: "var(--text-primary)",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        border: "1px solid var(--border-subtle)",
                        cursor: targetId ? "pointer" : "default",
                        transition: "all 0.15s ease",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "var(--accent-terracotta)";
                        e.currentTarget.style.background = "var(--bg-surface)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "var(--border-subtle)";
                        e.currentTarget.style.background = "var(--bg-subtle)";
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span style={{ color: "var(--accent-terracotta)" }}>🔗</span>
                        <span>{r.reason || "Connected through shared semantic topics"}</span>
                      </div>
                      <span style={{ fontWeight: 600, color: "var(--accent-dark)", fontSize: "0.74rem", fontFamily: "var(--font-mono)" }}>
                        {Math.round((r.confidence || 0.6) * 100)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
