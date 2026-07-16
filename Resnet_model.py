import os
import torch
from torch import nn
from torchvision import models
from torchsummary import summary
from smallest_unet_model import *
from scenesize_model import *
def compute_alpha(mask, threshold):
    """
    mask: UNet 输出，大小为 [B, 1, H, W]，值通常是[0, 1]之间
    返回: 每张图中火焰像素占比，形状为 [B, 1]
    """
    B = mask.shape[0]
    # 二值化：如果输出是概率图，可以加个阈值
    binary_mask = (mask > threshold).float()  # 或直接使用 mask（如果已是0或1）
    total_pixels = mask.shape[2] * mask.shape[3]
    fire_ratio = binary_mask.view(B, -1).sum(dim=1, keepdim=True) / total_pixels
    return fire_ratio  # [B, 1]


# class FireClassificationModel(nn.Module):
#     def __init__(self, unet, num_classes=4, threshold=0.5007):
#         super(FireClassificationModel, self).__init__()
#         self.unet = unet
#         self.num_classes = num_classes
#         self.threshold = threshold  # 把阈值保存成成员变量
#
#         # 冻结 UNet 参数，防止训练时更新
#         for param in self.unet.parameters():
#             param.requires_grad = False
#
#         # ResNet18 特征提取部分（去掉最后的fc）
#         base_model = models.resnet18(pretrained=False)
#         self.resnet_backbone = nn.Sequential(*list(base_model.children())[:-1])
#         self.backbone_out_dim = base_model.fc.in_features
#
#         # ResNet 输出一个值（图像预测强度）
#         self.res_output_layer = nn.Sequential(
#             nn.Linear(self.backbone_out_dim, 128),
#             nn.ReLU(),
#             nn.Linear(128, 1)
#         )
#
#         # 拼接 res_out 与 alpha，进行四分类
#         self.classifier = nn.Sequential(
#             nn.Linear(2, 64),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(64, self.num_classes)
#         )
#
#     def forward(self, x):
#         with torch.no_grad():  # 禁用梯度，节省显存并防止反向传播
#             mask = self.unet(x)             # [B, 1, H, W]
#             alpha = compute_alpha(mask, self.threshold)     # [B, 1]
#
#         # ResNet 提取图像特征
#         features = self.resnet_backbone(x)        # [B, C, 1, 1]
#         features = features.view(features.size(0), -1)  # [B, C]
#         res_out = self.res_output_layer(features)       # [B, 1]
#
#         # 拼接并分类
#         fusion = torch.cat([res_out, alpha], dim=1)     # [B, 2]
#         return self.classifier(fusion)                  # [B, 4]


class FireClassificationModel(nn.Module):
    def __init__(self, unet, scene_model, num_classes=4, threshold=0.5007):
        super(FireClassificationModel, self).__init__()
        self.unet = unet
        self.scene_model = scene_model  # 加载外部传入的 scene_size_model
        self.num_classes = num_classes
        self.threshold = threshold

        # 冻结 UNet 参数
        for param in self.unet.parameters():
            param.requires_grad = False

        # 冻结 scene_size_model 参数
        for param in self.scene_model.parameters():
            param.requires_grad = False

        # 提取 scene_size_model 的输出（假设其输出为 [B, 3] 三分类的logits）
        # 你可以根据是否想要softmax后的概率进行处理

        # UNet 输出的 alpha 值 + scene_model 的预测，共计 1 + 3 = 4 维输入
        self.classifier = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, self.num_classes)
        )

    def forward(self, x):
        with torch.no_grad():
            mask = self.unet(x)  # [B, 1, H, W]
            alpha = compute_alpha(mask, self.threshold)  # [B, 1]

            scene_logits = self.scene_model(x)  # [B, 3]，分类logits
            # 如果你想使用概率，可以加上 softmax
            scene_probs = torch.softmax(scene_logits, dim=1)

        # 拼接 alpha 和 scene_model 输出
        fusion = torch.cat([alpha, scene_probs], dim=1)  # [B, 1+3] = [B, 4]
        return self.classifier(fusion)  # [B, 4]


# 设备选择（优先使用 GPU，否则使用 CPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载 U-Net与scene-size模型，并将其移动到选定的设备上
net_UNet = smallest_UNet().to(device)
net_SceneSize = scenesize_model().to(device)

# 设定模型权重路径
weights_unet = 'train/pt7/UNet_student_44.pt'
weights_scenesize = 'train/size_pt/size_model_1.pt'

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
fire_model = FireClassificationModel(net_UNet, net_SceneSize).to(device)

print(fire_model)

# 打印模型摘要
summary(fire_model, (3, 640, 640))

