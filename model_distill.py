# import os
# import sys
# import time
# import torch
# import pandas as pd
#
# from PIL import Image
# from matplotlib import pyplot as plt
# from tqdm import tqdm
# from unet_model import UNet  # 大模型
# from simple_unet_model import simple_UNet1  # 小模型
# from smallest_unet_model import smallest_UNet
# from torch import nn, optim
# from torchvision import transforms
# from torch.utils.data import random_split
# from torch.utils.data import Dataset, DataLoader
#
# # 设备选择
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# # 数据路径
# images_dir = "dataset/Images"
# masks_dir = "dataset/Masks"
#
# train_losses = []  # 用于存储每轮训练的损失值
# val_losses = []  # 用于存储每轮验证的损失值
#
# #训练图片与权重文件保存路径
# save_path = 'D:/Python/Text/unet/train/pt6'
#
# # 训练超参数
# epoch = 50
# batch_size = 16
# learning_rate = 0.001
# transforms_Resize = 512
# train_val_split_rate = 0.85
# alpha = 0.5  # 蒸馏损失的权重 (0~1,0为不使用模型蒸馏，为1则不会进行训练，数字越大老师模型占的比重越大)
# weight_path_teacher = "train/pt2/UNet_model_19.pt"  # 大模型的预训练权重
#
# # **数据集定义**
# class SegmentationDataset(Dataset):
#     def __init__(self, images_dir, masks_dir, transform=None):
#         self.images_dir = images_dir
#         self.masks_dir = masks_dir
#         self.transform = transform
#         self.image_files = sorted(os.listdir(images_dir))
#         self.mask_files = sorted(os.listdir(masks_dir))
#
#     def __len__(self):
#         return len(self.image_files)
#
#     def __getitem__(self, idx):
#         image_path = os.path.join(self.images_dir, self.image_files[idx])
#         mask_path = os.path.join(self.masks_dir, self.mask_files[idx])
#         image = Image.open(image_path)
#         mask = Image.open(mask_path)
#
#         if self.transform:
#             image = self.transform(image)
#             mask = self.transform(mask)
#
#         return image, mask
#
# # **数据预处理**
# transform = transforms.Compose([
#     transforms.Resize((transforms_Resize, transforms_Resize)),
#     transforms.ToTensor(),
# ])
#
# # **数据加载**
# train_dataset = SegmentationDataset(images_dir, masks_dir, transform=transform)
#
# # **数据集划分 (90% 训练集, 10% 验证集)**
# total_size = len(train_dataset)
# train_size = int(train_val_split_rate * total_size)
# val_size = total_size - train_size  # 确保总数据量不变
#
# train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])
#
# #**数据加载器**
# train_dataloader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False)
# val_dataloader = DataLoader(dataset=val_dataset, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=False)
#
# # **加载 Teacher（大模型）**
# teacher_net = simple_UNet1().to(device)
# teacher_net.load_state_dict(torch.load(weight_path_teacher, map_location=device))
# teacher_net.eval()  # 大模型用于推理，不训练
#
# # **初始化 Student（小模型）**
# student_net = smallest_UNet().to(device)
#
# # **损失函数**
# bce_loss_fn = nn.BCELoss().to(device)
# kl_loss_fn = nn.KLDivLoss(reduction='batchmean').to(device)  # 蒸馏损失
#
# # **优化器**
# opt = optim.Adam(student_net.parameters(), lr=learning_rate)
#
# # 打印当前使用的设备（CPU或GPU）
# print(device)
#
# # 创建一个DataFrame来存储每轮训练的损失值
# columns = ['Epoch', 'Train Loss', 'Train Time', 'Val Loss', 'all time']
# training_results = pd.DataFrame(columns=columns)
#
# if os.path.exists(weight_path_teacher):
#     print('成功加载Teacher模型权重')
# else:
#     print('未成功加载Teacher模型权重')
#     sys.exit()  # 退出程序
#
# print("开始蒸馏训练...")
#
# if __name__ == '__main__':
#
#     # 记录训练开始时间
#     all_start_time = time.time()
#
#     for i in range(epoch):
#         print(f"第 {i} 轮训练开始")
#
#         train_loss = 0
#         val_loss = 0
#         batch_losses = []
#         start_train_time = time.time()
#
#         # 这行代码必须加（除非不在epoch里运行验证集，因为验证集会将模型弄为评估模式，如果不恢复训练模式则训练的权值会为全0！！！）
#         student_net.train()
#
#         with tqdm(train_dataloader, unit="batch") as tepoch:
#             for data in tepoch:
#                 image, mask = data
#                 image, mask = image.to(device), mask.to(device)
#
#                 # **大模型推理（不计算梯度）**
#                 with torch.no_grad():
#                     teacher_out = teacher_net(image)
#
#                 # **小模型前向传播**
#                 student_out = student_net(image)
#
#                 # **计算两种损失**
#                 loss_bce = bce_loss_fn(student_out, mask)  # 真实标签的 BCE Loss
#                 loss_kl_distill = kl_loss_fn(student_out.log_softmax(dim=1), teacher_out.softmax(dim=1))  # 蒸馏损失（KL 散度）
#                 # loss_kl_distill = kl_loss_fn(student_out, teacher_out)  #如果用这个不经过softmax操作的话，那么算的值会为负数
#
#                 loss = (1 - alpha) * loss_bce + alpha * loss_kl_distill  # 总损失
#
#                 # **反向传播**
#                 opt.zero_grad()
#                 loss.backward()  # 反向传播计算梯度
#                 opt.step()
#
#                 train_loss += loss.item()
#                 batch_losses.append(loss.item())
#
#                 tepoch.set_postfix(loss=train_loss / (tepoch.n + 1))
#
#                 # 计算 batch_losses 的最小值和最大值
#         min_loss = max(min(batch_losses), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
#         max_loss = max(batch_losses)
#
#         # 绘制每轮训练过程中batch损失的图像
#         plt.figure(figsize=(10, 5))
#         plt.plot(batch_losses, label='Batch Loss')
#         plt.xlabel('Batch')
#         plt.ylabel('Loss')
#         plt.title(f'Batch Loss for Epoch {i}')
#         plt.legend()  # 显示图例
#         plt.yscale('log')  # 设置 y 轴为对数尺度
#         plt.ylim(min_loss * 0.9, max_loss * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
#         plt.savefig(f'{save_path}/batch_loss_epoch_{i}.png')  # 保存每轮的batch损失图
#         plt.close()  # 关闭图像
#
#         train_loss /= len(train_dataloader)  # 计算每轮的平均训练损失
#         train_losses.append(train_loss)  # 保存每轮的损失
#
#         end_train_time = time.time()  # 记录训练结束时间
#         train_duration = end_train_time - start_train_time  # 计算训练轮次耗时
#         minutes, seconds = divmod(train_duration, 60)
#         print(f"第{i}轮训练结束，耗时 {int(minutes)} 分 {int(seconds)} 秒")
#
#         # **验证模式**
#         student_net.eval()
#         with tqdm(val_dataloader, unit="batch") as tepoch:
#             with torch.no_grad():
#                 for data in tepoch:
#                     image, mask = data  # 正确解包当前batch的数据
#                     image, mask = image.to(device), mask.to(device)
#                     student_out = student_net(image)
#
#                     # **计算损失**
#                     loss_bce = bce_loss_fn(student_out, mask)  # 真实标签的 BCE Loss
#                     val_loss += loss_bce.item()  # 累加总验证损失
#
#             val_loss /= len(val_dataloader)  # 计算平均验证损失
#             tepoch.set_postfix(loss=val_loss)
#
#         val_losses.append(val_loss)  # 保存每轮的损失
#
#         print(f"训练集损失: {train_loss:.6f}，验证集损失: {val_loss:.6f}")  #这个验证损失并非蒸馏总损失，而是模型的BCELoss损失，而训练损失则为蒸馏损失
#
#         # 将当前轮次的损失保存到DataFrame中
#         training_results = training_results.append({
#             'Epoch': i,
#             'Train Loss': train_loss,
#             'Train Time': f'{int(minutes)} 分 {int(seconds)} 秒',  # 以分钟和秒的格式保存
#             'Val Loss': val_loss
#         }, ignore_index=True)
#
#         # **保存模型**
#         torch.save(student_net.state_dict(), f"{save_path}/UNet_student_{i}.pt")
#         print(f"第{i}次模型已保存")
#
#     # 计算总训练时间
#     all_over_time = time.time()
#     all_over = all_over_time - all_start_time
#     all_hours, all_remainder = divmod(all_over, 3600)  # 转换为小时和剩余的秒数
#     all_minutes, all_seconds = divmod(all_remainder, 60)   # 转换为分钟和秒
#     print(f"训练总时长，耗时 {int(all_hours)} 小时 {int(all_minutes)} 分 {int(all_seconds)} 秒")
#
#     # 将训练总时间保存到DataFrame中
#     training_results = training_results.append({
#         'all time': f'{int(all_hours)} 小时 {int(all_minutes)} 分 {int(all_seconds)} 秒'
#     }, ignore_index=True)
#
#     # 保存训练结果到Excel文件
#     training_results.to_excel(f'{save_path}/training_results.xlsx', index=False)
#
#     min_loss = max(min(train_losses), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
#     max_loss = max(val_losses)
#
#     # 绘制训练损失图并保存
#     plt.figure(figsize=(10, 5))  # 设置图形的大小
#     plt.plot(range(epoch), train_losses, label='Training Loss', color='blue')  # 训练损失为蓝色
#     plt.plot(range(epoch), val_losses, label='Validation Loss', linestyle='--', color='red')  # 验证损失为红色，虚线
#     plt.xlabel('Epoch')  # 设置x轴标签
#     plt.ylabel('Loss')  # 设置y轴标签
#     plt.title('Training & Validation Loss')
#     plt.legend()  # 显示图例
#     plt.yscale('log')  # 设置 y 轴为对数尺度
#     plt.ylim(min_loss * 0.9, max_loss * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
#     plt.savefig(f'{save_path}/training_val_loss.png')  # 保存图表为PNG文件
#     plt.show()  # 显示训练损失图


