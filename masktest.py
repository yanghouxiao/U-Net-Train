# from PIL import Image
# import numpy as np
#
# # 加载掩膜图像，并转换为灰度模式（如果它不是的话）
# mask = Image.open('C:/Users/yanghouxiao/Desktop/1/28_860221784_json/label.png').convert('L')
#
# # 将图像转换为numpy数组
# mask_array = np.array(mask)
#
# # 计算像素值为0和1的数量
# count_0 = np.sum(mask_array == 0)
# count_1 = np.sum(mask_array == 1)
#
# print(f"Pixel value 0 count: {count_0}")
# print(f"Pixel value 1 count: {count_1}")


# from PIL import Image
# import numpy as np
#
#
# def count_pixel_values(image_path):
#     """
#     统计给定图像中每个像素值的出现次数。
#
#     :param image_path: 图像文件的路径
#     """
#     # 打开图像并转换为灰度模式（如果需要处理多通道图像，则省略.convert('L')）
#     mask = Image.open(image_path).convert('L')
#
#     # 将图像转换为numpy数组
#     mask_array = np.array(mask)
#
#     # 获取所有唯一的像素值及其对应的计数
#     unique, counts = np.unique(mask_array, return_counts=True)
#
#     # 创建一个字典来存储每个像素值及其出现次数
#     pixel_value_counts = dict(zip(unique, counts))
#
#     return pixel_value_counts
#
#
# # 示例用法
# image_path = 'C:/Users/yanghouxiao/Desktop/1/28_860221784_json/label.png'  # 替换为你的掩膜图像路径
# pixel_value_counts = count_pixel_values(image_path)
#
# # 输出每个像素值及其出现次数
# for pixel_value, count in sorted(pixel_value_counts.items()):
#     print(f"Pixel value {pixel_value}: {count} occurrences")


# from PIL import Image
# import numpy as np
# import matplotlib.pyplot as plt
#
# def visualize_mask(mask_array):
#     """简单地将前四个类别映射到颜色以供可视化"""
#     colors = np.zeros((*mask_array.shape, 3), dtype=np.uint8)
#     # 背景(0): 黑色
#     colors[mask_array == 0] = [0, 0, 0]
#     # 类别38: 红色
#     colors[mask_array == 1] = [255, 0, 0]
#     # 类别75: 绿色
#     colors[mask_array == 75] = [0, 255, 0]
#     # 类别113: 蓝色
#     colors[mask_array == 113] = [0, 0, 255]
#
#     plt.imshow(colors)
#     plt.axis('off')
#     plt.show()
#
# # 假设你已经有了mask_array
# # mask_array = np.array(Image.open('your_mask.png').convert('L'))
#
# # 如果你想直接从图像路径开始
# image_path = 'D:/Python/Text/unet/dataset/Masks/image_0.png'  # 替换为你的掩膜图像路径
# mask = Image.open(image_path).convert('L')
# mask_array = np.array(mask)
#
# visualize_mask(mask_array)


# from PIL import Image
# import numpy as np
# import matplotlib.pyplot as plt
#
#
# def visualize_overlay(image_path, mask_path):
#     """
#     将原始图像和掩膜叠加显示
#     """
#     # 加载原始图像
#     image = Image.open(image_path).convert('RGB')  # 确保是RGB模式
#     image_array = np.array(image)
#
#     # 加载掩膜图像
#     mask = Image.open(mask_path).convert('L')  # 确保是灰度模式
#     mask_array = np.array(mask)
#
#     # 创建一个与原图同样大小的彩色掩膜
#     overlay = np.zeros_like(image_array)
#
#     # 根据掩膜值设置颜色
#     # 注意：这里根据你之前的统计结果调整了类别
#     # 类别1 (火焰): 红色
#     overlay[mask_array == 1] = [255, 0, 0]  # 红色
#     # 类别75: 绿色 (如果需要显示)
#     # overlay[mask_array == 75] = [0, 255, 0]  # 绿色
#     # 类别113: 蓝色 (如果需要显示)
#     # overlay[mask_array == 113] = [0, 0, 255]  # 蓝色
#
#     # 创建图形和轴
#     fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
#
#     # 显示原始图像
#     ax1.imshow(image_array)
#     ax1.set_title('Original Image')
#     ax1.axis('off')
#
#     # 显示掩膜（转换为彩色以便查看）
#     mask_color = np.zeros((*mask_array.shape, 3), dtype=np.uint8)
#     mask_color[mask_array == 1] = [255, 0, 0]  # 火焰-红色
#     mask_color[mask_array == 75] = [0, 255, 0]  # 绿色
#     mask_color[mask_array == 113] = [0, 0, 255]  # 蓝色
#     ax2.imshow(mask_color)
#     ax2.set_title('Mask (Colored)')
#     ax2.axis('off')
#
#     # 显示叠加效果
#     ax3.imshow(image_array)
#     ax3.imshow(overlay, alpha=0.5)  # alpha控制透明度
#     ax3.set_title('Overlay (Original + Mask)')
#     ax3.axis('off')
#
#     plt.tight_layout()
#     plt.show()
#
#
# # 定义路径
# image_dir = 'D:/Python/Text/unet/dataset/Images/'
# mask_dir = 'D:/Python/Text/unet/dataset/Masks/'
#
# # 图像编号
# img_num = 0  # 对应 image_0.png
#
# # 构建完整路径
# image_path = f"{image_dir}image_{img_num}.jpg"
# mask_path = f"{mask_dir}image_{img_num}.png"
#
# # 执行可视化
# visualize_overlay(image_path, mask_path)


from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def visualize_overlay(image_path, mask_path):
    """
    将原始图像和掩膜叠加显示，采用竖向排列展示
    """
    # 加载原始图像
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)

    # 加载掩膜图像
    mask = Image.open(mask_path).convert('L')
    mask_array = np.array(mask)

    # 创建一个与原图同样大小的彩色掩膜
    overlay = np.zeros_like(image_array)
    overlay[mask_array == 1] = [255, 0, 0]

    # 彩色掩膜图（用于展示）
    mask_color = np.zeros((*mask_array.shape, 3), dtype=np.uint8)
    mask_color[mask_array == 1] = [255, 0, 0]
    mask_color[mask_array == 75] = [0, 255, 0]
    mask_color[mask_array == 113] = [0, 0, 255]

    # 创建图形和子图（3行1列）
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 20))

    # 原图
    ax1.imshow(image_array)
    ax1.set_title('Original Image', fontsize=16)
    ax1.axis('off')

    # 掩膜
    ax2.imshow(mask_color)
    ax2.set_title('Mask (Colored)', fontsize=16)
    ax2.axis('off')

    # 叠加图
    ax3.imshow(image_array)
    ax3.imshow(overlay, alpha=0.5)
    ax3.set_title('Overlay (Original + Mask)', fontsize=16)
    ax3.axis('off')

    # 调整子图间距，防止标题被遮挡
    plt.subplots_adjust(hspace=0.3)
    plt.show()


# 路径定义
image_dir = 'D:/Python/Text/unet/dataset/Images/'
mask_dir = 'D:/Python/Text/unet/dataset/Masks/'
img_num = 0

image_path = f"{image_dir}image_{img_num}.jpg"
mask_path = f"{mask_dir}image_{img_num}.png"

visualize_overlay(image_path, mask_path)




