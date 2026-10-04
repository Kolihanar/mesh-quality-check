# 网格质量检查报告

- 生成时间：2026-10-04 18:06:24
- 输入：`/home/foamuser/OpenFOAM/foamuser-12/run/motorBikeSteady-layer-validation-20261004`
- 识别结果：**OpenFOAM**（case）——找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict

## 结论：🔴 高风险

已检查指标存在高风险偏离；需结合实际边界条件及目标量验证其影响。

CFD 适用性判断：**高风险指标待复核，关键结果证据不足**。

checkMesh 自身结论：`Failed 4 mesh checks`

## 1. 网格基本信息

| 项目 | 值 |
|---|---|
| 单元数 | 353779 |
| 面数 | 1108744 |
| 内部面数 | 1059085 |
| 节点数 | 406140 |
| 维度 | 3D |
| OpenFOAM 版本 | 12 |
| 单元类型 | hexahedra 307995，prisms 7326，wedges 1007，pyramids 10，tet wedges 1698，tetrahedra 39，polyhedra 35704 |
| 包围盒 | [-5.0, -4.0, 0.0] → [15.0, 4.0, 8.0] |
| 单元体积 | 最小 1.355e-08，最大 1.006 |
| 边界 | frontAndBack[patch](360)，inlet[patch](72)，outlet[patch](72)，lowerWall[wall](5341)，upperWall[patch](160)，motorBike_frt-fairing:001%1[wall](5292)，motorBike_windshield:002%2[wall](51)，motorBike_rr-wh-rim:005%5[wall](127)，motorBike_rr-wh-rim:010%10[wall](347)，motorBike_fr-wh-rim:011%11[wall](492)，motorBike_fr-wh-brake-disk:012%12[wall](42)，motorBike_frame:016-shadow%13[wall](105)，motorBike_rear-susp:014%14[wall](802)，motorBike_rear-susp:014-shadow%15[wall](452)，motorBike_frame:016%16[wall](61)，motorBike_rr-wh-rim:005-shadow%17[wall](61)，motorBike_rr-wh-chain-hub:022%22[wall](121)，motorBike_rearseat%24[wall](393)，motorBike_frt-fairing%25[wall](613)，motorBike_windshield%26[wall](358)，motorBike_headlights%27[wall](157)，motorBike_driversseat%28[wall](360)，motorBike_rear-body%29[wall](2037)，motorBike_fuel-tank%30[wall](873)，motorBike_exhaust%31[wall](2312)，motorBike_rr-wh-rim%32[wall](1352)，motorBike_fr-mud-guard%33[wall](636)，motorBike_fr-wh-rim%34[wall](557)，motorBike_fr-wh-brake-disk%35[wall](424)，motorBike_fr-brake-caliper%36[wall](155)，motorBike_fr-wh-tyre%37[wall](1103)，motorBike_hbars%38[wall](509)，motorBike_fr-forks%39[wall](1078)，motorBike_chain%40[wall](452)，motorBike_rr-wh-tyre%41[wall](1858)，motorBike_square-dial%42[wall](6)，motorBike_round-dial%43[wall](15)，motorBike_dial-holder%44[wall](83)，motorBike_rear-susp%45[wall](1690)，motorBike_rear-brake-lights%46[wall](52)，motorBike_rear-light-bracket%47[wall](157)，motorBike_frame%48[wall](1959)，motorBike_rear-mud-guard%49[wall](653)，motorBike_rear-susp-spring-damp%50[wall](78)，motorBike_fairing-inner-plate%51[wall](430)，motorBike_clutch-housing%52[wall](899)，motorBike_radiator%53[wall](40)，motorBike_water-pipe%54[wall](89)，motorBike_water-pump%55[wall](73)，motorBike_engine%56[wall](2261)，motorBike_rear-shock-link%57[wall](25)，motorBike_rear-brake-fluid-pot-bracket%58[wall](35)，motorBike_rear-brake-fluid-pot%59[wall](50)，motorBike_footpeg%60[wall](88)，motorBike_rr-wh-chain-hub%61[wall](117)，motorBike_rear-brake-caliper%62[wall](134)，motorBike_rider-helmet%65[wall](740)，motorBike_rider-visor%66[wall](157)，motorBike_rider-boots%67[wall](1004)，motorBike_rider-gloves%68[wall](308)，motorBike_rider-body%69[wall](4560)，motorBike_frame:0%70[wall](37)，motorBike_frt-fairing:001-shadow%74[wall](3309)，motorBike_windshield-shadow%75[wall](275)，motorBike_fr-mud-guard-shadow%81[wall](346)，motorBike_fr-wh-brake-disk-shadow%83[wall](204)，motorBike_rear-mud-guard-shadow%84[wall](415)，motorBike_rear-susp-spring-damp-shadow%85[wall](46)，motorBike_radiator-shadow%86[wall](33)，motorBike_rear-shock-link-shadow%87[wall](13)，motorBike_rear-brake-fluid-pot-bracket-shadow%88[wall](30)，motorBike_rr-wh-chain-hub-shadow%89[wall](63) |

## 2. 致命/拓扑问题

- 🔴 **checkMesh 检查失败项**（高风险）：范围 未知（只有极值），极值 4

## 3. CFD 适用性与近壁检查

当前范围：OpenFOAM 单相 RANS 内流。计算前 y⁺ 为估算，已有试算的 yPlus 场为求解后证据。

算例识别：求解器 foamRun；湍流类型 RAS；模型 kOmegaSST。

