# mesh-quality-check

CFD 网格质量与算例适用性检查 Skill：**识别来源 → 检查网格 → 结合工况和已有试算判断 → 输出位置明确的优化建议**。

| 输入 | 识别为 | 检查方式 |
|---|---|---|
| OpenFOAM 算例目录 / `constant/polyMesh` / `.foam` | OpenFOAM | 有 checkMesh 时自动运行；ASCII polyMesh 额外用 Python 计算分布和坏面位置 |
| checkMesh 输出日志 | OpenFOAM | 解析日志 |
| Fluent `mesh/check`、`mesh/quality` 输出或 transcript | Fluent | 解析日志（含最差单元的 zone 和坐标） |
| Fluent `.msh` / `.cas(.h5)` | Fluent | 有 Fluent 时批处理运行；否则生成 journal，ASCII `.msh` 另用通用路线评估 |
| Gmsh `.msh` | Gmsh | meshio + VTK 指标，按物理组定位 |
| `.vtk/.vtu/.cgns/.inp/.med/...` | 通用 | meshio + VTK 指标 |

## 安装

把整个文件夹放到 Agent 的 skills 目录（Codex 为 `~/.codex/skills/`；Claude Code 为 `~/.claude/skills/` 或项目内 `.claude/skills/`），然后安装依赖：

```bash
pip install -r requirements.txt
```

## 直接使用

```bash
python scripts/mesh_check.py <算例目录或文件> -o report_dir
python scripts/mesh_check.py case/ --checkmesh-log case/log.checkMesh -o report_dir
```

输出 `mesh_report.md`（中文报告）和 `mesh_report.json`（结构化结果），视情况附带 `log.checkMesh`、`fluent_mesh_check.jou`、`mesh_quality.vtu`。

### OpenFOAM 单相 RANS 内流

```bash
python scripts/mesh_check.py case/ --context cfd_context.json -o report_dir
python scripts/mesh_check.py case/ --context cfd_context.json --yplus-field case/1000/yPlus -o report_dir
python scripts/mesh_check.py case/ --context cfd_context.json --layer-field case/1/nSurfaceLayers -o report_dir
```

工况文件格式、单位和输入来源见 [`reference/cfd_openfoam.md`](reference/cfd_openfoam.md)。工具直接计算实际网格的首层单元中心距及首层附近的非正交性、歪斜度；有摩擦速度和黏度时估算计算前 y⁺，有 ASCII `yPlus` 场时复核试算后 y⁺。若生成了 ASCII `nSurfaceLayers` 场，工具会自动读取壁面实际层数并计算面积加权覆盖率和缺层位置；也可用 `--layer-field` 显式指定。实际层增长率仍可通过工况文件提供，报告注明外部测量来源。已有试算的质量通量或恒密度流体积通量、能量通量、监测量及三套网格目标量也可纳入复核。与当前网格匹配的原生 `checkMesh` 结果是完整适用性判断的必要证据。官方算例验证路线见 [`reference/official_validation.md`](reference/official_validation.md)。

报告的 `overall` 表示**已执行的网格质量指标**，`readiness` 表示当前 CFD 适用性判断；`cfd.missing` 列出还缺少的关键证据。没有可用检查数据时退出码为 3，不会给出“可接受”。“按优先级排列的网格优化建议”一节列出位置、证据、修改办法和复核方法。

## 调整阈值

所有阈值在 `scripts/thresholds.json`，按软件分开。改动后运行 `python tests/run_tests.py` 确认回归测试仍通过（若期望结果随之改变，同步修改 `tests/run_tests.py` 中的 CASES）。
OpenFOAM CFD 路线可另运行 `python tests/test_cfd.py`。

当前回归结果及三张验证图见 [`validation/summary.md`](validation/summary.md)。运行 `python validation/generate.py` 可从测试样例重新生成 PNG、SVG 和 `evidence.json`；其中近壁示例的 y⁺、层数为人为赋值。[OpenFOAM 12 官方内流算例实测验证](validation/official_openfoam12/README.md) 提供原生 `checkMesh`、求解器和 `yPlus` 输出、计算前/试算后报告及独立核对脚本。[三网格内流实测验证](validation/official_openfoam12_grid/README.md) 提供真实目标量监测、严格续算和网格对照，检出残差停止后压力目标量仍漂移、均值趋稳后仍往复波动的情况，明确将网格比较标为初步结果。[官方封闭内流加层实测](validation/official_openfoam12_igloo/README.md) 以真实 `nSurfaceLayers` 证明高覆盖率仍可能有大量壁面未达到目标层数，并保留原生凹单元失败结论。[官方 motorBikeSteady 加层实测](validation/official_openfoam12_motorbike/README.md) 补充外流复杂 patch 名的字段验证。

公开的验证日志和报告已将运行者账号、主机名及本机路径替换为示例值；网格、求解和检查数值未改动。`validation/official_openfoam12_igloo/native.sha256` 记录匿名化后保存文件的 SHA-256。

## 扩展到新软件

1. 在 `detect.py` 里加入识别规则；
2. 在 `scripts/adapters/` 新建适配器，返回与现有适配器相同结构的结果（`mesh_info`、`findings`、`limitations`）；
3. 在 `thresholds.json` 增加该软件的阈值，在 `reference/` 写一份指标说明；
4. 在 `mesh_check.py` 中注册，并在 `tests/` 加样例。
