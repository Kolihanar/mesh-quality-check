"""Independently compare a real enclosed-flow layer field with the Skill report."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
TARGETS = {"igloo": 1, "twoFridgeFreezers_seal_0": 3, "twoFridgeFreezers_herring_1": 3}


def poly_list(path: Path, kind: str):
    text = path.read_text(encoding="utf-8")
    marker = re.search(r"\n(\d+)\s*\(\s*\n", text)
    assert marker, path
    count = int(marker.group(1))
    body = text[marker.end():]
    if kind == "points":
        entries = [tuple(map(float, row.split())) for row in re.findall(r"\(([-+\d.eE\s]+)\)", body)]
    else:
        entries = []
        for n, row in re.findall(r"(\d+)\((\d+(?:\s+\d+)*)\)", body):
            face = tuple(map(int, row.split()))
            assert len(face) == int(n)
            entries.append(face)
    assert len(entries) == count, (path, len(entries), count)
    return entries


def boundary() -> dict[str, tuple[int, int]]:
    text = (ROOT / "boundary").read_text(encoding="utf-8")
    entries = {}
    for name, body in re.findall(r"([^\s{}();]+)\s*\{([^}]*)\}", text):
        n = re.search(r"\bnFaces\s+(\d+)\s*;", body)
        start = re.search(r"\bstartFace\s+(\d+)\s*;", body)
        if n and start:
            entries[name] = (int(start.group(1)), int(n.group(1)))
    return entries


def field_values(name: str, count: int) -> np.ndarray:
    text = (ROOT / "nSurfaceLayers.0").read_text(encoding="utf-8")
    match = re.search(rf"\b{re.escape(name)}\s*\{{([^}}]*)\}}", text, re.S)
    assert match, name
    body = match.group(1)
    nonuniform = re.search(r"\bvalue\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", body, re.S)
    if nonuniform:
        assert int(nonuniform.group(1)) == count
        values = np.fromstring(nonuniform.group(2), sep=" ")
    else:
        uniform = re.search(r"\bvalue\s+uniform\s+([-+\d.eE]+)\s*;", body)
        assert uniform, name
        values = np.full(count, float(uniform.group(1)))
    assert len(values) == count
    return values


def face_area(points: np.ndarray, face: tuple[int, ...]) -> float:
    polygon = points[list(face)]
    cross_sum = np.cross(polygon, np.roll(polygon, -1, axis=0)).sum(axis=0)
    return float(np.linalg.norm(cross_sum) / 2)


def close(actual: float, expected: float, label: str) -> None:
    assert math.isclose(actual, expected, rel_tol=2e-6, abs_tol=1e-8), (label, actual, expected)


def main() -> None:
    for line in (ROOT / "native.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split()
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    report = json.loads((ROOT / "report/mesh_report.json").read_text(encoding="utf-8"))
    context = json.loads((ROOT / "context.json").read_text(encoding="utf-8"))
    mesh_log = (ROOT / "log.checkMesh").read_text(encoding="utf-8")
    layer_log = (ROOT / "log.snappyHexMesh").read_text(encoding="utf-8")
    assert "Failed 1 mesh checks." in mesh_log
    assert "Concave cells (using face planes) found, number of cells: 1733" in mesh_log
    assert report["mesh_info"]["n_cells"] == 11274
    assert report["overall"] == "high"
    assert next(f for f in report["findings"] if f["metric"] == "native_mesh_checks_failed")["severity"] == "high"
    assert next(f for f in report["findings"] if f["metric"] == "concave_cells")["n_bad"] == 1733
    assert report["cfd"]["case_setup"]["turbulence_model"] == "kEpsilon"
    assert not any("缺少 0/nut" in item for item in report["cfd"]["missing"])
    points = np.asarray(poly_list(ROOT / "points", "points"), dtype=float)
    faces = poly_list(ROOT / "faces", "faces")
    patches = boundary()
    for name, target in TARGETS.items():
        first, count = patches[name]
        values = field_values(name, count)
        areas = np.asarray([face_area(points, face) for face in faces[first:first + count]])
        assert np.all(areas > 0), name
        result = report["cfd"]["wall_checks"][name]
        dist = result["layer_distribution"]
        assert result["layer_source"] == "mesh_generation_field"
        assert result["wall_field_source"] == "patch_group:wall"
        assert result["wall_field_types"]["nut"] == "nutkWallFunction"
        assert result["wall_field_types"]["epsilon"] == "epsilonWallFunction"
        assert result["wall_field_types"]["alphat"] == "compressible::alphatJayatillekeWallFunction"
        assert dist["n_faces"] == count
        assert dist["n_covered"] == int(np.count_nonzero(values))
        assert dist["n_under_target"] == int(np.count_nonzero(values < target))
        close(dist["coverage_area_fraction"], areas[values > 0].sum() / areas.sum(), f"{name} coverage")
        close(dist["under_target_area_fraction"], areas[values < target].sum() / areas.sum(), f"{name} under target")
        close(dist["mean"], float(np.dot(values, areas) / areas.sum()), f"{name} area-weighted mean")
        assert context["walls"][name]["target_layers"] == target
        native_matches = re.findall(rf"^{re.escape(name)}\s+(\d+)\s+([\d.]+)\s+", layer_log, re.M)
        assert native_matches and int(native_matches[-1][0]) == count, name
        assert abs(float(native_matches[-1][1]) - float(values.mean())) < 0.006, (
            name, native_matches[-1][1], float(values.mean()))
    ground_start, ground_count = patches["ground"]
    assert ground_count == 918 and np.count_nonzero(field_values("ground", ground_count)) == 0
    assert not any(f["metric"] == "boundary_layers" and "ground" in f["name_zh"] for f in report["findings"])
    print("OpenFOAM 12 enclosed-flow native/Skill comparison: passed (failed mesh check, group wall functions, actual layer counts and area fractions)")


if __name__ == "__main__":
    main()
