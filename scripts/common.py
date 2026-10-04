"""Shared data model: findings, severity grading, thresholds, step log."""
from __future__ import annotations

import json
import os
import time

SEVERITY_ORDER = ["ok", "moderate", "high", "critical"]
SEVERITY_ZH = {"ok": "可接受", "moderate": "中等", "high": "高风险", "critical": "致命", "unknown": "证据不足"}
SCOPE_ZH = {"isolated": "零星", "local": "局部", "widespread": "大面积", None: "未知（只有极值）"}

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "thresholds.json"), encoding="utf-8") as _f:
    THRESHOLDS = json.load(_f)


def worst(levels):
    levels = [l for l in levels if l]
    if not levels:
        return "ok"
    return max(levels, key=SEVERITY_ORDER.index)


def grade(source: str, metric: str, value) -> str:
    """Grade a single extreme value against thresholds.json."""
    t = THRESHOLDS.get(source, {}).get(metric)
    if t is None or value is None:
        return "ok"
    worse = (lambda v, th: v > th) if t["direction"] == "max" else (lambda v, th: v < th)
    for level in ("critical", "high", "moderate"):
        th = t.get(level)
        if th is not None and worse(value, th):
            return level
    return "ok"


def scope_of(n_bad, n_total):
    if n_bad is None or not n_total:
        return None, None
    frac = n_bad / n_total
    s = THRESHOLDS["scope"]
    if frac < s["isolated_max_fraction"]:
        return frac, "isolated"
    if frac < s["local_max_fraction"]:
        return frac, "local"
    return frac, "widespread"


def finding(metric, name_zh, *, category="quality", value=None, stat=None, unit="",
            severity=None, source=None, n_bad=None, n_total=None, total_kind="单元",
            location=None, raw=None, definition=None, advice=None, threshold_used=None):
    """Build one finding dict. If severity is None it is graded from thresholds."""
    if severity is None:
        severity = grade(source, metric, value) if source else "ok"
    frac, scope = scope_of(n_bad, n_total)
    if threshold_used is None and source:
        t = THRESHOLDS.get(source, {}).get(metric)
        if t:
            threshold_used = {k: t[k] for k in ("direction", "moderate", "high", "critical") if k in t}
    return {
        "metric": metric, "name_zh": name_zh, "category": category,
        "value": value, "stat": stat, "unit": unit,
        "severity": severity, "severity_zh": SEVERITY_ZH[severity],
        "n_bad": n_bad, "n_total": n_total, "total_kind": total_kind,
        "fraction": frac, "scope": scope, "scope_zh": SCOPE_ZH[scope],
        "location": location, "raw": raw, "definition": definition,
        "threshold": threshold_used, "advice": advice or [],
    }


class StepLog:
    """Timestamped log of what the checker actually did (goes into the report)."""

    def __init__(self):
        self.t0 = time.time()
        self.items = []

    def add(self, msg: str, cmd: str | None = None, status: str = "ok"):
        self.items.append({"t": round(time.time() - self.t0, 2), "msg": msg, "cmd": cmd, "status": status})