import os
import sys
import time
import torch
import numpy as np
import pandas as pd


from PIL import Image
from tqdm import tqdm
from medpy import metric
from matplotlib import pyplot as plt
from unet_model import UNet  # 大模型
from simple_unet_model import simple_UNet1  # 小模型
from smallest_unet_model import smallest_UNet
from torch import nn, optim
from torchvision import transforms
from torch.utils.data import random_split
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

# 设备选择
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 数据路径
images_dir = "dataset/Images"
masks_dir = "dataset/Masks"

train_losses = []  # 用于存储每轮训练的损失值
val_losses = []  # 用于存储每轮验证的损失值

val_precision = []
val_recall = []
val_f1_score = []
val_sensitivity = []
val_specificity = []
val_iou = []
val_auc = []

#训练图片与权重文件保存路径
save_path = 'D:/Python/Text/unet/train/pt9'

# 训练超参数
epoch = 50
batch_size = 10
learning_rate = 0.001
transforms_Resize = 128
train_val_split_rate = 0.85
alpha = 0.5  # 蒸馏损失的权重 (0~1,0为不使用模型蒸馏，为1则不会进行训练，数字越大老师模型占的比重越大)
threshold = 0.5007
weight_path_teacher = "train/pt2/UNet_model_19.pt"  # 大模型的预训练权重

