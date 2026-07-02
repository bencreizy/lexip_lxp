# lexipmetrics.py
# Metrics Module for tracking processing throughput and performance telemetry

import time
import numpy as np

class LexipMetrics:
    """
    Performance tracking telemetry framework for the Lexip processing stack.
    Monitors algorithmic compression ratios, throughput speeds, and data density optimization.
    """
    def __init__(self):
        self.reset_metrics()

    def reset_metrics(self):
        """Zeroes all tracking channels to restore a clean baseline context."""
        self.timers = {}
        self.compression_logs = []
        self.processed_points = 0

    def start_timer(self, operational_layer: str):
        """Anchors an execution timestamp mark to calculate processing latency."""
        self.timers[str(operational_layer)] = time.perf_counter()

    def stop_timer(self, operational_layer: str) -> float:
        """Stops the targeted operational timer, returning total execution duration."""
        label = str(operational_layer)
        if label not in self.timers:
            return 0.0
        duration = time.perf_counter() - self.timers[label]
        self.timers[label] = duration
        return float(duration)

    def log_compression_ratio(self, uncompressed_bytes: int, compressed_bytes: int):
        """Computes and logs systemic volume retention data for pipeline metrics."""
        u_bytes = max(1, int(uncompressed_bytes))
        c_bytes = int(compressed_bytes)
        ratio = u_bytes / max(1, c_bytes)
        savings = (1.0 - (c_bytes / u_bytes)) * 100.0
        
        self.compression_logs.append({
            "uncompressed": u_bytes,
            "compressed": c_bytes,
            "ratio": float(ratio),
            "savings_pct": float(savings)
        })

    def track_points(self, point_count: int):
        """Increments total geometric vector units processed through system loops."""
        self.processed_points += max(0, int(point_count))

    def generate_telemetry_report(self) -> dict:
        """Compiles tracked metrics into a structured operational performance log."""
        ratios = [log["ratio"] for log in self.compression_logs]
        avg_ratio = float(np.mean(ratios)) if ratios else 1.0
        
        return {
            "total_processed_points": self.processed_points,
            "active_layer_latencies": {k: float(v) for k, v in self.timers.items() if isinstance(v, float)},
            "average_compression_ratio": avg_ratio,
            "compression_operations_count": len(self.compression_logs)
        }
