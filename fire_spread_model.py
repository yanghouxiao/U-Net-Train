# import numpy as np  # 导入numpy库，用于数学计算
# import matplotlib.pyplot as plt  # 导入matplotlib库，用于绘图
#
# # 参数设置
# a = 1 / 6 * 1000  # 单元格边长（米），假设为1/6千米
# dt = 3600  # 时间步长（秒），设定为1小时
# W = 5  # 风速等级（风速5级）
# h_humidity = 21  # 湿度（%）
# T = 23.4  # 温度（°C）
# V = 10.0  # 风速（m/s）
# wind_angle = 225  # 风向角度（西北风225度）
# Ks = 1.0  # 可燃物修正因子（云南松）
#
# # 地形参数
# height_map = np.random.rand(50, 50) * 50  # 随机生成一个20x20的高度图，值在0到50米之间
#
# # 公式3计算R0（单位：m/h ），用来表示基础蔓延速度
# R0 = (0.02997 * T + 0.047 * W + 0.009 * (100 - h_humidity) - 0.304) * 1000 / 3600
#
# # 计算指定方向的蔓延速度的函数
# def calculate_R(i, j, di, dj):
#     """计算从(i,j)到(i+di,j+dj)方向的蔓延速度"""
#     # 计算高度差
#     ni, nj = i + di, j + dj  # 目标细胞坐标
#     if ni < 0 or nj < 0 or ni >= 50 or nj >= 50:  # 如果目标细胞越界，返回0
#         return 0
#     h = height_map[ni, nj] - height_map[i, j]  # 高度差
#
#     # 判断是否为对角线方向（次相邻）
#     is_diagonal = (di != 0 and dj != 0)
#
#     # 计算地形修正因子K_phi（公式4/5）
#     if is_diagonal:
#         K_phi = np.exp(3.5339 * (-1) * (abs(h) / (np.sqrt(2) * a)) ** 1.2)  # 次相邻方向的修正因子
#     else:
#         K_phi = np.exp(3.5339 * (-1) * (abs(h) / a) ** 1.2)  # 相邻方向的修正因子
#
#     # 计算风向修正因子K_w（公式6）
#     direction_angle = np.arctan2(di, dj) * 180 / np.pi  # 传播方向的角度（弧度转为度）
#     angle_diff = wind_angle - direction_angle  # 风向与传播方向的角度差
#     K_w = np.exp(0.1783 * V * np.cos(np.deg2rad(angle_diff)))  # 风向的修正因子
#
#     return R0 * Ks * K_w * K_phi  # 返回蔓延速度
#
# # 初始化网格，大小为20x20，初始值为0
# grid_size = 50
# grid = np.zeros((grid_size, grid_size))
# grid[grid_size // 2, grid_size // 2] = 1  # 中心为火源（燃烧状态）
#
# # 定义方向分组，分别为相邻方向和次相邻方向
# adjacent = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上、下、左、右
# diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # 四个对角方向
#
# # 更新火灾蔓延的函数
# def update_fire_spread(grid):
#     new_grid = grid.copy()  # 复制当前网格，用于存放更新后的火灾状态
#     for i in range(grid_size):
#         for j in range(grid_size):
#             if grid[i, j] >= 1:  # 如果该细胞已经完全燃烧，不再传播
#                 continue
#
#             # 步骤1：收集所有可能传播到(i,j)的源细胞
#             max_adjacent = 0
#             max_diagonal = 0
#
#             # 检查相邻的8个方向
#             for dx, dy in adjacent + diagonal:
#                 si, sj = i - dx, j - dy  # 计算源细胞坐标
#                 if 0 <= si < grid_size and 0 <= sj < grid_size:  # 如果源细胞在网格范围内
#                     if grid[si, sj] >= 1:  # 如果源细胞完全燃烧
#                         # 步骤2：计算该方向的蔓延速度R
#                         R = calculate_R(si, sj, dx, dy)
#
#                         # 步骤3：分组记录最大值
#                         if (dx, dy) in adjacent:  # 如果是相邻方向
#                             max_adjacent = max(max_adjacent, R)
#                         else:  # 如果是次相邻方向
#                             max_diagonal = max(max_diagonal, R)
#
#             # 步骤4：按公式7计算贡献
#             if max_adjacent == 0 and max_diagonal == 0:  # 如果没有可传播的方向，跳过
#                 continue
#
#             # 相邻方向贡献（线性项）
#             adj_contribution = (max_adjacent * dt / 60) / a  # dt转换为分钟，单位：每个单位面积的蔓延速度
#
#             # 次相邻方向贡献（平方项）
#             diag_contribution = 0.785 * (max_diagonal * dt / 60) ** 2 / a ** 2  # 0.785为圆形面积修正因子
#
#             # 步骤5：取最大值叠加
#             total_contribution = max(adj_contribution, diag_contribution)  # 选择最大的蔓延贡献
#
#             # 步骤6：更新细胞状态
#             new_grid[i, j] = min(grid[i, j] + total_contribution, 1.0)  # 最大值为1，表示完全燃烧
#
#             # 完全燃烧标记
#             if new_grid[i, j] >= 1:
#                 new_grid[i, j] = 1  # 将完全燃烧的细胞标记为1，后续可标记为2表示已燃尽
#
#     return new_grid  # 返回更新后的网格
#
# # 可视化过程
# plt.figure(figsize=(10, 10))  # 设置绘图窗口大小
#
# for step in range(50):  # 进行50步更新
#     plt.subplot(5, 10, step + 1)  # 将每一步的结果显示在5行10列的子图中
#     plt.imshow(grid, cmap='hot', vmin=0, vmax=1)  # 使用热力图显示火灾蔓延，0为未燃烧，1为完全燃烧
#     plt.title(f"Step {step}")  # 每个子图的标题显示当前步骤
#     grid = update_fire_spread(grid)  # 更新火灾蔓延状态
# plt.tight_layout()  # 调整布局，避免重叠
# plt.show()  # 显示绘制的图形
#


