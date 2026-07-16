# import os  # 导入操作系统模块，用于文件路径管理
# import torch  # 导入 PyTorch 库
# import matplotlib  # 导入 Matplotlib 进行设置
# import matplotlib.pyplot as plt  # 导入 Matplotlib 的 pyplot 用于绘图
#
# from PIL import Image  # 导入 PIL（Pillow）用于图像处理
# from unet_model import UNet  # 导入自定义的 U-Net 模型（确保此模块已正确实现）
# from simple_unet_model import *
# from smallest_unet_model import *
# from torchvision import transforms  # 从 torchvision 导入 transforms 进行图像预处理
#
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
#
# # 解决 Matplotlib 中文乱码
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体
# matplotlib.rcParams['axes.unicode_minus'] = False   # 解决 Matplotlib 负号显示问题
#
# # 设备选择（优先使用 GPU，否则使用 CPU）
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# # 加载 U-Net 模型，并将其移动到选定的设备上
# # net = UNet().to(device)
# # net = simple_UNet().to(device)
# net = smallest_UNet().to(device)
#
# # 设定模型权重路径
# weights = 'train/pt7/UNet_student_44.pt'
#
# # 检查权重文件是否存在
# if os.path.exists(weights):
#     net.load_state_dict(torch.load(weights, map_location=device))  # 加载权重
#     print('✅ 成功加载模型权重')  # 打印成功信息
# else:
#     print('❌ 无模型权重')  # 打印错误信息
#     exit()  # 终止程序
#
# # 设置模型为评估模式（推理模式）
# net.eval()
#
# # 读取测试图片
# # 请确保路径正确，如果需要测试其他图片，请修改文件路径
# test_img_path = 'scene_size_judgment_dataset/train/small_scene/fire_image_2_00264.jpg'
# image = Image.open(test_img_path).convert("RGB")  # 以 RGB 模式打开图片
#
# # 定义图像预处理步骤
# transform = transforms.Compose([
#     transforms.Resize((512, 512)),  # 调整图片大小至 512x512
#     transforms.ToTensor(),  # 转换为 PyTorch Tensor 格式
# ])
#
# # 应用预处理，并增加 batch 维度
# input_tensor = transform(image).unsqueeze(0).to(device)
#
# # 进行推理（无梯度计算，提高推理速度）
# with torch.no_grad():
#     output = net(input_tensor)  # 前向传播，获取模型输出
#     print("模型输出最小值:", output.min(), "最大值:", output.max())  # 输出张量的最小值和最大值
#     print(output)
#     output = torch.sigmoid(output)  # 通过 Sigmoid 函数归一化到 0-1 范围
#     print(output)
#     output = output.squeeze().cpu().numpy()  # 去掉 batch 维度，并转换为 NumPy 数组(只有在CPU上才能用Matplotlib)
#     print("student_out min:", output.min().item(), "max:", output.max().item())
#
# # 创建 Matplotlib 图表
# plt.figure(figsize=(12, 5))  # 设置画布大小
#
# # 显示原始输入图片
# plt.subplot(1, 2, 1)  # 创建 1 行 2 列的子图，选择第 1 个
# plt.imshow(image)  # 显示图片
# plt.title("原始图片")  # 设置标题
# plt.axis("off")  # 关闭坐标轴
#
# # 显示模型输出的热力图
# plt.subplot(1, 2, 2)  # 选择第 2 个子图
# plt.imshow(output, cmap="viridis")  # 使用 Viridis 颜色映射显示输出
# plt.colorbar()  # 添加颜色条
# plt.title("经过viridis颜色映射的模型原始输出")  # 设置标题
# plt.axis("off")  # 关闭坐标轴
#
# # 显示最终结果
# plt.show()

# import torch
# from PIL import Image
# import torchvision.transforms as transforms
#
# # 加载图像
# data = Image.open('dataset/Masks/image_0.png')
#
# # 转换为张量
# transform = transforms.ToTensor()
# data = transform(data)
#
# print("无Sigmoid的最小值:", data.min().item(), "最大值:", data.max().item())
#
# # 应用 Sigmoid 操作
# data_sigmoid = torch.sigmoid(data)
#
# # 如果你需要将结果从张量转换回 NumPy 数组，可以使用 .cpu().numpy()
# data_sigmoid_cpu = data_sigmoid.cpu().numpy()
#
# # 输出 Sigmoid 后的结果
# print("Sigmoid后最小值:", data_sigmoid.min().item(), "最大值:", data_sigmoid.max().item())