# **数据集定义**
class SegmentationDataset(Dataset):
    def __init__(self, images_dir, masks_dir, transform=None):
        self.images_dir = images_dir
        self.masks_dir = masks_dir
        self.transform = transform
        self.image_files = sorted(os.listdir(images_dir))
        self.mask_files = sorted(os.listdir(masks_dir))

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_path = os.path.join(self.images_dir, self.image_files[idx])
        mask_path = os.path.join(self.masks_dir, self.mask_files[idx])
        image = Image.open(image_path)
        mask = Image.open(mask_path)

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask

# **数据预处理**
transform = transforms.Compose([
    transforms.Resize((transforms_Resize, transforms_Resize)),
    transforms.ToTensor(),
])

# **数据加载**
train_dataset = SegmentationDataset(images_dir, masks_dir, transform=transform)

# **数据集划分 (90% 训练集, 10% 验证集)**
total_size = len(train_dataset)
train_size = int(train_val_split_rate * total_size)
val_size = total_size - train_size  # 确保总数据量不变

train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])

#**数据加载器**
train_dataloader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False)
val_dataloader = DataLoader(dataset=val_dataset, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=False)

# **加载 Teacher（大模型）**
teacher_net = simple_UNet1().to(device)
teacher_net.load_state_dict(torch.load(weight_path_teacher, map_location=device))
teacher_net.eval()  # 大模型用于推理，不训练