# import numpy as np
# import matplotlib.pyplot as plt
#
# # 参数设置
# a = 1 / 6 * 1000  # 单元格边长（米）
# dt = 3600  # 时间步长（秒）
# W = 5  # 风速等级
# h_humidity = 21  # 湿度（%）
# T = 23.4  # 温度（°C）
# V = 10  # 风速（m/s）
# wind_angle = 225  # 风向角度（西南风，气象学来向）
# Ks = 1  # 可燃物修正因子
#
# # 将风向转换为数学极坐标中的风吹去的方向
# # 步骤1：计算风吹去的方向（气象学角度）
# wind_direction_met = (wind_angle + 180) % 360
# # 步骤2：将气象学角度转换为数学极坐标角度（0度东，逆时针转）
# math_wind_direction = (90 - wind_direction_met) % 360
#
# # 地形参数
# height_map = np.random.rand(50, 50) * 50  # 50x50高度图
#
# # 公式3计算R0
# R0 = (0.02997 * T + 0.047 * W + 0.009 * (100 - h_humidity) - 0.304) * 1000 / 3600
#
# def calculate_R(i, j, di, dj):
#     """计算从源细胞(si,sj)向目标细胞(i+di,j+dj)的蔓延速度"""
#     ni, nj = i + di, j + dj
#     if ni < 0 or nj < 0 or ni >= 50 or nj >= 50:
#         return 0
#     h = height_map[ni, nj] - height_map[i, j]
#
#     is_diagonal = (di != 0 and dj != 0)
#
#     # 地形修正因子K_phi
#     if is_diagonal:
#         distance = np.sqrt(2) * a
#     else:
#         distance = a
#     K_phi = np.exp(3.5339 * (-1) * (abs(h) / distance) ** 1.2)  # 修正：加上缺失的右括号
#
#     # 计算传播方向在数学极坐标中的角度
#     dx_math = dj  # 东方向为x轴正
#     dy_math = -di  # 北方向为y轴正，南为负
#     direction_angle = np.arctan2(dy_math, dx_math) * 180 / np.pi
#     direction_angle = direction_angle % 360  # 转换为0-360度
#
#     # 计算风向修正因子K_w
#     angle_diff = math_wind_direction - direction_angle
#     angle_diff_rad = np.deg2rad(angle_diff)
#     K_w = np.exp(0.1783 * V * np.cos(angle_diff_rad))
#
#     return R0 * Ks * K_w * K_phi
#
# # 初始化网格
# grid_size = 50
# grid = np.zeros((grid_size, grid_size))
# grid[grid_size // 2, grid_size // 2] = 1  # 中心点火
#
# # 方向定义
# adjacent = [(-1, 0), (1, 0), (0, -1), (0, 1)]
# diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
#
# def update_fire_spread(grid):
#     new_grid = grid.copy()
#     for i in range(grid_size):
#         for j in range(grid_size):
#             if grid[i, j] >= 1:
#                 continue
#
#             max_adjacent = 0
#             max_diagonal = 0
#
#             for dx, dy in adjacent + diagonal:
#                 si, sj = i - dx, j - dy
#                 if 0 <= si < grid_size and 0 <= sj < grid_size:
#                     if grid[si, sj] >= 1:
#                         R = calculate_R(si, sj, dx, dy)
#                         if (dx, dy) in adjacent:
#                             max_adjacent = max(max_adjacent, R)
#                         else:
#                             max_diagonal = max(max_diagonal, R)
#
#             if max_adjacent == 0 and max_diagonal == 0:
#                 continue
#
#             adj_contribution = (max_adjacent * dt / 60) / a
#             diag_contribution = 0.785 * (max_diagonal * dt / 60) ** 2 / a ** 2
#             total_contribution = adj_contribution + diag_contribution
#             new_grid[i, j] = min(grid[i, j] + total_contribution, 1.0)
#
#     return new_grid
#
# # 可视化
# plt.figure(figsize=(10, 10))
# for step in range(50):
#     plt.subplot(5, 10, step + 1)
#     plt.imshow(grid, cmap='hot', vmin=0, vmax=1)
#     plt.axis('off')
#     plt.title(f"Step {step}")
#     grid = update_fire_spread(grid)
# plt.tight_layout()
# plt.show()


