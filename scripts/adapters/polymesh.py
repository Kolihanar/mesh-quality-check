"""Minimal reader for ASCII OpenFOAM polyMesh + OpenFOAM-style quality metrics.

Used to get per-face/per-cell distributions and *locations* of bad elements,
which checkMesh's console output does not give, and as a fallback when
OpenFOAM itself is not installed (e.g. on Windows without WSL).

Formulas follow OpenFOAM primitiveMesh / primitiveMeshTools
(face centres/areas by triangle decomposition, cell centres/volumes by pyramid
decomposition, non-orthogonality, skewness, cell aspect ratio). Small numeric
differences from checkMesh are possible; checkMesh stays authoritative.
"""
from __future__ import annotations

import gzip
import os
import re

import numpy as np

_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


class BinaryFormatError(RuntimeError):
    pass


def _read(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            opener = gzip.open if p.endswith(".gz") else open
            with opener(p, "rb") as f:
                return f.read().decode("latin-1")
    raise FileNotFoundError(path)


def _header_and_body(txt):
    txt = _COMMENT.sub("", txt)
    m = re.search(r"FoamFile\s*\{(.*?)\}", txt, re.S)
    header = {}
    if m:
        for k, v in re.findall(r"(\w+)\s+([^;]+);", m.group(1)):
            header[k] = v.strip().strip('"')
        txt = txt[m.end():]
    if header.get("format", "ascii") != "ascii":
        raise BinaryFormatError("binary polyMesh")
    return header, txt


def _first_list(body):
    """Return (N, content_between_outer_parens) of the first top-level list."""
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise ValueError("no list found")
    n = int(m.group(1))
    i = m.end()
    depth = 1
    j = i
    while depth:
        c = body[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        j += 1
    return n, body[i:j - 1], body[j:]


def read_points(pm):
    _, body = _header_and_body(_read(os.path.join(pm, "points")))
    n, content, _ = _first_list(body)
    arr = np.array(content.replace("(", " ").replace(")", " ").split(), dtype=float)
    return arr.reshape(n, 3)


def read_faces(pm):
    header, body = _header_and_body(_read(os.path.join(pm, "faces")))
    if "Compact" in header.get("class", ""):
        n1, offs, rest = _first_list(body)
        _, labs, _ = _first_list(rest)
        offs = np.array(offs.split(), dtype=np.int64)
        labs = np.array(labs.split(), dtype=np.int64)
        return [labs[offs[i]:offs[i + 1]] for i in range(len(offs) - 1)]
    n, content, _ = _first_list(body)
    faces = []
    for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", content):
        faces.append(np.array(m.group(2).split(), dtype=np.int64))
    if len(faces) != n:
        raise ValueError(f"faces: expected {n}, parsed {len(faces)}")
    return faces


def read_labels(pm, name):
    _, body = _header_and_body(_read(os.path.join(pm, name)))
    n, content, _ = _first_list(body)
    return np.array(content.split(), dtype=np.int64)


def read_boundary(pm):
    _, body = _header_and_body(_read(os.path.join(pm, "boundary")))
    m = re.search(r"\d+\s*\((.*)\)", body, re.S)
    patches = []
    for name, block in re.findall(r'("[^"]+"|[^\s{}();]+)\s*\{([^}]*)\}', m.group(1) if m else body):
        name = name.strip('"')
        d = dict(re.findall(r"(\w+)\s+([^;]+);", block))
        group_match = re.search(r"\(([^)]*)\)", d.get("inGroups", ""))
        patch_groups = group_match.group(1).split() if group_match else []
        patches.append({"name": name, "type": d.get("type", "?").strip(),
                        "nFaces": int(d.get("nFaces", 0)), "startFace": int(d.get("startFace", 0)),
                        "groups": patch_groups})
    return patches


# ----------------------------------------------------------------- geometry

def _group_by_size(faces):
    groups = {}
    for i, f in enumerate(faces):
        groups.setdefault(len(f), []).append(i)
    return {k: (np.array(v), np.array([faces[i] for i in v])) for k, v in groups.items()}


def face_geometry(points, groups, n_faces):
    ctr = np.zeros((n_faces, 3))
    area = np.zeros((n_faces, 3))
    for k, (ids, F) in groups.items():
        P = points[F]                                   # (m,k,3)
        if k == 3:
            ctr[ids] = P.mean(1)
            area[ids] = 0.5 * np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
            continue
        fc = P.mean(1)                                  # (m,3)
        Pn = np.roll(P, -1, axis=1)
        c = P + Pn + fc[:, None, :]
        n = np.cross(Pn - P, fc[:, None, :] - P)
        a = np.linalg.norm(n, axis=2)
        sumA = a.sum(1)
        sumAc = (a[:, :, None] * c).sum(1)
        good = sumA > 1e-300
        cc = fc.copy()
        cc[good] = sumAc[good] / (3.0 * sumA[good, None])
        ctr[ids] = cc
        area[ids] = 0.5 * n.sum(1)
    return ctr, area


def cell_geometry(fctr, farea, owner, neigh, n_cells):
    nInt = len(neigh)
    cEst = np.zeros((n_cells, 3))
    cnt = np.zeros(n_cells)
    np.add.at(cEst, owner, fctr)
    np.add.at(cnt, owner, 1)
    np.add.at(cEst, neigh, fctr[:nInt])
    np.add.at(cnt, neigh, 1)
    cEst /= cnt[:, None]

    vol = np.zeros(n_cells)
    cc = np.zeros((n_cells, 3))
    pv_o = np.einsum("ij,ij->i", farea, fctr - cEst[owner])
    pc_o = 0.75 * fctr + 0.25 * cEst[owner]
    np.add.at(vol, owner, pv_o)
    np.add.at(cc, owner, pv_o[:, None] * pc_o)
    pv_n = np.einsum("ij,ij->i", farea[:nInt], cEst[neigh] - fctr[:nInt])
    pc_n = 0.75 * fctr[:nInt] + 0.25 * cEst[neigh]
    np.add.at(vol, neigh, pv_n)
    np.add.at(cc, neigh, pv_n[:, None] * pc_n)
    good = np.abs(vol) > 1e-300
    cc[good] /= vol[good, None]
    cc[~good] = cEst[~good]
    return cc, vol / 3.0


def analyse(pm, max_list=10):
    """Return a dict of per-element metrics + locations for an ASCII polyMesh."""
    points = read_points(pm)
    faces = read_faces(pm)
    owner = read_labels(pm, "owner")
    neigh = read_labels(pm, "neighbour")
    patches = read_boundary(pm)
    nF, nInt = len(faces), len(neigh)
    nC = int(max(owner.max(), neigh.max() if nInt else 0)) + 1

    groups = _group_by_size(faces)
    fctr, farea = face_geometry(points, groups, nF)
    cctr, cvol = cell_geometry(fctr, farea, owner, neigh, nC)
    magS = np.linalg.norm(farea, axis=1) + 1e-300

    # empty directions -> 2D
    sol_dirs = np.ones(3, bool)
    for p in patches:
        if p["type"] == "empty" and p["nFaces"]:
            n = farea[p["startFace"]:p["startFace"] + p["nFaces"]]
            d = np.abs(n).sum(0)
            sol_dirs[np.argmax(d)] = False
    n_dims = int(sol_dirs.sum())

    # non-orthogonality (internal faces)
    d = cctr[neigh] - cctr[owner[:nInt]]
    cosang = np.einsum("ij,ij->i", d, farea[:nInt]) / (np.linalg.norm(d, axis=1) * magS[:nInt] + 1e-300)
    nonortho = np.degrees(np.arccos(np.clip(cosang, -1, 1)))

    # skewness (all faces)
    Cpf = fctr - cctr[owner]
    dd = np.empty_like(Cpf)
    dd[:nInt] = d
    nb = farea[nInt:] / magS[nInt:, None]
    dd[nInt:] = nb * np.einsum("ij,ij->i", nb, Cpf[nInt:])[:, None]
    sv = Cpf - (np.einsum("ij,ij->i", farea, Cpf) / (np.einsum("ij,ij->i", farea, dd) + 1e-300))[:, None] * dd
    msv = np.linalg.norm(sv, axis=1)
    svHat = sv / (msv[:, None] + 1e-300)
    fd = 0.2 * np.linalg.norm(dd, axis=1) + 1e-300
    for k, (ids, F) in groups.items():
        proj = np.abs(np.einsum("mkj,mj->mk", points[F] - fctr[ids][:, None, :], svHat[ids])).max(1)
        fd[ids] = np.maximum(fd[ids], proj)
    skew = msv / fd

    # cell aspect ratio (OpenFOAM cellAspectRatio)
    sumMag = np.zeros((nC, 3))
    np.add.at(sumMag, owner, np.abs(farea))
    np.add.at(sumMag, neigh, np.abs(farea[:nInt]))
    sm = sumMag[:, sol_dirs]
    ar = sm.max(1) / (sm.min(1) + 1e-300)
    if n_dims == 3:
        v = np.maximum(np.abs(cvol), 1e-300)
        ar = np.maximum(ar, sumMag.sum(1) / 6.0 / v ** (2.0 / 3.0))

    # nearest boundary patch for locating problems
    bpatch = np.full(nF, -1)
    for i, p in enumerate(patches):
        bpatch[p["startFace"]:p["startFace"] + p["nFaces"]] = i
    real = [i for i, p in enumerate(patches) if p["type"] not in ("empty", "wedge", "symmetryPlane") and p["nFaces"]]
    bmask = np.isin(bpatch, real)
    tree = None
    try:
        from scipy.spatial import cKDTree
        if bmask.any():
            tree = cKDTree(fctr[bmask])
            bidx = np.where(bmask)[0]
    except Exception:
        pass

    def nearest_patch(xyz):
        if tree is None:
            return None, None
        dist, j = tree.query(xyz)
        return patches[bpatch[bidx[j]]]["name"], float(dist)

    bbox = points.min(0), points.max(0)
    Lref = float(np.linalg.norm(bbox[1] - bbox[0])) or 1.0

    def locate(ids, xyz_all, vals, worst_is_max=True):
        if len(ids) == 0:
            return None
        order = ids[np.argsort(vals[ids])[::-1 if worst_is_max else 1]][:max_list]
        xyz = xyz_all[ids]
        names = []
        if tree is not None:
            dist, j = tree.query(xyz)
            pn = [patches[bpatch[bidx[jj]]]["name"] for jj in j]
            near = dist < 0.05 * Lref
            from collections import Counter
            cnt = Counter(np.array(pn)[near])
            names = [{"patch": k, "count": int(v)} for k, v in cnt.most_common(5)]
            far = int((~near).sum())
            if far:
                names.append({"patch": "（远离边界的内部区域）", "count": far})
        worst_items = []
        for i in order:
            pname, dist = nearest_patch(xyz_all[i])
            worst_items.append({"id": int(i), "value": float(vals[i]),
                                "xyz": [round(float(x), 6) for x in xyz_all[i]],
                                "nearest_patch": pname,
                                "dist_to_patch": None if dist is None else float(f"{dist:.3g}")})
        return {"bbox_min": [float(f"{x:.4g}") for x in xyz.min(0)],
                "bbox_max": [float(f"{x:.4g}") for x in xyz.max(0)],
                "near_patches": names, "worst": worst_items}

    return {
        "n_points": len(points), "n_faces": nF, "n_internal_faces": nInt, "n_cells": nC,
        "n_dims": n_dims, "patches": patches,
        "bounds": [bbox[0].tolist(), bbox[1].tolist()],
        "face_sizes": {int(k): int(len(v[0])) for k, v in groups.items()},
        "fctr": fctr, "cctr": cctr, "nInt": nInt,
        "farea": farea, "faces": faces, "owner": owner, "neigh": neigh,
        "vol": cvol, "nonortho": nonortho, "skew": skew, "aspect": ar,
        "locate": locate,
    }
