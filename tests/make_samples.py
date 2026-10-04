"""Generate test inputs: OpenFOAM polyMesh cases (good / distorted / inverted, 2D & 3D),
a Gmsh mesh with a sliver element, and a VTU. checkMesh/Fluent logs are static files."""
import os
import shutil

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "samples")

HDR = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "constant/polyMesh";
    object      {obj};
}}
"""


def write_polymesh(case, X, patch_map, two_d=False):
    """X: (nx+1, ny+1, nz+1, 3) node coords. patch_map: {'xmin':name,...}."""
    nx, ny, nz = (s - 1 for s in X.shape[:3])
    pid = lambda i, j, k: (k * (ny + 1) + j) * (nx + 1) + i  # noqa: E731
    cid = lambda i, j, k: (k * ny + j) * nx + i  # noqa: E731
    pts = np.array([X[i, j, k] for k in range(nz + 1) for j in range(ny + 1) for i in range(nx + 1)])

    def fx(i, j, k):
        return [pid(i, j, k), pid(i, j + 1, k), pid(i, j + 1, k + 1), pid(i, j, k + 1)]

    def fy(i, j, k):
        return [pid(i, j, k), pid(i, j, k + 1), pid(i + 1, j, k + 1), pid(i + 1, j, k)]

    def fz(i, j, k):
        return [pid(i, j, k), pid(i + 1, j, k), pid(i + 1, j + 1, k), pid(i, j + 1, k)]

    internal = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                c = cid(i, j, k)
                if i < nx - 1:
                    internal.append((c, cid(i + 1, j, k), fx(i + 1, j, k)))
                if j < ny - 1:
                    internal.append((c, cid(i, j + 1, k), fy(i, j + 1, k)))
                if k < nz - 1:
                    internal.append((c, cid(i, j, k + 1), fz(i, j, k + 1)))
    internal.sort(key=lambda t: (t[0], t[1]))

    bfaces = {}
    for k in range(nz):
        for j in range(ny):
            bfaces.setdefault("xmin", []).append((cid(0, j, k), fx(0, j, k)[::-1]))
            bfaces.setdefault("xmax", []).append((cid(nx - 1, j, k), fx(nx, j, k)))
    for k in range(nz):
        for i in range(nx):
            bfaces.setdefault("ymin", []).append((cid(i, 0, k), fy(i, 0, k)[::-1]))
            bfaces.setdefault("ymax", []).append((cid(i, ny - 1, k), fy(i, ny, k)))
    for j in range(ny):
        for i in range(nx):
            bfaces.setdefault("zmin", []).append((cid(i, j, 0), fz(i, j, 0)[::-1]))
            bfaces.setdefault("zmax", []).append((cid(i, j, nz - 1), fz(i, j, nz)))

    # merge sides that map to the same patch name
    patches = {}
    for side in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
        name, ptype = patch_map[side]
        patches.setdefault(name, [ptype, []])[1].extend(bfaces[side])

    faces = [f for _, _, f in internal]
    owner = [o for o, _, _ in internal]
    neigh = [n for _, n, _ in internal]
    bnd = []
    start = len(faces)
    for name, (ptype, lst) in patches.items():
        bnd.append((name, ptype, len(lst), start))
        for o, f in lst:
            faces.append(f)
            owner.append(o)
        start += len(lst)

    pm = os.path.join(case, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    with open(os.path.join(case, "system", "controlDict"), "w") as f:
        f.write(HDR.format(cls="dictionary", obj="controlDict").replace('constant/polyMesh', 'system') +
                "application simpleFoam;\nwriteFormat ascii;\n")
    with open(os.path.join(pm, "points"), "w") as f:
        f.write(HDR.format(cls="vectorField", obj="points") + f"\n{len(pts)}\n(\n")
        f.writelines(f"({p[0]:.10g} {p[1]:.10g} {p[2]:.10g})\n" for p in pts)
        f.write(")\n")
    with open(os.path.join(pm, "faces"), "w") as f:
        f.write(HDR.format(cls="faceList", obj="faces") + f"\n{len(faces)}\n(\n")
        f.writelines(f"4({' '.join(map(str, fc))})\n" for fc in faces)
        f.write(")\n")
    for nm, lst in (("owner", owner), ("neighbour", neigh)):
        with open(os.path.join(pm, nm), "w") as f:
            f.write(HDR.format(cls="labelList", obj=nm) + f"\n{len(lst)}\n(\n")
            f.writelines(f"{x}\n" for x in lst)
            f.write(")\n")
    with open(os.path.join(pm, "boundary"), "w") as f:
        f.write(HDR.format(cls="polyBoundaryMesh", obj="boundary") + f"\n{len(bnd)}\n(\n")
        for name, ptype, n, st in bnd:
            f.write(f"    {name}\n    {{\n        type {ptype};\n        nFaces {n};\n        startFace {st};\n    }}\n")
        f.write(")\n")


def grid(nx, ny, nz, Lx=1.0, Ly=1.0, Lz=1.0):
    x, y, z = np.linspace(0, Lx, nx + 1), np.linspace(0, Ly, ny + 1), np.linspace(0, Lz, nz + 1)
    return np.stack(np.meshgrid(x, y, z, indexing="ij"), -1)


def main():
    if os.path.exists(S):
        shutil.rmtree(S)
    os.makedirs(S)
    pm2d = {"xmin": ("inlet", "patch"), "xmax": ("outlet", "patch"), "ymin": ("bottomWall", "wall"),
            "ymax": ("topWall", "wall"), "zmin": ("frontAndBack", "empty"), "zmax": ("frontAndBack", "empty")}
    pm3d = {"xmin": ("inlet", "patch"), "xmax": ("outlet", "patch"), "ymin": ("walls", "wall"),
            "ymax": ("walls", "wall"), "zmin": ("walls", "wall"), "zmax": ("walls", "wall")}

    # 1. good 3D
    write_polymesh(os.path.join(S, "of_good_3d"), grid(12, 10, 8, 2, 1, 1), pm3d)

    # 2. 2D channel with a strongly sheared region near the bottom wall at the outlet end
    X = grid(40, 20, 1, 4, 1, 0.1)
    for i in range(30, 41):
        for j in range(0, 6):
            s = (i - 30) / 10 * (1 - j / 6)
            X[i, j, :, 0] += 0.0
            X[i, j, :, 1] = X[i, j, :, 1] * (1 - 0.8 * s) + 0.0
    for i in range(32, 39):          # zig-zag shear -> high non-orthogonality
        X[i, 1:5, :, 0] += 0.09 * ((-1) ** i)
    write_polymesh(os.path.join(S, "of_distorted_2d"), X, pm2d, two_d=True)

    # 2b. valid 2D mesh with a strongly sheared near-wall strip -> high non-orthogonality, no inversion
    X = grid(40, 20, 1, 4, 1, 0.1)
    for j in range(21):
        X[:, j, :, 0] += 0.15 * min(j, 5)
    write_polymesh(os.path.join(S, "of_sheared_2d"), X, pm2d, two_d=True)

    # 3. 3D with an inverted cell (one interior node pushed through its neighbour)
    X = grid(8, 8, 8)
    X[4, 4, 4] += np.array([0.2, 0.2, 0.2])
    write_polymesh(os.path.join(S, "of_inverted_3d"), X, pm3d)

    # 4. Gmsh tet mesh with physical groups and a sliver tet
    import meshio
    import pyvista as pv
    rng = np.random.default_rng(0)
    box = pv.Box(bounds=(0, 1, 0, 1, 0, 1), level=3).triangulate()
    inner = rng.random((300, 3)) * 0.9 + 0.05
    cloud = pv.PolyData(np.vstack([box.points, inner]))
    tet = cloud.delaunay_3d()
    cells = tet.cells_dict[pv.CellType.TETRA]
    P = np.asarray(tet.points)
    # add a sliver: 4 almost-coplanar points outside the box
    base = len(P)
    P = np.vstack([P, [[1.2, 0, 0], [1.3, 0.1, 0], [1.2, 0.1, 0.0], [1.25, 0.05, 0.001]]])
    cells = np.vstack([cells, [[base, base + 1, base + 2, base + 3]]])
    surf = box.faces.reshape(-1, 4)[:, 1:]
    zmin_mask = np.isclose(P[surf].mean(1)[:, 2], 0)
    tags_tet = np.ones(len(cells), dtype=int)
    tags_tet[-1] = 2
    m = meshio.Mesh(P, [("triangle", surf[zmin_mask]), ("triangle", surf[~zmin_mask]), ("tetra", cells)],
                    cell_data={"gmsh:physical": [np.full(zmin_mask.sum(), 10), np.full((~zmin_mask).sum(), 11), tags_tet],
                               "gmsh:geometrical": [np.full(zmin_mask.sum(), 10), np.full((~zmin_mask).sum(), 11), tags_tet]},
                    field_data={"fluid": np.array([1, 3]), "fin": np.array([2, 3]),
                                "bottom": np.array([10, 2]), "outer": np.array([11, 2])})
    meshio.write(os.path.join(S, "gmsh_box_sliver.msh"), m, file_format="gmsh22", binary=False)

    # 5. clean VTU (hex)
    g = pv.StructuredGrid(*np.meshgrid(np.linspace(0, 1, 6), np.linspace(0, 1, 6), np.linspace(0, 0.5, 4), indexing="ij"))
    g.cast_to_unstructured_grid().save(os.path.join(S, "hex_block.vtu"))
    print("samples written to", S)


if __name__ == "__main__":
    main()
