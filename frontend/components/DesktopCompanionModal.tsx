"use client";
import React, { useState, useEffect } from "react";
import {
  Monitor,
  Shield,
  EyeOff,
  Copy,
  Plus,
  Trash2,
  CheckCircle2,
  X,
  Keyboard,
  Lock,
} from "lucide-react";
import { getDesktopStatus, updateDesktopConfig } from "@/lib/api";

interface DesktopCompanionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DesktopCompanionModal({ isOpen, onClose }: DesktopCompanionModalProps) {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [newApp, setNewApp] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await getDesktopStatus();
      setStatus(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const config = status?.config || {
    capture_enabled: true,
    is_paused: false,
    private_mode: false,
    hotkey: "Ctrl+Shift+A",
    excluded_applications: ["1Password", "Bitwarden", "KeePass", "Chrome Incognito", "Banking"],
    clipboard_memory_enabled: true,
    total_os_captures: 0,
  };

  const handleToggle = async (key: string, value: boolean) => {
    setSaving(true);
    try {
      await updateDesktopConfig({ [key]: value });
      await fetchStatus();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleAddExcludedApp = async () => {
    if (!newApp.trim()) return;
    const updated = [...config.excluded_applications, newApp.trim()];
    setSaving(true);
    try {
      await updateDesktopConfig({ excluded_applications: updated });
      setNewApp("");
      await fetchStatus();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveExcludedApp = async (appToRemove: string) => {
    const updated = config.excluded_applications.filter((a: string) => a !== appToRemove);
    setSaving(true);
    try {
      await updateDesktopConfig({ excluded_applications: updated });
      await fetchStatus();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(30, 25, 20, 0.45)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: "1rem",
      }}
      onClick={onClose}
    >
      <div
        className="paper-card"
        style={{
          width: "100%",
          maxWidth: 580,
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-md)",
          padding: "1.75rem",
          boxShadow: "var(--shadow-raised)",
          border: "1px solid var(--border-medium)",
          display: "flex",
          flexDirection: "column",
          gap: "1.25rem",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: "var(--radius-sm)",
                background: "var(--accent-light)",
                border: "1px solid var(--accent-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Monitor size={20} color="var(--accent-terracotta)" />
            </div>
            <div>
              <h2 style={{ fontSize: "1.15rem", fontFamily: "var(--font-serif)", fontWeight: 600, color: "var(--text-primary)" }}>
                AURA Desktop Companion
              </h2>
              <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                OS-Level Visual Memory Layer & Privacy Gate
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn-paper"
            style={{ padding: "0.4rem", borderRadius: "50%" }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Status Banner */}
        <div
          style={{
            padding: "0.85rem 1rem",
            borderRadius: "var(--radius-sm)",
            background: "var(--bg-subtle)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "var(--severity-public)",
                boxShadow: "0 0 8px var(--severity-public)",
              }}
            />
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)" }}>
              Global Hotkey Capture Active
            </span>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              fontSize: "0.78rem",
              fontFamily: "var(--font-mono)",
              background: "var(--bg-surface)",
              padding: "3px 8px",
              borderRadius: "var(--radius-xs)",
              border: "1px solid var(--border-medium)",
              color: "var(--accent-dark)",
              fontWeight: 600,
            }}
          >
            <Keyboard size={13} />
            <span>{config.hotkey}</span>
          </div>
        </div>

        {/* Privacy Gate Controls */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Privacy Gate & Controls
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.75rem 0.85rem",
              background: "var(--bg-subtle)",
              borderRadius: "var(--radius-xs)",
              border: "1px solid var(--border-subtle)",
            }}
          >
            <div>
              <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--text-primary)" }}>
                OS Screenshot Ingestion
              </div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>
                Capture screen with active window context on hotkey
              </div>
            </div>
            <input
              type="checkbox"
              checked={config.capture_enabled}
              onChange={(e) => handleToggle("capture_enabled", e.target.checked)}
              disabled={saving}
              style={{ cursor: "pointer", width: 16, height: 16, accentColor: "var(--accent-terracotta)" }}
            />
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.75rem 0.85rem",
              background: "var(--bg-subtle)",
              borderRadius: "var(--radius-xs)",
              border: "1px solid var(--border-subtle)",
            }}
          >
            <div>
              <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: 5 }}>
                <EyeOff size={14} color="var(--accent-terracotta)" />
                <span>Private Mode</span>
              </div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>
                Temporarily pause all ingestion and context tracking
              </div>
            </div>
            <input
              type="checkbox"
              checked={config.private_mode}
              onChange={(e) => handleToggle("private_mode", e.target.checked)}
              disabled={saving}
              style={{ cursor: "pointer", width: 16, height: 16, accentColor: "var(--accent-terracotta)" }}
            />
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.75rem 0.85rem",
              background: "var(--bg-subtle)",
              borderRadius: "var(--radius-xs)",
              border: "1px solid var(--border-subtle)",
            }}
          >
            <div>
              <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: 5 }}>
                <Copy size={14} color="var(--accent-terracotta)" />
                <span>Smart Clipboard Memory</span>
              </div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>
                Correlate recently copied URLs and notes with captures
              </div>
            </div>
            <input
              type="checkbox"
              checked={config.clipboard_memory_enabled}
              onChange={(e) => handleToggle("clipboard_memory_enabled", e.target.checked)}
              disabled={saving}
              style={{ cursor: "pointer", width: 16, height: 16, accentColor: "var(--accent-terracotta)" }}
            />
          </div>
        </div>

        {/* Application Exclusion List */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", display: "flex", alignItems: "center", gap: 4 }}>
              <Lock size={12} />
              <span>Excluded Applications ({config.excluded_applications?.length || 0})</span>
            </div>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", maxHeight: 110, overflowY: "auto", padding: "0.2rem 0" }}>
            {config.excluded_applications?.map((app: string, idx: number) => (
              <span
                key={idx}
                style={{
                  fontSize: "0.74rem",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-xs)",
                  background: "var(--bg-subtle)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem",
                  color: "var(--text-secondary)",
                }}
              >
                <span>{app}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveExcludedApp(app)}
                  style={{ background: "none", border: "none", cursor: "pointer", padding: 0, color: "var(--text-muted)" }}
                >
                  <X size={11} />
                </button>
              </span>
            ))}
          </div>

          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.2rem" }}>
            <input
              type="text"
              placeholder="Add application name (e.g. Chrome, KeePass)..."
              value={newApp}
              onChange={(e) => setNewApp(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddExcludedApp()}
              style={{
                flex: 1,
                fontSize: "0.78rem",
                padding: "0.4rem 0.65rem",
                borderRadius: "var(--radius-xs)",
                border: "1px solid var(--border-medium)",
                background: "var(--bg-surface)",
                outline: "none",
              }}
            />
            <button
              type="button"
              onClick={handleAddExcludedApp}
              className="btn-paper"
              style={{ fontSize: "0.78rem", padding: "0.4rem 0.75rem", display: "flex", alignItems: "center", gap: 4 }}
            >
              <Plus size={13} />
              <span>Add</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "0.5rem", borderTop: "1px solid var(--border-subtle)", fontSize: "0.74rem", color: "var(--text-muted)" }}>
          <span>Run <code>python desktop_agent.py</code> to capture from OS</span>
          <button
            type="button"
            onClick={onClose}
            className="btn-paper primary"
            style={{ fontSize: "0.8rem", padding: "0.4rem 1rem" }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
