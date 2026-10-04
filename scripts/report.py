"""Render the unified result as a Markdown report (Chinese) + JSON."""
from __future__ import annotations

import datetime as dt
import json
import re

from common import SEVERITY_ZH, worst

SOURCE_ZH = {"openfoam": "OpenFOAM", "fluent": "ANSYS Fluent", "gmsh": "Gmsh", "generic": "通用格式（meshio）",
             "unknown": "未知"}
ICON = {"critical": "⛔", "high": "🔴", "moderate": "🟡", "ok": "🟢", "unknown": "⚪"}
VERDICT = {
    "critical": "存在致命问题，**不应开始计算**，先修复网格。",
    "high": "已检查指标存在高风险偏离；需结合实际边界条件及目标量验证其影响。",
    "moderate": "已检查指标存在中等问题，应结合当前算例的近壁要求和数值设置决定是否试算。",
    "ok": "已执行的网格质量指标未见超限；完整 CFD 适用性见下方证据检查。",
    "unknown": "没有取得足够的检查数据，当前无法判断网格是否合格。",
}


def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        if v == 0 or 1e-3 <= abs(v) < 1e5:
            return f"{v:.4g}"
        return f"{v:.3e}"
    return str(v)


def _scope(f):
    if f["n_bad"] is None:
        return "未知（只有极值）"
    if f["n_bad"] == 0:
        return "0"
    s = f"{f['n_bad']} 个{f['total_kind']}"
    if f["fraction"] is not None:
        s += f"（{f['fraction'] * 100:.3g}%，{f['scope_zh']}）"
    return s


def _location_lines(loc):
    out = []
    if not loc:
        return out
    if loc.get("zones"):
        out.append("所在区域：" + "，".join(f"{z['zone']}（{z['count']}）" for z in loc["zones"]))
    if loc.get("near_patches"):
        out.append("靠近边界：" + "，".join(f"{p['patch']}（{p['count']}）" for p in loc["near_patches"]))
    if loc.get("bbox_min"):
        out.append(f"包围盒：{loc['bbox_min']} → {loc['bbox_max']}")
    if loc.get("worst"):
        w = loc["worst"][0]
        s = f"最差：值 {_fmt(w.get('value'))}"
        if w.get("xyz"):
            s += f"，坐标 {w['xyz']}"
        if w.get("zone") is not None:
            s += f"，zone {w['zone']}"
        if w.get("id") is not None:
            s += f"，编号 {w['id']}"
        if w.get("nearest_patch"):
            s += f"，最近边界 {w['nearest_patch']}（距离 {_fmt(w.get('dist_to_patch'))}）"
        out.append(s)
    return out


