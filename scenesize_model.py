# import os
# import torch
# from torch import nn
# from torchvision import models
# from torchsummary import summary
#
# class scenesize_model(nn.Module):
#     def __init__(self, num_classes=3):
#         super(scenesize_model, self).__init__()
#
#         # 加载预训练的 ResNet18 模型
#         self.backbone = models.resnet18(pretrained=True)
#
#         # 替换最后的全连接层以适应三分类
#         in_features = self.backbone.fc.in_features
#         self.backbone.fc = nn.Linear(in_features, num_classes)
#
#     def forward(self, x):
#         return self.backbone(x)
#
# # 设备选择（优先使用 GPU，否则使用 CPU）
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# # 加载scene-size模型，并将其移动到选定的设备上
# net_SceneSize = scenesize_model().to(device)
#
# # 设定模型权重路径
# weights_scenesize = 'train/size_pt/size_model_1.pt'
#
# # 检查权重文件是否存在
# if os.path.exists(weights_scenesize):
#     net_SceneSize.load_state_dict(torch.load(weights_scenesize, map_location=device))  # 加载权重
#     print('✅ 成功加载SceneSize模型权重')  # 打印成功信息
# else:
#     print('❌ 无SceneSize模型权重')  # 打印错误信息
#     exit()  # 终止程序
#
# # 设置模型为评估模式（推理模式）
# net_SceneSize.eval()
# fire_model = scenesize_model().to(device)
#
# print(fire_model)
#
# # 打印模型摘要
# summary(fire_model, (3, 640, 640))


import torch
from torch import nn
from torchvision import models
from torchsummary import summary

# =========================
# 1. CBAM模块定义
# =========================
class ChannelAttention(nn.Module):
    def __init__(self, in_planes, ratio=16):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)

        self.fc = nn.Sequential(
            nn.Conv2d(in_planes, in_planes // ratio, 1, bias=False),
            nn.ReLU(),
            nn.Conv2d(in_planes // ratio, in_planes, 1, bias=False)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        out = avg_out + max_out
        return self.sigmoid(out)

class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super(SpatialAttention, self).__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x = torch.cat([avg_out, max_out], dim=1)
        x = self.conv(x)
        return self.sigmoid(x)

class CBAM(nn.Module):
    def __init__(self, in_planes, ratio=16, kernel_size=7):
        super(CBAM, self).__init__()
        self.channel_attention = ChannelAttention(in_planes, ratio)
        self.spatial_attention = SpatialAttention(kernel_size)

    def forward(self, x):
        out = x * self.channel_attention(x)
        out = out * self.spatial_attention(out)
        return out

# =========================
# 2. ResNet18 + CBAM模型定义
# =========================
class scenesize_model(nn.Module):
    def __init__(self, num_classes=3):
        super(scenesize_model, self).__init__()

        # 加载官方预训练 ResNet18
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

        # CBAM插入
        self.cbam1 = CBAM(64)
        self.cbam2 = CBAM(128)
        self.cbam3 = CBAM(256)
        self.cbam4 = CBAM(512)

        # 替换全连接层为三分类
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)

        x = self.backbone.layer1(x)
        x = self.cbam1(x)

        x = self.backbone.layer2(x)
        x = self.cbam2(x)

        x = self.backbone.layer3(x)
        x = self.cbam3(x)

        x = self.backbone.layer4(x)
        x = self.cbam4(x)

        x = self.backbone.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.backbone.fc(x)

        return x

# =========================
# 3. 打印模型结构
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

net_SceneSize = scenesize_model().to(device)

# 打印模型结构
print(net_SceneSize)

summary(net_SceneSize, (3, 640, 640))