# **初始化 Student（小模型）**
student_net = smallest_UNet().to(device)

# **损失函数**
bce_loss_fn = nn.BCELoss().to(device)
kl_loss_fn = nn.KLDivLoss(reduction='batchmean').to(device)  # 蒸馏损失

# **优化器**
opt = optim.Adam(student_net.parameters(), lr=learning_rate)

# 打印当前使用的设备（CPU或GPU）
print(device)

# 创建一个DataFrame来存储每轮训练的损失值
columns = ['Epoch', 'Train Loss', 'Train Time', 'Val Loss', 'Precision (%)', 'Recall (%)'
           , 'F1 Score (%)', 'Sensitivity (%)', 'Specificity (%)', 'IOU (%)', 'AUC (%)', 'all time']
training_results = pd.DataFrame(columns=columns)


if os.path.exists(weight_path_teacher):
    print('成功加载Teacher模型权重')
else:
    print('未成功加载Teacher模型权重')
    sys.exit()  # 退出程序


def compute_metrics(y_true, y_pred, threshold=threshold):
    # 将模型输出和真实标签转换为numpy数组
    y_true = y_true.cpu().numpy() if isinstance(y_true, torch.Tensor) else y_true
    y_pred = y_pred.cpu().numpy() if isinstance(y_pred, torch.Tensor) else y_pred

    # 确保 y_true 和 y_pred 具有相同的形状
    assert y_true.shape == y_pred.shape, "y_true and y_pred must have the same shape"

    # 展平为一维数组
    y_true_binary = y_true.flatten()  # 将真实标签展平成1维数组
    y_pred_flat = y_pred.flatten()  # 将模型输出展平成1维数组

    # 阈值化 y_true_flat 以确保其为二进制值
    y_true_binary = (y_true_binary > 0).astype(int)
    y_pred_binary = (y_pred_flat > threshold).astype(int)

    # 计算AUC
    auc = roc_auc_score(y_true_binary, y_pred_flat)  # AUC计算使用概率值

    # 计算精度、召回率、F1等，使用二进制的预测值 y_pred_binary
    precision = precision_score(y_true_binary, y_pred_binary, average='binary', zero_division=1)
    recall = recall_score(y_true_binary, y_pred_binary, average='binary', zero_division=1)
    f1 = f1_score(y_true_binary, y_pred_binary, average='binary', zero_division=1)

    # 计算混淆矩阵（从中提取灵敏度、特异性等）
    cm = confusion_matrix(y_true_binary, y_pred_binary)

    # 如果混淆矩阵不是 2x2，进行处理
    if cm.size == 1:
        tn, fp, fn, tp = 0, 0, 0, cm[0]  # 假设只有一个类别（只有1或只有0的情况）
    elif cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = 0, 0, 0, 0  # 如果有异常，默认值为0

    # 计算灵敏度（sensitivity）、特异性（specificity）和IOU
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # 避免除零
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # 避免除零
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0  # 避免除零

    return precision, recall, f1, sensitivity, specificity, iou, auc


