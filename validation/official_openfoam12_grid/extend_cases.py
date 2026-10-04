"""Create isolated strict-stop continuations of monitored three-grid cases."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


RUN = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run"


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text()
    assert content.count(old) == 1, (path, old)
    path.write_text(content.replace(old, new))


def main() -> None:
    grades = sys.argv[1:] or ["fine"]
    assert all(grade in {"coarse", "medium", "fine"} for grade in grades)
    for grade in grades:
        source = RUN / f"pitzDailySteady-grid-{grade}-monitored-20261004"
        target = RUN / f"pitzDailySteady-grid-{grade}-extended-20261004"
        assert source.is_dir()
        assert target.resolve().is_relative_to(RUN.resolve())
        if target.exists():
            raise FileExistsError(target)
        shutil.copytree(source, target)
        control = target / "system/controlDict"
        replace_once(control, "startFrom       startTime;", "startFrom       latestTime;")
        replace_once(control, "endTime         2000;", "endTime         1000;")
        solution = target / "system/fvSolution"
        replace_once(solution, "p               1e-2;", "p               1e-4;")
        replace_once(solution, "U               1e-3;", "U               1e-5;")
        replace_once(solution, '"(k|epsilon|omega|f|v2)" 1e-3;', '"(k|epsilon|omega|f|v2)" 1e-5;')
        print(target)


if __name__ == "__main__":
    main()
