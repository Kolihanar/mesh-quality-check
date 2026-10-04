"""Copy raw OpenFOAM layer and mesh evidence from the isolated tutorial case."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASE = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run/iglooWithFridges-layer-validation-20261004"
FILES = {
    "log.blockMesh": "log.blockMesh",
    "log.snappyHexMesh": "log.snappyHexMesh",
    "log.checkMesh": "log.checkMesh",
    "0/nSurfaceLayers": "nSurfaceLayers.0",
    "constant/polyMesh/points": "points",
    "constant/polyMesh/faces": "faces",
    "constant/polyMesh/boundary": "boundary",
    "system/snappyHexMeshDict": "snappyHexMeshDict",
    "0/nut": "nut.0",
    "0/epsilon": "epsilon.0",
    "0/alphat": "alphat.0",
}


def main() -> None:
    assert CASE.is_dir()
    checksums = []
    for source, target in FILES.items():
        content = (CASE / source).read_bytes()
        (HERE / target).write_bytes(content)
        checksums.append(f"{hashlib.sha256(content).hexdigest()}  {target}")
    (HERE / "native.sha256").write_text("\n".join(checksums) + "\n")
    print(f"Saved {len(FILES)} native OpenFOAM files to {HERE}")


if __name__ == "__main__":
    main()
