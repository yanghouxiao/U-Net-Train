import os
import time
import pandas as pd
from tqdm import tqdm
from PIL import Image
from scenesize_model import *
from Resnet_model import *
import matplotlib.pyplot as plt
from smallest_unet_model import *
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader

# 设置训练参数
size = 640  #设置输入图片尺寸
epoch = 100  # 设置训练轮数
batch_size = 16  # 设置每个批次的样本数量
num_classes = 4  #设置模型输出的类别数
threshold = 0.5007  #设置UNet网络的二值化阈值
weight_decay = 0.0001  # L2正则化系数λ（adam中）
learning_rate = 0.001  # 设置Adam优化器的学习率
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 检查是否有可用GPU，如果有则使用GPU，否则使用CPU

# 用于记录每轮的训练和测试损失，以及准确率
train_losses = []  # 存储每轮训练的损失
test_losses = []  # 存储每轮测试的损失
train_accuracies = []  # 存储每轮训练的准确率
test_accuracies = []  # 存储每轮测试的准确率

# 设备选择（优先使用 GPU，否则使用 CPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载 U-Net 模型，并将其移动到选定的设备上
net_UNet = smallest_UNet().to(device)
net_SceneSize = scenesize_model().to(device)

# 设定模型权重路径
weights_unet = 'train/pt7/UNet_student_44.pt'
weights_scenesize = 'train/size_pt/size_model_8.pt'

# 检查权重文件是否存在
if os.path.exists(weights_unet):
    net_UNet.load_state_dict(torch.load(weights_unet, map_location=device))  # 加载权重
    print('✅ 成功加载UNet模型权重')  # 打印成功信息
else:
    print('❌ 无UNet模型权重')  # 打印错误信息
    exit()  # 终止程序

# 检查权重文件是否存在
if os.path.exists(weights_scenesize):
    net_SceneSize.load_state_dict(torch.load(weights_scenesize, map_location=device))  # 加载权重
    print('✅ 成功加载SceneSize模型权重')  # 打印成功信息
else:
    print('❌ 无SceneSize模型权重')  # 打印错误信息
    exit()  # 终止程序

# 设置模型为评估模式（推理模式）
net_UNet.eval()
net_SceneSize.eval()

# 自定义数据集类：支持四分类（Small_fire, Mid_fire, Big_fire, No_fire）
class Firedata(Dataset):
    def __init__(self, root_dir, label_dir, transform=None):
        """
        初始化数据集，传入图片的根目录路径、类别目录名和transform操作。
        """
        self.root_dir = root_dir  # 图片根目录路径
        self.label_dir = label_dir  # 当前类别的目录名
        self.path = os.path.join(self.root_dir, self.label_dir)  # 类别文件夹路径
        self.img_path = os.listdir(self.path)  # 类别目录下所有图片文件名
        self.transform = transform  # 数据增强或变换操作

        # 类别映射：可根据需要自行调整顺序和对应标签
        self.label_map = {
            "No_fire": 0,
            "Small_fire": 1,
            "Mid_fire": 2,
            "Big_fire": 3
        }

    def __getitem__(self, idx):
        """
        根据索引返回一张图片及其对应的标签。
        """
        img_name = self.img_path[idx]
        img_item_path = os.path.join(self.root_dir, self.label_dir, img_name)
        img = Image.open(img_item_path).convert("RGB")  # 确保是RGB图像

        label = self.label_map[self.label_dir]  # 根据目录名确定标签

        if self.transform:
            img = self.transform(img)

        return img, torch.tensor(label, dtype=torch.long)  # 用于分类任务的标签推荐使用 long 类型

    def __len__(self):
        return len(self.img_path)

# 设置训练集和测试集的根目录路径以及标签目录路径
train_root_dir = "yangnet_dataset/train"  # 训练集根目录路径
test_root_dir = "yangnet_dataset/test"  # 测试集根目录路径
Small_fire_label_dir = "Small_fire"  # 火灾类别目录
Mid_fire_label_dir = "Mid_fire"
Big_fire_label_dir = "Big_fire"
nofire_label_dir = "No_fire"  # 非火灾类别目录

# 定义图像转换操作，将图片转换为Tensor格式并归一化到 [0, 1]
transform_compose_rescale = transforms.Compose([
    transforms.Resize((size, size)),   # 调整图像大小为640x640
    transforms.ToTensor(),  # 将图片转换为Tensor，并自动将像素值归一化到 [0, 1]
])

# 定义训练集的数据增强操作
train_transform = transforms.Compose([
    transforms.Resize((size, size)),   # 调整图像大小为640x640
    transforms.RandomHorizontalFlip(),  # 随机水平翻转
    transforms.RandomRotation(15),  # 随机旋转最大15度
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),  # 随机改变亮度、对比度、饱和度和色调
    transforms.ToTensor(),  # 将图片转换为Tensor，并自动将像素值归一化到 [0, 1]
])

