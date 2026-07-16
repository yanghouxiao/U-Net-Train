import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from matplotlib.widgets import Button
import matplotlib.animation as animation

class OceanCurrentsVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(16, 10))
        self.current_season = "summer"
        self.arrows = []  # 保存箭头对象
        self.setup_map()
        self.setup_controls()
        self.setup_currents_data()

    def setup_map(self):
        """使用 Basemap 绘制地图"""
        self.ax = self.fig.add_subplot(111)

        # Robinson 投影
        self.m = Basemap(projection='robin', lon_0=0, resolution='c')

        # 海陆颜色
        self.m.drawmapboundary(fill_color='#1a2639')
        self.m.fillcontinents(color='#2d3740', lake_color='#1a2639')

        # 海岸线 & 国界
        self.m.drawcoastlines(linewidth=0.5, color='white')
        self.m.drawcountries(linewidth=0.3, color='white')

        # 网格线
        self.m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0], color='gray', dashes=[1, 3], alpha=0.4)
        self.m.drawmeridians(np.arange(-180, 181, 60), labels=[0, 0, 0, 1], color='gray', dashes=[1, 3], alpha=0.4)

        plt.title("全球洋流系统可视化（Basemap 版本）", fontsize=16, fontweight='bold')

    def setup_controls(self):
        ax_summer = plt.axes([0.15, 0.02, 0.12, 0.04])
        ax_winter = plt.axes([0.28, 0.02, 0.12, 0.04])
        ax_anim = plt.axes([0.41, 0.02, 0.12, 0.04])

        self.btn_summer = Button(ax_summer, '夏季模式', color='#ff6b6b')
        self.btn_winter = Button(ax_winter, '冬季模式', color='#4ecdc4')
        self.btn_anim = Button(ax_anim, '动画演示', color='#45b7d1')

        self.btn_summer.on_clicked(self.set_summer)
        self.btn_winter.on_clicked(self.set_winter)
        self.btn_anim.on_clicked(self.toggle_animation)

    def setup_currents_data(self):
        """洋流数据（经纬度）"""
        self.currents = {
            'kuroshio': {
                'name': '黑潮',
                'type': 'warm',
                'path': np.array([[15, 120], [25, 130], [35, 140], [40, 150], [45, 160]]),
                'width': 3
            },
            'north_pacific': {
                'name': '北太平洋暖流',
                'type': 'warm',
                'path': np.array([[35, 140], [40, 160], [45, -170], [50, -160], [45, -140]]),
                'width': 2.5
            },
            'california': {
                'name': '加州寒流',
                'type': 'cold',
                'path': np.array([[40, -125], [35, -120], [30, -115], [25, -110]]),
                'width': 2
            },
            'peru': {
                'name': '秘鲁寒流',
                'type': 'cold',
                'path': np.array([[-5, -80], [-10, -75], [-15, -70], [-20, -65]]),
                'width': 2
            },
            'east_aus': {
                'name': '东澳暖流',
                'type': 'warm',
                'path': np.array([[-35, 155], [-30, 155], [-25, 155]]),
                'width': 2
            },
            'gulf': {
                'name': '墨西哥湾暖流',
                'type': 'warm',
                'path': np.array([[20, -85], [25, -80], [30, -75], [35, -70], [40, -65]]),
                'width': 3.5
            },
            'lab': {
                'name': '拉布拉多寒流',
                'type': 'cold',
                'path': np.array([[60, -60], [55, -55], [50, -50], [45, -45]]),
                'width': 2
            }
        }

        self.indian_currents = {
            'summer': {
                'path': np.array([[5, 65], [10, 70], [15, 75], [20, 80], [15, 85], [10, 80], [5, 75]]),
                'width': 2.5
            },
            'winter': {
                'path': np.array([[5, 75], [10, 80], [15, 85], [20, 80], [15, 75], [10, 70], [5, 65]]),
                'width': 2.5
            }
        }

    def clear_currents(self):
        """删除洋流线和箭头，保留地图底图"""
        for line in list(self.ax.lines):
            line.remove()
        for arrow in self.arrows:
            arrow.remove()
        self.arrows = []

    def draw_currents(self):
        """清理 & 重画所有洋流"""
        self.clear_currents()

        # 主洋流
        for cid, cur in self.currents.items():
            self.draw_single_current(cur['path'], cur['type'], cur['width'])

        # 季节性洋流
        self.draw_single_current(
            self.indian_currents[self.current_season]['path'],
            'seasonal',
            2.5
        )

        plt.draw()

    def draw_single_current(self, path, ctype, width):
        """绘制单条洋流线（Basemap 投影）"""
        lats, lons = path[:, 0], path[:, 1]
        x, y = self.m(lons, lats)

        if ctype == 'warm':
            color = '#ff6b6b'
        elif ctype == 'cold':
            color = '#4ecdc4'
        else:
            color = '#a855f7'

        self.ax.plot(x, y, color=color, linewidth=width, alpha=0.9)

        # 添加箭头（取中点）
        if len(x) >= 2:
            mid = len(x) // 2
            arrow = self.ax.annotate(
                '', xy=(x[mid], y[mid]), xytext=(x[mid-1], y[mid-1]),
                arrowprops=dict(arrowstyle='->', color=color, lw=width * 0.8)
            )
            self.arrows.append(arrow)

    def set_summer(self, event):
        self.current_season = 'summer'
        self.draw_currents()
        plt.title("全球洋流 - 夏季模式")

    def set_winter(self, event):
        self.current_season = 'winter'
        self.draw_currents()
        plt.title("全球洋流 - 冬季模式")

    def toggle_animation(self, event):
        self.animate_currents()

    def animate_currents(self):
        def update(frame):
            alpha = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(frame * 0.3))
            self.draw_currents()

            # 调整透明度增强流动效果
            for line in self.ax.lines:
                line.set_alpha(alpha)

            return self.ax.lines

        animation.FuncAnimation(self.fig, update, frames=30, interval=200, blit=False)

    def show(self):
        self.draw_currents()
        plt.tight_layout()
        plt.show()


def main():
    print("正在启动洋流可视化…")
    vis = OceanCurrentsVisualizer()
    vis.show()


if __name__ == "__main__":
    main()