# def compute_metrics(y_true, y_pred, threshold=0.5007, epsilon=1e-7):
#     # 将模型输出和真实标签转换为numpy数组
#     y_true = y_true.cpu().numpy() if isinstance(y_true, torch.Tensor) else y_true
#     y_pred = y_pred.cpu().numpy() if isinstance(y_pred, torch.Tensor) else y_pred
#
#     # 确保 y_true 和 y_pred 具有相同的形状
#     assert y_true.shape == y_pred.shape, "y_true and y_pred must have the same shape"
#
#     # 展平为一维数组
#     y_true_binary = y_true.flatten()  # 将真实标签展平成1维数组
#     y_pred_flat = y_pred.flatten()  # 将模型输出展平成1维数组
#
#     # 阈值化 y_true_flat 以确保其为二进制值
#     y_true_binary = (y_true_binary > 0).astype(int)
#     y_pred_binary = (y_pred_flat > threshold).astype(int)
#
#     # 统计 y_true_binary 和 y_pred_binary 中 0 和 1 的个数
#     y_true_zeros = np.sum(y_true_binary == 0)  # 统计 0 的个数
#     y_true_ones = np.sum(y_true_binary == 1)  # 统计 1 的个数
#
#     y_pred_zeros = np.sum(y_pred_binary == 0)  # 统计 0 的个数
#     y_pred_ones = np.sum(y_pred_binary == 1)  # 统计 1 的个数
#
#     print("y_true_binary - 0's:", y_true_zeros, "1's:", y_true_ones)
#     print("y_pred_binary - 0's:", y_pred_zeros, "1's:", y_pred_ones)
#
#     # 计算AUC
#     auc = roc_auc_score(y_true_binary, y_pred_flat)  # AUC计算使用概率值
#
#     # 计算混淆矩阵
#     out = confusion_matrix(y_true_binary, y_pred_binary, labels=[0, 1])
#
#     TN = out[0][0]
#     FP = out[0][1]
#     FN = out[1][0]
#     TP = out[1][1]
#
#     # 计算精确度、召回率和交并比
#     precision = TP / (TP + FP + epsilon)
#     recall = TP / (TP + FN + epsilon)
#     iou = TP / (TP + FP + FN + epsilon)
#     specificity = TN / (TN + FP + epsilon)
#     f1 = 2 * (precision * recall) / (precision + recall + epsilon)
#
#     sensitivity = recall
#
#     return precision, recall, f1, sensitivity, specificity, iou, auc



print("开始蒸馏训练...")

