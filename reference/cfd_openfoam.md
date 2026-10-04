# OpenFOAM 单相 RANS 内流适用性检查

此路线读取 OpenFOAM 算例目录，保留原有的 checkMesh/ASCII polyMesh 质量检查，并增加近壁几何、y⁺、实际层记录和已有试算摘要。输入参数不足时，在 `cfd.missing` 中列出缺口，不把缺口当作通过。

要得到“现有证据支持当前用途”的判断，需有与当前 polyMesh 的单元/面数量匹配、结论为 `Mesh OK` 的完整 checkMesh 输出。仅有 Python 的几何计算时仍可得到分布与优化建议，但会标出原生拓扑检查缺口。

## 工况 JSON

`--context` 接受 JSON 文件。下面的值仅为格式示例，使用时应替换为该算例的实际物性与测量值：

```json
{
  "flow": {
    "turbulence_model": "kOmegaSST",
    "nu": 1e-6,
    "rho": 1000,
    "heat_transfer": true
  },
  "wall_defaults": {
    "treatment": "wall_resolved",
    "wall_conditions_verified": true,
    "target_yplus": [0, 2],
    "friction_velocity": 0.05,
    "target_layers": 12,
    "min_layer_coverage": 0.95,
    "max_growth_p95": 1.25
  },
  "walls": {
    "heatedWall": {
      "measured_layers": 12,
      "measured_layer_coverage": 0.97,
      "measured_growth_p95": 1.18
    }
  },
  "results": {
    "mass_flux_kg_s": {"inlet": -1.0, "outlet": 1.001},
    "advective_enthalpy_W": {"inlet": -10000, "outlet": 12000},
    "wall_heat_flow_W": {"heatedWall": -2000},
    "monitor_history": {
      "pressure_drop_Pa_coarse": [103, 103, 103, 103, 103, 103, 103, 103, 103, 103],
      "pressure_drop_Pa_medium": [101, 101, 101, 101, 101, 101, 101, 101, 101, 101],
      "pressure_drop_Pa_fine": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    },
    "grid_study": [
      {"n_cells": 200000, "pressure_drop_Pa": 103},
      {"n_cells": 400000, "pressure_drop_Pa": 101},
      {"n_cells": 800000, "pressure_drop_Pa": 100}
    ]
  }
}
```

壁面专属的 `walls.<patch>` 值覆盖 `wall_defaults`。如果未显式设置 `target_yplus`，`wall_resolved` 默认筛查目标为 0–2，`standard_wall_function` 为 30–300；自动或混合壁面处理必须显式给出目标。这些默认区间不是全部壁面函数的有效性硬界，应按具体 OpenFOAM 版本、边界条件和关注结果确认。报告的 `target_source` 区分用户显式目标与 treatment 默认值。`nu` 单位 m²/s，`rho` 为 kg/m³，`friction_velocity` 为 m/s。也可用 `wall_shear_stress`（Pa）和 `rho` 代替摩擦速度。程序会从简单的 `transportProperties` 或 OpenFOAM 12 的 `physicalProperties` 中读取 `nu`，从 `turbulenceProperties`/`momentumTransport` 中读取湍流模型，从 `0/nut` 等记录壁面场类型；复杂 include、变量和 codeStream 配置需显式补充。

若实际壁面场文件不在常规 `0/` 目录，先核对其壁面条件，再用 `wall_conditions_verified: true` 明确记录已人工核对。该标志是外部声明，报告不会把它描述为程序自动检查。

只有网格时，用单元中心到壁面平面的法向投影作首层距离；提供摩擦速度后估算 `y⁺ = y uτ / nu`。这是计算前估算。已有试算时，优先读取最新时间目录的 ASCII `yPlus` 场，或用 `--yplus-field` 指定场文件。只有实际 yPlus 输出才可核对运行后的近壁分布；报告列出各壁面的面积加权统计和目标区间外的壁面面积比例。OpenFOAM 的 yPlus 功能对象可调用壁面函数自己的 `yPlus()` 定义，解释该场时须核对所用壁面函数。

报告还单独统计每个 wall patch 首层单元邻接内部面的非正交角、歪斜度和首层单元长宽比，供区分规则的近壁拉伸与局部层扭曲。

若 snappyHexMesh 启用了 `writeFlags (layerFields);`，本工具自动在算例时间目录及 `constant/` 寻找 ASCII `nSurfaceLayers` 场；也可用 `--layer-field` 指定。读取该场各 wall patch 的 `boundaryField` 实际层数，按壁面面积计算层覆盖率、低于目标层数的面积比例，并给出缺层位置。报告会核对边界面数和场内单元数（若字段为非均匀内部场）；字段错误时不把它计为通过。`snappyHexMeshDict` 中同名 `nSurfaceLayers` 设置是**期望层数**，不能替代生成后的场；OpenFOAM 源码也将实际层数写入壁面边界场。未产生层字段时，可在 `measured_layers` 与 `measured_layer_coverage` 中填写从生成记录或 ParaView 核对过的实测值。OpenFOAM `boundary` 的 `inGroups` 会用于把 `0/nut`、`0/epsilon`、`0/alphat` 的壁面组条件映射到实际 patch；同一字段若有 patch 专属条件，以专属条件为准。

