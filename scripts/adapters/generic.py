"""Generic route: any mesh meshio can read (Gmsh .msh, VTK, CGNS, Abaqus .inp,
ASCII Fluent .msh, MED, ...). Quality is evaluated with VTK/Verdict measures,
which use one definition for every source -> comparable across software.
"""
from __future__ import annotations

import os
from collections import Counter

import numpy as np

from common import finding, grade, THRESHOLDS

DIM = {"vertex": 0, "line": 1, "line3": 1, "triangle": 2, "triangle6": 2, "quad": 2, "quad8": 2, "quad9": 2,
       "polygon": 2, "tetra": 3, "tetra10": 3, "hexahedron": 3, "hexahedron20": 3, "hexahedron27": 3,
       "wedge": 3, "wedge15": 3, "wedge18": 3, "pyramid": 3, "pyramid13": 3, "pyramid14": 3}
LINEAR = {"triangle": ("triangle", 3, 5), "triangle6": ("triangle", 3, 5), "quad": ("quad", 4, 9),
          "quad8": ("quad", 4, 9), "quad9": ("quad", 4, 9), "tetra": ("tetra", 4, 10), "tetra10": ("tetra", 4, 10),
          "hexahedron": ("hexahedron", 8, 12), "hexahedron20": ("hexahedron", 8, 12),
          "hexahedron27": ("hexahedron", 8, 12), "wedge": ("wedge", 6, 13), "wedge15": ("wedge", 6, 13),
          "wedge18": ("wedge", 6, 13), "pyramid": ("pyramid", 5, 14), "pyramid13": ("pyramid", 5, 14),
          "pyramid14": ("pyramid", 5, 14)}
TYPE_ZH = {5: "三角形", 9: "四边形", 10: "四面体", 12: "六面体", 13: "三棱柱", 14: "金字塔"}

# measure -> {vtk cell type: vtk measure name}
MEASURES = {
    "scaled_jacobian": {5: "scaled_jacobian", 9: "scaled_jacobian", 10: "scaled_jacobian", 12: "scaled_jacobian",
                        13: "scaled_jacobian", 14: "scaled_jacobian"},
    "aspect_ratio": {5: "aspect_ratio", 9: "aspect_ratio", 10: "aspect_ratio", 12: "max_aspect_frobenius",
                     13: "max_aspect_frobenius"},
    "skew": {9: "skew", 12: "skew"},
    "min_angle": {5: "min_angle", 9: "min_angle", 10: "min_angle"},
}
ZH = {"scaled_jacobian": "缩放雅可比（Scaled Jacobian）", "aspect_ratio": "长宽比", "skew": "歪斜度（VTK 定义）",
      "min_angle": "最小内角"}
DEF = {"scaled_jacobian": "VTK/Verdict 定义，1 为理想，≤0 表示单元翻转",
       "aspect_ratio": "tri/quad/tet 为 aspect_ratio，hex/wedge 为 max_aspect_frobenius；1 为理想",
       "skew": "VTK 定义，仅四边形/六面体，0 为理想", "min_angle": "单元最小内角，仅三角形/四边形/四面体"}
ADVICE = {
    "inverted": ["存在翻转（缩放雅可比 ≤ 0）或零/负尺寸单元，求解器无法使用，必须在网格生成阶段修复。",
                 "Gmsh：检查几何是否有重叠面或极小特征，可尝试 Mesh.Optimize=1 / Mesh.OptimizeNetgen=1，或调整 Mesh.Algorithm3D。"],
    "scaled_jacobian": ["缩放雅可比低的单元形状严重畸变，优先查看报告中的位置；Gmsh 可开启网格优化（Optimize/OptimizeNetgen/HighOrderOptimize）。"],
    "aspect_ratio": ["若位于边界层属正常；否则调整局部尺寸场，使网格尺寸过渡更平缓。"],
    "skew": ["四边形/六面体歪斜通常来自结构化分块不合理或扫掠方向扭曲，可调整块划分或加平滑。"],
    "min_angle": ["小角度单元多出现在尖角、薄层附近，可局部加密或用更优的三角化/四面体化算法。"],
}


def _vtk_grid(blocks, points):
    import pyvista as pv
    cells, types, owner_block = [], [], []
    for bi, (ctype, data) in enumerate(blocks):
        _, nn, vt = LINEAR[ctype]
        d = data[:, :nn]
        cells.append(np.hstack([np.full((len(d), 1), nn), d]).ravel())
        types.append(np.full(len(d), vt, dtype=np.uint8))
        owner_block.append(np.full(len(d), bi))
    return (pv.UnstructuredGrid(np.concatenate(cells), np.concatenate(types), points),
            np.concatenate(types), np.concatenate(owner_block))