if __name__ == '__main__':

    # 记录训练开始时间
    all_start_time = time.time()
    
    for i in range(epoch):

        print(f"第 {i} 轮训练开始")

        train_loss = 0
        val_loss = 0
        precision_all = 0
        recall_all = 0
        f1_all = 0
        sensitivity_all = 0
        specificity_all = 0
        iou_all = 0
        AUC_all = 0

        batch_losses = []

        start_train_time = time.time()

        # 这行代码必须加（除非不在epoch里运行验证集，因为验证集会将模型弄为评估模式，如果不恢复训练模式则训练的权值会为全0！！！）
        student_net.train()

        with tqdm(train_dataloader, unit="batch") as tepoch:
            for data in tepoch:
                image, mask = data
                image, mask = image.to(device), mask.to(device)

                # **大模型推理（不计算梯度）**
                with torch.no_grad():
                    teacher_out = teacher_net(image)

                # **小模型前向传播**
                student_out = student_net(image)

                # **计算两种损失**
                loss_bce = bce_loss_fn(student_out, mask)  # 真实标签的 BCE Loss
                loss_kl_distill = kl_loss_fn(student_out.log_softmax(dim=1), teacher_out.softmax(dim=1))  # 蒸馏损失（KL 散度）
                # loss_kl_distill = kl_loss_fn(student_out, teacher_out)  #如果用这个不经过softmax操作的话，那么算的值会为负数

                loss = (1 - alpha) * loss_bce + alpha * loss_kl_distill  # 总损失

                # **反向传播**
                opt.zero_grad()
                loss.backward()  # 反向传播计算梯度
                opt.step()

                train_loss += loss.item()
                batch_losses.append(loss.item())

                tepoch.set_postfix(loss=train_loss / (tepoch.n + 1))

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
        plt.savefig(f'{save_path}/batch_loss_epoch_{i}.png')  # 保存每轮的batch损失图
        plt.close()  # 关闭图像

        train_loss /= len(train_dataloader)  # 计算每轮的平均训练损失
        train_losses.append(train_loss)  # 保存每轮的损失

        end_train_time = time.time()  # 记录训练结束时间
        train_duration = end_train_time - start_train_time  # 计算训练轮次耗时
        minutes, seconds = divmod(train_duration, 60)
        print(f"第{i}轮训练结束，耗时 {int(minutes)} 分 {int(seconds)} 秒")


        # **验证模式**
        student_net.eval()
        with tqdm(val_dataloader, unit="batch") as tepoch:
            with torch.no_grad():
                for data in tepoch:
                    image, mask = data  # 正确解包当前batch的数据
                    image, mask = image.to(device), mask.to(device)

                    student_out = student_net(image)

                    # **计算损失**
                    loss_bce = bce_loss_fn(student_out, mask)  # 真实标签的 BCE Loss
                    val_loss += loss_bce.item()  # 累加总验证损失

                    student_out = torch.sigmoid(student_out)  # 通过 Sigmoid 函数归一化到 0-1 范围

                    # 在计算损失和指标之前，打印 mask 和 student_out 的范围
                    # print("mask min:", mask.min().item(), "max:", mask.max().item())
                    # print("student_out min:", student_out.min().item(), "max:", student_out.max().item())

                    precision, recall, f1, sensitivity, specificity, iou, AUC = compute_metrics(mask, student_out)

                    precision_all += precision
                    recall_all += recall
                    f1_all += f1
                    sensitivity_all += sensitivity
                    specificity_all += specificity
                    iou_all += iou
                    AUC_all += AUC

                    tepoch.set_postfix(loss=loss_bce, precision=precision, recall=recall, f1=f1, sensitivity=sensitivity, specificity=specificity, iou=iou, AUC=AUC)

            val_loss /= len(val_dataloader)  # 计算平均验证损失

            precision_all /= len(val_dataloader)
            recall_all /= len(val_dataloader)
            f1_all /= len(val_dataloader)
            sensitivity_all /= len(val_dataloader)
            specificity_all /= len(val_dataloader)
            iou_all /= len(val_dataloader)
            AUC_all /= len(val_dataloader)

        val_losses.append(val_loss)  # 保存每轮的损失

        val_precision.append(precision_all)
        val_recall.append(recall_all)
        val_f1_score.append(f1_all)
        val_sensitivity.append(sensitivity_all)
        val_specificity.append(specificity_all)
        val_iou.append(iou_all)
        val_auc.append(AUC_all)

        print(f"训练集损失: {train_loss:.6f}，验证集损失: {val_loss:.6f}")  #这个验证损失并非蒸馏总损失，而是模型的BCELoss损失，而训练损失则为蒸馏损失
        print(f"Precision: {precision_all}, Recall: {recall_all}, F1 Score: {f1_all},"
              f"Sensitivity: {sensitivity_all}, Specificity: {specificity_all}, IOU: {iou_all}, AUC: {AUC_all}")

        # 将当前轮次的损失保存到DataFrame中
        training_results = training_results.append({
            'Epoch': i,
            'Train Loss': train_loss,
            'Train Time': f'{int(minutes)} 分 {int(seconds)} 秒',  # 以分钟和秒的格式保存
            'Val Loss': val_loss,
            'Precision (%)': precision_all * 100,
            'Recall (%)': recall_all * 100,
            'F1 Score (%)': f1_all * 100,
            'Sensitivity (%)': sensitivity_all * 100,
            'Specificity (%)': specificity_all * 100,
            'IOU (%)': iou_all * 100,
            'AUC (%)': AUC_all * 100,
        }, ignore_index=True)

        # **保存模型**
        torch.save(student_net.state_dict(), f"{save_path}/UNet_student_{i}.pt")
        print(f"第{i}次模型已保存")

    # 计算总训练时间
    all_over_time = time.time()
    all_over = all_over_time - all_start_time
    all_hours, all_remainder = divmod(all_over, 3600)  # 转换为小时和剩余的秒数
    all_minutes, all_seconds = divmod(all_remainder, 60)   # 转换为分钟和秒
    print(f"训练总时长，耗时 {int(all_hours)} 小时 {int(all_minutes)} 分 {int(all_seconds)} 秒")

    # 将训练总时间保存到DataFrame中
    training_results = training_results.append({
        'all time': f'{int(all_hours)} 小时 {int(all_minutes)} 分 {int(all_seconds)} 秒'
    }, ignore_index=True)

    # 保存训练结果到Excel文件
    training_results.to_excel(f'{save_path}/training_results.xlsx', index=False)

    min_loss = max(min(train_losses), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_loss = max(val_losses)

    min_precision = max(min(val_precision), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_precision = max(val_precision)

    min_recall = max(min(val_recall), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_recall = max(val_recall)

    min_f1_score = max(min(val_f1_score), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_f1_score = max(val_f1_score)

    min_sensitivity = max(min(val_sensitivity), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_sensitivity = max(val_sensitivity)

    min_specificity = max(min(val_specificity), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_specificity = max(val_specificity)

    min_iou = max(min(val_iou), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_iou = max(val_iou)

    min_auc = max(min(val_auc), 1e-6)  # 确保最小值不为 0，防止 log 计算问题
    max_auc = max(val_auc)


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), train_losses, label='Training Loss', color='blue')  # 训练损失为蓝色
    plt.plot(range(epoch), val_losses, label='Validation Loss', linestyle='--', color='red')  # 验证损失为红色，虚线
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('Loss')  # 设置y轴标签
    plt.title('Training & Validation Loss')
    plt.legend()  # 显示图例
    plt.yscale('log')  # 设置 y 轴为对数尺度
    plt.ylim(min_loss * 0.9, max_loss * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/training_val_loss.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_precision, label='val_precision', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_precision')  # 设置y轴标签
    plt.title('val_precision')
    plt.legend()  # 显示图例
    plt.ylim(min_precision * 0.9, max_precision * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_precision.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_recall, label='val_recall', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_recall')  # 设置y轴标签
    plt.title('val_recall')
    plt.legend()  # 显示图例
    plt.ylim(min_recall * 0.9, max_recall * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_recall.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_f1_score, label='val_f1_score', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_f1_score')  # 设置y轴标签
    plt.title('val_f1_score')
    plt.legend()  # 显示图例
    plt.ylim(min_f1_score * 0.9, max_f1_score * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_f1_score.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_sensitivity, label='val_sensitivity', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_sensitivity')  # 设置y轴标签
    plt.title('val_sensitivity')
    plt.legend()  # 显示图例
    plt.ylim(min_sensitivity * 0.9, max_sensitivity * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_sensitivity.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_specificity, label='val_specificity', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_specificity')  # 设置y轴标签
    plt.title('val_specificity')
    plt.legend()  # 显示图例
    plt.ylim(min_specificity * 0.9, max_specificity * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_specificity.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图


    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_iou, label='val_iou', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_iou')  # 设置y轴标签
    plt.title('val_iou')
    plt.legend()  # 显示图例
    plt.ylim(min_iou * 0.9, max_iou * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_iou.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图

    # 绘制训练损失图并保存
    plt.figure(figsize=(10, 5))  # 设置图形的大小
    plt.plot(range(epoch), val_auc, label='val_auc', color='blue')  # 训练损失为蓝色
    plt.xlabel('Epoch')  # 设置x轴标签
    plt.ylabel('val_auc')  # 设置y轴标签
    plt.title('val_auc')
    plt.legend()  # 显示图例
    plt.ylim(min_auc * 0.9, max_auc * 1.1)  # 让 y 轴范围稍微扩展一点，避免数据过于贴近边界
    plt.savefig(f'{save_path}/val_auc.png')  # 保存图表为PNG文件
    plt.show()  # 显示训练损失图