def render(res: dict, det: dict, steps, input_path: str) -> tuple[str, dict]:
    findings = res.get("findings", [])
    overall = worst([f["severity"] for f in findings])
    if not findings:
        overall = "unknown"
    res["overall"] = overall
    cfd = res.get("cfd")
    if overall == "critical":
        readiness = "必须修复网格"
    elif overall == "high":
        readiness = "高风险指标待复核，关键结果证据不足" if cfd and cfd.get("missing") else "高风险指标待复核"
    elif overall == "unknown":
        readiness = "证据不足"
    elif cfd and cfd.get("missing"):
        readiness = "关键 CFD 证据不足"
    elif cfd and all(k in cfd.get("solution_checks", {}) for k in ("mass_balance", "monitor_drift", "grid_sensitivity")) \
            and any(e.get("kind") == "solver_result" for e in cfd.get("evidence", [])):
        readiness = "现有证据支持当前用途；按目标误差要求审阅结果"
    elif cfd and any(e.get("kind") == "solver_result" for e in cfd.get("evidence", [])):
        readiness = "近壁复核已完成；仍需结果与网格敏感性验证"
    elif not cfd:
        readiness = "基础质量已检查；CFD 适用性待工况核对"
    else:
        readiness = "可进入试算；需复核实际 y⁺ 与结果"
    res["readiness"] = readiness
    info = res.get("mesh_info", {})
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    L = []
    L.append("# 网格质量检查报告\n")
    L.append(f"- 生成时间：{now}")
    L.append(f"- 输入：`{input_path}`")
    L.append(f"- 识别结果：**{SOURCE_ZH.get(res.get('source'), res.get('source'))}**（{det.get('kind')}）——"
             + "；".join(det.get("evidence", [])))
    if res.get("route_note"):
        L.append(f"- 说明：{res['route_note']}")
    L.append(f"\n## 结论：{ICON[overall]} {SEVERITY_ZH[overall]}\n")
    L.append(VERDICT[overall] + "\n")
    L.append(f"CFD 适用性判断：**{readiness}**。\n")
    if res.get("extra", {}).get("checkmesh_verdict"):
        L.append(f"checkMesh 自身结论：`{res['extra']['checkmesh_verdict']}`\n")

    # 1 basic info
    L.append("## 1. 网格基本信息\n")
    rows = [("单元数", info.get("n_cells")), ("面数", info.get("n_faces")), ("内部面数", info.get("n_internal_faces")),
            ("节点数", info.get("n_points")), ("维度", f"{info['n_dims']}D" if info.get("n_dims") else None),
            ("OpenFOAM 版本", info.get("version"))]
    if info.get("cell_types"):
        rows.append(("单元类型", "，".join(f"{k} {v}" for k, v in info["cell_types"].items())))
    if info.get("bounds"):
        rows.append(("包围盒", f"{[round(x, 6) for x in info['bounds'][0]]} → {[round(x, 6) for x in info['bounds'][1]]}"))
    for key, zh in (("cell_volume", "单元体积"), ("cell_area", "单元面积")):
        if info.get(key):
            rows.append((zh, f"最小 {_fmt(info[key].get('min'))}，最大 {_fmt(info[key].get('max'))}"))
    if info.get("patches"):
        rows.append(("边界", "，".join(f"{p['name']}" + (f"[{p['type']}]" if p.get("type") else "") + f"({p['nFaces']})"
                                     for p in info["patches"])))
    if info.get("zones") and len(info["zones"]) > 1 or (info.get("zones") and "（未分组）" not in info["zones"]):
        rows.append(("体区域", "，".join(f"{k}({v})" for k, v in info["zones"].items())))
    if info.get("boundary_groups"):
        rows.append(("边界分组", "，".join(f"{k}({v})" for k, v in info["boundary_groups"].items())))
    L.append("| 项目 | 值 |\n|---|---|")
    for k, v in rows:
        if v is not None and v != "":
            L.append(f"| {k} | {v} |")
    L.append("")

    # 2 critical
    crit = [f for f in findings if f["category"] == "critical"]
    L.append("## 2. 致命/拓扑问题\n")
    if not crit:
        L.append("本次已执行的检查中未报告致命拓扑问题；未执行的检查见局限与说明。\n")
    for f in crit:
        L.append(f"- {ICON[f['severity']]} **{f['name_zh']}**（{f['severity_zh']}）：范围 {_scope(f)}"
                 + (f"，极值 {_fmt(f['value'])}" if f["value"] is not None else ""))
        if f.get("note"):
            L.append(f"  - {f['note']}")
        if f.get("raw"):
            L.append(f"  - 原始输出：`{f['raw']}`")
        for line in _location_lines(f.get("location")):
            L.append(f"  - {line}")
    L.append("")

    if cfd:
        L.append("## 4. CFD 适用性与近壁检查\n")
        missing = cfd.get("missing", [])
        L.append("当前范围：OpenFOAM 单相 RANS 内流。计算前 y⁺ 为估算，已有试算的 yPlus 场为求解后证据。\n")
        setup = cfd.get("case_setup", {})
        if setup:
            L.append(f"算例识别：求解器 {setup.get('application', '未读到')}；湍流类型 {setup.get('simulation_type', '未读到')}；"
                     f"模型 {setup.get('turbulence_model', '未读到')}。\n")
        L.append("| 壁面 | 首层中心距：最小/中位/P95 | y⁺ 证据 | y⁺：P05/中位/P95 | 目标 | 区间外面积 |\n|---|---|---|---|---|---|")
        for name, check in cfd.get("wall_checks", {}).items():
            geom, yp = check.get("geometry", {}), check.get("yplus", {})
            ds = "/".join(_fmt(geom.get(k)) for k in ("distance_min", "distance_median", "distance_p95"))
            ys = "/".join(_fmt(yp.get(k)) for k in ("p05", "median", "p95"))
            target = check.get("target_yplus")
            outside = f"{yp['outside_area_fraction']:.1%}" if "outside_area_fraction" in yp else "—"
            L.append(f"| {name} | {ds} | {check.get('provenance', '待补全')} | {ys} | "
                     f"{target if target else '待指定'} | {outside} |")
        if not cfd.get("wall_checks"):
            L.append("| — | — | — | — | — | — |")
        L.append("\n表中 y⁺ 目标是所选工况的筛查区间，区间外比例表示目标偏离，并不单独证明求解失败或结果不可靠。首层中心距按单元中心到边界面平面的法向投影计算。近壁层数与覆盖率需要实际生成记录或可识别的层字段；规则六面体的连续排列不直接算作边界层。\n")
        for name, check in cfd.get("wall_checks", {}).items():
            geom = check.get("geometry", {})
            types = check.get("wall_field_types", {})
            if types:
                L.append(f"- {name} 壁面场类型：" + "、".join(f"{k}={v}" for k, v in types.items()))
            elif check.get("wall_conditions_verified"):
                L.append(f"- {name} 壁面条件：由外部声明已核对。")
            if check.get("low_y_wall_function"):
                L.append(f"- {name}：OpenFOAM 12 的 nutkWallFunction / epsilonWallFunction 含低 y⁺ 分支；"
                         "低于筛查下限时先核对实际分支、壁面剪切及压降/换热的网格敏感性，再决定是否调整首层尺寸。")
            if geom.get("near_wall_internal_faces"):
                L.append(f"- {name} 首层相邻内部面：非正交角最大 {_fmt(geom['near_wall_nonortho_max'])}°、"
                         f">70° {geom['near_wall_nonortho_over70']} 面；歪斜度最大 {_fmt(geom['near_wall_skew_max'])}、"
                         f">4 {geom['near_wall_skew_over4']} 面；首层单元长宽比 P95 {_fmt(geom['first_cell_aspect_p95'])}。")
        layer_lines = []
        for name, check in cfd.get("wall_checks", {}).items():
            observed = [f"实际层数最小值 {check['measured_layers']}"] if "measured_layers" in check else []
            if "measured_layer_coverage" in check:
                observed.append(f"覆盖率 {check['measured_layer_coverage']:.1%}")
            dist = check.get("layer_distribution")
            if dist:
                observed.append(f"面积加权平均层数 {_fmt(dist['mean'])}")
                observed.append(f"有层面数 {dist['n_covered']}/{dist['n_faces']}")
                if "under_target_area_fraction" in dist:
                    observed.append(f"低于目标的面积比例 {dist['under_target_area_fraction']:.1%}")
            if "measured_growth_p95" in check:
                observed.append(f"层增长率 P95 {_fmt(check['measured_growth_p95'])}（外部输入）")
            if observed:
                source = "snappyHexMesh nSurfaceLayers 边界场" if check.get("layer_source") == "mesh_generation_field" else "外部实测输入"
                layer_lines.append(f"- {name}：" + "，".join(observed) + f"（来自{source}）")
        if layer_lines:
            L.append("**边界层实测数据**\n")
            L.extend(layer_lines)
            L.append("")
        checks = cfd.get("solution_checks", {})
        if checks:
            L.append("**已有试算的复核结果**\n")
            if "mass_balance" in checks:
                b = checks["mass_balance"]
                if b.get("basis") == "volumetric_flux_m3_s":
                    L.append(f"- 恒密度流体积通量相对不平衡：{b['relative_imbalance']:.4%}；容差 {b['tolerance']:.2%}")
                else:
                    L.append(f"- 质量通量不平衡：{b['relative_imbalance']:.2%}；容差 {b['tolerance']:.2%}")
            if "energy_balance" in checks:
                b = checks["energy_balance"]
                L.append(f"- 能量通量不平衡：{b['relative_imbalance']:.2%}；容差 {b['tolerance']:.2%}")
            for name, b in checks.get("monitor_drift", {}).items():
                L.append(f"- {name} 末段漂移：{b['relative_change']:.2%}；容差 {b['tolerance']:.2%}")
            for name, b in checks.get("monitor_spread", {}).items():
                L.append(f"- {name} 末段 P05–P95 波动：{b['relative_span']:.2%}；容差 {b['tolerance']:.2%}")
            for name, b in checks.get("grid_sensitivity", {}).items():
                L.append(f"- {name} 细/中网格变化：{b['fine_medium_relative_change']:.2%}；容差 {b['tolerance']:.2%}")
                if b.get("unstable_monitor_histories"):
                    L.append("  - 相关监测量末段仍在漂移或波动：" + "、".join(b["unstable_monitor_histories"])
                             + "；当前网格差异只是初步比较，先使各套网格的目标量稳定，再判断网格敏感性。")
                elif b.get("missing_monitor_histories"):
                    L.append("  - 缺少粗、中、细网格各自的目标量监测序列；当前网格差异只是初步比较。")
            L.append("")
        if missing:
            L.append("**待补全的关键证据**\n")
            L.extend(f"- {m}" for m in missing)
            L.append("")

    # 3 quality table
    qual = [f for f in findings if f["category"] == "quality"]
    L.append("## 3. 质量指标\n")
    if qual:
        L.append("| 指标 | 极值 | 阈值（中等/高/致命） | 超标范围 | 等级 |\n|---|---|---|---|---|")
        for f in qual:
            t = f.get("threshold") or {}
            ths = "/".join(_fmt(t.get(k)) for k in ("moderate", "high", "critical")) if t else "—"
            if t:
                ths = ("> " if t.get("direction") == "max" else "< ") + ths
            stat = {"max": "最大", "min": "最小", "maximum": "最大", "minimum": "最小"}.get(f["stat"], "")
            L.append(f"| {f['name_zh']} | {stat} {_fmt(f['value'])}{f['unit']} | {ths} | {_scope(f)} | "
                     f"{ICON[f['severity']]} {f['severity_zh']} |")
        L.append("")
        for f in qual:
            notes = []
            if f.get("average") is not None:
                notes.append(f"平均值 {_fmt(f['average'])}{f['unit']}")
            if f.get("mean") is not None:
                notes.append(f"平均值 {_fmt(f['mean'])}{f['unit']}")
            if f.get("distribution"):
                notes.append("分布：" + "，".join(f"{k}: {v}" for k, v in f["distribution"].items()))
            if f.get("count_criterion"):
                notes.append(f"超标计数标准 {f['count_criterion']}")
            if f.get("definition"):
                notes.append(f"定义：{f['definition']}")
            if f.get("note"):
                notes.append(f["note"])
            if notes:
                L.append(f"- **{f['name_zh']}**：" + "；".join(notes))
    else:
        L.append("没有可用的质量指标数据。")
    L.append("")

    # 4 location
    located = [f for f in findings if f.get("location") and f["severity"] != "ok"]
    L.append("## 4. 问题定位\n")
    if located:
        for f in located:
            L.append(f"**{f['name_zh']}**")
            for line in _location_lines(f["location"]):
                L.append(f"- {line}")
            L.append("")
    else:
        L.append("没有需要定位的问题，或输入不含位置信息。\n")
    if res.get("visualize_hint") and overall != "ok":
        L.append(f"可视化：{res['visualize_hint']}\n")
    if res.get("extra", {}).get("vtu"):
        L.append(f"已输出 `{res['extra']['vtu']}`，在 ParaView 中可按 scaled_jacobian 等字段着色，用 Threshold 过滤出坏单元。\n")

    # 5 advice
    L.append("## 5. 按优先级排列的网格优化建议\n")
    recommendations = res.get("recommendations", [])
    if recommendations:
        for i, item in enumerate(recommendations, 1):
            L.append(f"{i}. **{item['issue']}**（{SEVERITY_ZH[item['priority']]}）")
            L.append(f"   - 位置：{item['where']}")
            L.append(f"   - 证据：{item['evidence']}")
            L.append(f"   - 修改：{item['mesh_action']}")
            L.append(f"   - 验证：{item['verification']}")
    elif overall == "unknown":
        L.append("先补全检查数据，再制定网格修改方案。")
    else:
        L.append("已评估指标无需修改；若关注压降或换热精度，继续检查 y⁺、近壁层和目标量的网格敏感性。")
    if cfd and cfd.get("missing"):
        L.append("\n**下一步取证**\n")
        for missing in cfd["missing"]:
            L.append(f"- {missing}")
        L.append("- 已有试算时，可用 OpenFOAM 的 `yPlus` 功能对象输出壁面场；提供该 ASCII 场用于逐壁面复核。")
    L.append("")

    # 6 raw flagged lines
    ex = res.get("extra", {})
    raw_lines = ex.get("checkmesh_flagged_lines") or (ex.get("warnings", []) + ex.get("errors", []))
    if raw_lines or ex.get("fatal"):
        L.append("## 6. 原始报警行\n")
        L.append("```")
        L.extend(ex.get("fatal", []) + raw_lines)
        L.append("```\n")

    # 7 limitations
    L.append("## 7. 局限与说明\n")
    for s in res.get("limitations", []):
        L.append(f"- {s}")
    L.append("- 阈值为经验值（见 `scripts/thresholds.json`），严重程度需结合求解类型判断：同样的指标对稳态 RANS 和瞬态多相/动网格计算的影响不同。")
    L.append("")

    # 8 step log
    L.append("## 8. 检查日志\n")
    L.append("| 时间(s) | 状态 | 步骤 | 命令 |\n|---|---|---|---|")
    for s in steps.items:
        L.append(f"| {s['t']} | {s['status']} | {s['msg']} | {('`' + s['cmd'] + '`') if s['cmd'] else ''} |")
    L.append("")

    # renumber sections (optional section 6 may be absent)
    n = iter(range(1, 20))
    L = [re.sub(r"^## \d+\.", lambda m: f"## {next(n)}.", x) for x in L]

    data = {"generated": now, "input": input_path, "detection": det, "overall": overall,
            "overall_zh": SEVERITY_ZH[overall], **{k: v for k, v in res.items() if k != "overall"},
            "steps": steps.items}
    return "\n".join(L), data


def dump_json(data, path):
    def conv(o):
        try:
            import numpy as np
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
        except Exception:  # noqa: BLE001
            pass
        return str(o)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=conv)