| 壁面 | 首层中心距：最小/中位/P95 | y⁺ 证据 | y⁺：P05/中位/P95 | 目标 | 区间外面积 |
|---|---|---|---|---|---|
| lowerWall | 3.417e-04/0.009375/0.03679 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frt-fairing:001%1 | 1.452e-04/0.002275/0.00766 | 待补全 | —/—/— | 待指定 | — |
| motorBike_windshield:002%2 | 3.163e-04/0.002266/0.004618 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-rim:005%5 | 3.508e-04/0.006099/0.01051 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-rim:010%10 | 2.735e-04/0.007203/0.009898 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-rim:011%11 | 2.822e-04/0.005221/0.009156 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-brake-disk:012%12 | 0.003282/0.008976/0.01092 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frame:016-shadow%13 | 3.176e-04/0.004707/0.0126 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-susp:014%14 | 2.938e-04/0.002611/0.008263 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-susp:014-shadow%15 | 1.790e-04/0.002846/0.008272 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frame:016%16 | 2.452e-04/0.004033/0.009217 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-rim:005-shadow%17 | 3.406e-04/0.006376/0.01059 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-chain-hub:022%22 | 3.867e-04/0.006561/0.008971 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rearseat%24 | 3.477e-04/0.002207/0.006469 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frt-fairing%25 | 2.737e-04/0.002073/0.008018 | 待补全 | —/—/— | 待指定 | — |
| motorBike_windshield%26 | 3.645e-04/0.00213/0.005816 | 待补全 | —/—/— | 待指定 | — |
| motorBike_headlights%27 | 3.352e-04/0.002164/0.002355 | 待补全 | —/—/— | 待指定 | — |
| motorBike_driversseat%28 | 3.184e-04/0.004293/0.008932 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-body%29 | 2.916e-04/0.00222/0.008302 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fuel-tank%30 | 2.762e-04/0.002166/0.007374 | 待补全 | —/—/— | 待指定 | — |
| motorBike_exhaust%31 | 2.724e-04/0.002358/0.0107 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-rim%32 | 3.446e-07/0.001574/0.008143 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-mud-guard%33 | 2.596e-04/0.003141/0.009155 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-rim%34 | 2.947e-04/0.001488/0.01013 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-brake-disk%35 | 3.068e-04/0.006862/0.00906 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-brake-caliper%36 | 0.001397/0.008554/0.01129 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-tyre%37 | 2.766e-04/0.002305/0.01052 | 待补全 | —/—/— | 待指定 | — |
| motorBike_hbars%38 | 0.002371/0.007668/0.01149 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-forks%39 | 2.877e-04/0.002771/0.01013 | 待补全 | —/—/— | 待指定 | — |
| motorBike_chain%40 | 3.163e-04/0.008807/0.01205 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-tyre%41 | 3.289e-04/0.002345/0.007649 | 待补全 | —/—/— | 待指定 | — |
| motorBike_square-dial%42 | 4.073e-04/6.087e-04/8.838e-04 | 待补全 | —/—/— | 待指定 | — |
| motorBike_round-dial%43 | 3.977e-04/5.917e-04/0.009537 | 待补全 | —/—/— | 待指定 | — |
| motorBike_dial-holder%44 | 3.789e-04/0.005627/0.01151 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-susp%45 | 2.885e-04/0.004223/0.01072 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-brake-lights%46 | 0.001878/0.006798/0.0111 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-light-bracket%47 | 3.426e-04/0.003109/0.009274 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frame%48 | 2.667e-04/0.002208/0.009892 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-mud-guard%49 | 1.466e-04/0.002255/0.007832 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-susp-spring-damp%50 | 0.001055/0.005451/0.01042 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fairing-inner-plate%51 | 3.032e-04/0.00223/0.007882 | 待补全 | —/—/— | 待指定 | — |
| motorBike_clutch-housing%52 | 2.880e-04/0.001809/0.009402 | 待补全 | —/—/— | 待指定 | — |
| motorBike_radiator%53 | 0.003226/0.01047/0.0142 | 待补全 | —/—/— | 待指定 | — |
| motorBike_water-pipe%54 | 0.003673/0.009446/0.01369 | 待补全 | —/—/— | 待指定 | — |
| motorBike_water-pump%55 | 3.317e-04/0.004866/0.01054 | 待补全 | —/—/— | 待指定 | — |
| motorBike_engine%56 | 2.928e-04/0.001905/0.009078 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-shock-link%57 | 0.001796/0.005884/0.01043 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-brake-fluid-pot-bracket%58 | 3.146e-04/0.005444/0.008997 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-brake-fluid-pot%59 | 0.003122/0.008783/0.01118 | 待补全 | —/—/— | 待指定 | — |
| motorBike_footpeg%60 | 0.002316/0.007561/0.01148 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-chain-hub%61 | 3.547e-04/0.006388/0.00835 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-brake-caliper%62 | 2.447e-04/0.006111/0.01116 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rider-helmet%65 | 3.629e-04/0.002357/0.002386 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rider-visor%66 | 0.001042/0.002348/0.00236 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rider-boots%67 | 3.111e-04/0.002239/0.007943 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rider-gloves%68 | 3.248e-04/0.005402/0.01059 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rider-body%69 | 2.597e-04/0.002312/0.005662 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frame:0%70 | 0.00206/0.007317/0.009878 | 待补全 | —/—/— | 待指定 | — |
| motorBike_frt-fairing:001-shadow%74 | 2.687e-04/0.00224/0.007594 | 待补全 | —/—/— | 待指定 | — |
| motorBike_windshield-shadow%75 | 3.252e-04/0.002188/0.006112 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-mud-guard-shadow%81 | 2.794e-04/0.002868/0.008488 | 待补全 | —/—/— | 待指定 | — |
| motorBike_fr-wh-brake-disk-shadow%83 | 3.116e-04/0.00707/0.009496 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-mud-guard-shadow%84 | 1.733e-04/0.002144/0.00716 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-susp-spring-damp-shadow%85 | 0.001835/0.006322/0.01068 | 待补全 | —/—/— | 待指定 | — |
| motorBike_radiator-shadow%86 | 0.002725/0.01072/0.01536 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-shock-link-shadow%87 | 0.002665/0.004698/0.01178 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rear-brake-fluid-pot-bracket-shadow%88 | 3.162e-04/0.003961/0.007833 | 待补全 | —/—/— | 待指定 | — |
| motorBike_rr-wh-chain-hub-shadow%89 | 3.724e-04/0.006278/0.008929 | 待补全 | —/—/— | 待指定 | — |

表中 y⁺ 目标是所选工况的筛查区间，区间外比例表示目标偏离，并不单独证明求解失败或结果不可靠。首层中心距按单元中心到边界面平面的法向投影计算。近壁层数与覆盖率需要实际生成记录或可识别的层字段；规则六面体的连续排列不直接算作边界层。

