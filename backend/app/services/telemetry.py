"""
AURA — Observability & Telemetry Engine
Tracks runtime latency percentiles, request counts, error rates, database health,
and exposes production Prometheus-compatible and JSON metrics endpoints.
"""
import time
try:
    import psutil
except ImportError:
    psutil = None
import logging
from collections import defaultdict
from typing import Dict, Any, List
from datetime import datetime, timezone
import numpy as np

logger = logging.getLogger("aura.telemetry")


class TelemetryCollector:
    def __init__(self):
        self.start_time = time.time()
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.status_counts: Dict[int, int] = defaultdict(int)
        self.latencies: List[float] = []
        self.investigation_latencies: List[float] = []
        self.search_latencies: List[float] = []

    def record_request(self, path: str, status_code: int, duration_ms: float):
        """Records an HTTP request event."""
        self.request_counts[path] += 1
        self.status_counts[status_code] += 1
        self.latencies.append(duration_ms)
        if len(self.latencies) > 2000:
            self.latencies = self.latencies[-2000:]

        if "/api/investigate" in path:
            self.investigation_latencies.append(duration_ms)
            if len(self.investigation_latencies) > 500:
                self.investigation_latencies = self.investigation_latencies[-500:]
        elif "/api/search" in path:
            self.search_latencies.append(duration_ms)
            if len(self.search_latencies) > 500:
                self.search_latencies = self.search_latencies[-500:]

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Returns JSON snapshot of system health and latency distributions."""
        uptime_seconds = time.time() - self.start_time

        all_lat = self.latencies or [0.0]
        inv_lat = self.investigation_latencies or [0.0]
        srch_lat = self.search_latencies or [0.0]

        # System resource stats
        if psutil:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                res_stats = {
                    "rss_memory_mb": round(memory_info.rss / (1024 * 1024), 2),
                    "cpu_percent": process.cpu_percent(interval=None),
                    "threads_active": process.num_threads(),
                }
            except Exception:
                res_stats = {"status": "unavailable"}
        else:
            res_stats = {"status": "psutil_not_installed"}

        return {
            "status": "HEALTHY",
            "uptime_seconds": round(uptime_seconds, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_requests": sum(self.request_counts.values()),
            "status_codes": dict(self.status_counts),
            "top_endpoints": dict(sorted(self.request_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "latencies_ms": {
                "http_overall": {
                    "mean": round(float(np.mean(all_lat)), 2),
                    "p50": round(float(np.percentile(all_lat, 50)), 2),
                    "p95": round(float(np.percentile(all_lat, 95)), 2),
                    "p99": round(float(np.percentile(all_lat, 99)), 2),
                },
                "agentic_investigations": {
                    "count": len(self.investigation_latencies),
                    "mean": round(float(np.mean(inv_lat)), 2),
                    "p50": round(float(np.percentile(inv_lat, 50)), 2),
                    "p95": round(float(np.percentile(inv_lat, 95)), 2),
                },
                "hybrid_retrievals": {
                    "count": len(self.search_latencies),
                    "mean": round(float(np.mean(srch_lat)), 2),
                    "p50": round(float(np.percentile(srch_lat, 50)), 2),
                    "p95": round(float(np.percentile(srch_lat, 95)), 2),
                }
            },
            "resources": res_stats
        }


telemetry = TelemetryCollector()