# import numpy as np  # 导入NumPy库，用于进行高效的数值计算和数组操作
# import matplotlib.pyplot as plt  # 导入Matplotlib的pyplot模块，用于绘制各种类型的图表和数据可视化
# import matplotlib.animation as animation  # 导入Matplotlib的animation模块，用于创建动画效果，如动态更新的图表
#
#
# # 可燃物修正因子
# """
# 扁平针叶：Ks = 0.8
# 枯枝落叶层：KS = 1.2
# 杂草：KS = 1.6
# 柏树/樱桃桦树：KS = 1.8
# 牧场草地：KS = 2.0
# 红松/华山松/云南松：KS = 1.0
# """
#
#
# # 风速等级与风速的大小
# """
# | (W) | Wind speed (m/s) | (W) | Wind speed (m/s) | (W) | Wind speed (m/s) |
# ----------------------------------------------------------------------------
# | 0   | 0.0-0.2          | 6   | 10.8-13.8        | 12  | 32.7-36.9        |
# | 1   | 0.3-1.5          | 7   | 13.9-17.1        | 13  | 37.0-41.4        |
# | 2   | 1.6-3.3          | 8   | 17.2-20.7        | 14  | 41.5-46.1        |
# | 3   | 3.4-5.4          | 9   | 20.8-24.4        | 15  | 46.2-50.9        |
# | 4   | 5.5-7.9          | 10  | 24.5-28.4        | 16  | 51.0-56.0        |
# | 5   | 8.0-10.7         | 11  | 28.5-32.6        | 17  | ≥56.1            |
# """
#
#
# """
# 上北下南，左西右东。
# wind_angle | 风向（极坐标角度，逆时针为正方向）
# ----------------------------------------
#  0+360*n   | 西风（从左朝右吹）
#  45+360*n  | 西南风（从左下朝右上吹）
#  90+360*n  | 南风（从下朝上吹）
#  135+360*n | 东南风（从右下朝左上吹）
#  180+360*n | 东风（从右朝左吹）
#  225+360*n | 西北风（从右上朝左下吹）
#  270+360*n | 北风（从上朝下吹）
#  315+360*n | 东北风（从左上朝右下吹）
# """
#
# # 参数设置
# a = 100  # 单元格边长（米），用于计算距离
# dt = 60  # 时间步长（秒），定义每次更新时间
# W = 5  # 风速等级，风速的等级（这里只是一个初始化的默认值）
# h_humidity = 21  # 湿度（%），空气湿度影响火灾蔓延
# T = 23.4  # 温度（°C），环境温度影响火灾蔓延
# V = 10  # 风速（m/s），风速的大小
# wind_angle = 45  # 风向角度（西南风，气象学角度），影响火灾的蔓延方向
# Ks = 2  # 可燃物修正因子，考虑可燃物特性对蔓延的影响
# map_l = 100  # 定义地图的长度大小为多少
# map_w = 100  # 定义地图的宽度大小为多少
#
# # 将风向转换为数学极坐标中的风吹去的方向，计算风吹去的方向（气象学角度）
# math_wind_direction = (wind_angle) % 360  # 根据气象学角度计算反向风向（% 360将输入的度数控制在0~360度之间）
#
# # 地形参数
# height_map = np.random.rand(map_l, map_w) * 50  # 随机生成的高度地图（0~1的数，经过*50给它放大50倍），影响蔓延速度
#
# # 公式3计算R0
# R0 = (0.02997 * T + 0.047 * W + 0.009 * (100 - h_humidity) - 0.304) * 1000 / 3600  # 基本蔓延速度计算公式（m/s）
#
# def calculate_R(i, j, di, dj):  # i为行值，j为列值。di为上下方向，-1为上，+1为下。dj为左右方向，-1为左，+1为右。
#     """计算从源细胞(si,sj)向目标细胞(i+di,j+dj)的蔓延速度"""
#     ni, nj = i + di, j + dj  # 目标单元格的坐标
#     if ni < 0 or nj < 0 or ni >= map_w or nj >= map_l:  # 边界检查
#         return 0  # 如果目标超出边界，返回0
#     h = height_map[ni, nj] - height_map[i, j]  # 计算高度差
#
#     is_diagonal = (di != 0 and dj != 0)  # 判断是否是对角线方向
#
#     # 地形修正因子K_phi
#     if is_diagonal:
#         distance = np.sqrt(2) * a  # 对角线距离
#     else:
#         distance = a  # 正常水平或垂直距离
#     K_phi = np.exp(3.5339 * (-1) * (abs(h) / distance) ** 1.2)  # 地形修正因子，影响蔓延速度
#
#     # 计算传播方向在数学极坐标中的角度
#     dx_math = dj  # 东方向为x轴正
#     dy_math = -di  # 北方向为y轴正，南为负
#     direction_angle = np.arctan2(dy_math, dx_math) * 180 / np.pi  # 计算方向角度（弧度 / π * 180 = 角度）
#     direction_angle = direction_angle % 360  # 转换为0-360度
#
#     # 计算风向修正因子K_w
#     angle_diff = math_wind_direction - direction_angle  # 风向与蔓延方向的角度差
#     angle_diff_rad = np.deg2rad(angle_diff)  # 转换为弧度
#     K_w = np.exp(0.1783 * V * np.cos(angle_diff_rad))  # 风向修正因子，影响蔓延速度
#
#     return R0 * Ks * K_w * K_phi  # 返回蔓延速度
#
# # 初始化网格
# grid = np.zeros((map_l, map_w))  # 创建一个全零网格
# grid[map_l // 2, map_w // 2] = 1  # 设置网格中心点为火源
#
# # 方向定义
# adjacent = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4个邻近方向：上、下、左、右
# diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # 4个对角线方向：左上、右上、左下、右下
#
# def update_fire_spread(grid):
#     new_grid = grid.copy()  # 创建一个新的网格，用来存储更新后的火势分布
#     for i in range(map_l):
#         for j in range(map_w):
#             if grid[i, j] >= 1:  # 如果当前格子已经有火，跳过
#                 continue
#
#             max_adjacent = 0  # 最大邻近蔓延速度
#             max_diagonal = 0  # 最大对角线蔓延速度
#
#             # 遍历所有邻近和对角线方向
#             for dx, dy in adjacent + diagonal:
#                 si, sj = i - dx, j - dy  # 计算源细胞坐标
#                 if 0 <= si < map_l and 0 <= sj < map_w:  # 边界检查
#                     if grid[si, sj] >= 1:  # 如果源细胞有火
#                         R = calculate_R(si, sj, dx, dy)  # 计算蔓延速度
#                         if (dx, dy) in adjacent:  # 如果是邻近方向
#                             max_adjacent = max(max_adjacent, R)
#                         else:  # 如果是对角线方向
#                             max_diagonal = max(max_diagonal, R)
#
#             if max_adjacent == 0 and max_diagonal == 0:  # 如果没有蔓延速度
#                 continue
#
#             adj_contribution = (max_adjacent * dt ) / a  # 邻近方向的贡献
#             diag_contribution = 0.785 * (max_diagonal * dt ) ** 2 / a ** 2  # 对角线方向的贡献
#             total_contribution = max(adj_contribution, diag_contribution)  # 选择最大的贡献值
#             new_grid[i, j] = min(grid[i, j] + total_contribution, 1.0)  # 更新目标单元格的火势
#
#     return new_grid  # 返回更新后的网格
#
# # 动画更新函数
# def animate(step):
#     global grid  # 使用全局网格变量
#     grid = update_fire_spread(grid)  # 更新火势蔓延
#     ax.clear()  # 清空当前图形
#     ax.imshow(grid, cmap='hot', vmin=0, vmax=1)  # 显示更新后的网格，使用热力图色彩
#     ax.set_title(f"Step {step}")  # 设置标题
#     ax.axis('off')  # 关闭坐标轴
#
# # 创建图形和动画
# fig, ax = plt.subplots(figsize=(10, 10))  # 创建绘图窗口
#
# # 创建动画对象
# # animation.FuncAnimation 用于生成动画
# # fig: 图形对象，表示动画将在该图形中显示
# # animate: 动画更新函数，每帧更新时调用该函数
# # frames=200: 动画的帧数，表示动画将播放 200 帧
# # interval=200: 每帧之间的时间间隔，单位为毫秒，表示每 100 毫秒更新一次帧
# # repeat=False: 动画播放完后不会自动重新开始，设置为 False
# ani = animation.FuncAnimation(fig, animate, frames=100, interval=100, repeat=False)  # 创建动画
#
# # 显示动画
# plt.show()  # 显示图形
#
# # 创建动画对象
# ani = animation.FuncAnimation(fig, animate, frames=100, interval=100)
#
# # 保存动画为MP4
# ani.save('fire_spread_simulation.mp4', writer='ffmpeg', fps=10)
#
# plt.show()


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 可燃物修正因子
# （略，参考你的注释）