- lowerWall 壁面场类型：nut=nutkWallFunction、omega=omegaWallFunction
- lowerWall 首层相邻内部面：非正交角最大 64.69°、>70° 0 面；歪斜度最大 0.4557、>4 0 面；首层单元长宽比 P95 5.41。
- motorBike_frt-fairing:001%1 首层相邻内部面：非正交角最大 64.93°、>70° 0 面；歪斜度最大 1.478、>4 0 面；首层单元长宽比 P95 8.424。
- motorBike_windshield:002%2 首层相邻内部面：非正交角最大 45.84°、>70° 0 面；歪斜度最大 0.552、>4 0 面；首层单元长宽比 P95 3.734。
- motorBike_rr-wh-rim:005%5 首层相邻内部面：非正交角最大 52.62°、>70° 0 面；歪斜度最大 0.317、>4 0 面；首层单元长宽比 P95 15.86。
- motorBike_rr-wh-rim:010%10 首层相邻内部面：非正交角最大 64.07°、>70° 0 面；歪斜度最大 1.819、>4 0 面；首层单元长宽比 P95 10。
- motorBike_fr-wh-rim:011%11 首层相邻内部面：非正交角最大 63.98°、>70° 0 面；歪斜度最大 0.6482、>4 0 面；首层单元长宽比 P95 14.53。
- motorBike_fr-wh-brake-disk:012%12 首层相邻内部面：非正交角最大 36.58°、>70° 0 面；歪斜度最大 0.2838、>4 0 面；首层单元长宽比 P95 1.869。
- motorBike_frame:016-shadow%13 首层相邻内部面：非正交角最大 60.94°、>70° 0 面；歪斜度最大 0.4296、>4 0 面；首层单元长宽比 P95 4.935。
- motorBike_rear-susp:014%14 首层相邻内部面：非正交角最大 64.96°、>70° 0 面；歪斜度最大 1.059、>4 0 面；首层单元长宽比 P95 16.38。
- motorBike_rear-susp:014-shadow%15 首层相邻内部面：非正交角最大 63.77°、>70° 0 面；歪斜度最大 0.9483、>4 0 面；首层单元长宽比 P95 16.87。
- motorBike_frame:016%16 首层相邻内部面：非正交角最大 59.88°、>70° 0 面；歪斜度最大 0.381、>4 0 面；首层单元长宽比 P95 5.518。
- motorBike_rr-wh-rim:005-shadow%17 首层相邻内部面：非正交角最大 64.07°、>70° 0 面；歪斜度最大 0.7425、>4 0 面；首层单元长宽比 P95 16.35。
- motorBike_rr-wh-chain-hub:022%22 首层相邻内部面：非正交角最大 44.14°、>70° 0 面；歪斜度最大 0.6639、>4 0 面；首层单元长宽比 P95 4.268。
- motorBike_rearseat%24 首层相邻内部面：非正交角最大 54.27°、>70° 0 面；歪斜度最大 1.105、>4 0 面；首层单元长宽比 P95 8.531。
- motorBike_frt-fairing%25 首层相邻内部面：非正交角最大 64.87°、>70° 0 面；歪斜度最大 1.418、>4 0 面；首层单元长宽比 P95 8.762。
- motorBike_windshield%26 首层相邻内部面：非正交角最大 64.49°、>70° 0 面；歪斜度最大 0.6035、>4 0 面；首层单元长宽比 P95 5.096。
- motorBike_headlights%27 首层相邻内部面：非正交角最大 64.55°、>70° 0 面；歪斜度最大 0.8789、>4 0 面；首层单元长宽比 P95 3.546。
- motorBike_driversseat%28 首层相邻内部面：非正交角最大 64.33°、>70° 0 面；歪斜度最大 1.042、>4 0 面；首层单元长宽比 P95 10.83。
- motorBike_rear-body%29 首层相邻内部面：非正交角最大 63.87°、>70° 0 面；歪斜度最大 1.878、>4 0 面；首层单元长宽比 P95 7.839。
- motorBike_fuel-tank%30 首层相邻内部面：非正交角最大 64.78°、>70° 0 面；歪斜度最大 0.8804、>4 0 面；首层单元长宽比 P95 6.862。
- motorBike_exhaust%31 首层相邻内部面：非正交角最大 62.31°、>70° 0 面；歪斜度最大 1.224、>4 0 面；首层单元长宽比 P95 5.496。
- motorBike_rr-wh-rim%32 首层相邻内部面：非正交角最大 63.09°、>70° 0 面；歪斜度最大 0.9694、>4 0 面；首层单元长宽比 P95 8.778。
- motorBike_fr-mud-guard%33 首层相邻内部面：非正交角最大 64.33°、>70° 0 面；歪斜度最大 1.277、>4 0 面；首层单元长宽比 P95 5.907。
- motorBike_fr-wh-rim%34 首层相邻内部面：非正交角最大 63.83°、>70° 0 面；歪斜度最大 0.964、>4 0 面；首层单元长宽比 P95 10.04。
- motorBike_fr-wh-brake-disk%35 首层相邻内部面：非正交角最大 55.66°、>70° 0 面；歪斜度最大 0.7885、>4 0 面；首层单元长宽比 P95 14.94。
- motorBike_fr-brake-caliper%36 首层相邻内部面：非正交角最大 48.63°、>70° 0 面；歪斜度最大 0.4477、>4 0 面；首层单元长宽比 P95 2.069。
- motorBike_fr-wh-tyre%37 首层相邻内部面：非正交角最大 64.16°、>70° 0 面；歪斜度最大 0.9103、>4 0 面；首层单元长宽比 P95 6.915。
- motorBike_hbars%38 首层相邻内部面：非正交角最大 43.36°、>70° 0 面；歪斜度最大 0.6789、>4 0 面；首层单元长宽比 P95 2.111。
- motorBike_fr-forks%39 首层相邻内部面：非正交角最大 59.76°、>70° 0 面；歪斜度最大 0.8105、>4 0 面；首层单元长宽比 P95 5.043。
- motorBike_chain%40 首层相邻内部面：非正交角最大 59.28°、>70° 0 面；歪斜度最大 0.5624、>4 0 面；首层单元长宽比 P95 2.483。
- motorBike_rr-wh-tyre%41 首层相邻内部面：非正交角最大 64.69°、>70° 0 面；歪斜度最大 0.8391、>4 0 面；首层单元长宽比 P95 5.394。
- motorBike_square-dial%42 首层相邻内部面：非正交角最大 29.15°、>70° 0 面；歪斜度最大 0.3371、>4 0 面；首层单元长宽比 P95 13.06。
- motorBike_round-dial%43 首层相邻内部面：非正交角最大 46°、>70° 0 面；歪斜度最大 0.2965、>4 0 面；首层单元长宽比 P95 13.36。
- motorBike_dial-holder%44 首层相邻内部面：非正交角最大 43.78°、>70° 0 面；歪斜度最大 0.5775、>4 0 面；首层单元长宽比 P95 9.44。
- motorBike_rear-susp%45 首层相邻内部面：非正交角最大 64.42°、>70° 0 面；歪斜度最大 1.059、>4 0 面；首层单元长宽比 P95 13.97。
- motorBike_rear-brake-lights%46 首层相邻内部面：非正交角最大 38.62°、>70° 0 面；歪斜度最大 0.2912、>4 0 面；首层单元长宽比 P95 2.321。
- motorBike_rear-light-bracket%47 首层相邻内部面：非正交角最大 51.34°、>70° 0 面；歪斜度最大 0.5115、>4 0 面；首层单元长宽比 P95 15.92。
- motorBike_frame%48 首层相邻内部面：非正交角最大 64.83°、>70° 0 面；歪斜度最大 1.084、>4 0 面；首层单元长宽比 P95 13.47。
- motorBike_rear-mud-guard%49 首层相邻内部面：非正交角最大 64.39°、>70° 0 面；歪斜度最大 0.944、>4 0 面；首层单元长宽比 P95 8.131。
- motorBike_rear-susp-spring-damp%50 首层相邻内部面：非正交角最大 52.07°、>70° 0 面；歪斜度最大 0.4786、>4 0 面；首层单元长宽比 P95 4。
- motorBike_fairing-inner-plate%51 首层相邻内部面：非正交角最大 62.4°、>70° 0 面；歪斜度最大 0.7901、>4 0 面；首层单元长宽比 P95 13.1。
- motorBike_clutch-housing%52 首层相邻内部面：非正交角最大 64.61°、>70° 0 面；歪斜度最大 1.109、>4 0 面；首层单元长宽比 P95 13.77。
- motorBike_radiator%53 首层相邻内部面：非正交角最大 36.92°、>70° 0 面；歪斜度最大 0.5442、>4 0 面；首层单元长宽比 P95 1.924。
- motorBike_water-pipe%54 首层相邻内部面：非正交角最大 38.29°、>70° 0 面；歪斜度最大 0.355、>4 0 面；首层单元长宽比 P95 1.794。
- motorBike_water-pump%55 首层相邻内部面：非正交角最大 60.66°、>70° 0 面；歪斜度最大 0.7127、>4 0 面；首层单元长宽比 P95 6.554。
- motorBike_engine%56 首层相邻内部面：非正交角最大 60.18°、>70° 0 面；歪斜度最大 1.742、>4 0 面；首层单元长宽比 P95 14.08。
- motorBike_rear-shock-link%57 首层相邻内部面：非正交角最大 45.41°、>70° 0 面；歪斜度最大 0.315、>4 0 面；首层单元长宽比 P95 3.678。
- motorBike_rear-brake-fluid-pot-bracket%58 首层相邻内部面：非正交角最大 36.6°、>70° 0 面；歪斜度最大 0.4641、>4 0 面；首层单元长宽比 P95 15.36。
- motorBike_rear-brake-fluid-pot%59 首层相邻内部面：非正交角最大 38.95°、>70° 0 面；歪斜度最大 0.2981、>4 0 面；首层单元长宽比 P95 1.886。
- motorBike_footpeg%60 首层相邻内部面：非正交角最大 39.55°、>70° 0 面；歪斜度最大 0.8267、>4 0 面；首层单元长宽比 P95 2.54。
- motorBike_rr-wh-chain-hub%61 首层相邻内部面：非正交角最大 39.24°、>70° 0 面；歪斜度最大 0.4147、>4 0 面；首层单元长宽比 P95 13.51。
- motorBike_rear-brake-caliper%62 首层相邻内部面：非正交角最大 54.12°、>70° 0 面；歪斜度最大 0.6903、>4 0 面；首层单元长宽比 P95 12.4。
- motorBike_rider-helmet%65 首层相邻内部面：非正交角最大 64.89°、>70° 0 面；歪斜度最大 1.297、>4 0 面；首层单元长宽比 P95 6.737。
- motorBike_rider-visor%66 首层相邻内部面：非正交角最大 56.61°、>70° 0 面；歪斜度最大 1.027、>4 0 面；首层单元长宽比 P95 3.039。
- motorBike_rider-boots%67 首层相邻内部面：非正交角最大 62.44°、>70° 0 面；歪斜度最大 1.143、>4 0 面；首层单元长宽比 P95 6.433。
- motorBike_rider-gloves%68 首层相邻内部面：非正交角最大 51.41°、>70° 0 面；歪斜度最大 2.638、>4 0 面；首层单元长宽比 P95 6.025。
- motorBike_rider-body%69 首层相邻内部面：非正交角最大 64.97°、>70° 0 面；歪斜度最大 1.279、>4 0 面；首层单元长宽比 P95 5.766。
- motorBike_frame:0%70 首层相邻内部面：非正交角最大 33.29°、>70° 0 面；歪斜度最大 0.2936、>4 0 面；首层单元长宽比 P95 3.434。
- motorBike_frt-fairing:001-shadow%74 首层相邻内部面：非正交角最大 64.93°、>70° 0 面；歪斜度最大 1.478、>4 0 面；首层单元长宽比 P95 8.624。
- motorBike_windshield-shadow%75 首层相邻内部面：非正交角最大 64.89°、>70° 0 面；歪斜度最大 0.6035、>4 0 面；首层单元长宽比 P95 5.277。
- motorBike_fr-mud-guard-shadow%81 首层相邻内部面：非正交角最大 65.16°、>70° 0 面；歪斜度最大 0.9857、>4 0 面；首层单元长宽比 P95 5.809。
- motorBike_fr-wh-brake-disk-shadow%83 首层相邻内部面：非正交角最大 51.71°、>70° 0 面；歪斜度最大 0.7449、>4 0 面；首层单元长宽比 P95 18.1。
- motorBike_rear-mud-guard-shadow%84 首层相邻内部面：非正交角最大 64.69°、>70° 0 面；歪斜度最大 1.03、>4 0 面；首层单元长宽比 P95 7.896。
- motorBike_rear-susp-spring-damp-shadow%85 首层相邻内部面：非正交角最大 48.98°、>70° 0 面；歪斜度最大 0.4562、>4 0 面；首层单元长宽比 P95 3.416。
- motorBike_radiator-shadow%86 首层相邻内部面：非正交角最大 36.92°、>70° 0 面；歪斜度最大 0.5442、>4 0 面；首层单元长宽比 P95 2.183。
- motorBike_rear-shock-link-shadow%87 首层相邻内部面：非正交角最大 41.25°、>70° 0 面；歪斜度最大 0.4、>4 0 面；首层单元长宽比 P95 3.688。
- motorBike_rear-brake-fluid-pot-bracket-shadow%88 首层相邻内部面：非正交角最大 35.59°、>70° 0 面；歪斜度最大 0.3464、>4 0 面；首层单元长宽比 P95 16.16。
- motorBike_rr-wh-chain-hub-shadow%89 首层相邻内部面：非正交角最大 44.14°、>70° 0 面；歪斜度最大 0.3711、>4 0 面；首层单元长宽比 P95 10.36。
**边界层实测数据**