# 创建训练集数据集对象，应用数据增强
train_small_fire_dataset = Firedata(train_root_dir, Small_fire_label_dir, transform=train_transform)
train_mid_fire_dataset = Firedata(train_root_dir, Mid_fire_label_dir, transform=train_transform)
train_big_fire_dataset = Firedata(train_root_dir, Big_fire_label_dir, transform=train_transform)
train_nofire_dataset = Firedata(train_root_dir, nofire_label_dir, transform=train_transform)

# 创建测试集数据集对象，测试集不做数据增强，只进行标准化
test_small_fire_dataset = Firedata(test_root_dir, Small_fire_label_dir, transform=transform_compose_rescale)
test_mid_fire_dataset = Firedata(test_root_dir, Mid_fire_label_dir, transform=transform_compose_rescale)
test_big_fire_dataset = Firedata(test_root_dir, Big_fire_label_dir, transform=transform_compose_rescale)
test_nofire_dataset = Firedata(test_root_dir, nofire_label_dir, transform=transform_compose_rescale)

# 合并训练集和测试集数据集
train_dataset = train_small_fire_dataset + train_mid_fire_dataset + train_big_fire_dataset + train_nofire_dataset  # 合并训练集中的火灾和非火灾数据
test_dataset = test_small_fire_dataset + test_mid_fire_dataset + test_big_fire_dataset + test_nofire_dataset  # 合并测试集中的火灾和非火灾数据

# DataLoader，用于批量加载数据
train_dataloder = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False)
test_dataloder = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=False)

# 实例化网络模型
fire_model = FireClassificationModel(net_UNet, net_SceneSize, num_classes, threshold).to(device)

# 损失函数：交叉熵损失函数
loss_fn = nn.CrossEntropyLoss().to(device)

# 优化器：Adam优化器
optimizer = torch.optim.Adam(fire_model.parameters(), lr=learning_rate, weight_decay=weight_decay)

print(device)

# 创建一个DataFrame来存储每轮的损失和准确率
columns = ['Epoch', 'Train Loss', 'Train Accuracy', 'Test Loss', 'Test Accuracy']
training_results = pd.DataFrame(columns=columns)

#定义训练开始的时间（用于计算最后的总时间）
all_start_time = time.time()

# 训练循环
for i in range(epoch):  # 遍历所有的训练轮次
    print(f"第{i}轮训练开始")

    # 训练阶段
    train_loss = 0  # 初始化每轮的训练损失
    train_accuracy = 0  # 初始化每轮的训练准确率

    correct_train = 0  # 累计预测正确的数量
    total_train = 0  # 累计样本总数

    fire_model.train()  # 将模型设置为训练模式
    start_train_time = time.time()  # 记录训练开始时间
    with tqdm(train_dataloder, unit="batch") as tepoch:  # 使用tqdm显示训练进度条
        for data in tepoch:
            imgs, labels = data  # 获取当前批次的图像数据和标签
            imgs, labels = imgs.to(device), labels.to(device)  # 将数据移到GPU或CPU

            optimizer.zero_grad()  # 清空梯度
            outputs = fire_model(imgs)  # 模型前向传播
            loss = loss_fn(outputs, labels)  # 计算损失
            loss.backward()  # 反向传播计算梯度
            optimizer.step()  # 更新模型参数

            train_loss += loss.item()  # 累加训练损失

            _, predicted = torch.max(outputs.data, 1)  # 获得最大概率的类别索引
            batch_total_train = labels.size(0)  # 当前batch样本数量
            batch_correct_train = (predicted == labels).sum().item()  # 当前batch预测正确数
            batch_acc_train = 100. * batch_correct_train / batch_total_train  # 当前batch准确率（百分比）

            # 同时累加整个epoch的正确数和样本总数
            correct_train += batch_correct_train
            total_train += batch_total_train

            tepoch.set_postfix(train_loss=loss.item(), batch_acc_train=batch_acc_train, epoch_acc=100. * correct_train / total_train)  # 更新进度条，显示当前的损失和准确率

    end_train_time = time.time()  # 记录训练结束时间

    train_duration = end_train_time - start_train_time  # 计算训练轮次耗时

    print(f"第{i}轮训练结束，耗时 {train_duration:.2f}秒")

    train_loss /= len(train_dataloder)  # 当前轮次训练平均损失
    train_losses.append(train_loss)  # 保存每轮的损失

    train_accuracy = 100. * correct_train / total_train  # 当前轮次训练准确率
    train_accuracies.append(train_accuracy)  # 保存每轮的损失

    print(f"训练损失: {train_loss:.6f}")
    print(f"训练准确率: {train_accuracy:.6f}%")

    # 每轮训练后保存模型的权重
    torch.save(fire_model.state_dict(), f"D:/Python/Text/unet/train/yangnet_pt/fire_model_{i}.pt")
    print(f"第{i}次模型已保存")

    # 测试阶段
    test_loss = 0  # 初始化每轮的测试损失
    test_accuracy = 0  # 初始化每轮的测试准确率

    correct_test = 0  # 累计预测正确的数量
    total_test = 0  # 累计样本总数

    fire_model.eval()  # 设置为评估模式（不启用Dropout、BatchNorm）
    start_test_time = time.time()  # 记录测试开始时间

    with torch.no_grad():  # 禁用梯度计算，提高推理速度，节省显存
        with tqdm(test_dataloder, unit="batch") as tepoch:
            for data in tepoch:
                imgs, labels = data  # 获取当前批次的图像数据和标签
                imgs, labels = imgs.to(device), labels.to(device)  # 移动到设备

                outputs = fire_model(imgs)  # 模型前向传播
                loss = loss_fn(outputs, labels)  # 计算损失
                test_loss += loss.item()  # 累加测试损失

                _, predicted = torch.max(outputs.data, 1)  # 获取最大概率的类别索引
                batch_total_test = labels.size(0)  # 当前batch样本数量
                batch_correct_test = (predicted == labels).sum().item()  # 当前batch预测正确数
                batch_acc_test = 100. * batch_correct_test / batch_total_test  # 当前batch准确率（百分比）

                correct_test += batch_correct_test
                total_test += batch_total_test

                tepoch.set_postfix(test_loss=loss.item(), batch_acc_test=batch_acc_test, epoch_acc=100. * correct_test / total_test)

    end_test_time = time.time()  # 记录测试结束时间

    test_duration = end_test_time - start_test_time  # 计算测试轮次耗时

    print(f"第{i}轮测试结束，耗时 {test_duration:.2f}秒")

    test_loss /= len(test_dataloder)  # 当前轮次测试平均损失
    test_losses.append(test_loss)  # 保存每轮的测试损失

    test_accuracy = 100. * correct_test / total_test  # 当前轮次测试准确率
    test_accuracies.append(test_accuracy)  # 保存每轮的测试准确率

    print(f"测试损失: {test_loss:.6f}")
    print(f"测试准确率: {test_accuracy:.6f}%")

    # scheduler.step(test_loss)  # 根据测试损失调整学习率

    # 保存每轮的结果到DataFrame
    training_results = training_results.append({
        'Epoch': i,
        'Train Loss': train_loss,
        'Train Accuracy': train_accuracy,
        'Test Loss': test_loss,
        'Test Accuracy': test_accuracy
    }, ignore_index=True)

