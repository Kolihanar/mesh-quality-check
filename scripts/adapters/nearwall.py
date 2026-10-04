"""Geometry-based first-cell measurements for OpenFOAM wall patches.

These measurements describe the actual mesh. They do not infer a prism-layer
count from a run of aligned core cells.
"""
from __future__ import annotations

import numpy as np


def inspect(an: dict) -> dict:
    faces, owner, fctr, farea = an["faces"], an["owner"], an["fctr"], an["farea"]
    cctr, vol = an["cctr"], an["vol"]
    n_internal = an["nInt"]
    face_mag = np.linalg.norm(farea, axis=1)
    wall_stats = {}
    for patch in an["patches"]:
        if patch["type"] != "wall" or not patch["nFaces"]:
            continue
        ids = np.arange(patch["startFace"], patch["startFace"] + patch["nFaces"])
        good = face_mag[ids] > 0
        ids = ids[good]
        if not len(ids):
            wall_stats[patch["name"]] = {"n_faces": patch["nFaces"], "status": "invalid_faces"}
            continue
        normal = farea[ids] / face_mag[ids, None]
        distance = np.abs(np.einsum("ij,ij->i", cctr[owner[ids]] - fctr[ids], normal))
        equivalent_height = np.abs(vol[owner[ids]]) / face_mag[ids]
        perimeter_scale = np.sqrt(face_mag[ids])
        area = face_mag[ids]
        cells = np.unique(owner[ids])
        adjacent_internal = np.isin(owner[:n_internal], cells) | np.isin(an["neigh"], cells)
        no = an["nonortho"][adjacent_internal]
        skew = an["skew"][:n_internal][adjacent_internal]
        wall_stats[patch["name"]] = {
            "n_faces": patch["nFaces"],
            "measured_faces": int(len(ids)),
            "face_ids": ids.tolist(),
            "local_face_indices": np.where(good)[0].tolist(),
            "face_centres": fctr[ids].tolist(),
            "wall_distance": distance.tolist(),
            "first_cell_volume_over_face_area": equivalent_height.tolist(),
            "face_sqrt_area": perimeter_scale.tolist(),
            "face_area": area.tolist(),
            "distance_min": float(distance.min()),
            "distance_p05": float(np.percentile(distance, 5)),
            "distance_median": float(np.median(distance)),
            "distance_p95": float(np.percentile(distance, 95)),
            "distance_max": float(distance.max()),
            "normal_to_tangential_scale_p95": float(np.percentile(equivalent_height / perimeter_scale, 95)),
            "first_cell_aspect_p95": float(np.percentile(an["aspect"][cells], 95)),
            "near_wall_internal_faces": int(len(no)),
            "near_wall_nonortho_max": float(no.max()) if len(no) else None,
            "near_wall_nonortho_p95": float(np.percentile(no, 95)) if len(no) else None,
            "near_wall_nonortho_over70": int((no > 70).sum()),
            "near_wall_nonortho_over65": int((no > 65).sum()),
            "near_wall_skew_max": float(skew.max()) if len(skew) else None,
            "near_wall_skew_p95": float(np.percentile(skew, 95)) if len(skew) else None,
            "near_wall_skew_over4": int((skew > 4).sum()),
            "near_wall_skew_over2_5": int((skew > 2.5).sum()),
        }
    return wall_stats


def compact(raw: dict) -> dict:
    """Strip per-face arrays from the human-sized JSON summary."""
    return {name: {k: v for k, v in data.items() if k not in
            {"face_ids", "local_face_indices", "face_centres", "wall_distance", "first_cell_volume_over_face_area", "face_sqrt_area", "face_area"}}
            for name, data in raw.items()}