- lowerWall：实际层数最小值 0，覆盖率 100.0%，面积加权平均层数 0.9999，有层面数 5307/5341，低于目标的面积比例 0.0%（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frt-fairing:001%1：实际层数最小值 0，覆盖率 39.7%，面积加权平均层数 0.3968，有层面数 2056/5292，低于目标的面积比例 60.3%（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_windshield:002%2：实际层数最小值 0，覆盖率 93.2%，面积加权平均层数 0.9321，有层面数 44/51（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-rim:005%5：实际层数最小值 0，覆盖率 37.5%，面积加权平均层数 0.3749，有层面数 45/127（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-rim:010%10：实际层数最小值 0，覆盖率 16.7%，面积加权平均层数 0.1671，有层面数 53/347（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-rim:011%11：实际层数最小值 0，覆盖率 34.7%，面积加权平均层数 0.3468，有层面数 154/492，低于目标的面积比例 65.3%（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-brake-disk:012%12：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/42（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frame:016-shadow%13：实际层数最小值 0，覆盖率 0.9%，面积加权平均层数 0.008916，有层面数 1/105（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-susp:014%14：实际层数最小值 0，覆盖率 35.3%，面积加权平均层数 0.3532，有层面数 272/802（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-susp:014-shadow%15：实际层数最小值 0，覆盖率 34.8%，面积加权平均层数 0.3482，有层面数 139/452（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frame:016%16：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/61（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-rim:005-shadow%17：实际层数最小值 0，覆盖率 19.7%，面积加权平均层数 0.1965，有层面数 12/61（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-chain-hub:022%22：实际层数最小值 0，覆盖率 2.8%，面积加权平均层数 0.0279，有层面数 3/121（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rearseat%24：实际层数最小值 0，覆盖率 88.5%，面积加权平均层数 0.8847，有层面数 343/393（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frt-fairing%25：实际层数最小值 0，覆盖率 75.8%，面积加权平均层数 0.7575，有层面数 458/613（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_windshield%26：实际层数最小值 0，覆盖率 9.3%，面积加权平均层数 0.09344，有层面数 37/358（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_headlights%27：实际层数最小值 0，覆盖率 99.2%，面积加权平均层数 0.9915，有层面数 151/157（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_driversseat%28：实际层数最小值 0，覆盖率 31.9%，面积加权平均层数 0.3188，有层面数 110/360（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-body%29：实际层数最小值 0，覆盖率 75.5%，面积加权平均层数 0.7547，有层面数 1532/2037（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fuel-tank%30：实际层数最小值 0，覆盖率 81.0%，面积加权平均层数 0.8101，有层面数 721/873（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_exhaust%31：实际层数最小值 0，覆盖率 53.7%，面积加权平均层数 0.5372，有层面数 1217/2312（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-rim%32：实际层数最小值 0，覆盖率 74.6%，面积加权平均层数 0.7459，有层面数 976/1352（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-mud-guard%33：实际层数最小值 0，覆盖率 33.7%，面积加权平均层数 0.3373，有层面数 193/636（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-rim%34：实际层数最小值 0，覆盖率 60.2%，面积加权平均层数 0.6022，有层面数 335/557（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-brake-disk%35：实际层数最小值 0，覆盖率 31.3%，面积加权平均层数 0.3128，有层面数 134/424（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-brake-caliper%36：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/155（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-tyre%37：实际层数最小值 0，覆盖率 65.2%，面积加权平均层数 0.6523，有层面数 707/1103（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_hbars%38：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/509（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-forks%39：实际层数最小值 0，覆盖率 48.2%，面积加权平均层数 0.482，有层面数 502/1078（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_chain%40：实际层数最小值 0，覆盖率 3.2%，面积加权平均层数 0.03237，有层面数 15/452（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-tyre%41：实际层数最小值 0，覆盖率 79.5%，面积加权平均层数 0.7949，有层面数 1477/1858（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_square-dial%42：实际层数最小值 1，覆盖率 100.0%，面积加权平均层数 1，有层面数 6/6（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_round-dial%43：实际层数最小值 0，覆盖率 82.4%，面积加权平均层数 0.824，有层面数 11/15（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_dial-holder%44：实际层数最小值 0，覆盖率 6.5%，面积加权平均层数 0.06499，有层面数 7/83（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-susp%45：实际层数最小值 0，覆盖率 42.6%，面积加权平均层数 0.4256，有层面数 699/1690（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-brake-lights%46：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/52（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-light-bracket%47：实际层数最小值 0，覆盖率 47.0%，面积加权平均层数 0.4702，有层面数 70/157（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frame%48：实际层数最小值 0，覆盖率 53.5%，面积加权平均层数 0.5347，有层面数 1027/1959（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-mud-guard%49：实际层数最小值 0，覆盖率 31.4%，面积加权平均层数 0.3135，有层面数 195/653（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-susp-spring-damp%50：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/78（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fairing-inner-plate%51：实际层数最小值 0，覆盖率 59.1%，面积加权平均层数 0.5914，有层面数 245/430（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_clutch-housing%52：实际层数最小值 0，覆盖率 69.9%，面积加权平均层数 0.6986，有层面数 641/899（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_radiator%53：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/40（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_water-pipe%54：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/89（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_water-pump%55：实际层数最小值 0，覆盖率 19.5%，面积加权平均层数 0.1952，有层面数 15/73（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_engine%56：实际层数最小值 0，覆盖率 75.9%，面积加权平均层数 0.7591，有层面数 1711/2261（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-shock-link%57：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/25（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-brake-fluid-pot-bracket%58：实际层数最小值 0，覆盖率 19.2%，面积加权平均层数 0.192，有层面数 6/35（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-brake-fluid-pot%59：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/50（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_footpeg%60：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/88（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-chain-hub%61：实际层数最小值 0，覆盖率 8.6%，面积加权平均层数 0.08577，有层面数 11/117（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-brake-caliper%62：实际层数最小值 0，覆盖率 18.0%，面积加权平均层数 0.1796，有层面数 26/134（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rider-helmet%65：实际层数最小值 0，覆盖率 95.6%，面积加权平均层数 0.9557，有层面数 704/740（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rider-visor%66：实际层数最小值 1，覆盖率 100.0%，面积加权平均层数 1，有层面数 157/157（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rider-boots%67：实际层数最小值 0，覆盖率 85.0%，面积加权平均层数 0.8496，有层面数 834/1004（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rider-gloves%68：实际层数最小值 0，覆盖率 31.0%，面积加权平均层数 0.3098，有层面数 95/308（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rider-body%69：实际层数最小值 0，覆盖率 86.7%，面积加权平均层数 0.8674，有层面数 3974/4560（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frame:0%70：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/37（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_frt-fairing:001-shadow%74：实际层数最小值 0，覆盖率 41.4%，面积加权平均层数 0.414，有层面数 1242/3309（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_windshield-shadow%75：实际层数最小值 0，覆盖率 10.8%，面积加权平均层数 0.1084，有层面数 29/275（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-mud-guard-shadow%81：实际层数最小值 0，覆盖率 28.0%，面积加权平均层数 0.28，有层面数 97/346（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_fr-wh-brake-disk-shadow%83：实际层数最小值 0，覆盖率 32.7%，面积加权平均层数 0.3268，有层面数 62/204（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-mud-guard-shadow%84：实际层数最小值 0，覆盖率 34.3%，面积加权平均层数 0.3427，有层面数 131/415（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-susp-spring-damp-shadow%85：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/46（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_radiator-shadow%86：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/33（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-shock-link-shadow%87：实际层数最小值 0，覆盖率 0.0%，面积加权平均层数 0，有层面数 0/13（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rear-brake-fluid-pot-bracket-shadow%88：实际层数最小值 0，覆盖率 44.7%，面积加权平均层数 0.4475，有层面数 12/30（来自snappyHexMesh nSurfaceLayers 边界场）
- motorBike_rr-wh-chain-hub-shadow%89：实际层数最小值 0，覆盖率 10.8%，面积加权平均层数 0.1077，有层面数 7/63（来自snappyHexMesh nSurfaceLayers 边界场）

