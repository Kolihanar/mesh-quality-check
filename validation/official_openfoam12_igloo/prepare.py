"""Copy official iglooWithFridges and enable observed layer-field output."""
from __future__ import annotations

import os
import shutil
from pathlib import Path


SOURCE = Path(os.environ["FOAM_TUTORIALS"]) / "fluid/iglooWithFridges"
RUN = Path.home() / "OpenFOAM" / f"{os.environ['USER']}-12" / "run"
TARGET = RUN / "iglooWithFridges-layer-validation-20261004"


def main() -> None:
    assert SOURCE.is_dir()
    assert TARGET.resolve().is_relative_to(RUN.resolve())
    if TARGET.exists():
        raise FileExistsError(TARGET)
    shutil.copytree(SOURCE, TARGET)
    path = TARGET / "system/snappyHexMeshDict"
    content = path.read_text()
    assert "addLayers       true;" in content
    assert "writeFlags" not in content
    path.write_text(content + "\nwriteFlags (layerFields);\n")
    print(TARGET)


if __name__ == "__main__":
    main()
