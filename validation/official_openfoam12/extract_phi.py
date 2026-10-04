"""Extract signed inlet/outlet volume fluxes from the saved ASCII phi field."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def extract(path: Path) -> dict:
    text = path.read_text(encoding="ascii")
    if not re.search(r"\bformat\s+ascii\s*;", text) or not re.search(r"\bclass\s+surfaceScalarField\s*;", text):
        raise ValueError("需要 ASCII surfaceScalarField")
    dimensions = re.search(r"\bdimensions\s+(\[[^]]+\])\s*;", text)
    # m^3/s is not kg/s; the Skill uses this only for constant-density flow.
    if not dimensions or [int(x) for x in re.findall(r"-?\d+", dimensions.group(1))] != [0, 3, -1, 0, 0, 0, 0]:
        raise ValueError("phi 不是体积通量 [0 3 -1 0 0 0 0]")
    boundary = re.search(r"\bboundaryField\s*\{", text)
    if not boundary:
        raise ValueError("缺少 boundaryField")
    suffix = text[boundary.end():]
    fluxes, faces = {}, {}
    for patch in ("inlet", "outlet"):
        block = re.search(rf"(?ms)^\s*{patch}\s*\{{(.*?)^\s*\}}", suffix)
        if not block:
            raise ValueError(f"缺少 {patch}")
        values = re.search(r"\bvalue\s+nonuniform\s+List<scalar>\s+(\d+)\s*\(([^)]*)\)", block.group(1), re.DOTALL)
        if not values:
            raise ValueError(f"{patch} 缺少逐面 phi")
        parsed = [float(x) for x in values.group(2).split()]
        if len(parsed) != int(values.group(1)):
            raise ValueError(f"{patch} 面数与 phi 数量不一致")
        fluxes[patch], faces[patch] = sum(parsed), len(parsed)
    scale = max(-min(fluxes["inlet"], 0), max(fluxes["outlet"], 0))
    return {"source": path.name, "dimensions": "[0 3 -1 0 0 0 0]",
            "n_faces": faces, "volumetric_flux_m3_s": fluxes,
            "relative_imbalance": abs(sum(fluxes.values())) / scale}


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("phi.286")
    print(json.dumps(extract(source), indent=2))