**待补全的关键证据**

- 缺少与当前网格匹配且结论为 Mesh OK 的完整 checkMesh 检查
- 壁面 lowerWall 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing:001%1 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing:001%1 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield:002%2 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield:002%2 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:005%5 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:005%5 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:010%10 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:010%10 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-rim:011%11 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-rim:011%11 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk:012%12 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk:012%12 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:016-shadow%13 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:016-shadow%13 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp:014%14 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp:014%14 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp:014-shadow%15 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp:014-shadow%15 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:016%16 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:016%16 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:005-shadow%17 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:005-shadow%17 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub:022%22 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub:022%22 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rearseat%24 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rearseat%24 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing%25 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing%25 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield%26 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield%26 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_headlights%27 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_headlights%27 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_driversseat%28 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_driversseat%28 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-body%29 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-body%29 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fuel-tank%30 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fuel-tank%30 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_exhaust%31 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_exhaust%31 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim%32 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim%32 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-mud-guard%33 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-mud-guard%33 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-rim%34 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-rim%34 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk%35 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk%35 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-brake-caliper%36 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-brake-caliper%36 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-tyre%37 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-tyre%37 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_hbars%38 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_hbars%38 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-forks%39 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-forks%39 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_chain%40 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_chain%40 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-tyre%41 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-tyre%41 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_square-dial%42 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_square-dial%42 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_round-dial%43 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_round-dial%43 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_dial-holder%44 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_dial-holder%44 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp%45 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp%45 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-lights%46 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-lights%46 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-light-bracket%47 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-light-bracket%47 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame%48 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame%48 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-mud-guard%49 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-mud-guard%49 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp-spring-damp%50 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp-spring-damp%50 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fairing-inner-plate%51 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fairing-inner-plate%51 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_clutch-housing%52 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_clutch-housing%52 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_radiator%53 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_radiator%53 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_water-pipe%54 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_water-pipe%54 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_water-pump%55 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_water-pump%55 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_engine%56 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_engine%56 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-shock-link%57 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-shock-link%57 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot-bracket%58 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot-bracket%58 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot%59 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot%59 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_footpeg%60 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_footpeg%60 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub%61 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub%61 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-caliper%62 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-caliper%62 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-helmet%65 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-helmet%65 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-visor%66 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-visor%66 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-boots%67 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-boots%67 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-gloves%68 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-gloves%68 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-body%69 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-body%69 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:0%70 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:0%70 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing:001-shadow%74 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing:001-shadow%74 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield-shadow%75 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield-shadow%75 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-mud-guard-shadow%81 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-mud-guard-shadow%81 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk-shadow%83 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk-shadow%83 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-mud-guard-shadow%84 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-mud-guard-shadow%84 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp-spring-damp-shadow%85 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp-spring-damp-shadow%85 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_radiator-shadow%86 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_radiator-shadow%86 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-shock-link-shadow%87 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-shock-link-shadow%87 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub-shadow%89 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub-shadow%89 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 缺少试算后各入口/出口的有符号质量通量，无法核对质量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性

## 4. 质量指标