# 风速等级与风速大小
# （略，参考你的注释）

# 风向定义
# （略，参考你的注释）

# 参数设置
a = 100  # 单元格边长（米）
dt = 60  # 时间步长（秒）
W = 0  # 风速等级
h_humidity = 21  # 湿度（%）
T = 23.4  # 温度（°C）
V = 0  # 风速（m/s）
wind_angle = 0  # 风向角度（°）
Ks = 2  # 可燃物修正因子
map_l = 100  # 地图长度
map_w = 100  # 地图宽度

# 风向处理
math_wind_direction = (wind_angle) % 360

# 地形
height_map = np.random.rand(map_l, map_w) * 50  # 随机地形高度

# 基础蔓延速度公式
R0 = (0.02997 * T + 0.047 * W + 0.009 * (100 - h_humidity) - 0.304) * 1000 / 3600

def calculate_R(i, j, di, dj):
    """计算从源单元格到目标单元格的蔓延速度"""
    ni, nj = i + di, j + dj
    if ni < 0 or nj < 0 or ni >= map_w or nj >= map_l:
        return 0
    h = height_map[ni, nj] - height_map[i, j]

    is_diagonal = (di != 0 and dj != 0)
    distance = np.sqrt(2) * a if is_diagonal else a
    K_phi = np.exp(3.5339 * (-1) * (abs(h) / distance) ** 1.2)

    dx_math = dj
    dy_math = -di
    direction_angle = np.arctan2(dy_math, dx_math) * 180 / np.pi
    direction_angle = direction_angle % 360

    angle_diff = math_wind_direction - direction_angle
    angle_diff_rad = np.deg2rad(angle_diff)
    K_w = np.exp(0.1783 * V * np.cos(angle_diff_rad))

    return R0 * Ks * K_w * K_phi

