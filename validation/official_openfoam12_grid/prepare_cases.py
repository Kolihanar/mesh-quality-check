"""Copy the OpenFOAM 12 pitzDailySteady tutorial into a three-grid study.

Run inside the sourced OpenFOAM environment. Existing target cases are never
overwritten, so previous trial results remain available for inspection.
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ["FOAM_TUTORIALS"]) / "incompressibleFluid/pitzDailySteady"
RUN = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run"
ORIGINAL = [(18, 30), (180, 27), (180, 30), (25, 27), (25, 30)]
GRIDS = {
    "coarse": [(12, 20), (120, 18), (120, 20), (17, 18), (17, 20)],
    "medium": ORIGINAL,
    "fine": [(27, 45), (270, 41), (270, 45), (38, 41), (38, 45)],
}
PATTERN = re.compile(r"(hex\s*\([^)]*\)\s*\n\s*)\((\d+)\s+(\d+)\s+1\)")


def main() -> None:
    original_mesh = (SOURCE / "system/blockMeshDict").read_text()
    matches = PATTERN.findall(original_mesh)
    assert [(int(x), int(y)) for _, x, y in matches] == ORIGINAL, matches

    original_functions = (SOURCE / "system/functions").read_text()
    assert "streamlinesLine" in original_functions
    function_body = re.sub(
        r"\AFoamFile\s*\{[^}]*\}\s*", "", (HERE.parent / "official_openfoam12/functions").read_text(), count=1
    )
    assert function_body.count("type surfaceFieldValue;") == 4
    assert function_body.count("writeControl writeTime;") == 4
    function_body = function_body.replace(
        "writeControl writeTime;", "writeControl timeStep;\n        writeInterval 1;"
    )
    functions = original_functions + "\n" + function_body + "\n"

    RUN.mkdir(parents=True, exist_ok=True)
    for name, grid in GRIDS.items():
        target = RUN / f"pitzDailySteady-grid-{name}-monitored-20261004"
        assert target.resolve().is_relative_to(RUN.resolve())
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite existing case: {target}")
        replacements = iter(grid)

        def replace(match: re.Match[str]) -> str:
            x, y = next(replacements)
            return f"{match.group(1)}({x} {y} 1)"

        mesh = PATTERN.sub(replace, original_mesh)
        assert not list(replacements)
        assert len(PATTERN.findall(mesh)) == 5
        shutil.copytree(SOURCE, target)
        (target / "system/blockMeshDict").write_text(mesh)
        (target / "system/functions").write_text(functions)
        expected = sum(x * y for x, y in grid)
        print(f"{name}: {target} ({expected} expected cells)")


if __name__ == "__main__":
    main()