| 指标 | 极值 | 阈值（中等/高/致命） | 超标范围 | 等级 |
|---|---|---|---|---|
| 凹单元 |  — | — | 15226 个单元（4.3%，大面积） | 🟡 中等 |
| 非正交性 | 最大 64.99° | > 65/70/85 | 0 | 🟢 可接受 |
| 歪斜度（OpenFOAM 定义） | 最大 9.576 | > 2.5/4/20 | 15 个面（0.00135%，零星） | 🔴 高风险 |
| 长宽比 | 最大 40.91 | > 1000/10000/— | 0 | 🟢 可接受 |
| 单元行列式 | 最小 0 | < 0.01/0.001/— | 73 个单元（0.0206%，零星） | 🔴 高风险 |
| 面插值权重 | 最小 0.02245 | < 0.05/0.02/— | 996 个内部面（0.094%，零星） | 🟡 中等 |
| 相邻单元体积比 | 最小 0.01005 | < 0.01/0.001/— | 0 | 🟢 可接受 |
| 壁面 lowerWall 实际边界层层数 | 最小 0 | — | 34 个壁面面（0.637%，局部） | 🟢 可接受 |
| 壁面 lowerWall 边界层覆盖率 |  0.9999 | — | 34 个壁面面（0.637%，局部） | 🟢 可接受 |
| 壁面 lowerWall 的近壁内部面非正交角 | 最大 64.69° | — | 0 | 🟢 可接受 |
| 壁面 lowerWall 的近壁内部面歪斜度 | 最大 0.4557 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing:001%1 实际边界层层数 | 最小 0 | — | 3236 个壁面面（61.1%，大面积） | 🔴 高风险 |
| 壁面 motorBike_frt-fairing:001%1 边界层覆盖率 |  0.3968 | — | 3236 个壁面面（61.1%，大面积） | 🔴 高风险 |
| 壁面 motorBike_frt-fairing:001%1 的近壁内部面非正交角 | 最大 64.93° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing:001%1 的近壁内部面歪斜度 | 最大 1.478 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield:002%2 的近壁内部面非正交角 | 最大 45.84° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield:002%2 的近壁内部面歪斜度 | 最大 0.552 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:005%5 的近壁内部面非正交角 | 最大 52.62° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:005%5 的近壁内部面歪斜度 | 最大 0.317 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:010%10 的近壁内部面非正交角 | 最大 64.07° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:010%10 的近壁内部面歪斜度 | 最大 1.819 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-rim:011%11 实际边界层层数 | 最小 0 | — | 338 个壁面面（68.7%，大面积） | 🔴 高风险 |
| 壁面 motorBike_fr-wh-rim:011%11 边界层覆盖率 |  0.3468 | — | 338 个壁面面（68.7%，大面积） | 🔴 高风险 |
| 壁面 motorBike_fr-wh-rim:011%11 的近壁内部面非正交角 | 最大 63.98° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-rim:011%11 的近壁内部面歪斜度 | 最大 0.6482 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk:012%12 的近壁内部面非正交角 | 最大 36.58° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk:012%12 的近壁内部面歪斜度 | 最大 0.2838 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:016-shadow%13 的近壁内部面非正交角 | 最大 60.94° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:016-shadow%13 的近壁内部面歪斜度 | 最大 0.4296 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp:014%14 的近壁内部面非正交角 | 最大 64.96° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp:014%14 的近壁内部面歪斜度 | 最大 1.059 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp:014-shadow%15 的近壁内部面非正交角 | 最大 63.77° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp:014-shadow%15 的近壁内部面歪斜度 | 最大 0.9483 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:016%16 的近壁内部面非正交角 | 最大 59.88° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:016%16 的近壁内部面歪斜度 | 最大 0.381 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:005-shadow%17 的近壁内部面非正交角 | 最大 64.07° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim:005-shadow%17 的近壁内部面歪斜度 | 最大 0.7425 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub:022%22 的近壁内部面非正交角 | 最大 44.14° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub:022%22 的近壁内部面歪斜度 | 最大 0.6639 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rearseat%24 的近壁内部面非正交角 | 最大 54.27° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rearseat%24 的近壁内部面歪斜度 | 最大 1.105 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing%25 的近壁内部面非正交角 | 最大 64.87° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing%25 的近壁内部面歪斜度 | 最大 1.418 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield%26 的近壁内部面非正交角 | 最大 64.49° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield%26 的近壁内部面歪斜度 | 最大 0.6035 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_headlights%27 的近壁内部面非正交角 | 最大 64.55° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_headlights%27 的近壁内部面歪斜度 | 最大 0.8789 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_driversseat%28 的近壁内部面非正交角 | 最大 64.33° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_driversseat%28 的近壁内部面歪斜度 | 最大 1.042 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-body%29 的近壁内部面非正交角 | 最大 63.87° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-body%29 的近壁内部面歪斜度 | 最大 1.878 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fuel-tank%30 的近壁内部面非正交角 | 最大 64.78° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fuel-tank%30 的近壁内部面歪斜度 | 最大 0.8804 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_exhaust%31 的近壁内部面非正交角 | 最大 62.31° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_exhaust%31 的近壁内部面歪斜度 | 最大 1.224 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim%32 的近壁内部面非正交角 | 最大 63.09° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-rim%32 的近壁内部面歪斜度 | 最大 0.9694 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-mud-guard%33 的近壁内部面非正交角 | 最大 64.33° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-mud-guard%33 的近壁内部面歪斜度 | 最大 1.277 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-rim%34 的近壁内部面非正交角 | 最大 63.83° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-rim%34 的近壁内部面歪斜度 | 最大 0.964 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk%35 的近壁内部面非正交角 | 最大 55.66° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk%35 的近壁内部面歪斜度 | 最大 0.7885 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-brake-caliper%36 的近壁内部面非正交角 | 最大 48.63° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-brake-caliper%36 的近壁内部面歪斜度 | 最大 0.4477 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-tyre%37 的近壁内部面非正交角 | 最大 64.16° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-tyre%37 的近壁内部面歪斜度 | 最大 0.9103 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_hbars%38 的近壁内部面非正交角 | 最大 43.36° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_hbars%38 的近壁内部面歪斜度 | 最大 0.6789 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-forks%39 的近壁内部面非正交角 | 最大 59.76° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-forks%39 的近壁内部面歪斜度 | 最大 0.8105 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_chain%40 的近壁内部面非正交角 | 最大 59.28° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_chain%40 的近壁内部面歪斜度 | 最大 0.5624 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-tyre%41 的近壁内部面非正交角 | 最大 64.69° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-tyre%41 的近壁内部面歪斜度 | 最大 0.8391 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_square-dial%42 的近壁内部面非正交角 | 最大 29.15° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_square-dial%42 的近壁内部面歪斜度 | 最大 0.3371 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_round-dial%43 的近壁内部面非正交角 | 最大 46° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_round-dial%43 的近壁内部面歪斜度 | 最大 0.2965 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_dial-holder%44 的近壁内部面非正交角 | 最大 43.78° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_dial-holder%44 的近壁内部面歪斜度 | 最大 0.5775 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp%45 的近壁内部面非正交角 | 最大 64.42° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp%45 的近壁内部面歪斜度 | 最大 1.059 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-lights%46 的近壁内部面非正交角 | 最大 38.62° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-lights%46 的近壁内部面歪斜度 | 最大 0.2912 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-light-bracket%47 的近壁内部面非正交角 | 最大 51.34° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-light-bracket%47 的近壁内部面歪斜度 | 最大 0.5115 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame%48 的近壁内部面非正交角 | 最大 64.83° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame%48 的近壁内部面歪斜度 | 最大 1.083 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-mud-guard%49 的近壁内部面非正交角 | 最大 64.39° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-mud-guard%49 的近壁内部面歪斜度 | 最大 0.944 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp-spring-damp%50 的近壁内部面非正交角 | 最大 52.07° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp-spring-damp%50 的近壁内部面歪斜度 | 最大 0.4786 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fairing-inner-plate%51 的近壁内部面非正交角 | 最大 62.4° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fairing-inner-plate%51 的近壁内部面歪斜度 | 最大 0.7901 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_clutch-housing%52 的近壁内部面非正交角 | 最大 64.61° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_clutch-housing%52 的近壁内部面歪斜度 | 最大 1.109 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_radiator%53 的近壁内部面非正交角 | 最大 36.92° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_radiator%53 的近壁内部面歪斜度 | 最大 0.5442 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_water-pipe%54 的近壁内部面非正交角 | 最大 38.29° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_water-pipe%54 的近壁内部面歪斜度 | 最大 0.355 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_water-pump%55 的近壁内部面非正交角 | 最大 60.66° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_water-pump%55 的近壁内部面歪斜度 | 最大 0.7127 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_engine%56 的近壁内部面非正交角 | 最大 60.18° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_engine%56 的近壁内部面歪斜度 | 最大 1.742 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-shock-link%57 的近壁内部面非正交角 | 最大 45.41° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-shock-link%57 的近壁内部面歪斜度 | 最大 0.315 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot-bracket%58 的近壁内部面非正交角 | 最大 36.6° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot-bracket%58 的近壁内部面歪斜度 | 最大 0.4641 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot%59 的近壁内部面非正交角 | 最大 38.95° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot%59 的近壁内部面歪斜度 | 最大 0.2981 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_footpeg%60 的近壁内部面非正交角 | 最大 39.55° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_footpeg%60 的近壁内部面歪斜度 | 最大 0.8267 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub%61 的近壁内部面非正交角 | 最大 39.24° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub%61 的近壁内部面歪斜度 | 最大 0.4147 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-caliper%62 的近壁内部面非正交角 | 最大 54.12° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-caliper%62 的近壁内部面歪斜度 | 最大 0.6903 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-helmet%65 的近壁内部面非正交角 | 最大 64.89° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-helmet%65 的近壁内部面歪斜度 | 最大 1.297 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-visor%66 的近壁内部面非正交角 | 最大 56.61° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-visor%66 的近壁内部面歪斜度 | 最大 1.027 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-boots%67 的近壁内部面非正交角 | 最大 62.44° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-boots%67 的近壁内部面歪斜度 | 最大 1.143 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-gloves%68 的近壁内部面非正交角 | 最大 51.41° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-gloves%68 的近壁内部面歪斜度 | 最大 2.638 | — | 1 个内部面（0.1%，局部） | 🟡 中等 |
| 壁面 motorBike_rider-body%69 的近壁内部面非正交角 | 最大 64.97° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rider-body%69 的近壁内部面歪斜度 | 最大 1.279 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:0%70 的近壁内部面非正交角 | 最大 33.29° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frame:0%70 的近壁内部面歪斜度 | 最大 0.2936 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing:001-shadow%74 的近壁内部面非正交角 | 最大 64.93° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_frt-fairing:001-shadow%74 的近壁内部面歪斜度 | 最大 1.478 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield-shadow%75 的近壁内部面非正交角 | 最大 64.89° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_windshield-shadow%75 的近壁内部面歪斜度 | 最大 0.6035 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面非正交角 | 最大 65.16° | — | 1 个内部面（0.0799%，零星） | 🟡 中等 |
| 壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面歪斜度 | 最大 0.9857 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk-shadow%83 的近壁内部面非正交角 | 最大 51.71° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_fr-wh-brake-disk-shadow%83 的近壁内部面歪斜度 | 最大 0.7449 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-mud-guard-shadow%84 的近壁内部面非正交角 | 最大 64.69° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-mud-guard-shadow%84 的近壁内部面歪斜度 | 最大 1.03 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp-spring-damp-shadow%85 的近壁内部面非正交角 | 最大 48.98° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-susp-spring-damp-shadow%85 的近壁内部面歪斜度 | 最大 0.4562 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_radiator-shadow%86 的近壁内部面非正交角 | 最大 36.92° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_radiator-shadow%86 的近壁内部面歪斜度 | 最大 0.5442 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-shock-link-shadow%87 的近壁内部面非正交角 | 最大 41.25° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-shock-link-shadow%87 的近壁内部面歪斜度 | 最大 0.4 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 的近壁内部面非正交角 | 最大 35.59° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 的近壁内部面歪斜度 | 最大 0.3464 | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub-shadow%89 的近壁内部面非正交角 | 最大 44.14° | — | 0 | 🟢 可接受 |
| 壁面 motorBike_rr-wh-chain-hub-shadow%89 的近壁内部面歪斜度 | 最大 0.3711 | — | 0 | 🟢 可接受 |

