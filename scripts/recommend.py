"""Turn findings into location-specific, verifiable mesh improvement actions."""
from __future__ import annotations


ACTION = {
    "native_mesh_checks_failed": ("按原生 checkMesh 的失败项逐项排查对应区域；优先检查贴体面、尖角和加层终止处，修复后重新生成网格。", "重新运行 checkMesh -allGeometry -allTopology，确认 Failed mesh checks 归零。"),
    "negative_volume": ("检查反转单元的节点顺序、重叠/自交几何和极薄间隙；修复几何后重划局部网格。", "重新运行 checkMesh，确认零/负体积单元为 0。"),
    "inverted": ("检查翻转单元的节点顺序和局部几何，重新生成这些单元及相邻区域。", "确认缩放雅可比与体积均为正。"),
    "face_pyramids": ("检查报警面两侧单元及面法向，修复面朝向或重新划分扭曲单元。", "重新运行 checkMesh，确认面金字塔错误消失。"),
    "face_area": ("合并重复点并清除退化面，重新划分该表面及邻近体单元。", "重新运行 checkMesh，确认零面积面为 0。"),
    "open_cells": ("检查缺失面、重复面和导入接口，修补后重划相邻单元。", "重新运行 checkMesh，确认单元和边界封闭。"),
    "multiple_regions": ("检查小区域是否为预期的流体区域；若属孤立碎片，修复封闭性和 locationInMesh 后重划。", "确认连通区域的数量与物理区域一致。"),
    "non_orthogonality": ("在标出的位置平滑尺寸过渡、调整块划分或贴体/层网格；优先处理壁面和高梯度区域。", "重新检查超过 70° 的面数和最大值，并对照修改前的局部位置。"),
    "skewness": ("定位歪斜面的邻接单元，清理尖角/窄缝，平滑表面尺寸过渡并重新贴体。", "重新检查超标面数、分布和最大歪斜度。"),
    "aspect_ratio": ("若位于规则近壁层，先核对壁面法向厚度与层间过渡；若位于核心流区，缩小相邻尺寸跳变并重划。", "确认高长宽比单元位于设计的近壁层，且非正交性与歪斜度未恶化。"),
    "cell_determinant": ("检查近退化单元的尖角、压扁层和节点位置，重新划分该局部。", "重新运行 checkMesh，确认单元行列式达到所用规则阈值。"),
    "interpolation_weight": ("在报警面两侧增加过渡层，降低相邻单元尺寸突变。", "重新检查插值权重低于阈值的面数。"),
    "volume_ratio": ("平滑局部网格尺寸场，避免大单元直接连接很小的单元。", "重新检查相邻体积比及其位置。"),
    "concave_cells": ("检查贴体面尖角、狭缝、层终止处及相邻细化级别的过渡；按问题区域调整表面分辨率、层厚和层生长限制后重新划分。", "重新运行完整 checkMesh，比较凹单元数量及失败检查项，并复核加层覆盖率。"),
    "near_wall_nonortho": ("在该壁面首层单元与第二层之间改善法向排列；检查贴体面、层坍塌和层末端到核心网格的尺寸突变。", "复查该壁面首层相邻内部面的最大非正交角和超过 70° 的面数。"),
    "near_wall_skew": ("检查该壁面首层单元的扭曲和层间连接；平滑壁面单元尺寸并避免层在局部突然终止。", "复查该壁面首层相邻内部面的最大歪斜度和超过 4 的面数。"),
    "boundary_layers": ("在低于目标层数的壁面区域检查尖角、狭缝及贴体面尺寸；核对 snappyHexMesh 的 minThickness、featureAngle 与层末端缓冲设置，再局部重划。", "重新读取 nSurfaceLayers 边界场，确认低于目标层数的面积比例与位置改善，并复查近壁歪斜和非正交性。"),
    "layer_coverage": ("在零层覆盖的壁面区域检查表面尺寸、曲率与狭缝；核对 minThickness、maxFaceThicknessRatio、maxThicknessToMedialRatio 等加层限制，分区调参后重划。", "重新读取 nSurfaceLayers 边界场，确认零层面积比例下降且问题没有转移到相邻壁面。"),
    "layer_growth": ("降低层间增长率，并协调最后一层与核心网格尺寸；必要时增加层数以保持总厚度。", "重新统计层间增长率 P95，并检查层末端的非正交性与歪斜度。"),
    "mass_balance": ("先核对入口/出口通量的单位与符号、遗漏的开口及边界条件；再检查严重畸变单元与求解收敛。", "复算所有边界质量通量，确认相对不平衡低于设定容差。"),
    "energy_balance": ("核对壁面热流、出入口焓流、热源及功项是否完整；在温度梯度大的壁面补足法向网格后复算。", "复算完整的能量收支并对比换热量。"),
    "monitor_drift": ("先检查残差停止条件、边界条件和数值设置，并继续迭代至目标量稳定；若仍持续漂移，再定位相关壁面或强梯度区域并调整局部网格。", "重新检查目标量监测序列，确认末段变化低于容差后再比较不同网格。"),
    "monitor_spread": ("检查目标量在末段是否仍往复波动；先核对残差、松弛因子和边界条件，并继续迭代或调整求解设置。若波动持续，检查当前稳态模型是否适合该流动。", "重新检查末段 P05–P95 波动范围；确认低于容差后再比较不同网格。"),
    "grid_sensitivity": ("对目标量影响最大的壁面、弯头、入口发展段或温度梯度区继续局部加密；各网格保持同一物理模型与边界条件。", "增加更细网格并比较目标量，直到细/中网格变化低于设定容差。"),
}


