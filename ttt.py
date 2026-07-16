import numpy as np
import torch
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


def compute_metrics(y_true, y_pred):
    # 将模型输出和真实标签转换为numpy数组
    y_true = y_true.cpu().numpy() if isinstance(y_true, torch.Tensor) else y_true
    y_pred = y_pred.cpu().numpy() if isinstance(y_pred, torch.Tensor) else y_pred

    # 展平为一维数组
    y_true_flat = y_true.flatten()
    y_pred_flat = y_pred.flatten()

    # 将输出值和标签值阈值化，以便计算精度、召回率、F1等
    threshold = 0.5
    y_pred_binary = (y_pred_flat > threshold).astype(int)
    y_true_binary = (y_true_flat > threshold).astype(int)

    # 计算精度、召回率、F1等，添加zero_division=1，避免警告
    precision = precision_score(y_true_binary, y_pred_binary, zero_division=1)
    recall = recall_score(y_true_binary, y_pred_binary, zero_division=1)
    f1 = f1_score(y_true_binary, y_pred_binary, zero_division=1)

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

    return precision, recall, f1, sensitivity, specificity, iou


# 示例使用
y_true = np.random.rand(1, 128, 128)  # 模拟真实标签，形状为 (1, 128, 128)
print(type(y_true))
print(y_true)
y_pred = np.random.rand(1, 128, 128)  # 模拟模型输出，形状为 (1, 128, 128)
print(type(y_pred))
print(y_pred)

from PIL import Image
import numpy as np

# 加载图像分割蒙版
mask_image = Image.open("dataset/Masks/image_0.png")

# 将图像转换为数组
mask_array = np.array(mask_image)

# 打印蒙版的像素值
print(mask_array)

# 查看某些具体像素值
print(mask_array[0, 0])  # 左上角像素值
print(mask_array[-1, -1])  # 右下角像素值

# 如果有多个类别，可以统计每个类别的像素数量
unique, counts = np.unique(mask_array, return_counts=True)

# 输出每个类别的像素数量
print(f"类别像素统计：")
for u, c in zip(unique, counts):
    print(f"类别 {u} 的像素数: {c}")


precision, recall, f1, sensitivity, specificity, iou = compute_metrics(y_true, y_pred)

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
print(f"Sensitivity: {sensitivity}")
print(f"Specificity: {specificity}")
print(f"IOU: {iou}")