- **非正交性**：平均值 9.986°；分布：>50°: 1576，>65°: 1，>70°: 0，>80°: 0；定义：面法向与相邻单元中心连线的夹角（仅内部面），0° 为理想
- **歪斜度（OpenFOAM 定义）**：分布：>1: 2376，>2.5: 334，>4: 23，>10: 0；定义：面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
- **长宽比**：定义：OpenFOAM cellAspectRatio，1 为理想
- **壁面 lowerWall 实际边界层层数**：定义：目标至少 1 层；按面积计算不足比例 0.0%；来自 nSurfaceLayers 边界场
- **壁面 lowerWall 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 lowerWall 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 lowerWall 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing:001%1 实际边界层层数**：定义：目标至少 1 层；按面积计算不足比例 60.3%；来自 nSurfaceLayers 边界场
- **壁面 motorBike_frt-fairing:001%1 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 motorBike_frt-fairing:001%1 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing:001%1 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield:002%2 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield:002%2 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:005%5 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:005%5 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:010%10 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:010%10 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-rim:011%11 实际边界层层数**：定义：目标至少 1 层；按面积计算不足比例 65.3%；来自 nSurfaceLayers 边界场
- **壁面 motorBike_fr-wh-rim:011%11 边界层覆盖率**：定义：目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
- **壁面 motorBike_fr-wh-rim:011%11 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-rim:011%11 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk:012%12 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk:012%12 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:016-shadow%13 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:016-shadow%13 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp:014%14 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp:014%14 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp:014-shadow%15 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp:014-shadow%15 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:016%16 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:016%16 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:005-shadow%17 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim:005-shadow%17 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub:022%22 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub:022%22 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rearseat%24 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rearseat%24 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing%25 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing%25 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield%26 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield%26 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_headlights%27 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_headlights%27 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_driversseat%28 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_driversseat%28 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-body%29 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-body%29 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fuel-tank%30 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fuel-tank%30 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_exhaust%31 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_exhaust%31 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim%32 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-rim%32 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-mud-guard%33 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-mud-guard%33 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-rim%34 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-rim%34 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk%35 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk%35 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-brake-caliper%36 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-brake-caliper%36 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-tyre%37 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-tyre%37 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_hbars%38 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_hbars%38 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-forks%39 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-forks%39 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_chain%40 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_chain%40 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-tyre%41 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-tyre%41 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_square-dial%42 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_square-dial%42 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_round-dial%43 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_round-dial%43 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_dial-holder%44 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_dial-holder%44 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp%45 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp%45 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-lights%46 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-lights%46 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-light-bracket%47 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-light-bracket%47 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame%48 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame%48 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-mud-guard%49 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-mud-guard%49 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp-spring-damp%50 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp-spring-damp%50 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fairing-inner-plate%51 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fairing-inner-plate%51 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_clutch-housing%52 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_clutch-housing%52 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_radiator%53 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_radiator%53 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_water-pipe%54 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_water-pipe%54 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_water-pump%55 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_water-pump%55 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_engine%56 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_engine%56 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-shock-link%57 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-shock-link%57 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot-bracket%58 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot-bracket%58 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot%59 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot%59 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_footpeg%60 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_footpeg%60 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub%61 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub%61 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-caliper%62 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-caliper%62 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-helmet%65 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-helmet%65 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-visor%66 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-visor%66 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-boots%67 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-boots%67 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-gloves%68 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-gloves%68 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-body%69 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rider-body%69 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:0%70 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frame:0%70 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing:001-shadow%74 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_frt-fairing:001-shadow%74 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield-shadow%75 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_windshield-shadow%75 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk-shadow%83 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_fr-wh-brake-disk-shadow%83 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-mud-guard-shadow%84 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-mud-guard-shadow%84 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp-spring-damp-shadow%85 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-susp-spring-damp-shadow%85 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_radiator-shadow%86 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_radiator-shadow%86 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-shock-link-shadow%87 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-shock-link-shadow%87 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub-shadow%89 的近壁内部面非正交角**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
- **壁面 motorBike_rr-wh-chain-hub-shadow%89 的近壁内部面歪斜度**：定义：壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标

## 5. 问题定位

**歪斜度（OpenFOAM 定义）**
- 靠近边界：motorBike_frt-fairing:001%1（7），motorBike_rear-susp%45（4），motorBike_frt-fairing:001-shadow%74（2），motorBike_fr-wh-rim:011%11（1），motorBike_frame:016%16（1）
- 包围盒：[-0.149, -0.2701, 0.1479] → [1.134, 0.258, 1.057]
- 最差：值 9.531，坐标 [0.30117, -0.170005, 1.052457]，编号 1105051，最近边界 motorBike_frt-fairing:001-shadow%74（距离 0）

**壁面 motorBike_frt-fairing:001%1 实际边界层层数**
- 靠近边界：motorBike_frt-fairing:001%1（3236）
- 包围盒：[0.035005483596162054, -0.27931196429317784, 0.1521914000581499] → [1.0383220957461414, 0.2677120516778979, 1.0549811407007166]

**壁面 motorBike_frt-fairing:001%1 边界层覆盖率**
- 靠近边界：motorBike_frt-fairing:001%1（3236）
- 包围盒：[0.035005483596162054, -0.27931196429317784, 0.1521914000581499] → [1.0383220957461414, 0.2677120516778979, 1.0549811407007166]

**壁面 motorBike_fr-wh-rim:011%11 实际边界层层数**
- 靠近边界：motorBike_fr-wh-rim:011%11（338）
- 包围盒：[-0.20796713733170258, -0.12256321916847247, 0.07344472770205407] → [0.2407105900682959, 0.12217497668799343, 0.5219404424778372]

**壁面 motorBike_fr-wh-rim:011%11 边界层覆盖率**
- 靠近边界：motorBike_fr-wh-rim:011%11（338）
- 包围盒：[-0.20796713733170258, -0.12256321916847247, 0.07344472770205407] → [0.2407105900682959, 0.12217497668799343, 0.5219404424778372]

**壁面 motorBike_rider-gloves%68 的近壁内部面歪斜度**
- 靠近边界：motorBike_rider-gloves%68（1）

**壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面非正交角**
- 靠近边界：motorBike_fr-mud-guard-shadow%81（1）

可视化：checkMesh 会把坏面/坏单元写成集合（如 nonOrthoFaces、skewFaces）。用 `foamToVTK -faceSet nonOrthoFaces`（单元集合用 -cellSet）转成 VTK，或 ESI 版直接用 `checkMesh -allGeometry -allTopology -writeSets vtk`，在 ParaView 中查看。

## 6. 按优先级排列的网格优化建议

1. **checkMesh 检查失败项**（高风险）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 4
   - 修改：针对超标位置调整局部尺寸、单元形状和连接方式。
   - 验证：重复同一指标检查并比较超标单元数。
2. **歪斜度（OpenFOAM 定义）**（高风险）
   - 位置：边界 motorBike_frt-fairing:001%1、motorBike_rear-susp%45、motorBike_frt-fairing:001-shadow%74，坐标范围 [-0.149, -0.2701, 0.1479] 至 [1.134, 0.258, 1.057]
   - 证据：极值 9.5763；范围 15 / 1108744；面中心相对两单元中心连线交点的偏移，按面尺寸归一化；无上界，0 为理想
   - 修改：定位歪斜面的邻接单元，清理尖角/窄缝，平滑表面尺寸过渡并重新贴体。
   - 验证：重新检查超标面数、分布和最大歪斜度。
3. **单元行列式**（高风险）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 0.0；范围 73 / 353779
   - 修改：检查近退化单元的尖角、压扁层和节点位置，重新划分该局部。
   - 验证：重新运行 checkMesh，确认单元行列式达到所用规则阈值。
4. **壁面 motorBike_frt-fairing:001%1 实际边界层层数**（高风险）
   - 位置：边界 motorBike_frt-fairing:001%1，坐标范围 [0.035005483596162054, -0.27931196429317784, 0.1521914000581499] 至 [1.0383220957461414, 0.2677120516778979, 1.0549811407007166]
   - 证据：极值 0；范围 3236 / 5292；目标至少 1 层；按面积计算不足比例 60.3%；来自 nSurfaceLayers 边界场
   - 修改：在低于目标层数的壁面区域检查尖角、狭缝及贴体面尺寸；核对 snappyHexMesh 的 minThickness、featureAngle 与层末端缓冲设置，再局部重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认低于目标层数的面积比例与位置改善，并复查近壁歪斜和非正交性。
5. **壁面 motorBike_frt-fairing:001%1 边界层覆盖率**（高风险）
   - 位置：边界 motorBike_frt-fairing:001%1，坐标范围 [0.035005483596162054, -0.27931196429317784, 0.1521914000581499] 至 [1.0383220957461414, 0.2677120516778979, 1.0549811407007166]
   - 证据：极值 0.396753；范围 3236 / 5292；目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
   - 修改：在零层覆盖的壁面区域检查表面尺寸、曲率与狭缝；核对 minThickness、maxFaceThicknessRatio、maxThicknessToMedialRatio 等加层限制，分区调参后重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认零层面积比例下降且问题没有转移到相邻壁面。
