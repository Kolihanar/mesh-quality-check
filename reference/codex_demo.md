# 在 Codex 中使用与演示 mesh-quality-check

本文给出可复制的提示词，以及仓库内已保存的 OpenFOAM 12 官方算例验证。图展示的是**已运行算例的实际数据与本 Skill 报告的对照**；它能检验这些检查路径，不能证明所有 CFD 算例都适用。

## 安装和调用

[OpenAI 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)列出用户级目录 `$HOME/.agents/skills`，并说明可在提示词中显式提及 Skill。Windows PowerShell 示例：

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/Kolihanar/mesh-quality-check.git "$HOME/.agents/skills/mesh-quality-check"
```

已有本仓库副本时，无须重复克隆；也可先让 Codex 直接读取该副本的 `SKILL.md` 完成演示。若安装后 Codex 没发现 Skill，重启 Codex。需要运行检查脚本时，在执行 Python 的环境中安装依赖：

```powershell
py -m pip install -r "$HOME/.agents/skills/mesh-quality-check/requirements.txt"
```

在 Linux/WSL 中将 `py` 换成 `python3`，并使用该环境可访问的 Skill 路径。OpenFOAM 的 `checkMesh`、`foamPostProcess` 必须在已加载 OpenFOAM 环境的终端运行；复核本仓库保存的日志、场文件和报告则不需要重新运行 OpenFOAM。若在其他项目工作，用该项目的绝对路径指向算例，输出报告目录也应放在该项目可写位置。

提示词最好包含：**算例绝对路径、OpenFOAM 版本/流动模型、计算前或试算后、已有日志与场文件路径、关注的目标量、希望的输出**。缺少工况值时让 Codex 列出缺口，不要要求它猜测摩擦速度、实际 y⁺ 或能量通量。报告的 `overall` 是已执行网格指标分级；是否有足够证据支持当前 CFD 用途，还要看 `readiness` 和 `cfd.missing`。

## 演示一：用仓库自带的真实输出复核 Skill

打开本仓库作为 Codex 工作区，然后粘贴：

```text
$mesh-quality-check 请用本仓库保存的 OpenFOAM 12 官方算例做一次可核对的效果演示。
先运行 validation/official_openfoam12/verify.py、
validation/official_openfoam12_igloo/verify.py 和
validation/official_openfoam12_grid/verify.py。
对照原生日志、yPlus/nSurfaceLayers 场与 mesh_report.json，分别说明：
1. pitzDailySteady 的 y⁺ 极值、目标外面数和体积通量守恒是否一致；
2. iglooWithFridges 的原生 checkMesh 失败、实际层覆盖率和未达目标层数面积；
3. 三网格续算中为何不能仅凭残差或均值漂移宣称网格收敛。
请链接相应图和报告，区分本次复核保存证据与重新运行 OpenFOAM。
```

尚未安装为 Skill 时，将第一行改为“请先读取本仓库的 `SKILL.md`，然后……”。这三个 `verify.py` 只依赖 Python 标准库与 NumPy；在仓库根目录运行即可。下面是仓库保存结果的可核查要点：

本次 Codex 已在仓库根目录实际执行以下命令，四个原生证据核对均通过；Linux/WSL 把 `py` 换成 `python3`：

```powershell
py validation/official_openfoam12/verify.py
py validation/official_openfoam12_igloo/verify.py
py validation/official_openfoam12_grid/verify.py
py validation/official_openfoam12_motorbike/verify.py
```

其中前三个与下表的三张实测图对应；`motorBikeSteady` 是外流案例，只验证真实加层字段与复杂 patch 名定位。

| 官方案例 | 原生证据与 Skill 的一致性 / 检出项 | 可得结论 |
|---|---|---|
| `pitzDailySteady` | 两面 y⁺ 最小/最大值与原生日志一致；显式 30–300 目标外分别为 223/223、250/250 面；体积通量相对不平衡约 0.0029003%，与原生 `phi` 一致 | 能读取实际试算场并核对守恒；低 y⁺ 需结合该壁面函数的低 y⁺ 分支解释 |
| `iglooWithFridges` | `checkMesh` 报 1 项失败、1,733 个凹单元；两个冰柜壁面的正层覆盖率约 97.51%、99.27%，未达三层目标的面积约 55.10%、57.88% | 能区分“有层”和“层数足够”，且保留原生网格失败结论 |
| `pitzDailySteady` 三网格 | 细网格在 1000 步时末两段均值漂移约 0.27%，最后窗口 P05–P95 相对跨度仍约 1.81%，超过本次 1% 筛查容差 | 会把细/中网格差异标为初步比较；尚不能据此宣称网格无关 |

图与逐项来源见 [pitzDailySteady](../validation/official_openfoam12/README.md)、[iglooWithFridges](../validation/official_openfoam12_igloo/README.md)、[三网格续算](../validation/official_openfoam12_grid/README.md)。`iglooWithFridges` 的网格未通过完整质量检查，因此没有继续做流动和换热求解；三网格案例是“发现未稳定目标量”的反例，不是可靠网格收敛的正例。

## 演示二：让 Codex 当场运行一个可携带样例

仓库包含人为构造的反转单元样例，适合验证命令调用和报告生成。提示词：

```text
$mesh-quality-check 请检查本仓库 tests/samples/of_inverted_3d，
把报告写到本仓库 demo_output/inverted。实际运行 scripts/mesh_check.py，
读取 mesh_report.md 和 mesh_report.json，给出最严重问题、
对应数值/位置、优化动作、还缺少哪些真实 CFD 工况证据。
说明这是合成回归样例，不把它当成真实工程检出率。
```

本仓库实际运行该样例时返回 `overall=critical`、`readiness=必须修复网格`，退出码为 2，表示检出了致命问题；这不是执行失败。`demo_output/` 已加入 `.gitignore`。该样例没有完整的原生 `checkMesh` 和求解结果，不能据此判断真实算例的 y⁺ 或解精度。

## 检查自己的 OpenFOAM 算例

计算前提示词：

```text
$mesh-quality-check 请检查 OpenFOAM 12 单相 RANS 内流算例
<算例绝对路径>。已有完整检查日志 <log.checkMesh 绝对路径>。
运行 Skill，重点解释拓扑、非正交/歪斜、近壁首层距离和边界层层数；
按位置和优先级给出具体网格修改及复查办法。
读取 overall、readiness、cfd.missing；没有流动参数时不要编造 y⁺。
```

已有试算后的提示词：

```text
$mesh-quality-check 请复核算例 <算例绝对路径> 的 CFD 适用性。
使用已有 checkMesh 日志 <路径>、ASCII yPlus 场 <路径>、
实际 nSurfaceLayers 场 <路径> 和工况 JSON <路径>（缺的文件请直接说明）。
核对壁面函数与显式 y⁺ 目标、实际层覆盖率、守恒和目标量末段稳定性；
若给了三套网格，只有三套目标量都稳定时才评价网格差异。
生成 Markdown/JSON 报告，列出问题位置、证据、具体优化动作及复查步骤。
```

Codex 应运行的 CLI 形式如下；`--yplus-field`、`--layer-field`、`--context` 都是按实际已有文件添加：

```bash
python3 scripts/mesh_check.py /absolute/path/to/case \
  --checkmesh-log /absolute/path/to/log.checkMesh \
  --context /absolute/path/to/cfd_context.json \
  --yplus-field /absolute/path/to/yPlus \
  --layer-field /absolute/path/to/nSurfaceLayers \
  -o /absolute/path/to/report
```

工况 JSON 字段与单位见 [OpenFOAM CFD 输入说明](cfd_openfoam.md)。计算前估算 y⁺ 需要黏度与摩擦速度或壁面剪切数据；已有试算的真实 y⁺ 必须来自实际场文件。完整官方案例的网格生成、求解及后处理命令见 [官方验证路线](official_validation.md)。
