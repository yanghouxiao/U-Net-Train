# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# # 1. 定义参数与公式
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     参数：
#     P: 含水层水压（MPa）
#     h: 开采深度（m）
#     Lf: 断层密度（条/km²）
#     Fs: 支护阻力（kN/m），需转换为MPa·m（1MPa·m=1000kN/m）
#     返回：
#     R: 突水风险值
#     risk_level: 风险等级（低/中/高）
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     # 统一量纲：Fs转换为MPa·m
#     Fs_mpa_m = Fs / 1000
#     # 岩体抗渗力（MPa·m）
#     rock_resist = gamma * h * tan_phi / 1000  # 转换为MPa·m
#     # 风险公式
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))  # 风险值限定在0-1之间
#
#     # 划分风险等级
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# # 2. 实例计算（题目给定参数）
# if __name__ == "__main__":
#     # 设置中文字体
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     # 输入参数列表（可扩展多组参数）
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},
#         {"P": 2.2, "h": 850, "Lf": 4, "Fs": 6500, "roadway": "支巷道1"},
#         {"P": 1.9, "h": 780, "Lf": 2.5, "Fs": 5800, "roadway": "支巷道2"}
#     ]
#
#     # 计算并存储结果
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(
#             P=param["P"],
#             h=param["h"],
#             Lf=param["Lf"],
#             Fs=param["Fs"]
#         )
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     # 转换为DataFrame并保存为Excel
#     df_results = pd.DataFrame(results)
#
#     # 尝试保存Excel，如果失败则保存为CSV
#     try:
#         df_results.to_excel("突水风险预测结果.xlsx", index=False)
#         print("突水风险预测结果已保存为Excel文件！")
#     except Exception as e:
#         df_results.to_csv("突水风险预测结果.csv", index=False, encoding='utf-8-sig')
#         print(f"Excel保存失败，已保存为CSV文件。错误信息: {e}")
#
#     print("计算结果:")
#     print(df_results)
#
#     # 可视化风险分布
#     plt.figure(figsize=(10, 6))
#     x = df_results["巷道名称"]
#     y = df_results["突水风险值"]
#     colors = ["green" if level == "低风险" else "orange" if level == "中风险" else "red"
#               for level in df_results["风险等级"]]
#
#     bars = plt.bar(x, y, color=colors, alpha=0.7, edgecolor='black')
#     plt.axhline(y=0.3, color='gray', linestyle='--', label='低/中风险阈值(0.3)')
#     plt.axhline(y=0.6, color='black', linestyle='--', label='中/高风险阈值(0.6)')
#     plt.xlabel("巷道名称", fontsize=12)
#     plt.ylabel("突水风险值", fontsize=12)
#     plt.title("矿井各巷道突水风险分布", fontsize=14, fontweight='bold')
#     plt.ylim(0, 1)
#     plt.legend()
#
#     # 在柱状图上添加数值标签
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
#                  f'{height:.3f}', ha='center', va='bottom')
#
#     plt.tight_layout()
#
#     # 尝试保存图片
#     try:
#         plt.savefig("突水风险分布.png", dpi=300, bbox_inches='tight')
#         print("突水风险分布图已保存！")
#     except Exception as e:
#         print(f"图片保存失败: {e}")
#
#     plt.show()
#
#     # 打印详细分析
#     print("\n=== 风险分析报告 ===")
#     high_risk = df_results[df_results["风险等级"] == "高风险"]
#     medium_risk = df_results[df_results["风险等级"] == "中风险"]
#     low_risk = df_results[df_results["风险等级"] == "低风险"]
#
#     print(f"高风险巷道数量: {len(high_risk)}")
#     if len(high_risk) > 0:
#         print("高风险巷道:", list(high_risk["巷道名称"]))
#
#     print(f"中风险巷道数量: {len(medium_risk)}")
#     print(f"低风险巷道数量: {len(low_risk)}")
#
#     # 参数敏感性分析
#     print("\n=== 参数敏感性分析 ===")
#     base_params = params[0].copy()
#     print(
#         f"基准参数: P={base_params['P']}MPa, h={base_params['h']}m, Lf={base_params['Lf']}条/km², Fs={base_params['Fs']}kN/m")
#     base_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"基准风险值: {base_R:.3f}")
#
#     # 测试水压变化影响
#     test_P = base_params["P"] * 1.2  # 水压增加20%
#     test_R, _ = calculate_risk(test_P, base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"水压增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 测试支护阻力变化影响
#     test_Fs = base_params["Fs"] * 1.2  # 支护阻力增加20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], test_Fs)
#     print(f"支护阻力增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # 1. 清除环境变量与设置参数
# # 巷道网络参数（节点：交叉口，边：巷道段）
# # 节点坐标（x:南北方向，y:东西方向，单位：m）
# nodes = np.array([
#     [0, 0],  # 节点1（安全出口A）
#     [1500, 0],  # 节点2（安全出口B）
#     [750, 400],  # 节点3（突水点）
#     [300, 400],  # 节点4
#     [1200, 400],  # 节点5
#     [750, 800],  # 节点6
# ])
#
# # 巷道段连接关系（起点节点，终点节点，长度m，断面面积m²，高程差m）
# roadways = np.array([
#     [3, 4, 450, 15, -8],  # 突水点→节点4（主巷道）
#     [3, 5, 450, 15, -8],  # 突水点→节点5（主巷道）
#     [3, 6, 400, 12, 5],  # 突水点→节点6（支巷道）
#     [4, 1, 400, 12, -5],  # 节点4→安全出口A（支巷道）
#     [5, 2, 400, 12, -5],  # 节点5→安全出口B（支巷道）
#     [6, 4, 500, 8, 3],  # 节点6→节点4（支巷道）
#     [6, 5, 500, 8, 3],  # 节点6→节点5（支巷道）
# ])
#
# # 突水参数
# Q = 50  # 初始流量（m³/min）
# n = 0.012  # 巷道糙率（混凝土巷道）
# v0 = 4  # 人员正常逃生速度（m/s）
#
#
# # 2. 定义漫延时间计算函数
# def calculate_diffusion_time(Lt, S, DeltaH, Q, n):
#     """
#     计算突水漫延时间
#     参数：
#     Lt: 巷道长度(m)
#     S: 断面面积(m²)
#     DeltaH: 高程差(m)
#     Q: 初始流量(m³/min)
#     n: 巷道糙率
#     返回：
#     t: 漫延时间(min)
#     v: 水流速度(m/s)
#     """
#     # 计算水力半径Rh（矩形巷道：湿周C=2*(宽+高)，假设宽=S/高，高取2m简化）
#     height = 2
#     width = S / height
#     C = 2 * (width + height)  # 湿周（m）
#     Rh = S / C  # 水力半径（m）
#
#     # 水力坡度
#     I = abs(DeltaH) / Lt
#
#     # 曼宁公式计算水流速度（m/s）
#     v = (1 / n) * (Rh ** (2 / 3)) * (I ** (1 / 2))
#
#     # 高程修正系数
#     if DeltaH < 0:  # 下行巷道（加速）
#         alpha = 1 + 0.05 * abs(DeltaH)
#     else:  # 上行巷道（减速）
#         alpha = 1 - 0.05 * abs(DeltaH)
#         alpha = max(alpha, 0.5)  # 避免修正系数过小
#
#     # 漫延时间（min）- 使用充满巷道体积的时间
#     t = (Lt * S) / (Q * alpha)
#
#     return t, v
#
#
# # 3. 批量计算各巷道段漫延时间
# diffusion_results = []
# for i in range(len(roadways)):
#     start_node = int(roadways[i, 0])
#     end_node = int(roadways[i, 1])
#     Lt = roadways[i, 2]
#     S = roadways[i, 3]
#     DeltaH = roadways[i, 4]
#
#     # 计算漫延时间与水流速度
#     t, v = calculate_diffusion_time(Lt, S, DeltaH, Q, n)
#     # 计算人员通过该巷道的时间（考虑风险修正前，s）
#     people_time = Lt / v0
#
#     diffusion_results.append([
#         start_node, end_node, Lt, S, DeltaH,
#         round(v, 2), round(t, 2), round(people_time, 1)
#     ])
#
# # 4. 结果输出与保存
# columns = ['起点节点', '终点节点', '长度(m)', '断面面积(m²)', '高程差(m)',
#            '水流速度(m/s)', '漫延时间(min)', '人员通行时间(s)']
# df_diffusion = pd.DataFrame(diffusion_results, columns=columns)
#
# # 尝试保存Excel，如果失败则保存为CSV
# try:
#     df_diffusion.to_excel('突水漫延模拟结果.xlsx', index=False)
#     print("突水漫延模拟结果已保存为Excel文件！")
# except Exception as e:
#     df_diffusion.to_csv('突水漫延模拟结果.csv', index=False, encoding='utf-8-sig')
#     print(f"Excel保存失败，已保存为CSV文件。错误信息: {e}")
#
# print("计算结果:")
# print(df_diffusion)
#
# # 5. 可视化巷道网络与漫延时间
# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
# plt.rcParams['axes.unicode_minus'] = False
#
# plt.figure(figsize=(12, 8))
# plt.grid(True, alpha=0.3)
# plt.axis('equal')
#
# # 绘制节点
# node_labels = []
# for i in range(len(nodes)):
#     if i == 0 or i == 1:  # 安全出口
#         plt.plot(nodes[i, 0], nodes[i, 1], 'rs', markersize=12, label='安全出口' if i == 0 else "")
#     elif i == 2:  # 突水点
#         plt.plot(nodes[i, 0], nodes[i, 1], 'ro', markersize=12, label='突水点')
#     else:  # 普通节点
#         plt.plot(nodes[i, 0], nodes[i, 1], 'bo', markersize=10, label='普通节点' if i == 3 else "")
#
#     # 添加节点标签
#     plt.text(nodes[i, 0] + 30, nodes[i, 1] + 30, f'节点{i + 1}', fontsize=10)
#
# # 绘制巷道段并标注漫延时间
# for i in range(len(roadways)):
#     start_idx = int(roadways[i, 0]) - 1  # 转换为0-based索引
#     end_idx = int(roadways[i, 1]) - 1
#
#     x = [nodes[start_idx, 0], nodes[end_idx, 0]]
#     y = [nodes[start_idx, 1], nodes[end_idx, 1]]
#
#     t = diffusion_results[i][6]  # 漫延时间
#
#     # 根据漫延时间设置颜色
#     if t < 5:
#         color = 'green'
#     elif t < 10:
#         color = 'orange'
#     else:
#         color = 'red'
#
#     plt.plot(x, y, color=color, linewidth=2, alpha=0.7)
#
#     # 标注漫延时间
#     mid_x = np.mean(x)
#     mid_y = np.mean(y)
#     plt.text(mid_x, mid_y, f't={t:.1f}min', fontsize=9,
#              bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
#
# plt.xlabel('南北方向坐标(m)')
# plt.ylabel('东西方向坐标(m)')
# plt.title('矿井巷道网络与突水漫延时间分布')
#
# # 创建图例
# from matplotlib.lines import Line2D
#
# legend_elements = [
#     Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='安全出口'),
#     Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='突水点'),
#     Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='普通节点'),
#     Line2D([0], [0], color='green', lw=2, label='快速漫延(<5min)'),
#     Line2D([0], [0], color='orange', lw=2, label='中速漫延(5-10min)'),
#     Line2D([0], [0], color='red', lw=2, label='慢速漫延(>10min)')
# ]
# plt.legend(handles=legend_elements, loc='best')
#
# plt.tight_layout()
#
# # 尝试保存图片
# try:
#     plt.savefig('巷道网络与漫延时间.png', dpi=300, bbox_inches='tight')
#     print("巷道网络与漫延时间图已保存！")
# except Exception as e:
#     print(f"图片保存失败: {e}")
#
# plt.show()

# # 6. 额外分析：逃生路径评估
# print("\n=== 逃生路径分析 ===")
# # 找到从突水点（节点3）到安全出口的最短时间路径
# from_node = 3  # 突水点
#
# # 构建图数据结构
# graph = {}
# for i, row in enumerate(diffusion_results):
#     start, end, _, _, _, _, t_water, t_people = row
#     if start not in graph:
#         graph[start] = []
#     if end not in graph:
#         graph[end] = []
#
#     # 考虑水流影响的人员逃生时间修正
#     # 如果水流先到达，则人员无法通过
#     risk_factor = 1.0
#     if t_water * 60 < t_people:  # 漫延时间转换为秒比较
#         risk_factor = float('inf')  # 无法通行
#
#     graph[start].append((end, t_people, risk_factor))
#     graph[end].append((start, t_people, risk_factor))  # 双向通行
#
#
# # 简单的路径搜索函数
# def find_escape_paths(graph, start, safe_exits):
#     """找到从起点到安全出口的所有可能路径"""
#     paths = []
#
#     def dfs(current, path, total_time, visited):
#         if current in safe_exits:
#             paths.append((path.copy(), total_time))
#             return
#
#         for neighbor, time, risk in graph.get(current, []):
#             if neighbor not in visited and risk != float('inf'):
#                 visited.add(neighbor)
#                 dfs(neighbor, path + [neighbor], total_time + time, visited)
#                 visited.remove(neighbor)
#
#     dfs(start, [start], 0, {start})
#     return paths
#
#
# safe_exits = [1, 2]  # 安全出口节点
# escape_paths = find_escape_paths(graph, from_node, safe_exits)
#
# if escape_paths:
#     escape_paths.sort(key=lambda x: x[1])  # 按总时间排序
#     print("可用逃生路径（按时间排序）:")
#     for i, (path, total_time) in enumerate(escape_paths[:3]):  # 显示前3条最佳路径
#         path_str = ' → '.join(map(str, path))
#         print(f"路径{i + 1}: {path_str}, 总时间: {total_time:.1f}秒 ({total_time / 60:.1f}分钟)")
# else:
#     print("警告：未找到安全逃生路径！")
#
# # 7. 关键参数敏感性分析
# print("\n=== 参数敏感性分析 ===")
# base_params = roadways[0]  # 以第一条巷道为例
# Lt_base, S_base, DeltaH_base = base_params[2], base_params[3], base_params[4]
#
# # 测试不同流量下的漫延时间
# test_flows = [30, 50, 70, 100]
# print("不同流量下的漫延时间变化:")
# for flow in test_flows:
#     t, v = calculate_diffusion_time(Lt_base, S_base, DeltaH_base, flow, n)
#     print(f"流量 {flow}m³/min → 漫延时间: {t:.1f}min, 水流速度: {v:.2f}m/s")


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# # 1. 定义参数与公式
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     参数：
#     P: 含水层水压（MPa）
#     h: 开采深度（m）
#     Lf: 断层密度（条/km²）
#     Fs: 支护阻力（kN/m），需转换为MPa·m（1MPa·m=1000kN/m）
#     返回：
#     R: 突水风险值
#     risk_level: 风险等级（低/中/高）
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     # 统一量纲：Fs转换为MPa·m
#     Fs_mpa_m = Fs / 1000
#     # 岩体抗渗力（MPa·m）
#     rock_resist = gamma * h * tan_phi / 1000  # 转换为MPa·m
#     # 风险公式
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))  # 风险值限定在0-1之间
#
#     # 划分风险等级
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# # 2. 实例计算（题目给定参数）
# if __name__ == "__main__":
#     # 设置中文字体
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     # 输入参数列表（可扩展多组参数）
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},
#         {"P": 2.2, "h": 850, "Lf": 4, "Fs": 6500, "roadway": "支巷道1"},
#         {"P": 1.9, "h": 780, "Lf": 2.5, "Fs": 5800, "roadway": "支巷道2"}
#     ]
#
#     # 计算并存储结果
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(
#             P=param["P"],
#             h=param["h"],
#             Lf=param["Lf"],
#             Fs=param["Fs"]
#         )
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     # 转换为DataFrame并保存为Excel
#     df_results = pd.DataFrame(results)
#
#     # 尝试保存Excel，如果失败则保存为CSV
#     try:
#         df_results.to_excel("突水风险预测结果.xlsx", index=False)
#         print("突水风险预测结果已保存为Excel文件！")
#     except Exception as e:
#         df_results.to_csv("突水风险预测结果.csv", index=False, encoding='utf-8-sig')
#         print(f"Excel保存失败，已保存为CSV文件。错误信息: {e}")
#
#     print("计算结果:")
#     print(df_results)
#
#     # 可视化风险分布 - 使用更稳定的绘图方法
#     fig, ax = plt.subplots(figsize=(12, 8))
#
#     x = df_results["巷道名称"]
#     y = df_results["突水风险值"]
#     colors = ["green" if level == "低风险" else "orange" if level == "中风险" else "red"
#               for level in df_results["风险等级"]]
#
#     bars = ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black', width=0.6)
#     ax.axhline(y=0.3, color='gray', linestyle='--', label='低/中风险阈值(0.3)')
#     ax.axhline(y=0.6, color='black', linestyle='--', label='中/高风险阈值(0.6)')
#     ax.set_xlabel("巷道名称", fontsize=12)
#     ax.set_ylabel("突水风险值", fontsize=12)
#     ax.set_title("矿井各巷道突水风险分布", fontsize=14, fontweight='bold')
#     ax.set_ylim(0, 1)
#     ax.legend()
#
#     # 在柱状图上添加数值标签
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
#                 f'{height:.3f}', ha='center', va='bottom', fontsize=10)
#
#     # 添加网格以便更好地读取数值
#     ax.grid(True, axis='y', alpha=0.3, linestyle='-')
#
#     plt.tight_layout()
#
#     # 先保存图片，再尝试显示
#     try:
#         plt.savefig("突水风险分布.png", dpi=300, bbox_inches='tight')
#         print("突水风险分布图已保存为 '突水风险分布.png'！")
#     except Exception as e:
#         print(f"图片保存失败: {e}")
#         # 尝试其他格式
#         try:
#             plt.savefig("突水风险分布.jpg", dpi=300, bbox_inches='tight')
#             print("突水风险分布图已保存为 '突水风险分布.jpg'！")
#         except Exception as e2:
#             print(f"JPG格式保存也失败: {e2}")
#
#     # 尝试显示图形
#     try:
#         plt.show()
#         print("图形已显示")
#     except Exception as e:
#         print(f"图形显示失败: {e}")
#         print("但图形文件已成功保存，请在文件夹中查看")
#
#     # 打印详细分析
#     print("\n" + "=" * 50)
#     print("风险分析报告")
#     print("=" * 50)
#
#     high_risk = df_results[df_results["风险等级"] == "高风险"]
#     medium_risk = df_results[df_results["风险等级"] == "中风险"]
#     low_risk = df_results[df_results["风险等级"] == "低风险"]
#
#     print(f"高风险巷道数量: {len(high_risk)}")
#     if len(high_risk) > 0:
#         print("高风险巷道:", list(high_risk["巷道名称"]))
#
#     print(f"中风险巷道数量: {len(medium_risk)}")
#     if len(medium_risk) > 0:
#         print("中风险巷道:", list(medium_risk["巷道名称"]))
#
#     print(f"低风险巷道数量: {len(low_risk)}")
#     if len(low_risk) > 0:
#         print("低风险巷道:", list(low_risk["巷道名称"]))
#
#     # 参数敏感性分析
#     print("\n" + "=" * 50)
#     print("参数敏感性分析")
#     print("=" * 50)
#
#     base_params = params[0].copy()
#     print(
#         f"基准参数: P={base_params['P']}MPa, h={base_params['h']}m, Lf={base_params['Lf']}条/km², Fs={base_params['Fs']}kN/m")
#     base_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"基准风险值: {base_R:.3f}")
#
#     # 测试水压变化影响
#     test_P = base_params["P"] * 1.2  # 水压增加20%
#     test_R, _ = calculate_risk(test_P, base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"水压增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 测试支护阻力变化影响
#     test_Fs = base_params["Fs"] * 1.2  # 支护阻力增加20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], test_Fs)
#     print(f"支护阻力增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 测试断层密度变化影响
#     test_Lf = base_params["Lf"] * 1.2  # 断层密度增加20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], test_Lf, base_params["Fs"])
#     print(f"断层密度增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     print("\n程序执行完毕！请检查当前目录下的输出文件。")


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import os
# import sys
#
#
# # 1. 定义参数与公式
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     参数：
#     P: 含水层水压（MPa）
#     h: 开采深度（m）
#     Lf: 断层密度（条/km²）
#     Fs: 支护阻力（kN/m），需转换为MPa·m（1MPa·m=1000kN/m）
#     返回：
#     R: 突水风险值
#     risk_level: 风险等级（低/中/高）
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     # 统一量纲：Fs转换为MPa·m
#     Fs_mpa_m = Fs / 1000
#     # 岩体抗渗力（MPa·m）
#     rock_resist = gamma * h * tan_phi / 1000  # 转换为MPa·m
#     # 风险公式
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))  # 风险值限定在0-1之间
#
#     # 划分风险等级
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# # 2. 实例计算（题目给定参数）
# if __name__ == "__main__":
#     # 设置中文字体
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     # 输入参数列表（可扩展多组参数）
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},
#         {"P": 2.2, "h": 850, "Lf": 4, "Fs": 6500, "roadway": "支巷道1"},
#         {"P": 1.9, "h": 780, "Lf": 2.5, "Fs": 5800, "roadway": "支巷道2"}
#     ]
#
#     # 计算并存储结果
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(
#             P=param["P"],
#             h=param["h"],
#             Lf=param["Lf"],
#             Fs=param["Fs"]
#         )
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     # 转换为DataFrame并保存为Excel
#     df_results = pd.DataFrame(results)
#
#     # 尝试保存Excel，如果失败则保存为CSV
#     try:
#         df_results.to_excel("突水风险预测结果.xlsx", index=False)
#         print("突水风险预测结果已保存为Excel文件！")
#     except Exception as e:
#         df_results.to_csv("突水风险预测结果.csv", index=False, encoding='utf-8-sig')
#         print(f"Excel保存失败，已保存为CSV文件。错误信息: {e}")
#
#     print("计算结果:")
#     print(df_results)
#
#     # 可视化风险分布 - 使用非交互式后端
#     try:
#         # 检查是否在可能有图形界面的环境中
#         if hasattr(sys, 'ps1') or 'IPYTHON' in os.environ:
#             # 在交互式环境中，使用默认后端
#             pass
#         else:
#             # 在非交互式环境中，使用非交互式后端
#             plt.switch_backend('Agg')
#             print("使用非交互式后端生成图形...")
#     except:
#         pass
#
#     try:
#         fig, ax = plt.subplots(figsize=(12, 8))
#
#         x = df_results["巷道名称"]
#         y = df_results["突水风险值"]
#         colors = ["green" if level == "低风险" else "orange" if level == "中风险" else "red"
#                   for level in df_results["风险等级"]]
#
#         bars = ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black', width=0.6)
#         ax.axhline(y=0.3, color='gray', linestyle='--', label='低/中风险阈值(0.3)')
#         ax.axhline(y=0.6, color='black', linestyle='--', label='中/高风险阈值(0.6)')
#         ax.set_xlabel("巷道名称", fontsize=12)
#         ax.set_ylabel("突水风险值", fontsize=12)
#         ax.set_title("矿井各巷道突水风险分布", fontsize=14, fontweight='bold')
#         ax.set_ylim(0, 1)
#         ax.legend()
#
#         # 在柱状图上添加数值标签
#         for i, bar in enumerate(bars):
#             height = bar.get_height()
#             ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
#                     f'{height:.3f}', ha='center', va='bottom', fontsize=10)
#
#         # 添加网格以便更好地读取数值
#         ax.grid(True, axis='y', alpha=0.3, linestyle='-')
#
#         plt.tight_layout()
#
#         # 保存图片
#         plt.savefig("突水风险分布.png", dpi=300, bbox_inches='tight')
#         print("突水风险分布图已保存为 '突水风险分布.png'！")
#
#         # 只有在交互式环境中才尝试显示图形
#         if hasattr(sys, 'ps1') or 'IPYTHON' in os.environ:
#             try:
#                 plt.show()
#                 print("图形已显示")
#             except KeyboardInterrupt:
#                 print("图形显示被用户中断")
#             except Exception as e:
#                 print(f"图形显示失败: {e}")
#         else:
#             print("非交互式环境，跳过图形显示")
#             plt.close()  # 关闭图形以释放内存
#
#     except Exception as e:
#         print(f"图形生成失败: {e}")
#
#     # 打印详细分析
#     print("\n" + "=" * 50)
#     print("风险分析报告")
#     print("=" * 50)
#
#     high_risk = df_results[df_results["风险等级"] == "高风险"]
#     medium_risk = df_results[df_results["风险等级"] == "中风险"]
#     low_risk = df_results[df_results["风险等级"] == "低风险"]
#
#     print(f"高风险巷道数量: {len(high_risk)}")
#     if len(high_risk) > 0:
#         print("高风险巷道:", list(high_risk["巷道名称"]))
#
#     print(f"中风险巷道数量: {len(medium_risk)}")
#     if len(medium_risk) > 0:
#         print("中风险巷道:", list(medium_risk["巷道名称"]))
#
#     print(f"低风险巷道数量: {len(low_risk)}")
#     if len(low_risk) > 0:
#         print("低风险巷道:", list(low_risk["巷道名称"]))
#
#     # 参数敏感性分析
#     print("\n" + "=" * 50)
#     print("参数敏感性分析")
#     print("=" * 50)
#
#     base_params = params[0].copy()
#     print(
#         f"基准参数: P={base_params['P']}MPa, h={base_params['h']}m, Lf={base_params['Lf']}条/km², Fs={base_params['Fs']}kN/m")
#     base_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"基准风险值: {base_R:.3f}")
#
#     # 测试水压变化影响
#     test_P = base_params["P"] * 1.2  # 水压增加20%
#     test_R, _ = calculate_risk(test_P, base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"水压增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 测试支护阻力变化影响
#     test_Fs = base_params["Fs"] * 1.2  # 支护阻力增加20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], test_Fs)
#     print(f"支护阻力增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 测试断层密度变化影响
#     test_Lf = base_params["Lf"] * 1.2  # 断层密度增加20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], test_Lf, base_params["Fs"])
#     print(f"断层密度增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     print("\n程序执行完毕！")
#     print("请检查当前目录下的输出文件：")
#     print("- 突水风险预测结果.xlsx (或 .csv)")
#     print("- 突水风险分布.png")

"""
mine_water_inrush_risk_predict.py
矿井突水风险预测程序（含单位校核与可视化）

作者：ChatGPT（GPT-5）
说明：
本程序基于突水风险经验公式实现，可用于矿井巷道不同地段的突水风险评估。
"""

# import math
# import pandas as pd
# import matplotlib.pyplot as plt
#
# def predict_risk(P_mpa, h_m, Lf_per_km2, Fs_kN_per_m,
#                  gamma_kN_per_m3=25.0, phi_deg=35.0, influence_width_m=1.0):
#     """
#     ---------------------------
#     函数说明：
#     计算突水风险预测值 R。
#     ---------------------------
#
#     参数：
#     ----------
#     P_mpa : float
#         含水层水压（MPa）
#     h_m : float
#         开采深度（m）
#     Lf_per_km2 : float
#         断层密度（条/km²）
#     Fs_kN_per_m : float
#         支护阻力（kN/m）
#     gamma_kN_per_m3 : float, default 25.0
#         岩体容重（kN/m³）
#     phi_deg : float, default 35.0
#         岩体内摩擦角（°）
#     influence_width_m : float, default 1.0
#         支护作用影响宽度（m）
#         （用于将Fs换算为kN/m²）
#
#     返回：
#     ----------
#     dict 包含：
#         P_kN_per_m2, k_f, Fs_kN_per_m2, rock_term_kN_per_m2, R_raw, R_clamped
#     """
#     # 单位换算
#     P_kN_per_m2 = P_mpa * 1000.0              # 1 MPa = 1000 kN/m²
#     k_f = 1.0 + 0.2 * Lf_per_km2              # 断层系数
#     phi_rad = math.radians(phi_deg)           # 转为弧度
#
#     # 支护阻力换算到单位面积
#     Fs_kN_per_m2 = Fs_kN_per_m / influence_width_m
#
#     # 岩体项
#     rock_term_kN_per_m2 = gamma_kN_per_m3 * h_m * math.tan(phi_rad)
#
#     # 风险公式
#     numerator = Fs_kN_per_m2 + rock_term_kN_per_m2
#     denominator = P_kN_per_m2 * k_f
#
#     if denominator == 0:
#         R_raw = float('nan')
#     else:
#         R_raw = 1.0 - numerator / denominator
#
#     # 限定范围 [0, 1]
#     R_clamped = max(0.0, min(1.0, R_raw)) if not math.isnan(R_raw) else float('nan')
#
#     return {
#         'P_MPa': P_mpa,
#         'h_m': h_m,
#         'Lf_per_km2': Lf_per_km2,
#         'Fs_kN_per_m': Fs_kN_per_m,
#         'influence_width_m': influence_width_m,
#         'k_f': k_f,
#         'Fs_kN_per_m2': Fs_kN_per_m2,
#         'rock_term_kN_per_m2': rock_term_kN_per_m2,
#         'P_kN_per_m2': P_kN_per_m2,
#         'R_raw': R_raw,
#         'R_clamped': R_clamped
#     }
#
# # 示例参数（可修改）
# example_params = {
#     'P_mpa': 2.0,            # 含水层水压（MPa）
#     'h_m': 800.0,            # 开采深度（m）
#     'Lf_per_km2': 3.0,       # 断层密度（条/km²）
#     'Fs_kN_per_m': 6000.0,   # 支护阻力（kN/m）
#     'influence_width_m': 1.0 # 支护影响宽度（m）
# }
#
# # 计算
# res = predict_risk(**example_params)
#
# # 输出结果表格
# df = pd.DataFrame([res])
# print("\n=== 突水风险预测示例计算结果 ===")
# print(df.round(4))
#
# # 可视化（原始R与裁剪后R）
# plt.figure(figsize=(6, 4))
# plt.bar(['原始R'], [res['R_raw']], color='skyblue', label='R_raw')
# plt.bar(['裁剪后R'], [res['R_clamped']], color='orange', alpha=0.6, label='R_clamped')
# plt.ylabel("风险值 R")
# plt.title("突水风险预测（原始与裁剪后）")
# plt.legend()
# plt.tight_layout()
# plt.show()
#
# # 诊断与建议
# notes = pd.DataFrame([
#     {
#         "问题": "原始 R 值超出 [0,1]",
#         "说明": "表示输入参数或单位存在不一致，或模型参数（如支护影响宽度）需调整。"
#     },
#     {
#         "建议": "确认 Fs 单位是否应为 kN/m²（压力），若为 kN/m，则需提供影响宽度以换算。"
#     },
#     {
#         "示例": "若想得到论文中 R≈0.375 的结果，可调整 influence_width_m 使量纲匹配。"
#     }
# ])
# print("\n=== 诊断与建议 ===")
# print(notes)

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# # 1. 定义突水风险计算公式
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     参数：
#     P: 含水层水压（MPa）
#     h: 开采深度（m）
#     Lf: 断层密度（条/km²）
#     Fs: 支护阻力（kN/m），需转换为MPa·m（1MPa·m=1000kN/m）
#     返回：
#     R: 突水风险值
#     risk_level: 风险等级（低/中/高）
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     # 统一量纲：Fs转换为MPa·m
#     Fs_mpa_m = Fs / 1000
#     # 岩体抗渗力（MPa·m）
#     rock_resist = gamma * h * tan_phi / 1000  # 转换为MPa·m
#     # 风险公式
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))  # 风险值限定在0-1之间
#
#     # 划分风险等级
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# # 2. 主程序
# if __name__ == "__main__":
#     # 设置中文字体
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     # 输入参数列表（可扩展多组参数）
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},
#         {"P": 2.2, "h": 850, "Lf": 4, "Fs": 6500, "roadway": "支巷道1"},
#         {"P": 1.9, "h": 780, "Lf": 2.5, "Fs": 5800, "roadway": "支巷道2"}
#     ]
#
#     # 计算并存储结果
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(
#             P=param["P"],
#             h=param["h"],
#             Lf=param["Lf"],
#             Fs=param["Fs"]
#         )
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     # 转换为DataFrame并保存
#     df_results = pd.DataFrame(results)
#
#     try:
#         df_results.to_excel("突水风险预测结果.xlsx", index=False)
#         print("✅ 突水风险预测结果已保存为 Excel 文件！")
#     except Exception as e:
#         df_results.to_csv("突水风险预测结果.csv", index=False, encoding='utf-8-sig')
#         print(f"⚠️ Excel保存失败，已保存为CSV文件。错误信息: {e}")
#
#     print("\n=== 计算结果 ===")
#     print(df_results)
#
#     # ======== 可视化风险分布 ========
#     plt.figure(figsize=(9, 6))
#     x = np.arange(len(df_results))
#     y = df_results["突水风险值"]
#     labels = df_results["巷道名称"]
#     colors = ["#4CAF50" if level == "低风险" else "#FFC107" if level == "中风险" else "#F44336"
#               for level in df_results["风险等级"]]
#
#     bars = plt.bar(x, y, color=colors, alpha=0.8, width=0.55, edgecolor='black')
#
#     # 添加阈值线与说明
#     plt.axhline(y=0.3, color='gray', linestyle='--', label='低/中风险阈值 (0.3)')
#     plt.axhline(y=0.6, color='black', linestyle='--', label='中/高风险阈值 (0.6)')
#
#     plt.xticks(x, labels, fontsize=11)
#     plt.xlabel("巷道名称", fontsize=12)
#     plt.ylabel("突水风险值", fontsize=12)
#     plt.title("矿井各巷道突水风险分布", fontsize=15, fontweight='bold')
#     plt.ylim(0, 1.05)
#     plt.legend()
#
#     # 优化文字标签位置（防止重叠）
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width() / 2., height + 0.025,
#                  f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
#
#     plt.grid(axis='y', linestyle='--', alpha=0.4)
#     plt.tight_layout()
#
#     try:
#         plt.savefig("突水风险分布优化版.png", dpi=300, bbox_inches='tight')
#         print("✅ 突水风险分布图已保存为 '突水风险分布优化版.png'")
#     except Exception as e:
#         print(f"⚠️ 图片保存失败: {e}")
#
#     plt.show()
#
#     # ======== 打印风险报告 ========
#     print("\n=== 风险分析报告 ===")
#     high_risk = df_results[df_results["风险等级"] == "高风险"]
#     medium_risk = df_results[df_results["风险等级"] == "中风险"]
#     low_risk = df_results[df_results["风险等级"] == "低风险"]
#
#     print(f"高风险巷道数量: {len(high_risk)}")
#     if len(high_risk) > 0:
#         print("高风险巷道:", list(high_risk["巷道名称"]))
#
#     print(f"中风险巷道数量: {len(medium_risk)}")
#     print(f"低风险巷道数量: {len(low_risk)}")
#
#     # ======== 参数敏感性分析 ========
#     print("\n=== 参数敏感性分析 ===")
#     base_params = params[0].copy()
#     print(f"基准参数: P={base_params['P']}MPa, h={base_params['h']}m, Lf={base_params['Lf']}条/km², Fs={base_params['Fs']}kN/m")
#     base_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"基准风险值: {base_R:.3f}")
#
#     # 水压变化影响
#     test_P = base_params["P"] * 1.2  # +20%
#     test_R, _ = calculate_risk(test_P, base_params["h"], base_params["Lf"], base_params["Fs"])
#     print(f"水压增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")
#
#     # 支护阻力变化影响
#     test_Fs = base_params["Fs"] * 1.2  # +20%
#     test_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], test_Fs)
#     print(f"支护阻力增加20% → 风险值: {test_R:.3f} (变化: {test_R - base_R:+.3f})")

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     Fs_mpa_m = Fs / 1000
#     rock_resist = gamma * h * tan_phi / 1000
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))
#
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# if __name__ == "__main__":
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},
#         {"P": 2.2, "h": 850, "Lf": 4, "Fs": 6500, "roadway": "支巷道1"},
#         {"P": 1.9, "h": 780, "Lf": 2.5, "Fs": 5800, "roadway": "支巷道2"}
#     ]
#
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(param["P"], param["h"], param["Lf"], param["Fs"])
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     df_results = pd.DataFrame(results)
#     df_results.to_excel("突水风险预测结果.xlsx", index=False)
#
#     print("=== 计算结果 ===")
#     print(df_results)
#
#     # ===== 可视化部分 =====
#     plt.figure(figsize=(10, 6))
#     x = np.arange(len(df_results))
#     y = df_results["突水风险值"]
#     labels = df_results["巷道名称"]
#
#     colors = []
#     for level in df_results["风险等级"]:
#         if level == "低风险":
#             colors.append("#9FE2BF")  # 浅绿色（更亮）
#         elif level == "中风险":
#             colors.append("#FFC107")  # 橙色
#         else:
#             colors.append("#F44336")  # 红色
#
#     # 绘制背景安全区
#     plt.axhspan(0, 0.3, facecolor='#E0F7E9', alpha=0.6, label='低风险安全区 (R ≤ 0.3)')
#
#     bars = plt.bar(x, y, color=colors, alpha=0.9, width=0.55, edgecolor='black', linewidth=1.2)
#
#     plt.axhline(y=0.3, color='gray', linestyle='--', label='低/中风险阈值 (0.3)')
#     plt.axhline(y=0.6, color='black', linestyle='--', label='中/高风险阈值 (0.6)')
#
#     plt.xticks(x, labels, fontsize=11)
#     plt.xlabel("巷道名称", fontsize=12)
#     plt.ylabel("突水风险值", fontsize=12)
#     plt.title("矿井各巷道突水风险分布", fontsize=15, fontweight='bold')
#     plt.ylim(0, 1.05)
#     plt.legend(loc='upper left')
#
#     # 添加数值标签并凸显低风险
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         level = df_results.iloc[i]["风险等级"]
#         color = "darkgreen" if level == "低风险" else "black"
#         weight = "bold" if level == "低风险" else "normal"
#         plt.text(bar.get_x() + bar.get_width() / 2., height + 0.025,
#                  f'{height:.3f}', ha='center', va='bottom', fontsize=10, color=color, fontweight=weight)
#
#     plt.grid(axis='y', linestyle='--', alpha=0.4)
#     plt.tight_layout()
#
#     plt.savefig("突水风险分布_低风险凸显版.png", dpi=300, bbox_inches='tight')
#     plt.show()
#
#     # ===== 风险分析报告 =====
#     print("\n=== 风险分析报告 ===")
#     high_risk = df_results[df_results["风险等级"] == "高风险"]
#     medium_risk = df_results[df_results["风险等级"] == "中风险"]
#     low_risk = df_results[df_results["风险等级"] == "低风险"]
#
#     print(f"高风险巷道数量: {len(high_risk)}")
#     print(f"中风险巷道数量: {len(medium_risk)}")
#     print(f"低风险巷道数量: {len(low_risk)}")
#     if len(low_risk) > 0:
#         print("低风险巷道:", list(low_risk["巷道名称"]))

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# def calculate_risk(P, h, Lf, Fs):
#     """
#     计算突水风险值
#     """
#     gamma = 25  # 岩体容重（kN/m³）
#     phi = 35  # 岩体摩擦角（°）
#     tan_phi = np.tan(np.radians(phi))
#     kf = 1.0 + 0.2 * Lf  # 断层影响系数
#
#     Fs_mpa_m = Fs / 1000
#     rock_resist = gamma * h * tan_phi / 1000
#     R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
#     R = max(0, min(R, 1))
#
#     if R <= 0.3:
#         risk_level = "低风险"
#     elif 0.3 < R <= 0.6:
#         risk_level = "中风险"
#     else:
#         risk_level = "高风险"
#     return R, risk_level
#
#
# if __name__ == "__main__":
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     # 多组模拟参数（包含低、中、高风险）
#     params = [
#         {"P": 2.0, "h": 800, "Lf": 3, "Fs": 6000, "roadway": "主巷道1"},   # 低
#         {"P": 1.8, "h": 750, "Lf": 2, "Fs": 5500, "roadway": "主巷道2"},   # 低
#         {"P": 2.1, "h": 820, "Lf": 3.5, "Fs": 6000, "roadway": "支巷道3"},  # 中
#         {"P": 2.0, "h": 780, "Lf": 2.8, "Fs": 5900, "roadway": "采区巷道2"}, # 中
#         {"P": 2.5, "h": 900, "Lf": 4.5, "Fs": 5000, "roadway": "主巷道3"},   # 高
#         {"P": 2.8, "h": 950, "Lf": 5, "Fs": 4800, "roadway": "采区巷道1"}   # 高
#     ]
#
#     results = []
#     for param in params:
#         R, risk_level = calculate_risk(param["P"], param["h"], param["Lf"], param["Fs"])
#         results.append({
#             "巷道名称": param["roadway"],
#             "含水层水压(MPa)": param["P"],
#             "开采深度(m)": param["h"],
#             "断层密度(条/km²)": param["Lf"],
#             "支护阻力(kN/m)": param["Fs"],
#             "突水风险值": round(R, 3),
#             "风险等级": risk_level
#         })
#
#     df_results = pd.DataFrame(results)
#     df_results.to_excel("突水风险预测结果_多风险示例.xlsx", index=False)
#
#     print("=== 计算结果 ===")
#     print(df_results)
#
#     # ===== 可视化部分 =====
#     plt.figure(figsize=(10, 6))
#     x = np.arange(len(df_results))
#     y = df_results["突水风险值"]
#     labels = df_results["巷道名称"]
#
#     colors = []
#     for level in df_results["风险等级"]:
#         if level == "低风险":
#             colors.append("#9FE2BF")  # 浅绿
#         elif level == "中风险":
#             colors.append("#FFC107")  # 橙黄
#         else:
#             colors.append("#F44336")  # 红
#
#     # 背景区段
#     plt.axhspan(0, 0.3, facecolor='#E0F7E9', alpha=0.7, label='低风险安全区 (R ≤ 0.3)')
#     plt.axhspan(0.3, 0.6, facecolor='#FFF3E0', alpha=0.6, label='中风险过渡区 (0.3 < R ≤ 0.6)')
#     plt.axhspan(0.6, 1.0, facecolor='#FFEBEE', alpha=0.6, label='高风险警示区 (R > 0.6)')
#
#     bars = plt.bar(x, y, color=colors, alpha=0.9, width=0.55, edgecolor='black', linewidth=1.2)
#
#     plt.axhline(y=0.3, color='gray', linestyle='--')
#     plt.axhline(y=0.6, color='black', linestyle='--')
#
#     plt.xticks(x, labels, fontsize=11)
#     plt.xlabel("巷道名称", fontsize=12)
#     plt.ylabel("突水风险值", fontsize=12)
#     plt.title("矿井各巷道突水风险分布（低中高风险示例）", fontsize=15, fontweight='bold')
#     plt.ylim(0, 1.05)
#     plt.legend(loc='upper left')
#
#     # 添加柱体数值标签
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         level = df_results.iloc[i]["风险等级"]
#         if level == "低风险":
#             color, weight = "darkgreen", "bold"
#         elif level == "中风险":
#             color, weight = "darkorange", "bold"
#         else:
#             color, weight = "darkred", "bold"
#         plt.text(bar.get_x() + bar.get_width() / 2., height + 0.025,
#                  f'{height:.3f}', ha='center', va='bottom',
#                  fontsize=10, color=color, fontweight=weight)
#
#     plt.grid(axis='y', linestyle='--', alpha=0.4)
#     plt.tight_layout()
#     plt.savefig("突水风险分布_多风险凸显版.png", dpi=300, bbox_inches='tight')
#     plt.show()
#
#     # ===== 风险分析报告 =====
#     print("\n=== 风险分析报告 ===")
#     for level in ["高风险", "中风险", "低风险"]:
#         subset = df_results[df_results["风险等级"] == level]
#         print(f"{level}巷道数量: {len(subset)}")
#         if len(subset) > 0:
#             print(f"{level}巷道:", list(subset["巷道名称"]))
#

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calculate_risk(P, h, Lf, Fs):
    """
    计算突水风险值
    """
    gamma = 25  # 岩体容重（kN/m³）
    phi = 35  # 岩体摩擦角（°）
    tan_phi = np.tan(np.radians(phi))
    kf = 1.0 + 0.2 * Lf  # 断层影响系数

    Fs_mpa_m = Fs / 1000
    rock_resist = gamma * h * tan_phi / 1000
    R = 1 - (Fs_mpa_m + rock_resist) / (P * kf)
    R = max(0, min(R, 1))

    if R <= 0.3:
        risk_level = "低风险"
    elif 0.3 < R <= 0.6:
        risk_level = "中风险"
    else:
        risk_level = "高风险"
    return R, risk_level