def check(det: dict, log, out_dir: str) -> dict:
    import meshio
    path = det["path"]
    limits, findings = [], []
    log.add(f"用 meshio 读取网格：{path}", cmd=f"meshio.read('{os.path.basename(path)}')")
    try:
        m = meshio.read(path)
    except Exception as e:  # noqa: BLE001
        log.add(f"meshio 读取失败：{e}", status="error")
        return {"source": det["source"], "input_kind": "mesh", "mesh_info": {}, "findings": [],
                "limitations": [f"meshio 无法读取该文件：{e}。若是二进制 Fluent .msh，请导出为 ASCII 或 CGNS。"]}

    pts = np.asarray(m.points, dtype=float)
    if pts.shape[1] == 2:
        pts = np.hstack([pts, np.zeros((len(pts), 1))])

    # physical names (Gmsh)
    tagname = {}
    for name, val in (m.field_data or {}).items():
        try:
            tagname[(int(val[0]), int(val[1]))] = name
        except Exception:  # noqa: BLE001
            pass
    phys = m.cell_data.get("gmsh:physical") or m.cell_data.get("medit:ref") or m.cell_data.get("cell_tags")

    dims = [DIM.get(b.type, -1) for b in m.cells]
    top = max(dims) if dims else -1
    type_count = Counter()
    skipped = Counter()
    vol_blocks, vol_tags, bnd_ctr, bnd_tag = [], [], [], []
    for i, b in enumerate(m.cells):
        d = DIM.get(b.type, -1)
        tags = np.asarray(phys[i]) if phys is not None and i < len(phys) else None
        if d == top:
            if b.type in LINEAR:
                vol_blocks.append((b.type, np.asarray(b.data)))
                vol_tags.append(tags if tags is not None else np.full(len(b.data), -1))
                type_count[TYPE_ZH[LINEAR[b.type][2]]] += len(b.data)
            else:
                skipped[b.type] += len(b.data)
        elif d == top - 1 and b.type != "polygon":
            c = pts[np.asarray(b.data)].mean(1)
            bnd_ctr.append(c)
            nm = [tagname.get((int(t), d), f"tag {int(t)}") for t in tags] if tags is not None else [b.type] * len(c)
            bnd_tag += nm

    if skipped:
        limits.append("以下单元类型不支持 VTK 质量指标，未参与评估：" + "、".join(f"{k}×{v}" for k, v in skipped.items()))
    if not vol_blocks:
        return {"source": det["source"], "input_kind": "mesh", "mesh_info": {"n_points": len(pts)}, "findings": [],
                "limitations": limits + ["没有可评估的体（或二维面）单元。"]}

    grid, ctypes, _ = _vtk_grid(vol_blocks, pts)
    tags_all = np.concatenate(vol_tags)
    names_all = np.array([tagname.get((int(t), top), f"tag {int(t)}") if t >= 0 else "（未分组）" for t in tags_all])
    nC = grid.n_cells
    ctr = grid.cell_centers().points
    log.add(f"评估 {nC} 个 {top}D 单元：" + "、".join(f"{k} {v}" for k, v in type_count.items()))

    tree = None
    if bnd_ctr:
        from scipy.spatial import cKDTree
        bnd_ctr = np.vstack(bnd_ctr)
        tree = cKDTree(bnd_ctr)
        bnd_tag = np.array(bnd_tag)
    L = float(np.linalg.norm(pts.max(0) - pts.min(0))) or 1.0

    def locate(ids, vals, worst_is_max):
        if len(ids) == 0:
            return None
        order = ids[np.argsort(vals[ids])[::-1 if worst_is_max else 1]][:10]
        loc = {"bbox_min": [float(f"{x:.4g}") for x in ctr[ids].min(0)],
               "bbox_max": [float(f"{x:.4g}") for x in ctr[ids].max(0)],
               "zones": [{"zone": k, "count": int(v)} for k, v in Counter(names_all[ids]).most_common(5)]}
        if tree is not None:
            dist, j = tree.query(ctr[ids])
            near = dist < 0.05 * L
            cnt = Counter(bnd_tag[j[near]])
            loc["near_patches"] = [{"patch": k, "count": int(v)} for k, v in cnt.most_common(5)]
            if (~near).sum():
                loc["near_patches"].append({"patch": "（远离边界的内部区域）", "count": int((~near).sum())})
        loc["worst"] = []
        for i in order:
            w = {"id": int(i), "value": float(vals[i]), "xyz": [round(float(x), 6) for x in ctr[i]],
                 "zone": str(names_all[i]), "type": TYPE_ZH[int(ctypes[i])]}
            if tree is not None:
                dd, jj = tree.query(ctr[i])
                w["nearest_patch"], w["dist_to_patch"] = str(bnd_tag[jj]), float(f"{dd:.3g}")
            loc["worst"].append(w)
        return loc

    # size (volume/area) -> inverted / degenerate
    size_name = "volume" if top == 3 else "area"
    q = grid.cell_quality([size_name, "scaled_jacobian", "aspect_ratio", "max_aspect_frobenius", "skew", "min_angle"])
    size = np.asarray(q[size_name])
    out = grid.copy()
    out.cell_data[size_name] = size

    th = THRESHOLDS["generic"]
    vals = {}
    for metric, per_type in MEASURES.items():
        v = np.full(nC, np.nan)
        for vt, mname in per_type.items():
            mask = ctypes == vt
            if mask.any():
                v[mask] = np.asarray(q[mname])[mask]
        vals[metric] = v
        out.cell_data[metric] = v

    sj = vals["scaled_jacobian"]
    bad_inv = np.where((sj <= 0) | (size <= 0) if top == 3 else (sj <= 0))[0]
    if len(bad_inv):
        findings.append(finding("inverted", "翻转/退化单元", category="critical", severity="critical",
                                value=float(np.nanmin(sj)), stat="min", n_bad=len(bad_inv), n_total=nC,
                                location=locate(bad_inv, np.nan_to_num(sj, nan=1.0), False),
                                definition="缩放雅可比 ≤ 0 或体积 ≤ 0", advice=ADVICE["inverted"]))

    for metric in ("scaled_jacobian", "aspect_ratio", "skew", "min_angle"):
        v = vals[metric]
        ok = ~np.isnan(v)
        if not ok.any():
            continue
        t = th[metric]
        is_max = t["direction"] == "max"
        ext = float(np.nanmax(v) if is_max else np.nanmin(v))
        if metric == "scaled_jacobian" and len(bad_inv):
            ext_eval = float(np.nanmin(np.where(sj > 0, sj, np.nan))) if (sj > 0).any() else ext
        else:
            ext_eval = ext
        sev = grade("generic", metric, ext_eval)
        bad = np.where(ok & ((v > t["moderate"]) if is_max else (v < t["moderate"])))[0]
        if metric == "scaled_jacobian":
            bad = np.setdiff1d(bad, bad_inv)
        dist = {}
        for lvl in ("moderate", "high", "critical"):
            if t.get(lvl) is not None:
                key = f"{'>' if is_max else '<'}{t[lvl]}"
                dist[key] = int(((v > t[lvl]) if is_max else (v < t[lvl]))[ok].sum())
        f = finding(metric, ZH[metric], value=round(ext, 4), stat="max" if is_max else "min",
                    unit="°" if metric == "min_angle" else "", source="generic", severity=sev,
                    n_bad=len(bad), n_total=int(ok.sum()),
                    location=locate(bad, v, is_max) if len(bad) else None,
                    definition=DEF[metric], advice=ADVICE[metric] if sev != "ok" else [])
        f["count_criterion"] = f"{'>' if is_max else '<'} {t['moderate']}（中等阈值）"
        f["distribution"] = dist
        f["mean"] = float(np.nanmean(v))
        if metric == "scaled_jacobian" and len(bad_inv):
            f["note"] = "严重程度按非翻转单元评估，翻转单元已单列为致命问题"
        findings.append(f)

    # size ratio between neighbours is expensive in general; report global spread instead
    info = {"n_points": len(pts), "n_cells": nC, "n_dims": top, "cell_types": dict(type_count),
            "bounds": [pts.min(0).tolist(), pts.max(0).tolist()],
            "cell_volume" if top == 3 else "cell_area": {"min": float(size.min()), "max": float(size.max())},
            "zones": dict(Counter(names_all.tolist())),
            "boundary_groups": dict(Counter(bnd_tag.tolist())) if len(bnd_tag) else {}}

    vtu = os.path.join(out_dir, "mesh_quality.vtu")
    try:
        out.save(vtu)
        log.add(f"已写出带质量字段的 VTU，可在 ParaView 中按字段着色/阈值筛选：{vtu}")
    except Exception as e:  # noqa: BLE001
        log.add(f"VTU 写出失败：{e}", status="error")
        vtu = None
    limits.append("通用路线使用 VTK/Verdict 指标，定义与 Fluent/OpenFOAM 的同名指标不同，数值不可直接比较。"
                  "没有计算相邻单元尺寸比（增长率）和非正交性。")
    return {"source": det["source"], "input_kind": "mesh", "mesh_info": info, "findings": findings,
            "extra": {"vtu": vtu}, "limitations": limits}
