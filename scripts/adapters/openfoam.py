"""OpenFOAM adapter: run/parse checkMesh, add distributions & locations from polyMesh."""
from __future__ import annotations

import os
import re
import shutil
import subprocess

import numpy as np

from common import finding, grade, THRESHOLDS
from adapters import polymesh, nearwall

NUM = r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"

ADVICE = {
    "negative_volume": [
        "负体积单元会直接导致求解失败，必须先修复网格再计算。",
        "检查几何是否有自相交或极薄缝隙；snappyHexMesh 生成的网格可适当收紧 meshQualityDict（如 minVol、minTetQuality）后重新划分。",
        "blockMesh 网格检查顶点顺序（右手系）和是否存在被压扁的块。",
    ],
    "face_pyramids": [
        "面金字塔错误通常意味着面朝向错误或单元严重扭曲，求解器会出现负体积或除零。",
        "检查顶点编号顺序；导入网格（fluentMeshToFoam 等）后可尝试 renumberMesh，并确认转换时单位和朝向正确。",
    ],
    "face_area": ["存在零面积或负面积的面，需检查重复点、退化面，通常由几何清理不彻底引起。"],
    "open_cells": ["存在不封闭单元，网格拓扑有误，需重新生成或检查转换过程。"],
    "multiple_regions": [
        "网格存在多个互不连通的区域。若不是有意为之（如 CHT 拆分前的多区域），通常是 snappyHexMesh 的 locationInMesh 设置或几何漏洞导致。",
        "可用 splitMeshRegions -cellZones 或 regionCellSets 查看各区域，删除孤立的小区域。",
    ],
    "face_tets": ["面四面体分解质量差，会影响拉格朗日粒子追踪和部分插值；纯欧拉计算影响较小，但通常和高歪斜度同时出现。"],
    "concave_cells": ["存在凹单元，多见于 snappyHexMesh 贴体层；一般可接受，若和高非正交性同时出现应优先处理。"],
    "non_orthogonality": [
        "网格侧：在问题区域加密或改善贴体，snappyHexMesh 可降低 meshQualityControls 中的 maxNonOrtho 并增加 nSmoothPatch / nRelaxIter。",
        "数值侧（暂不改网格时）：fvSchemes 中 laplacianSchemes/snGradSchemes 使用 corrected（>70° 时改用 limited corrected 0.33~0.5），"
        "fvSolution 中 nNonOrthogonalCorrectors 设为 1~3；时间步也需相应减小。",
    ],
    "skewness": [
        "高歪斜度会降低插值精度，严重时导致发散。网格侧：在问题区域局部加密或调整 snappy 的 maxInternalSkewness / maxBoundarySkewness。",
        "数值侧：梯度格式使用 cellLimited Gauss linear 1，对流项使用有界格式（如 linearUpwind 配合限制器）。",
    ],
    "aspect_ratio": [
        "若大长宽比单元位于边界层（贴壁），一般是有意为之，可接受；若位于主流区或界面区域，应改善网格。",
        "大长宽比会使压力方程收敛变慢，可考虑 GAMG 求解器，并检查边界层增长率是否过大。",
    ],
    "cell_determinant": ["单元行列式过小说明单元在某个方向上几乎退化（极扁），会影响梯度计算的适定性。"],
    "interpolation_weight": ["面插值权重过小说明相邻两单元尺寸相差悬殊，应检查网格过渡（增长率）。"],
    "volume_ratio": ["相邻单元体积比过小，网格尺寸突变，会产生数值误差，应平滑过渡区网格。"],
}


def run_checkmesh(case, log, out_dir):
    exe = shutil.which("checkMesh")
    if not exe:
        log.add("未找到 checkMesh（OpenFOAM 环境未加载或未安装），跳过", status="skip")
        return None
    cmd = [exe, "-case", case, "-allGeometry", "-allTopology"]
    log.add("运行 checkMesh", cmd=" ".join(cmd))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    except Exception as e:  # noqa: BLE001
        log.add(f"checkMesh 运行失败：{e}", status="error")
        return None
    text = r.stdout + r.stderr
    path = os.path.join(out_dir, "log.checkMesh")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log.add(f"checkMesh 输出已保存：{path}（返回码 {r.returncode}）")
    return text


