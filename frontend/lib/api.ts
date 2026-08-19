const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T = any>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

export async function uploadMemory(file: File): Promise<Memory> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API}/api/memories/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export const apiUploadFile = uploadMemory;
export const API_URL = API;

export function getThumbnailUrl(memoryId: string): string {
  return `${API}/api/memories/${memoryId}/thumbnail`;
}

export function getImageUrl(memoryId: string): string {
  return `${API}/api/memories/${memoryId}/image`;
}

export async function searchByImage(file: File, topK: number = 5) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API}/api/memories/search-by-image?top_k=${topK}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Image search failed");
  }
  return res.json();
}


export async function getMemory(id: string): Promise<Memory> {
  return apiFetch(`/api/memories/${id}`);
}
export const apiGetMemory = getMemory;

export async function getMemories(params?: {
  page?: number;
  limit?: number;
  category?: string;
  constellation?: string;
  sensitivity?: string;
  sensitivity_level?: string;
  source_type?: string;
  sort_by?: string;
  search?: string;
}) {
  const q = new URLSearchParams();
  if (params?.page) q.set("page", String(params.page));
  if (params?.limit) q.set("per_page", String(params.limit));
  if (params?.category) q.set("category", params.category);
  if (params?.constellation) q.set("constellation", params.constellation);
  const sens = params?.sensitivity_level || params?.sensitivity;
  if (sens) q.set("sensitivity", sens);
  if (params?.source_type) q.set("source_type", params.source_type);
  if (params?.sort_by) q.set("sort_by", params.sort_by);
  if (params?.search) q.set("search", params.search);

  const data = await apiFetch(`/api/memories?${q.toString()}`);
  return {
    items: data.memories || data.items || [],
    total: data.total || 0,
    page: data.page || 1,
    pages: data.pages || 1,
  };
}

export interface ProviderInfo {
  provider: string;
  model: string;
  status: string;
  is_live: boolean;
}

export interface EvidenceTraceItem {
  memory_id: string;
  title: string;
  category: string;
  document_type?: string;
  visual_evidence: string;
  ocr_evidence: string;
  relationship_evidence: string;
  provenance: string[];
  confidence: number;
  sensitivity_level: string;
}

export interface Memory {
  id: string;
  original_filename: string;
  thumbnail_url: string;
  image_url: string;
  summary: string;
  visual_summary?: string;
  visual_details?: {
    theme?: string;
    layout_structure?: string;
    color_palette?: string[];
    has_charts_or_graphs?: boolean;
    has_tables?: boolean;
    has_diagram_flow?: boolean;
    has_code_syntax?: boolean;
    has_error_state?: boolean;
  };
  visual_objects?: string[];
  visual_entities?: string[];
  multimodal_provider?: string;
  multimodal_status?: string;
  provenance_ledger?: Array<{ field: string; source: string; confidence: number }>;
  category: string;
  sensitivity_level: "PUBLIC" | "PERSONAL" | "SENSITIVE" | "CRITICAL";
  importance_score: number;
  processing_status: string;
  is_locked: boolean;
  is_redacted: boolean;
  created_at: string;
  updated_at: string;
  application: string;
  window_title?: string;
  source_type?: "upload" | "desktop_capture" | "clipboard" | string;
  clipboard_context?: string;
  captured_at?: string;
  similarity_score?: number;

  topics?: string[];
  entities?: string[];
  ocr_text?: string;
  ocr_raw?: string;
  objects?: string[];
  document_type?: string;
  sensitivity_findings?: Array<{ type: string; match: string; severity: string }>;
  relevance_score?: number;
  visual_evidence?: string;
  score_breakdown?: Record<string, number>;
  _protected?: boolean;
  _expanded?: boolean;
}

export async function getDesktopStatus(): Promise<{
  status: string;
  config: {
    capture_enabled: boolean;
    is_paused: boolean;
    private_mode: boolean;
    hotkey: string;
    excluded_applications: string[];
    clipboard_memory_enabled: boolean;
    total_os_captures: number;
  };
  metrics: {
    total_desktop_captures: number;
    privacy_gate_active: boolean;
    clipboard_tracking_active: boolean;
  };
}> {
  return apiFetch("/api/desktop/status");
}

export async function updateDesktopConfig(config: {
  capture_enabled?: boolean;
  is_paused?: boolean;
  private_mode?: boolean;
  clipboard_memory_enabled?: boolean;
  excluded_applications?: string[];
}) {
  return apiFetch("/api/desktop/config", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export interface SearchResult {
  query: string;
  total: number;
  sensitive_count: number;
  provider_info?: ProviderInfo;
  results: Memory[];
}

export interface InvestigationResult {
  investigation_id: string;
  query: string;
  answer: string;
  confidence: number;
  key_findings: string[];
  suggested_actions: string[];
  plan: Array<{ step: string; label: string; status: string }>;
  provider_info?: ProviderInfo;
  evidence_trace?: EvidenceTraceItem[];
  results: Memory[];
  clusters: Array<{ name: string; category: string; memory_ids: string[]; count: number }>;
  relationships: Array<{ source: string; target: string; type: string; confidence: number; reason: string }>;
  stats: { total_found: number; clusters: number; relationships: number; sensitive_protected: number; expanded: number; multimodal_verified?: number };
}

export const SENSITIVITY_CONFIG = {
  PUBLIC: { label: "Safe", icon: "🟢", className: "badge-public" },
  PERSONAL: { label: "Personal", icon: "🟡", className: "badge-personal" },
  SENSITIVE: { label: "Sensitive", icon: "🟠", className: "badge-sensitive" },
  CRITICAL: { label: "Critical", icon: "🔴", className: "badge-critical" },
} as const;

export const CATEGORY_ICONS: Record<string, string> = {
  receipt: "🧾",
  invoice: "📄",
  recipe: "🍳",
  code: "💻",
  research: "🔬",
  chart: "📊",
  diagram: "🗺️",
  map: "📍",
  product: "📦",
  conversation: "💬",
  website: "🌐",
  presentation: "📊",
  document: "📝",
  terminal: "⌨️",
  ide: "💻",
  travel: "✈️",
  finance: "💰",
  shopping: "🛍️",
  education: "📚",
  credentials: "🔑",
  settings: "⚙️",
  other: "📷",
};
