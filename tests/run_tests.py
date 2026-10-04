"""Regression tests: every sample must be detected correctly and graded as expected.

    python tests/run_tests.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CASES = [
    # path, expected source, expected overall, metrics that must be flagged (non-ok)
    ("samples/of_good_3d", "openfoam", "ok", []),
    ("samples/of_sheared_2d", "openfoam", "high", ["non_orthogonality"]),
    ("samples/of_distorted_2d", "openfoam", "critical", ["negative_volume"]),
    ("samples/of_inverted_3d", "openfoam", "critical", ["negative_volume"]),
    ("logs/checkMesh_ok.log", "openfoam", "ok", []),
    ("logs/checkMesh_failed.log", "openfoam", "high",
     ["multiple_regions", "non_orthogonality", "skewness", "aspect_ratio", "cell_determinant", "concave_cells"]),
    ("logs/fluent_transcript.trn", "fluent", "high", ["orthogonal_quality", "skewness"]),
    ("samples/fluent_ascii.msh", "fluent", "ok", []),
    ("samples/gmsh_box_sliver.msh", "gmsh", "high", ["scaled_jacobian", "min_angle"]),
    ("samples/hex_block.vtu", "generic", "ok", []),
]


def main():
    if not os.path.exists(os.path.join(HERE, "samples")):
        subprocess.run([sys.executable, os.path.join(HERE, "make_samples.py")], check=True)
    if not os.path.exists(os.path.join(HERE, "samples", "fluent_ascii.msh")):
        import meshio
        m = meshio.read(os.path.join(HERE, "samples", "hex_block.vtu"))
        meshio.write(os.path.join(HERE, "samples", "fluent_ascii.msh"), m, file_format="ansys", binary=False)

    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for rel, src, overall, flagged in CASES:
            out = os.path.join(tmp, rel.replace("/", "_"))
            proc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "mesh_check.py"),
                                   os.path.join(HERE, rel), "-o", out], capture_output=True,
                                  text=True, encoding="utf-8",
                                  env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            try:
                with open(os.path.join(out, "mesh_report.json"), encoding="utf-8") as f:
                    d = json.load(f)
            except FileNotFoundError:
                detail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"exit {proc.returncode}"
                print(f"FAIL {rel}: no report ({detail})")
                fails += 1
                continue
            got = {f["metric"] for f in d["findings"] if f["severity"] != "ok"}
            errs = []
            if d["detection"]["source"] != src:
                errs.append(f"source {d['detection']['source']} != {src}")
            if d["overall"] != overall:
                errs.append(f"overall {d['overall']} != {overall}")
            missing = set(flagged) - got
            if missing:
                errs.append(f"not flagged: {sorted(missing)}")
            print(("FAIL " if errs else "ok   ") + f"{rel:32s} {d['detection']['source']:8s} {d['overall']:8s} "
                  + ("; ".join(errs) if errs else ""))
            fails += bool(errs)
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
