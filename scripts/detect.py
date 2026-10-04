"""Identify which software a mesh (or mesh-check log) comes from.

Returns a dict:
    {"source": "openfoam"|"fluent"|"gmsh"|"generic"|"unknown",
     "kind":   "case"|"log"|"mesh"|"case_file",
     "path":   resolved path (case dir for OpenFOAM),
     "evidence": [human-readable reasons]}
"""
from __future__ import annotations

import os
import re
import sys
import json

GENERIC_EXT = {
    ".vtk", ".vtu", ".vtp", ".vts", ".cgns", ".med", ".inp", ".bdf", ".nas",
    ".stl", ".obj", ".ply", ".off", ".mesh", ".meshb", ".xdmf", ".xmf", ".h5m",
    ".e", ".exo", ".exii", ".su2", ".dat", ".tec", ".ugrid", ".f3grid",
}
FLUENT_BINARY_EXT = (".cas", ".cas.h5", ".msh.h5", ".cas.gz", ".msh.gz", ".dat.h5")

OPENFOAM_LOG_MARKERS = [
    r"Checking topology\.\.\.", r"Checking geometry\.\.\.", r"Mesh stats",
    r"Failed \d+ mesh checks", r"^\s*Mesh OK\.", r"Mesh non-orthogonality Max",
    r"Application\s*:\s*checkMesh",
]
FLUENT_LOG_MARKERS = [
    r"Minimum Orthogonal Quality", r"Maximum (Ortho|Cell)? ?Skew", r"Domain Extents",
    r"Volume statistics", r"minimum volume \(m3\)", r"Mesh Quality:",
    r"Checking mesh\.+", r"Maximum Aspect Ratio",
]


def _head(path: str, n: int = 4096) -> bytes:
    with open(path, "rb") as f:
        return f.read(n)


def _read_text(path: str, limit: int = 2_000_000) -> str:
    with open(path, "rb") as f:
        return f.read(limit).decode("utf-8", errors="replace")


def _is_openfoam_case(d: str) -> str | None:
    for sub in ("constant/polyMesh", "polyMesh", "."):
        pm = os.path.join(d, sub)
        if all(os.path.exists(os.path.join(pm, f)) or os.path.exists(os.path.join(pm, f + ".gz"))
               for f in ("points", "faces", "owner")):
            return pm
    return None


def detect(path: str) -> dict:
    ev: list[str] = []
    p = os.path.abspath(path)

    if not os.path.exists(p):
        return {"source": "unknown", "kind": None, "path": p, "evidence": ["路径不存在"]}

    # ---- directories: OpenFOAM case
    if os.path.isdir(p):
        pm = _is_openfoam_case(p)
        if pm:
            case = p
            if pm.endswith(os.path.join("constant", "polyMesh")):
                ev.append("找到 constant/polyMesh/{points,faces,owner}")
            else:
                ev.append(f"找到 polyMesh 文件：{pm}")
                # polyMesh dir passed directly -> case is two levels up when possible
                if os.path.basename(pm.rstrip(os.sep)) == "polyMesh":
                    case = os.path.dirname(os.path.dirname(pm))
            if os.path.exists(os.path.join(case, "system", "controlDict")):
                ev.append("存在 system/controlDict")
            return {"source": "openfoam", "kind": "case", "path": case, "polymesh": pm, "evidence": ev}
        return {"source": "unknown", "kind": None, "path": p,
                "evidence": ["目录中没有找到 OpenFOAM polyMesh，也不是可识别的网格文件"]}

    name = os.path.basename(p).lower()

    # ---- *.foam / *.OpenFOAM marker file
    if name.endswith(".foam") or name.endswith(".openfoam"):
        case = os.path.dirname(p)
        pm = _is_openfoam_case(case)
        ev.append("ParaView 的 .foam 标记文件")
        if pm:
            return {"source": "openfoam", "kind": "case", "path": case, "polymesh": pm, "evidence": ev}

    # ---- Fluent binary/HDF5 case or mesh
    if name.endswith(FLUENT_BINARY_EXT):
        ev.append(f"扩展名 {name} 属于 Fluent 算例/网格文件")
        return {"source": "fluent", "kind": "case_file", "path": p, "evidence": ev}

    head = _head(p)

    # ---- .msh: Gmsh vs Fluent
    if name.endswith(".msh"):
        txt = head.decode("latin-1", errors="replace").lstrip()
        if txt.startswith("$MeshFormat"):
            ev.append("文件以 $MeshFormat 开头 → Gmsh 格式")
            return {"source": "gmsh", "kind": "mesh", "path": p, "evidence": ev}
        if re.match(r"^\(\s*\d+", txt):
            ev.append("文件以 '(索引 ...' 段落开头 → Fluent/ANSYS .msh 格式")
            return {"source": "fluent", "kind": "mesh", "path": p, "evidence": ev}
        ev.append(".msh 文件但无法从文件头判断格式")
        return {"source": "unknown", "kind": "mesh", "path": p, "evidence": ev}

    ext = os.path.splitext(name)[1]

    # ---- text logs (checkMesh / Fluent transcript)
    is_text = b"\x00" not in head
    if is_text and ext not in GENERIC_EXT:
        txt = _read_text(p)
        of_hits = [m for m in OPENFOAM_LOG_MARKERS if re.search(m, txt, re.M)]
        fl_hits = [m for m in FLUENT_LOG_MARKERS if re.search(m, txt, re.M | re.I)]
        if of_hits and len(of_hits) >= len(fl_hits):
            ev.append(f"日志中包含 checkMesh 特征行（{len(of_hits)} 项）")
            return {"source": "openfoam", "kind": "log", "path": p, "evidence": ev}
        if fl_hits:
            ev.append(f"日志中包含 Fluent mesh check/quality 特征行（{len(fl_hits)} 项）")
            return {"source": "fluent", "kind": "log", "path": p, "evidence": ev}

    if ext in GENERIC_EXT:
        ev.append(f"扩展名 {ext}：用通用路线（meshio + VTK 指标）读取")
        return {"source": "generic", "kind": "mesh", "path": p, "evidence": ev}

    return {"source": "unknown", "kind": None, "path": p,
            "evidence": ["既不是可识别的网格文件，也没有找到 checkMesh/Fluent 日志特征"]}


if __name__ == "__main__":
    print(json.dumps(detect(sys.argv[1]), ensure_ascii=False, indent=2))