def _where(f):
    loc = f.get("location") or {}
    if loc.get("near_patches"):
        label = "边界 " + "、".join(str(x["patch"]) for x in loc["near_patches"][:3])
        if loc.get("bbox_min"):
            label += f"，坐标范围 {loc['bbox_min']} 至 {loc['bbox_max']}"
        return label
    if loc.get("zones"):
        return "区域 " + "、".join(str(x["zone"]) for x in loc["zones"][:3])
    if loc.get("bbox_min"):
        return f"坐标范围 {loc['bbox_min']} 至 {loc['bbox_max']}"
    return "报告未提供局部坐标；先用 checkMesh 集合或质量场定位"


def build(res):
    items = []
    cfd = res.get("cfd", {})
    for f in res.get("findings", []):
        if f["severity"] == "ok":
            continue
        metric = f["metric"]
        if metric == "yplus":
            wall = f["name_zh"].split(" 的 y⁺")[0].removeprefix("壁面 ")
            check = cfd.get("wall_checks", {}).get(wall, {})
            stats = check.get("yplus", {})
            bounds = check.get("target_yplus", [])
            if len(bounds) == 2 and stats.get("p95", 0) > bounds[1]:
                factor = bounds[1] / stats["p95"]
                action = (f"壁面 {wall} 的高 y⁺ 区域优先减小第一层法向尺寸；按 y⁺ 与首层距离近似成正比，"
                          f"可先试约 {factor:.2f} 倍的当前首层距离，再重新求解校核。保持足够的总层数及平滑过渡。")
            elif check.get("low_y_wall_function"):
                action = (f"壁面 {wall} 的 y⁺ 低于所设筛查下限；先核对当前 nutkWallFunction / epsilonWallFunction 的低 y⁺ 分支"
                          "是否符合关注的壁面剪切、压降或换热目标。若需要把首层置于对数区，再按实际 y⁺ 分布增大首层法向距离，"
                          "同时检查尺寸过渡与局部流动分辨率；不要仅为满足区间而直接放粗网格。")
            else:
                action = (f"壁面 {wall} 的局部 y⁺ 低于目标下限；检查所用壁面函数与该区域是否匹配，"
                          "再调整首层距离或改用适合低 y⁺ 的壁面处理。")
            verify = "重新计算该壁面 yPlus，并比较壁面剪切、压降/换热量及其网格敏感性。"
            where = f"壁面 {wall}"
        else:
            action, verify = ACTION.get(metric, ("针对超标位置调整局部尺寸、单元形状和连接方式。", "重复同一指标检查并比较超标单元数。"))
            if metric == "native_mesh_checks_failed" and any(
                    item["metric"] == "concave_cells" and item["severity"] != "ok"
                    for item in res.get("findings", [])):
                action = ("本次原生失败项包含凹单元：先检查贴体表面转角、窄缝、层终止处和相邻细化级别的过渡，"
                          "再按局部位置调整表面网格、层厚和层生长限制；不要仅凭 snappyHexMesh 的完成信息放行。")
            if metric == "grid_sensitivity" and cfd.get("solution_checks", {}).get("grid_sensitivity"):
                if any(check.get("unstable_monitor_histories") for check in cfd["solution_checks"]["grid_sensitivity"].values()):
                    action = ("先使各套网格上的目标量监测序列稳定，再重新比较细/中结果；若变化仍超容差，"
                              "定位壁面、分离区和强梯度区后局部加密，保持物理模型与边界条件一致。")
                    verify = "各套目标量末段变化先低于容差，再比较细/中网格差异；必要时增加更细网格。"
                elif any(check.get("missing_monitor_histories") for check in cfd["solution_checks"]["grid_sensitivity"].values()):
                    action = "先补齐粗、中、细三套网格各自的目标量监测序列，并确认末段稳定；然后重新比较网格。"
                    verify = "三套网格目标量末段变化均低于容差后，重新计算细/中差异。"
            if metric in {"boundary_layers", "layer_coverage", "layer_growth"}:
                where = _where(f) if f.get("location") else "壁面 " + f["name_zh"].split()[1]
            elif metric in {"mass_balance", "energy_balance"}:
                where = "全域边界通量"
            elif metric in {"monitor_drift", "monitor_spread", "grid_sensitivity"}:
                where = "对应的监测目标量及影响区域"
            else:
                where = _where(f)
        evidence = f"极值 {f.get('value')}"
        if f.get("n_bad") is not None:
            evidence += f"；范围 {f['n_bad']} / {f.get('n_total') or '未知'}"
        if f.get("definition"):
            evidence += f"；{f['definition']}"
        items.append({"priority": f["severity"], "metric": metric, "issue": f["name_zh"],
                      "where": where, "evidence": evidence,
                      "mesh_action": action, "verification": verify})
    order = {"critical": 0, "high": 1, "moderate": 2}
    focus_order = {"monitor_drift": 0, "monitor_spread": 0, "grid_sensitivity": 1, "yplus": 2}
    return sorted(items, key=lambda item: (order.get(item["priority"], 3), focus_order.get(item["metric"], 3)))
