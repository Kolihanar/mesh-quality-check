#!/usr/bin/env python3
"""Mesh quality check: detect source software -> run matching check -> write report.

Usage:
    python mesh_check.py <path> [-o OUT_DIR] [--checkmesh-log LOG] [--force-source openfoam|fluent|generic]

<path> can be:
    - an OpenFOAM case directory (or its constant/polyMesh, or a .foam file)
    - a checkMesh log, or a Fluent transcript containing mesh/check + mesh/quality output
    - a Fluent .msh/.cas(.h5), a Gmsh .msh, or any meshio-readable mesh (.vtk/.vtu/.cgns/.inp/...)

Outputs (in OUT_DIR, default ./mesh_check_report):
    mesh_report.md     human-readable report (Chinese)
    mesh_report.json   the same content, structured
    plus log.checkMesh / fluent_mesh_check.jou / mesh_quality.vtu when applicable
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import StepLog  # noqa: E402
from detect import detect  # noqa: E402
import report  # noqa: E402
import cfd  # noqa: E402
import solution  # noqa: E402
import recommend  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("-o", "--out", default="mesh_check_report")
    ap.add_argument("--checkmesh-log", help="已有的 checkMesh 输出（配合 OpenFOAM 算例目录使用，跳过重新运行）")
    ap.add_argument("--force-source", choices=["openfoam", "fluent", "gmsh", "generic"])
    ap.add_argument("--context", help="CFD 工况 JSON：壁面处理、物性和近壁检查目标")
    ap.add_argument("--yplus-field", help="已有试算产生的 ASCII OpenFOAM yPlus 场；默认查找算例最新时间")
    ap.add_argument("--layer-field", help="snappyHexMesh layerFields 产生的 ASCII nSurfaceLayers 场；默认自动查找")
    a = ap.parse_args(argv)
    context = {}
    if a.context:
        try:
            with open(a.context, encoding="utf-8") as stream:
                context = json.load(stream)
            if not isinstance(context, dict):
                raise ValueError("顶层必须是 JSON 对象")
        except (OSError, ValueError) as exc:
            ap.error(f"工况文件读取失败：{exc}")

    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    log = StepLog()

    det = detect(a.path)
    if a.force_source:
        det["evidence"].append(f"用户指定来源：{a.force_source}")
        det["source"] = a.force_source
        det["kind"] = det.get("kind") or "mesh"
    log.add(f"识别网格来源：{det['source']} / {det['kind']}（{'；'.join(det['evidence'])}）")

    src = det["source"]
    if src == "openfoam":
        from adapters import openfoam
        text = None
        if a.checkmesh_log:
            with open(a.checkmesh_log, encoding="utf-8", errors="replace") as f:
                text = f.read()
            log.add(f"使用已有 checkMesh 日志：{a.checkmesh_log}")
        res = openfoam.check(det, log, out, log_text=text)
    elif src == "fluent":
        from adapters import fluent
        res = fluent.check(det, log, out)
    elif src in ("gmsh", "generic"):
        from adapters import generic
        res = generic.check(det, log, out)
    else:
        res = {"source": "unknown", "mesh_info": {}, "findings": [],
               "limitations": ["无法识别网格来源。可用 --force-source 指定，或提供 checkMesh 日志 / Fluent mesh check 输出。"]}
        log.add("无法识别来源，未执行检查", status="error")

    res = cfd.assess(res, det, context, a.yplus_field, a.layer_field)
    res = solution.assess(res, context)
    res["recommendations"] = recommend.build(res)
    md, data = report.render(res, det, log, os.path.abspath(a.path))
    md_path = os.path.join(out, "mesh_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    report.dump_json(data, os.path.join(out, "mesh_report.json"))

    print(f"[mesh-check] source={res.get('source')} overall={data['overall']} ({data['overall_zh']})")
    for fd in data["findings"]:
        if fd["severity"] != "ok":
            print(f"  - {fd['severity_zh']}: {fd['name_zh']} = {fd['value']} ({fd['n_bad']} bad)")
    print(f"[mesh-check] report: {md_path}")
    return 0 if data["overall"] in ("ok", "moderate") else (3 if data["overall"] == "unknown" else 2)


if __name__ == "__main__":
    sys.exit(main())