# 保存结果到Excel文件
training_results.to_excel('training_results.xlsx', index=False)

#计算训练总共花费的时间
all_over_time = time.time()
all_over = all_over_time - all_start_time

# 将训练总时间保存到DataFrame中
training_results = training_results.append({
    'all time(h)': all_over / 3600
}, ignore_index=True)

print(f"训练总时长，耗时 {all_over/3600:.2f}小时")

# 保存结果到Excel文件
training_results.to_excel('training_results.xlsx', index=False)

# 绘制训练损失图并保存
plt.figure(figsize=(10, 5))  # 设置图形大小
plt.plot(range(epoch), train_losses, label='Training Loss')  # 绘制训练损失曲线
plt.xlabel('Epoch')  # x轴标签
plt.ylabel('Loss')  # y轴标签
plt.title('Training Loss over Epochs')  # 图标题
plt.legend()  # 显示图例
plt.savefig('training_loss.png')  # 保存训练损失图
plt.show()  # 显示图形

# 绘制测试损失图并保存
plt.figure(figsize=(10, 5))  # 设置图形大小
plt.plot(range(epoch), test_losses, label='Test Loss')  # 绘制测试损失曲线
plt.xlabel('Epoch')  # x轴标签
plt.ylabel('Loss')  # y轴标签
plt.title('Test Loss over Epochs')  # 图标题
plt.legend()  # 显示图例
plt.savefig('test_loss.png')  # 保存测试损失图
plt.show()  # 显示图形

# 绘制训练准确率图并保存
plt.figure(figsize=(10, 5))  # 设置图形大小
plt.plot(range(epoch), train_accuracies, label='Training Accuracy')  # 绘制训练准确率曲线
plt.xlabel('Epoch')  # x轴标签
plt.ylabel('Accuracy')  # y轴标签
plt.title('Training Accuracy over Epochs')  # 图标题
plt.legend()  # 显示图例
plt.savefig('training_accuracy.png')  # 保存训练准确率图
plt.show()  # 显示图形

# 绘制测试准确率图并保存
plt.figure(figsize=(10, 5))  # 设置图形大小
plt.plot(range(epoch), test_accuracies, label='Test Accuracy')  # 绘制测试准确率曲线
plt.xlabel('Epoch')  # x轴标签
plt.ylabel('Accuracy')  # y轴标签
plt.title('Test Accuracy over Epochs')  # 图标题
plt.legend()  # 显示图例
plt.savefig('test_accuracy.png')  # 保存测试准确率图
plt.show()  # 显示图形