# import os
# import torch
# import matplotlib
# import matplotlib.pyplot as plt
# from PIL import Image
# from unet_model import UNet
# from simple_unet_model import *
# from smallest_unet_model import *
# from torchvision import transforms
# import numpy as np
#
# # 设置环境变量和 Matplotlib 字体
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# matplotlib.rcParams['axes.unicode_minus'] = False
#
# # 设备选择
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# # 加载模型
# # net = UNet().to(device)
# # net = simple_UNet().to(device)
# net = smallest_UNet().to(device)
#
# weights = 'train/pt7/UNet_student_44.pt'
# if os.path.exists(weights):
#     net.load_state_dict(torch.load(weights, map_location=device))
#     print('✅ 成功加载模型权重')
# else:
#     print('❌ 无模型权重')
#     exit()
#
# net.eval()
#
# # 加载测试图像
# test_img_path = "D:/UE/fire_text/froest/Saved/Screenshots/WindowsEditor/HighresScreenshot00000.png"
# image = Image.open(test_img_path).convert("RGB")
#
# # 图像预处理
# transform = transforms.Compose([
#     transforms.Resize((512, 512)),
#     transforms.ToTensor(),
# ])
# processed_img_tensor = transform(image)
# input_tensor = processed_img_tensor.unsqueeze(0).to(device)
# processed_img_np = processed_img_tensor.permute(1, 2, 0).cpu().numpy()
#
# # 模型推理
# with torch.no_grad():
#     output = net(input_tensor)
#     output = torch.sigmoid(output)
#     output = output.squeeze().cpu().numpy()
#
# # 生成掩膜并统计
# threshold = 0.5007
# mask = (output > threshold).astype(np.uint8)
#
# num_ones = np.sum(mask == 1)
# num_zeros = np.sum(mask == 0)
# total_pixels = mask.size
# fire_ratio = num_ones / total_pixels
# fire_ratio = fire_ratio * 100
#
# print(f"\n📊 掩膜统计：")
# print(f"✅ 掩膜中值为 1 的像素数量（火焰区域）：{num_ones}")
# print(f"✅ 掩膜中值为 0 的像素数量（非火焰区域）：{num_zeros}")
# print(f"🔥 占整个图像的比例：{fire_ratio:.2f}%")
# print(f"🧮 总像素核对：{num_ones + num_zeros} == {total_pixels}\n")
#
# # 可视化：原图、模型输出图、掩膜图
# plt.figure(figsize=(15, 5))
#
# # 原图
# plt.subplot(1, 3, 1)
# plt.imshow(processed_img_np, aspect='equal')
# plt.title("原始图片（512×512）")
# plt.axis("off")
#
# # 模型输出图（热力图）
# plt.subplot(1, 3, 2)
# plt.imshow(output, cmap="viridis", aspect='equal')
# plt.title("模型输出（热力图）")
# plt.axis("off")
#
# # 掩膜图
# plt.subplot(1, 3, 3)
# plt.imshow(mask, cmap="gray", aspect='equal')
# plt.title(f"掩膜图（>{threshold}）")
# plt.axis("off")
#
# plt.tight_layout()
# plt.show()



import os
import torch
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from unet_model import UNet
from simple_unet_model import *
from smallest_unet_model import *
from torchvision import transforms
import numpy as np

# 设置环境变量和 Matplotlib 字体
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 设备选择
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型
# net = UNet().to(device)
# net = simple_UNet().to(device)
net = smallest_UNet().to(device)

weights = 'train/pt8/UNet_student_47.pt'
if os.path.exists(weights):
    net.load_state_dict(torch.load(weights, map_location=device))
    print('✅ 成功加载模型权重')
else:
    print('❌ 无模型权重')
    exit()

net.eval()

# 加载测试图像 - 修复这里：去掉多余的引号
# test_img_path = "D:/UE/fire_text/froest/Saved/MovieRenders/NewLevelSequence1.1238.jpeg"
test_img_path = "D:/Python/Text/forest_fire_size_classification_network/ultralytics-main/yangnet/forest_fire_size_classification_dataset_detail/train/bigscene_bigfire/bigscene_bigfire_0000.jpg"
# 或者使用原始字符串：
# test_img_path = r"D:\UE\fire_text\froest\Saved\Screenshots\WindowsEditor\HighresScreenshot00000.png"

# 检查文件是否存在
if not os.path.exists(test_img_path):
    print(f'❌ 文件不存在: {test_img_path}')
    exit()

image = Image.open(test_img_path).convert("RGB")

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
])
processed_img_tensor = transform(image)
input_tensor = processed_img_tensor.unsqueeze(0).to(device)
processed_img_np = processed_img_tensor.permute(1, 2, 0).cpu().numpy()

# 模型推理
with torch.no_grad():
    output = net(input_tensor)
    output = torch.sigmoid(output)
    output = output.squeeze().cpu().numpy()

# 生成掩膜并统计
threshold = 0.5007
mask = (output > threshold).astype(np.uint8)

num_ones = np.sum(mask == 1)
num_zeros = np.sum(mask == 0)
total_pixels = mask.size
fire_ratio = num_ones / total_pixels
fire_ratio = fire_ratio * 100

print(f"\n📊 掩膜统计：")
print(f"✅ 掩膜中值为 1 的像素数量（火焰区域）：{num_ones}")
print(f"✅ 掩膜中值为 0 的像素数量（非火焰区域）：{num_zeros}")
print(f"🔥 占整个图像的比例：{fire_ratio:.2f}%")
print(f"🧮 总像素核对：{num_ones + num_zeros} == {total_pixels}\n")

# 可视化：原图、模型输出图、掩膜图
plt.figure(figsize=(15, 5))

# 原图
plt.subplot(1, 3, 1)
plt.imshow(processed_img_np, aspect='equal')
plt.title("原始图片（512×512）")
plt.axis("off")

# 模型输出图（热力图）
plt.subplot(1, 3, 2)
plt.imshow(output, cmap="viridis", aspect='equal')
plt.title("模型输出（热力图）")
plt.axis("off")

# 掩膜图
plt.subplot(1, 3, 3)
plt.imshow(mask, cmap="gray", aspect='equal')
plt.title(f"掩膜图（>{threshold}）")
plt.axis("off")

plt.tight_layout()
plt.show()