OpenFOAM 12 官方 [`motorBikeSteady` 加层实测](../validation/official_openfoam12_motorbike/README.md) 验证了实际层字段解析和含 `:`、`%` 的部件 patch 名定位。该算例是外流，仅作为层字段验证；其原生 `checkMesh` 未通过，不能用来证明网格适于求解。

OpenFOAM 12 官方 [`iglooWithFridges` 封闭内流加层实测](../validation/official_openfoam12_igloo/README.md) 进一步验证了面积加权层覆盖率与未达到目标层数面积的区分、壁面组函数继承及原生 `checkMesh` 失败项保留。该网格含大量凹单元，故未继续运行流动/热流求解器。

`measured_growth_p95` 仍需来自实际网格的层间厚度测量；期望 `expansionRatio` 不是实测值。报告不会把一串规则六面体自动认定为边界层。若同时提供层字段和外部实测层数/覆盖率，报告优先采用层字段，并保留增长率的外部输入。

已有试算的通量均采用**向计算域外为正**的符号约定。`mass_flux_kg_s` 是每个开口的质量通量；对恒密度不可压缩流，也可在 `flow.constant_density` 明确设为 `true` 后，用 `volumetric_flux_m3_s` 提供每个开口的体积通量，计算相对守恒不平衡，不需假定密度。若两者都给出，优先使用质量通量。OpenFOAM 的 `phi` 字段须先核对 `dimensions`：`[0 3 -1 0 0 0 0]` 是 m³/s，不能标作 kg/s。[官方内流算例](../validation/official_openfoam12/README.md) 已用原生 `surfaceFieldValue` 与 ASCII `phi` 相互核对。`advective_enthalpy_W` 与 `wall_heat_flow_W` 用于无未列体热源/功项的稳态算例。`monitor_history` 同时检查末尾两个窗口均值漂移（默认容差 0.5%）及最后 20% 样本的 P05–P95 相对跨度（默认容差 1%）；后者防止均值抵消往复波动。可分别用 `monitor_drift_tolerance`、`monitor_spread_tolerance` 调整筛查容差。`grid_study` 使用同一物理模型与边界条件的至少三套网格，按单元数排序后比较细/中网格目标量的相对变化；这是一项敏感性检查，不等同于严格 GCI 或误差上界。要把这项比较当作当前用途的充分证据，需同时提供 `目标量名_coarse`、`目标量名_medium`、`目标量名_fine` 三条监测序列并确认末段漂移和波动都在容差内。缺少任何一条或出现未稳定现象，网格差异均标为初步结果。[真实三网格内流算例](../validation/official_openfoam12_grid/README.md) 展示了均值漂移已低但末段仍往复波动的识别。

CLI：

```bash
python scripts/mesh_check.py case/ --context cfd_context.json --yplus-field case/1000/yPlus --layer-field case/1/nSurfaceLayers -o report_dir
```

## 判断和优化建议

先处理负体积、开放单元等致命错误，再处理壁面与强梯度区域的严重歪斜/非正交性；之后复核首层距离、真实 y⁺、层数/覆盖率与层末端的尺寸过渡。高长宽比若位于规则近壁层，结合正交性与层法向检查。对每条问题，报告给出问题位置、极值/范围、局部重划或尺寸调整动作，以及应重复的检查。y⁺ 高于目标时给出的首层尺寸比例只是首轮调整建议，需重算 yPlus 才能确认。y⁺ 低于 30 不能一概判为求解失败：OpenFOAM 12 的 `nutkWallFunction` 和 `epsilonWallFunction` 含低 y⁺ 分支；当程序识别到 kEpsilon + 这组条件时，建议先检查壁面剪切和目标量网格敏感性，再判断是否需要放大首层高度。[真实算例验证](../validation/official_openfoam12/README.md) 展示了这一情况。

参考：

- [OpenFOAM 壁面函数与 y⁺ 定义](https://doc.openfoam.com/2312/tools/processing/models/turbulence/ras/wall-functions/)
- [OpenFOAM Foundation 12 nutkWallFunction 源码](https://cpp.openfoam.org/v12/nutkWallFunctionFvPatchScalarField_8C_source.html)
- [OpenFOAM Foundation 12 epsilonWallFunction 源码](https://cpp.openfoam.org/v12/epsilonWallFunctionFvPatchScalarField_8C_source.html)
- [OpenFOAM Foundation 12 yPlus 功能对象源码](https://cpp.openfoam.org/v12/yPlus_8C_source.html)
- [OpenFOAM yPlus 功能对象](https://doc.openfoam.com/2212/tools/post-processing/function-objects/field/yPlus/)
- [OpenFOAM snappyHexMesh 层生成](https://doc.openfoam.com/2212/tools/pre-processing/mesh/generation/snappyhexmesh/layers/)
- [OpenFOAM 实际层数场写入源码](https://cpp.openfoam.org/v13/snappyLayerDriver_8C_source.html)
- [Fluent 网格分布与近壁解析原则](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridQuality.html)
