import os  # 导入操作系统相关模块，用于文件和路径操作
import time  # 导入时间模块，用于记录训练时间
import pandas as pd  # 导入pandas，用于数据处理和存储

from PIL import Image  # 导入PIL库，用于图像处理
from tqdm import tqdm  # 导入tqdm，用于显示训练进度条
from unet_model import *  # 导入自定义的UNet模型（需要在代码外部实现）
from simple_unet_model import *  # 导入自定义的UNet模型
from torch import nn, optim  # 导入PyTorch中的神经网络模块和优化器模块
from torchvision import transforms  # 导入torchvision中的图像转换模块
from matplotlib import pyplot as plt  # 导入matplotlib，用于绘制图形
from torch.utils.data import Dataset, DataLoader  # 导入PyTorch中的数据集和数据加载器模块

train_losses = []  # 用于存储每轮训练的损失值

epoch = 20  # 设定训练的总轮次为
batch_size = 8  # 设置每个batch的大小为
learning_rate = 0.001  # 设置模型学习率
weight_path = ''
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 检查是否有可用GPU，如果有，则使用GPU，否则使用CPU

images_dir = "dataset/Images"  # 定义图像文件夹的路径
masks_dir = "dataset/Masks"  # 定义蒙版文件夹的路径

# 定义图像分割数据集类，继承自PyTorch的Dataset类
class SegmentationDataset(Dataset):
    def __init__(self, images_dir, masks_dir, transform=None):
        # 初始化方法，定义图像和蒙版的路径，并指定可选的transform（数据预处理）
        self.images_dir = images_dir  # 图像文件夹路径
        self.masks_dir = masks_dir  # 蒙版文件夹路径
        self.transform = transform  # 数据预处理操作（如ToTensor等）

        # 获取并排序图像和蒙版的文件列表，确保它们一一对应
        self.image_files = sorted(os.listdir(images_dir))
        self.mask_files = sorted(os.listdir(masks_dir))

    def __len__(self):
        # 返回数据集的长度，即样本数量
        return len(self.image_files)

    def __getitem__(self, idx):
        # 根据索引获取图像和对应的蒙版
        image_path = os.path.join(self.images_dir, self.image_files[idx])  # 获取图像的完整路径
        mask_path = os.path.join(self.masks_dir, self.mask_files[idx])  # 获取蒙版的完整路径

        # 使用PIL库打开图像，保证图像为RGB格式
        image = Image.open(image_path)

        # 使用PIL库打开蒙版图像，并将其转换为灰度模式 ('L' 模式)
        mask = Image.open(mask_path)

        # 如果transform操作存在，则应用在图像和蒙版上
        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        # 返回经过处理的图像和蒙版（图像不需要归一化处理）
        return image, mask


# 定义图像的预处理变换
transform = transforms.Compose([
    transforms.Resize((512, 512)),  # 调整图像和蒙版的大小为 512x512
    transforms.ToTensor(),  # 将图像转换为Tensor类型，数值范围自动缩放至 [0, 1]
])

# 实例化数据集并创建数据加载器
train_dataset = SegmentationDataset(images_dir, masks_dir, transform=transform)
train_dataloader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False)

# 实例化UNet模型并将其移动到相应的设备（GPU或CPU）
# net = UNet().to(device)  #大模型
net = simple_UNet1().to(device)  #小模型

# 定义损失函数为二元交叉熵损失函数
loss_fn = nn.BCELoss().to(device)

# 使用Adam优化器，并设置学习率
opt = optim.Adam(net.parameters(), lr=learning_rate)

# 打印当前使用的设备（CPU或GPU）
print(device)

# 创建一个DataFrame来存储每轮训练的损失值
columns = ['Epoch', 'Train Loss', 'Train Time(s)', 'all time(h)']
training_results = pd.DataFrame(columns=columns)

if os.path.exists(weight_path):
    net.load_state_dict(torch.load(weight_path))
    print('成功加载预训练模型权重')
else:
    print('无预训练权重')