if __name__ == "__main__":
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # 修正后的参数 - 确保有高风险和低风险
    params = [
        # 高风险示例：高水压、高断层密度、低支护阻力
        {"P": 3.5, "h": 900, "Lf": 5, "Fs": 3000, "roadway": "高风险巷道1"},
        {"P": 3.2, "h": 850, "Lf": 4.5, "Fs": 3500, "roadway": "高风险巷道2"},

        # 中风险示例：中等参数
        {"P": 2.5, "h": 800, "Lf": 3.5, "Fs": 4500, "roadway": "中风险巷道1"},
        {"P": 2.3, "h": 780, "Lf": 3.2, "Fs": 4800, "roadway": "中风险巷道2"},

        # 低风险示例：低水压、低断层密度、高支护阻力
        {"P": 1.5, "h": 700, "Lf": 5, "Fs": 7000, "roadway": "低风险巷道1"},
        {"P": 1.8, "h": 720, "Lf": 8, "Fs": 6500, "roadway": "低风险巷道2"}
    ]

    results = []
    for param in params:
        R, risk_level = calculate_risk(param["P"], param["h"], param["Lf"], param["Fs"])
        results.append({
            "巷道名称": param["roadway"],
            "含水层水压(MPa)": param["P"],
            "开采深度(m)": param["h"],
            "断层密度(条/km²)": param["Lf"],
            "支护阻力(kN/m)": param["Fs"],
            "突水风险值": round(R, 3),
            "风险等级": risk_level
        })

    df_results = pd.DataFrame(results)
    df_results.to_excel("突水风险预测结果_多风险示例.xlsx", index=False)

    print("=== 计算结果 ===")
    print(df_results)

    # ===== 可视化部分 =====
    plt.figure(figsize=(12, 8))
    x = np.arange(len(df_results))
    y = df_results["突水风险值"]
    labels = df_results["巷道名称"]

    colors = []
    for level in df_results["风险等级"]:
        if level == "低风险":
            colors.append("#4CAF50")  # 绿色
        elif level == "中风险":
            colors.append("#FF9800")  # 橙色
        else:
            colors.append("#F44336")  # 红色

    # 背景区段
    plt.axhspan(0, 0.3, facecolor='#E8F5E9', alpha=0.7, label='低风险安全区 (R ≤ 0.3)')
    plt.axhspan(0.3, 0.6, facecolor='#FFF3E0', alpha=0.6, label='中风险过渡区 (0.3 < R ≤ 0.6)')
    plt.axhspan(0.6, 1.0, facecolor='#FFEBEE', alpha=0.6, label='高风险警示区 (R > 0.6)')

    bars = plt.bar(x, y, color=colors, alpha=0.9, width=0.6, edgecolor='black', linewidth=1.2)

    plt.axhline(y=0.3, color='gray', linestyle='--', linewidth=1)
    plt.axhline(y=0.6, color='black', linestyle='--', linewidth=1)

    plt.xticks(x, labels, fontsize=11, rotation=45)
    plt.xlabel("巷道名称", fontsize=12)
    plt.ylabel("突水风险值", fontsize=12)
    plt.title("矿井各巷道突水风险分布（低中高风险示例）", fontsize=15, fontweight='bold')
    plt.ylim(0, 1.05)
    plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)

    # 添加柱体数值标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        level = df_results.iloc[i]["风险等级"]
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                 f'{height:.3f}', ha='center', va='bottom',
                 fontsize=11, fontweight='bold')

    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig("突水风险分布_多风险凸显版.png", dpi=300, bbox_inches='tight')
    plt.show()

    # ===== 风险分析报告 =====
    print("\n=== 风险分析报告 ===")
    for level in ["高风险", "中风险", "低风险"]:
        subset = df_results[df_results["风险等级"] == level]
        print(f"{level}巷道数量: {len(subset)}")
        if len(subset) > 0:
            print(f"{level}巷道: {list(subset['巷道名称'])}")
            print(f"  平均风险值: {subset['突水风险值'].mean():.3f}")
            print(f"  风险范围: {subset['突水风险值'].min():.3f} - {subset['突水风险值'].max():.3f}")
            print()

    # ===== 高风险巷道详细分析 =====
    print("\n=== 高风险巷道详细分析 ===")
    high_risk = df_results[df_results["风险等级"] == "高风险"]
    if len(high_risk) > 0:
        for idx, row in high_risk.iterrows():
            print(f"\n{row['巷道名称']}:")
            print(f"  风险值: {row['突水风险值']}")
            print(f"  水压: {row['含水层水压(MPa)']} MPa")
            print(f"  断层密度: {row['断层密度(条/km²)']} 条/km²")
            print(f"  支护阻力: {row['支护阻力(kN/m)']} kN/m")
            print(f"  开采深度: {row['开采深度(m)']} m")

            # 建议措施
            if row['突水风险值'] > 0.8:
                print("  建议: 立即停止作业，采取紧急支护和排水措施")
            elif row['突水风险值'] > 0.6:
                print("  建议: 加强支护，增加排水设备，密切监测")

    # ===== 参数敏感性分析 =====
    print("\n=== 参数敏感性分析 ===")
    # 以第一个高风险巷道为例
    sample = high_risk.iloc[0] if len(high_risk) > 0 else df_results.iloc[0]
    base_params = {
        "P": sample["含水层水压(MPa)"],
        "h": sample["开采深度(m)"],
        "Lf": sample["断层密度(条/km²)"],
        "Fs": sample["支护阻力(kN/m)"]
    }

    base_R, _ = calculate_risk(base_params["P"], base_params["h"], base_params["Lf"], base_params["Fs"])
    print(f"基准风险值: {base_R:.3f}")

    # 测试不同参数变化的影响
    variations = [
        ("水压降低20%", {"P": base_params["P"] * 0.8}),
        ("水压增加20%", {"P": base_params["P"] * 1.2}),
        ("支护阻力增加30%", {"Fs": base_params["Fs"] * 1.3}),
        ("断层密度减少25%", {"Lf": base_params["Lf"] * 0.75}),
    ]

    for desc, change in variations:
        test_params = base_params.copy()
        test_params.update(change)
        test_R, _ = calculate_risk(**test_params)
        change_percent = (test_R - base_R) / base_R * 100
        print(f"{desc}: 风险值 = {test_R:.3f} (变化: {change_percent:+.1f}%)")

