"""Cross-check saved motorBikeSteady layer report against OpenFOAM output."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = json.loads((ROOT / "mesh_report.json").read_text(encoding="utf-8"))
FIELD = (ROOT / "nSurfaceLayers.0").read_text(encoding="ascii")
SNAPPY = (ROOT / "log.snappyHexMesh").read_text(encoding="utf-8")
CHECKMESH = (ROOT / "log.checkMesh").read_text(encoding="utf-8")
LAYER_TABLE = re.search(r"(?m)^patch\s+faces\s+layers\s+overall thickness", SNAPPY)
assert LAYER_TABLE


def match_number(text: str, pattern: str) -> float:
    result = re.search(pattern, text, re.MULTILINE)
    assert result, pattern
    return float(result.group(1))


def layer_values(patch: str) -> list[int]:
    block = re.search(rf"(?m)^\s*{re.escape(patch)}\s*\{{([^{{}}]*)\}}", FIELD)
    assert block, patch
    values = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\(([^)]*)\)", block.group(1), re.DOTALL)
    assert values, patch
    parsed = [int(float(v)) for v in values.group(2).split()]
    assert len(parsed) == int(values.group(1)), patch
    return parsed


def main() -> None:
    assert "Failed 4 mesh checks." in CHECKMESH
    assert REPORT["overall"] == "high"
    assert REPORT["extra"]["checkmesh_verdict"] == "Failed 4 mesh checks"
    assert not REPORT["extra"].get("consistency_errors")
    assert any(item["metric"] == "native_mesh_checks_failed" for item in REPORT["findings"])
    for native, key in (("points", "n_points"), ("faces", "n_faces"), ("cells", "n_cells")):
        count = int(match_number(CHECKMESH, rf"^\s*{native}:\s*(\d+)"))
        assert REPORT["mesh_info"][key] == count, key

    walls = REPORT["cfd"]["wall_checks"]
    assert "1" not in walls and "68" not in walls
    for patch in ("lowerWall", "motorBike_frt-fairing:001%1", "motorBike_fr-wh-rim:011%11"):
        values = layer_values(patch)
        summary = walls[patch]["layer_distribution"]
        face_count = len(values)
        covered = sum(v > 0 for v in values)
        assert summary["n_faces"] == face_count
        assert summary["n_covered"] == covered
        assert summary["min"] == min(values) and summary["max"] == max(values)
        assert summary["n_under_target"] == face_count - covered
        native_line = re.search(rf"(?m)^\s*{re.escape(patch)}\s+(\d+)\s+([\d.]+)\s+", SNAPPY[LAYER_TABLE.end():])
        assert native_line, patch
        assert int(native_line.group(1)) == face_count
        # snappyHexMesh reports a face-counted mean rounded to three decimals;
        # the Skill separately reports area-weighted coverage.
        assert math.isclose(covered / face_count, float(native_line.group(2)), abs_tol=5.1e-4), (patch, covered / face_count, native_line.group(2))
    assert 0 < walls["motorBike_frt-fairing:001%1"]["layer_distribution"]["coverage_area_fraction"] < 0.95
    print("OpenFOAM 12 motorBikeSteady layer-field comparison: passed")


if __name__ == "__main__":
    main()