def parse_checkmesh(text: str) -> dict:
    """Parse checkMesh console output into a dict of facts."""
    g = {}

    def grab(pat, cast=float, flags=re.I):
        m = re.search(pat, text, flags)
        return cast(m.group(1)) if m else None

    info = {
        "n_points": grab(r"^\s*points:\s+(\d+)", int, re.M),
        "n_faces": grab(r"^\s*faces:\s+(\d+)", int, re.M),
        "n_internal_faces": grab(r"^\s*internal faces:\s+(\d+)", int, re.M),
        "n_cells": grab(r"^\s*cells:\s+(\d+)", int, re.M),
        "version": (re.search(r"Version\s*:\s*(\S+)", text) or re.search(r"Build\s*:\s*(\S+)", text) or [None, None])[1],
    }
    types = {}
    for k in ("hexahedra", "prisms", "wedges", "pyramids", "tet wedges", "tetrahedra", "polyhedra"):
        m = re.search(rf"^\s*{k}:\s+(\d+)", text, re.M)
        if m and int(m.group(1)):
            types[k] = int(m.group(1))
    info["cell_types"] = types
    m = re.search(r"Mesh has\s+(\d+)\s+geometric \(non-empty/wedge\) directions", text)
    info["n_dims"] = int(m.group(1)) if m else None
    g["info"] = info

    # boundary patches table (name  nFaces ...)
    pats = []
    m = re.search(r"Checking patch topology for multiply connected surfaces\.\.\.(.*?)\n\s*\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1].isdigit() and parts[0] not in ("Patch", "Faces"):
                pats.append({"name": parts[0], "nFaces": int(parts[1])})
    g["patches"] = pats

    g["max_aspect"] = grab(r"Max aspect ratio\s*[=:]\s*" + NUM)
    m = re.search(r"High aspect ratio cells found.*?Max aspect ratio:\s*" + NUM + r".*?number of cells\s+(\d+)", text, re.I | re.S)
    if m:
        g["max_aspect"], g["n_bad_aspect"] = float(m.group(1)), int(m.group(2))
    g["nonortho_max"] = grab(r"non-orthogonality Max:\s*" + NUM)
    g["nonortho_avg"] = grab(r"non-orthogonality Max:\s*[-+\d.eE]+\s+average:\s*" + NUM)
    g["n_bad_nonortho"] = grab(r"severely non-orthogonal \(>\s*[\d.]+ degrees\) faces:\s*(\d+)", int)
    g["nonortho_threshold"] = grab(r"severely non-orthogonal \(>\s*([\d.]+) degrees\)")
    g["skew_max"] = grab(r"Max skewness\s*=\s*" + NUM)
    g["n_bad_skew"] = grab(r"Max skewness\s*=\s*[-+\d.eE]+,\s*(\d+)\s+highly skew faces", int)
    g["min_vol"] = grab(r"Min volume\s*=\s*" + NUM)
    g["max_vol"] = grab(r"Max volume\s*=\s*" + NUM)
    m = re.search(r"Zero or negative cell volume detected.*?Minimum negative volume:\s*" + NUM + r".*?Number of negative volume cells:\s*(\d+)", text, re.I | re.S)
    g["neg_vol"] = (float(m.group(1)), int(m.group(2))) if m else None
    g["n_bad_pyramids"] = grab(r"Error in face pyramids:\s*(\d+)", int)
    g["neg_area"] = bool(re.search(r"Zero or negative face area detected", text, re.I))
    g["n_open_cells"] = grab(r"Open cells found.*?number of open cells\s+(\d+)", int, re.I | re.S)
    g["n_regions"] = grab(r"Number of regions:\s*(\d+)", int)
    g["region_sizes"] = [int(x) for x in re.findall(r"Writing region \d+ with (\d+) cells", text)]
    g["n_concave"] = grab(r"Concave cells.*?found, number of cells:\s*(\d+)", int, re.I | re.S)
    g["n_bad_facetets"] = grab(r"Error in face tets:\s*(\d+)", int)
    g["det_min"] = grab(r"Cell determinant \(wellposedness\)\s*:\s*minimum:\s*" + NUM)
    g["n_bad_det"] = grab(r"Cells with small determinant.*?number of cells:\s*(\d+)", int, re.I | re.S)
    g["weight_min"] = grab(r"Face interpolation weight\s*:\s*minimum:\s*" + NUM)
    g["n_bad_weight"] = grab(r"Faces with small interpolation weight.*?number of faces:\s*(\d+)", int, re.I | re.S)
    g["vratio_min"] = grab(r"Face volume ratio\s*:\s*minimum:\s*" + NUM)
    g["n_bad_vratio"] = grab(r"Faces with small volume ratio.*?number of faces:\s*(\d+)", int, re.I | re.S)
    g["n_failed"] = grab(r"Failed\s+(\d+)\s+mesh checks", int)
    g["mesh_ok"] = bool(re.search(r"^\s*Mesh OK\.", text, re.M))
    g["flagged"] = [l.strip() for l in text.splitlines() if re.match(r"^\s*\*", l)]
    g["fatal"] = [l.strip() for l in text.splitlines() if "FOAM FATAL" in l]
    return g


def _loc(an, key, ids, xyz, vals, worst_is_max=True):
    if an is None or ids is None:
        return None
    return an["locate"](ids, xyz, vals, worst_is_max)


def check(det: dict, log, out_dir: str, log_text: str | None = None) -> dict:
    case = det["path"]
    findings, limits = [], []
    cm = None

    if det["kind"] == "log":
        log.add(f"读取 checkMesh 日志：{case}")
        with open(case, encoding="utf-8", errors="replace") as f:
            cm = parse_checkmesh(f.read())
        limits.append("只有 checkMesh 日志、没有网格本身：无法统计超标单元的空间位置。提供算例目录可获得定位信息。")
    else:
        text = log_text if log_text is not None else run_checkmesh(case, log, out_dir)
        if text:
            cm = parse_checkmesh(text)
            if cm["fatal"]:
                log.add("checkMesh 报 FOAM FATAL ERROR", status="error")
        else:
            limits.append("未运行 checkMesh：以下结果全部来自本工具对 polyMesh 的独立计算（仅 ASCII 格式），"
                          "未覆盖拓扑检查（zip-up、点使用等）和面四面体检查，结论需在装有 OpenFOAM 的机器上用 checkMesh 复核。")

    an = None
    if det["kind"] == "case":
        log.add("用 Python 读取 polyMesh，计算各面/单元指标分布和位置", cmd=f"polymesh.analyse({det['polymesh']})")
        try:
            an = polymesh.analyse(det["polymesh"])
            log.add(f"polyMesh 读取完成：{an['n_cells']} 个单元，{an['n_faces']} 个面")
        except polymesh.BinaryFormatError:
            log.add("polyMesh 为二进制格式，跳过分布/定位分析", status="skip")
            limits.append("polyMesh 是二进制格式，无法统计超标单元位置。可运行 `foamFormatConvert` 转为 ASCII "
                          "（controlDict 中 writeFormat ascii），或在 ParaView 中用 checkMesh -writeSets 的结果定位。")
        except Exception as e:  # noqa: BLE001
            log.add(f"polyMesh 读取失败：{e}", status="error")
            limits.append(f"polyMesh 解析失败（{e}），无位置信息。")

    if cm is None and an is None:
        return {"source": "openfoam", "mesh_info": {}, "findings": [], "limitations": limits + ["没有可用的数据。"]}

    info = dict(cm["info"]) if cm else {}
    consistency_errors = []
    if an:
        for k in ("n_points", "n_faces", "n_internal_faces", "n_cells", "n_dims"):
            if info.get(k) is not None and info[k] != an[k]:
                consistency_errors.append(f"checkMesh 的 {k}={info[k]}，当前 polyMesh 的 {k}={an[k]}")
            info[k] = an[k]
        info["bounds"] = an["bounds"]
        info["patches"] = [{"name": p["name"], "type": p["type"], "nFaces": p["nFaces"],
                            "groups": p.get("groups", [])} for p in an["patches"]]
        info["face_sizes"] = an["face_sizes"]
    elif cm:
        info["patches"] = cm["patches"]
    nC, nIF = info.get("n_cells"), info.get("n_internal_faces")
    nF = info.get("n_faces")
    th = THRESHOLDS["openfoam"]

    # ------------------------------------------------ critical / topology
    if cm and cm["fatal"]:
        findings.append(finding("checkmesh_fatal", "checkMesh 致命错误", category="critical", severity="critical",
                                raw=cm["fatal"][0], advice=["先修复 checkMesh 的致命错误，再检查其余质量指标。"]))
    if cm and cm["n_failed"]:
        findings.append(finding("native_mesh_checks_failed", "checkMesh 检查失败项", category="critical", severity="high",
                                value=cm["n_failed"], advice=["查看 checkMesh 报警行及生成的 cellSet/faceSet，逐项修复后重新运行完整检查。"]))
    neg_ids = None
    if an is not None:
        neg_ids = np.where(an["vol"] <= 0)[0]
    if (cm and cm["neg_vol"]) or (neg_ids is not None and len(neg_ids)):
        n = cm["neg_vol"][1] if cm and cm["neg_vol"] else len(neg_ids)
        v = cm["neg_vol"][0] if cm and cm["neg_vol"] else float(an["vol"][neg_ids].min())
        findings.append(finding("negative_volume", "负体积/零体积单元", category="critical", value=v, stat="min",
                                severity="critical", n_bad=n, n_total=nC,
                                location=_loc(an, "vol", neg_ids, an["cctr"], an["vol"], worst_is_max=False) if an is not None and neg_ids is not None and len(neg_ids) else None,
                                raw=next((l for l in (cm or {}).get("flagged", []) if "volume" in l.lower()), None),
                                advice=ADVICE["negative_volume"]))
    if cm:
        if cm["n_bad_pyramids"]:
            findings.append(finding("face_pyramids", "面金字塔错误（面朝向/单元扭曲）", category="critical",
                                    severity="critical", n_bad=cm["n_bad_pyramids"], n_total=nF, total_kind="面",
                                    raw=next((l for l in cm["flagged"] if "pyramid" in l.lower()), None),
                                    advice=ADVICE["face_pyramids"]))
        if cm["neg_area"]:
            findings.append(finding("face_area", "零面积/负面积的面", category="critical", severity="critical",
                                    raw=next((l for l in cm["flagged"] if "area" in l.lower()), None), advice=ADVICE["face_area"]))
        if cm["n_open_cells"]:
            findings.append(finding("open_cells", "不封闭单元", category="critical", severity="critical",
                                    n_bad=cm["n_open_cells"], n_total=nC, advice=ADVICE["open_cells"]))
        if cm["n_regions"] and cm["n_regions"] > 1:
            f = finding("multiple_regions", "多个不连通区域", category="critical", value=cm["n_regions"],
                        severity="high", advice=ADVICE["multiple_regions"])
            if cm["region_sizes"]:
                f["note"] = "各区域单元数：" + "，".join(str(x) for x in cm["region_sizes"])
                small = [x for x in cm["region_sizes"] if nC and x < 0.01 * nC]
                if small:
                    f["note"] += f"；其中 {len(small)} 个区域单元数不足总数 1%，很可能是几何漏洞或 locationInMesh 外侧残留的孤立网格"
            findings.append(f)
        if cm["n_bad_facetets"]:
            findings.append(finding("face_tets", "面四面体分解质量差", category="quality", severity="moderate",
                                    n_bad=cm["n_bad_facetets"], n_total=nF, total_kind="面", advice=ADVICE["face_tets"]))
        if cm["n_concave"]:
            findings.append(finding("concave_cells", "凹单元", category="quality", severity="moderate",
                                    n_bad=cm["n_concave"], n_total=nC, advice=ADVICE["concave_cells"]))

    # ------------------------------------------------ quality metrics
    t_no = th["non_orthogonality"]["high"]
    no_max = cm["nonortho_max"] if cm and cm["nonortho_max"] is not None else (float(an["nonortho"].max()) if an and an["nInt"] else None)
    if no_max is not None:
        ids = np.where(an["nonortho"] > t_no)[0] if an is not None else None
        n_bad = cm["n_bad_nonortho"] if cm and cm["n_bad_nonortho"] is not None else (len(ids) if ids is not None else (0 if cm else None))
        avg = cm["nonortho_avg"] if cm and cm["nonortho_avg"] is not None else (float(an["nonortho"].mean()) if an else None)
        f = finding("non_orthogonality", "非正交性", value=round(no_max, 3), stat="max", unit="°", source="openfoam",
                    n_bad=n_bad, n_total=nIF, total_kind="内部面",
                    location=_loc(an, "no", ids, an["fctr"], an["nonortho"]) if an is not None and ids is not None and len(ids) else None,
                    definition="面法向与相邻单元中心连线的夹角（仅内部面），0° 为理想",
                    raw=next((l for l in (cm or {}).get("flagged", []) if "orthogonal" in l.lower()), None),
                    advice=ADVICE["non_orthogonality"] if grade("openfoam", "non_orthogonality", no_max) != "ok" else [])
        f["average"] = avg
        if an is not None:
            f["distribution"] = {f">{a}°": int((an["nonortho"] > a).sum()) for a in (50, 65, 70, 80)}
        findings.append(f)

    t_sk = th["skewness"]["high"]
    sk_max = cm["skew_max"] if cm and cm["skew_max"] is not None else (float(an["skew"].max()) if an else None)
    if sk_max is not None:
        ids = np.where(an["skew"] > t_sk)[0] if an is not None else None
        n_bad = cm["n_bad_skew"] if cm and cm["n_bad_skew"] is not None else (len(ids) if ids is not None else (0 if cm else None))
        f = finding("skewness", "歪斜度（OpenFOAM 定义）", value=round(sk_max, 4), stat="max", source="openfoam",
                    n_bad=n_bad, n_total=nF, total_kind="面",
                    location=_loc(an, "sk", ids, an["fctr"], an["skew"]) if an is not None and ids is not None and len(ids) else None,
                    definition="面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想",
                    raw=next((l for l in (cm or {}).get("flagged", []) if "skew" in l.lower()), None),
                    advice=ADVICE["skewness"] if grade("openfoam", "skewness", sk_max) != "ok" else [])
        if an is not None:
            f["distribution"] = {f">{a}": int((an["skew"] > a).sum()) for a in (1, 2.5, 4, 10)}
        findings.append(f)

    ar_max = cm["max_aspect"] if cm and cm["max_aspect"] is not None else (float(an["aspect"].max()) if an else None)
    if ar_max is not None:
        t_ar = th["aspect_ratio"]["moderate"]
        ids = np.where(an["aspect"] > t_ar)[0] if an is not None else None
        n_bad = cm.get("n_bad_aspect") if cm and cm.get("n_bad_aspect") is not None else (len(ids) if ids is not None else (0 if cm else None))
        findings.append(finding("aspect_ratio", "长宽比", value=round(ar_max, 3), stat="max", source="openfoam",
                                n_bad=n_bad, n_total=nC,
                                location=_loc(an, "ar", ids, an["cctr"], an["aspect"]) if an is not None and ids is not None and len(ids) else None,
                                definition="OpenFOAM cellAspectRatio，1 为理想",
                                advice=ADVICE["aspect_ratio"] if grade("openfoam", "aspect_ratio", ar_max) != "ok" else []))

    if cm:
        for key, nkey, metric, zh in (("det_min", "n_bad_det", "cell_determinant", "单元行列式"),
                                      ("weight_min", "n_bad_weight", "interpolation_weight", "面插值权重"),
                                      ("vratio_min", "n_bad_vratio", "volume_ratio", "相邻单元体积比")):
            if cm[key] is not None:
                sev = grade("openfoam", metric, cm[key])
                findings.append(finding(metric, zh, value=cm[key], stat="min", source="openfoam",
                                        n_bad=cm[nkey] if cm[nkey] is not None else 0,
                                        n_total=nC if metric == "cell_determinant" else nIF,
                                        total_kind="单元" if metric == "cell_determinant" else "内部面",
                                        advice=ADVICE[metric] if sev != "ok" else []))

    vol_info = None
    if cm and cm["min_vol"] is not None:
        vol_info = {"min": cm["min_vol"], "max": cm["max_vol"]}
    elif an is not None:
        vol_info = {"min": float(an["vol"].min()), "max": float(an["vol"].max())}
    if vol_info:
        info["cell_volume"] = vol_info

    extra = {}
    if cm:
        extra["checkmesh_verdict"] = "Mesh OK" if cm["mesh_ok"] else (f"Failed {cm['n_failed']} mesh checks" if cm["n_failed"] else "未找到结论行")
        extra["checkmesh_flagged_lines"] = cm["flagged"]
        if cm["fatal"]:
            extra["fatal"] = cm["fatal"]
    if consistency_errors:
        extra["consistency_errors"] = consistency_errors
        limits.append("已有 checkMesh 日志与当前网格不一致：" + "；".join(consistency_errors))
    if cm and an is not None:
        limits.append("位置/分布统计来自本工具按 OpenFOAM 公式的独立计算，数值可能与 checkMesh 有微小差别；严重程度以 checkMesh 数值为准。")
    if info.get("n_dims") == 2:
        limits.append("二维网格（含 empty 面）：长宽比只在求解方向上计算。")

    return {"source": "openfoam", "input_kind": det["kind"], "mesh_info": info, "findings": findings,
            "near_wall_raw": nearwall.inspect(an) if an is not None else {},
            "extra": extra, "limitations": limits,
            "visualize_hint": "checkMesh 会把坏面/坏单元写成集合（如 nonOrthoFaces、skewFaces）。用 `foamToVTK -faceSet nonOrthoFaces`"
                              "（单元集合用 -cellSet）转成 VTK，或 ESI 版直接用 `checkMesh -allGeometry -allTopology -writeSets vtk`，在 ParaView 中查看。"}
