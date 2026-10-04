# Skill 验证图说明

图 1 基于 `tests/run_tests.py` 定义的 10 个预设样例。当前环境成功执行 7 项，7 项来源识别、总体分级及指定异常与预期一致；另 3 项因缺少 `meshio` / `pyvista` 未运行。预设样例的匹配率不能用作真实工程算例的检出率。

图 2 和图 3 使用 `tests/samples/of_good_3d` 的 432 个壁面面几何与面面积，但逐面 y⁺ 与 `nSurfaceLayers` 是为了测试检测路径而人为赋值。图 2 应检出 100 个 y⁺ 超标面，超标面积占 26.0%。图 3 的完全缺层场有 84.4% 面积覆盖率；另一场虽然覆盖率为 100%，但 15.6% 的面积低于 12 层目标。

三幅图展示了当前代码的回归表现和指标区分能力。另已完成 [OpenFOAM 12 内流算例的原生 y⁺ 对照](official_openfoam12/README.md)、[同一官方内流算例的三网格目标量监测与续算图](official_openfoam12_grid/README.md)、[官方封闭内流的实际加层与原生质量失败对照](official_openfoam12_igloo/README.md) 和 [OpenFOAM 12 motorBikeSteady 真实加层字段对照](official_openfoam12_motorbike/README.md)。三网格实测显示残差停止后目标量仍漂移；续算还显示均值漂移已低时仍可存在明显往复波动，因而网格差异只能作初步比较。iglooWithFridges 的完整 `checkMesh` 未通过，故仅验证真实层字段和壁面组函数；motorBikeSteady 是外流，仅验证字段读取和问题定位。换热目标量及目标量稳定后的网格收敛仍需验证。

首页另展示三张真实官方算例图：[`pitzDailySteady` 原生输出/Skill 直接对照](official_openfoam12/native_vs_skill.png)、[实际加层面积](official_openfoam12_igloo/actual_layers.png)和[三网格续算目标量监测](official_openfoam12_grid/extended_three_grid_evidence.png)。具体核对命令与 Codex 提示词见 [Codex 案例演示](../reference/codex_demo.md)。

复现：在 Skill 根目录运行 `python validation/generate.py`。原始结果保存于 `validation/evidence.json`；PNG 用于预览，SVG 可用于文档。
