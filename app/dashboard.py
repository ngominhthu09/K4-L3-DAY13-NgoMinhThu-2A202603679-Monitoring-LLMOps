from __future__ import annotations

import html
import json
from pathlib import Path
from statistics import mean
from typing import Any

LOG_PATH = Path("data/logs.jsonl")


def _records() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    index = max(0, min(len(items) - 1, round((percentile / 100) * len(items) + 0.5) - 1))
    return items[index]


def _card(title: str, unit: str, threshold: str, values: list[tuple[str, str]]) -> str:
    rows = "".join(
        f"<div class='metric'><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>"
        for label, value in values
    )
    return (
        "<section class='card'>"
        f"<h2>{html.escape(title)}</h2><p class='unit'>{html.escape(unit)}</p>"
        f"{rows}<p class='threshold'>Threshold: {html.escape(threshold)}</p></section>"
    )


def render_dashboard() -> str:
    records = _records()
    responses = [row for row in records if row.get("event") == "response_sent"]
    requests = [row for row in records if row.get("event") == "request_received"]
    failures = [row for row in records if row.get("event") == "request_failed"]
    latencies = [float(row["latency_ms"]) for row in responses if "latency_ms" in row]
    ttfts = [float(row["ttft_ms"]) for row in responses if "ttft_ms" in row]
    costs = [float(row.get("cost_usd", 0)) for row in responses]
    token_in = sum(int(row.get("tokens_in", 0)) for row in responses)
    token_out = sum(int(row.get("tokens_out", 0)) for row in responses)
    quality = [float(row["quality_score"]) for row in responses if "quality_score" in row]
    tool_events = [row for row in records if row.get("tool_success") is not None]
    tool_success = (sum(row.get("tool_success") is True for row in tool_events) / len(tool_events) * 100) if tool_events else 0.0
    error_rate = (len(failures) / len(requests) * 100) if requests else 0.0

    cards = [
        _card("Latency percentiles and TTFT", "ms", "P95 ≤ 2000 ms", [
            ("P50", f"{_percentile(latencies, 50):.0f} ms"),
            ("P95", f"{_percentile(latencies, 95):.0f} ms"),
            ("P99", f"{_percentile(latencies, 99):.0f} ms"),
            ("TTFT P95", f"{_percentile(ttfts, 95):.0f} ms"),
        ]),
        _card("Request traffic", "requests/minute", "≥ 1 request/minute", [
            ("Requests", str(len(requests))), ("Rate", f"{len(requests) / 60:.2f} req/min"),
        ]),
        _card("Error rate and retrieval success", "percent", "Error rate ≤ 2%", [
            ("Error rate", f"{error_rate:.1f}%"), ("Retrieval success", f"{tool_success:.1f}%"),
        ]),
        _card("Cost over time", "USD", "Total ≤ $2.50", [
            ("Total", f"${sum(costs):.4f}"), ("Average", f"${mean(costs):.4f}" if costs else "$0.0000"),
        ]),
        _card("Input and output tokens", "tokens", "Total ≤ 50,000", [
            ("Input", f"{token_in:,}"), ("Output", f"{token_out:,}"),
        ]),
        _card("Quality proxy", "score 0–1", "Mean ≥ 0.75", [
            ("Average", f"{mean(quality):.2f}" if quality else "0.00"), ("Responses", str(len(responses))),
        ]),
    ]
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><meta http-equiv='refresh' content='30'>
<title>LLMOps monitoring dashboard</title><style>
body{{font-family:system-ui,sans-serif;background:#f5f7fb;color:#182230;margin:0;padding:32px}}
header{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:24px}}
h1{{margin:0;font-size:28px}} .meta,.unit,.threshold{{color:#596579}} .grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
.card{{background:#fff;border:1px solid #dce3ee;border-radius:12px;padding:20px;box-shadow:0 2px 8px #15243a0d}} h2{{font-size:17px;margin:0 0 4px}}
.unit{{margin:0 0 18px;font-size:13px}} .metric{{display:flex;justify-content:space-between;padding:8px 0;border-top:1px solid #eef1f5}} strong{{font-variant-numeric:tabular-nums}}
.threshold{{background:#ecfdf3;color:#087443;border-radius:6px;padding:7px 9px;margin:16px 0 0;font-size:13px}} @media(max-width:800px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><header><div><h1>Day 13 LLMOps Monitoring</h1><p class='meta'>Structured-log dashboard · source: data/logs.jsonl</p></div><p class='meta'>Time range: last 60 minutes · Refresh: 30 seconds</p></header><main class='grid'>{''.join(cards)}</main></body></html>"""