# 初始化火源
grid = np.zeros((map_l, map_w))
grid[map_l // 2, map_w // 2] = 1  # 中心点为火源

# 定义方向
adjacent = [(-1, 0), (1, 0), (0, -1), (0, 1)]
diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

def update_fire_spread(grid):
    """更新火势蔓延"""
    new_grid = grid.copy()
    for i in range(map_l):
        for j in range(map_w):
            if grid[i, j] >= 1:
                continue

            max_adjacent = 0
            max_diagonal = 0

            for dx, dy in adjacent + diagonal:
                si, sj = i - dx, j - dy
                if 0 <= si < map_l and 0 <= sj < map_w:
                    if grid[si, sj] >= 1:
                        R = calculate_R(si, sj, dx, dy)
                        if (dx, dy) in adjacent:
                            max_adjacent = max(max_adjacent, R)
                        else:
                            max_diagonal = max(max_diagonal, R)

            if max_adjacent == 0 and max_diagonal == 0:
                continue

            adj_contribution = (max_adjacent * dt) / a
            diag_contribution = 0.785 * (max_diagonal * dt) ** 2 / a ** 2
            total_contribution = max(adj_contribution, diag_contribution)

            new_grid[i, j] = min(grid[i, j] + total_contribution, 1.0)

    return new_grid

# 动画更新函数
def animate(step):
    global grid
    grid = update_fire_spread(grid)
    ax.clear()
    ax.imshow(grid, cmap='hot', vmin=0, vmax=1)
    ax.set_title(f"Step {step}")
    ax.axis('off')

# 创建绘图窗口
fig, ax = plt.subplots(figsize=(10, 10))

# 创建动画
frames = 100  # 动画帧数（可以根据需要调大或调小）
interval = 200  # 每帧时间间隔（毫秒）

ani = animation.FuncAnimation(
    fig, animate, frames=frames, interval=interval, repeat=False
)

# 保存为MP4文件
# 需要安装ffmpeg库: pip install imageio[ffmpeg] 或者系统安装ffmpeg
ani.save('fire_spread_simulation.mp4', writer='ffmpeg', fps=5)

print("动画保存完成！文件名为：fire_spread_simulation.mp4")