# 记录训练开始时间
all_start_time = time.time()

# 开始训练循环
for i in range(epoch):  # 遍历所有的训练轮次
    print(f"第{i}轮训练开始")

    train_loss = 0  # 初始化每轮的训练损失
    batch_losses = []  # 用于记录每个batch的损失
    start_train_time = time.time()  # 记录当前轮次训练开始的时间

    with tqdm(train_dataloader, unit="batch") as tepoch:  # 使用tqdm显示进度条
        for data in tepoch:
            image, mask = data  # 获取图像和蒙版
            image, mask = image.to(device), mask.to(device)  # 将数据转移到指定的设备
            out_image = net(image)  # 将图像输入到UNet模型中获取输出
            loss = loss_fn(out_image, mask)  # 计算损失
            opt.zero_grad()  # 清除之前的梯度
            loss.backward()  # 反向传播计算梯度
            opt.step()  # 更新模型参数
            train_loss += loss.item()  # 累加损失
            batch_losses.append(loss.item())  # 记录每个batch的损失
            tepoch.set_postfix(loss=train_loss / (tepoch.n + 1))  # 更新进度条的损失信息

    # 计算 batch_losses 的最小值和最大值
    min_loss = max(min(batch_losses), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_loss = max(batch_losses)

    # 绘制每轮训练过程中batch损失的图像
    plt.figure(figsize=(10, 5))
    plt.plot(batch_losses, label='Batch Loss')
    plt.xlabel('Batch')
    plt.ylabel('Loss')
    plt.title(f'Batch Loss for Epoch {i}')
    plt.legend()  # 显示图例
    plt.yscale('log')  # 设置 y 轴为对数尺度
    plt.ylim(min_loss * 0.9, max_loss * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'batch_loss_epoch_{i}.png')  # 保存每轮的batch损失图
    plt.close()  # 关闭图像

    train_loss /= len(train_dataloader)  # 计算每轮的平均训练损失
    train_losses.append(train_loss)  # 保存每轮的损失

    end_train_time = time.time()  # 记录训练结束时间
    train_duration = end_train_time - start_train_time  # 计算训练轮次耗时

    print(f"第{i}轮训练结束，耗时 {train_duration:.2f}秒")
    print(f"训练损失: {train_loss:.6f}")

    # 每轮训练后保存模型的权重
    torch.save(net.state_dict(), f"D:/Python/Text/unet/pt2/UNet_model_{i}.pt")
    print(f"第{i}次模型已保存")

    # 将当前轮次的损失保存到DataFrame中
    training_results = training_results.append({
        'Epoch': i,
        'Train Loss': train_loss,
        'Train Time(s)': train_duration
    }, ignore_index=True)

# 计算总训练时间
all_over_time = time.time()
all_over = all_over_time - all_start_time
print(f"训练总时长，耗时 {all_over/3600:.2f}小时")

# 将训练总时间保存到DataFrame中
training_results = training_results.append({
    'all time(h)': all_over/3600
}, ignore_index=True)

# 保存训练结果到Excel文件
training_results.to_excel('training_results.xlsx', index=False)

# 绘制训练损失图并保存
plt.figure(figsize=(10, 5))  # 设置图形的大小
plt.plot(range(epoch), train_losses, label='Training Loss')  # 绘制训练损失曲线
plt.xlabel('Epoch')  # 设置x轴标签
plt.ylabel('Loss')  # 设置y轴标签
plt.title('Training Loss over Epochs')  # 设置图表标题
plt.legend()  # 显示图例
plt.yscale('log')  # 设置 y 轴为对数尺度
plt.ylim(1e-4, 1)  # 调整 y 轴范围，避免对数尺度下数值溢出
plt.savefig('training_loss.png')  # 保存图表为PNG文件
plt.show()  # 显示训练损失图





# # 示例：获取数据集中的第一个样本，并打印图像和蒙版的形状
# image, mask = dataset[0]
# print(image.shape, mask.shape)  # 输出图像和蒙版的形状