6. **壁面 motorBike_fr-wh-rim:011%11 实际边界层层数**（高风险）
   - 位置：边界 motorBike_fr-wh-rim:011%11，坐标范围 [-0.20796713733170258, -0.12256321916847247, 0.07344472770205407] 至 [0.2407105900682959, 0.12217497668799343, 0.5219404424778372]
   - 证据：极值 0；范围 338 / 492；目标至少 1 层；按面积计算不足比例 65.3%；来自 nSurfaceLayers 边界场
   - 修改：在低于目标层数的壁面区域检查尖角、狭缝及贴体面尺寸；核对 snappyHexMesh 的 minThickness、featureAngle 与层末端缓冲设置，再局部重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认低于目标层数的面积比例与位置改善，并复查近壁歪斜和非正交性。
7. **壁面 motorBike_fr-wh-rim:011%11 边界层覆盖率**（高风险）
   - 位置：边界 motorBike_fr-wh-rim:011%11，坐标范围 [-0.20796713733170258, -0.12256321916847247, 0.07344472770205407] 至 [0.2407105900682959, 0.12217497668799343, 0.5219404424778372]
   - 证据：极值 0.346763；范围 338 / 492；目标不低于 0.95；按壁面面积加权；来自 nSurfaceLayers 边界场
   - 修改：在零层覆盖的壁面区域检查表面尺寸、曲率与狭缝；核对 minThickness、maxFaceThicknessRatio、maxThicknessToMedialRatio 等加层限制，分区调参后重划。
   - 验证：重新读取 nSurfaceLayers 边界场，确认零层面积比例下降且问题没有转移到相邻壁面。
8. **凹单元**（中等）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 None；范围 15226 / 353779
   - 修改：针对超标位置调整局部尺寸、单元形状和连接方式。
   - 验证：重复同一指标检查并比较超标单元数。
9. **面插值权重**（中等）
   - 位置：报告未提供局部坐标；先用 checkMesh 集合或质量场定位
   - 证据：极值 0.0224494；范围 996 / 1059085
   - 修改：在报警面两侧增加过渡层，降低相邻单元尺寸突变。
   - 验证：重新检查插值权重低于阈值的面数。
10. **壁面 motorBike_rider-gloves%68 的近壁内部面歪斜度**（中等）
   - 位置：边界 motorBike_rider-gloves%68
   - 证据：极值 2.6379；范围 1 / 996；壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
   - 修改：检查该壁面首层单元的扭曲和层间连接；平滑壁面单元尺寸并避免层在局部突然终止。
   - 验证：复查该壁面首层相邻内部面的最大歪斜度和超过 4 的面数。
11. **壁面 motorBike_fr-mud-guard-shadow%81 的近壁内部面非正交角**（中等）
   - 位置：边界 motorBike_fr-mud-guard-shadow%81
   - 证据：极值 65.1613；范围 1 / 1252；壁面首层单元相邻内部面的独立几何计算；严重程度参照 OpenFOAM 同名指标
   - 修改：在该壁面首层单元与第二层之间改善法向排列；检查贴体面、层坍塌和层末端到核心网格的尺寸突变。
   - 验证：复查该壁面首层相邻内部面的最大非正交角和超过 70° 的面数。

**下一步取证**

- 缺少与当前网格匹配且结论为 Mesh OK 的完整 checkMesh 检查
- 壁面 lowerWall 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing:001%1 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing:001%1 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield:002%2 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield:002%2 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:005%5 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:005%5 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:010%10 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:010%10 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-rim:011%11 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-rim:011%11 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk:012%12 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk:012%12 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:016-shadow%13 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:016-shadow%13 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp:014%14 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp:014%14 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp:014-shadow%15 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp:014-shadow%15 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:016%16 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:016%16 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim:005-shadow%17 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim:005-shadow%17 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub:022%22 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub:022%22 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rearseat%24 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rearseat%24 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing%25 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing%25 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield%26 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield%26 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_headlights%27 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_headlights%27 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_driversseat%28 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_driversseat%28 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-body%29 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-body%29 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fuel-tank%30 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fuel-tank%30 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_exhaust%31 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_exhaust%31 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-rim%32 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-rim%32 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-mud-guard%33 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-mud-guard%33 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-rim%34 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-rim%34 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk%35 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk%35 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-brake-caliper%36 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-brake-caliper%36 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-tyre%37 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-tyre%37 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_hbars%38 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_hbars%38 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-forks%39 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-forks%39 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_chain%40 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_chain%40 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-tyre%41 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-tyre%41 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_square-dial%42 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_square-dial%42 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_round-dial%43 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_round-dial%43 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_dial-holder%44 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_dial-holder%44 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp%45 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp%45 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-lights%46 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-lights%46 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-light-bracket%47 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-light-bracket%47 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame%48 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame%48 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-mud-guard%49 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-mud-guard%49 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp-spring-damp%50 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp-spring-damp%50 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fairing-inner-plate%51 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fairing-inner-plate%51 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_clutch-housing%52 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_clutch-housing%52 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_radiator%53 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_radiator%53 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_water-pipe%54 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_water-pipe%54 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_water-pump%55 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_water-pump%55 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_engine%56 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_engine%56 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-shock-link%57 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-shock-link%57 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot-bracket%58 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot-bracket%58 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot%59 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot%59 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_footpeg%60 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_footpeg%60 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub%61 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub%61 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-caliper%62 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-caliper%62 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-helmet%65 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-helmet%65 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-visor%66 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-visor%66 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-boots%67 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-boots%67 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-gloves%68 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-gloves%68 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rider-body%69 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rider-body%69 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frame:0%70 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frame:0%70 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_frt-fairing:001-shadow%74 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_frt-fairing:001-shadow%74 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_windshield-shadow%75 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_windshield-shadow%75 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-mud-guard-shadow%81 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-mud-guard-shadow%81 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_fr-wh-brake-disk-shadow%83 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_fr-wh-brake-disk-shadow%83 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-mud-guard-shadow%84 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-mud-guard-shadow%84 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-susp-spring-damp-shadow%85 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-susp-spring-damp-shadow%85 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_radiator-shadow%86 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_radiator-shadow%86 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-shock-link-shadow%87 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-shock-link-shadow%87 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rear-brake-fluid-pot-bracket-shadow%88 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 壁面 motorBike_rr-wh-chain-hub-shadow%89 缺少 0/nut 等实际壁面场定义；提供该算例文件或确认 wall_conditions_verified
- 壁面 motorBike_rr-wh-chain-hub-shadow%89 缺少 treatment 或 target_yplus，无法判断近壁模型匹配
- 缺少试算后各入口/出口的有符号质量通量，无法核对质量守恒
- 缺少压降、流量或换热量的监测序列，无法复核结果稳定性
- 缺少至少三套网格的同一目标量结果，无法检查网格敏感性
- 已有试算时，可用 OpenFOAM 的 `yPlus` 功能对象输出壁面场；提供该 ASCII 场用于逐壁面复核。

## 7. 原始报警行

```
***Max skewness = 9.57634, 15 highly skew faces detected which may impair the quality of the results
*There are 1784 faces with concave angles between consecutive edges. Max concave angle = 79.9595 degrees.
*There are 286 faces with ratio between projected and actual area < 0.8
***Cells with small determinant (< 0.001) found, number of cells: 73
***Concave cells (using face planes) found, number of cells: 15226
***Faces with small interpolation weight (< 0.05) found, number of faces: 996
```

## 8. 局限与说明

- 位置/分布统计来自本工具按 OpenFOAM 公式的独立计算，数值可能与 checkMesh 有微小差别；严重程度以 checkMesh 数值为准。
- 阈值为经验值（见 `scripts/thresholds.json`），严重程度需结合求解类型判断：同样的指标对稳态 RANS 和瞬态多相/动网格计算的影响不同。

## 9. 检查日志

| 时间(s) | 状态 | 步骤 | 命令 |
|---|---|---|---|
| 0.0 | ok | 识别网格来源：openfoam / case（找到 constant/polyMesh/{points,faces,owner}；存在 system/controlDict） |  |
| 0.06 | ok | 使用已有 checkMesh 日志：/home/foamuser/OpenFOAM/foamuser-12/run/motorBikeSteady-layer-validation-20261004/log.checkMesh |  |
| 0.07 | ok | 用 Python 读取 polyMesh，计算各面/单元指标分布和位置 | `polymesh.analyse(/home/foamuser/OpenFOAM/foamuser-12/run/motorBikeSteady-layer-validation-20261004/constant/polyMesh)` |
| 10.79 | ok | polyMesh 读取完成：353779 个单元，1108744 个面 |  |
