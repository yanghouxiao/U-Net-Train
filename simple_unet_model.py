# import torch
# from torch import nn
# from torchsummary import summary
# from torch.nn import functional as F
#
# class Conv_Block(nn.Module):
#     def __init__(self, in_channel, out_channel):
#         super(Conv_Block, self).__init__()
#         self.layer = nn.Sequential(
#             nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
#             nn.BatchNorm2d(out_channel),
#             nn.LeakyReLU(),
#             nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
#             nn.BatchNorm2d(out_channel),
#             nn.LeakyReLU()
#         )
#
#     def forward(self, x):
#         return self.layer(x)
#
#
# class DownSample(nn.Module):
#     def __init__(self, channel):
#         super(DownSample, self).__init__()
#         self.layer = nn.Sequential(
#             nn.Conv2d(channel, channel, kernel_size=3, stride=2, padding=1, bias=False),  # 用卷积代替池化
#             nn.BatchNorm2d(channel),
#             nn.LeakyReLU()
#         )
#
#     def forward(self, x):
#         return self.layer(x)
#
#
# class UpSample(nn.Module):
#     def __init__(self, channel):
#         super(UpSample, self).__init__()
#         self.conv = nn.Conv2d(channel, channel//2, kernel_size=3, stride=1, padding=1, bias=False)  #channel//2为向下取整
#
#     def forward(self, x, feature_map):
#         up = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)  # 最近邻改成双线性插值
#         out = self.conv(up)
#         return torch.cat((out, feature_map), dim=1)
#
#
# class simple_UNet0(nn.Module):
#     def __init__(self):
#         super(simple_UNet0, self).__init__()
#         self.c1 = Conv_Block(3, 32)
#         self.d1 = DownSample(32)
#         self.c2 = Conv_Block(32, 64)
#         self.d2 = DownSample(64)
#         self.c3 = Conv_Block(64, 128)
#         self.d3 = DownSample(128)
#         self.c4 = Conv_Block(128, 256)
#         self.d4 = DownSample(256)
#         self.c5 = Conv_Block(256, 512)
#         self.u1 = UpSample(512)
#         self.c6 = Conv_Block(512, 256)
#         self.u2 = UpSample(256)
#         self.c7 = Conv_Block(256, 128)
#         self.u3 = UpSample(128)
#         self.c8 = Conv_Block(128, 64)
#         self.u4 = UpSample(64)
#         self.c9 = Conv_Block(64, 32)
#         self.out = nn.Conv2d(32, 1, kernel_size=1)
#         self.th = nn.Sigmoid()
#
#     def forward(self, x):
#         r1 = self.c1(x)
#         r2 = self.c2(self.d1(r1))
#         r3 = self.c3(self.d2(r2))
#         r4 = self.c4(self.d3(r3))
#         r5 = self.c5(self.d4(r4))
#         o1 = self.c6(self.u1(r5, r4))
#         o2 = self.c7(self.u2(o1, r3))
#         o3 = self.c8(self.u3(o2, r2))
#         o4 = self.c9(self.u4(o3, r1))
#         return self.th(self.out(o4))
#
#
# # 初始化模型并迁移到正确的设备
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# fire_model = simple_UNet0().to(device)
#
# # 输出模型的结构
# summary(fire_model, (3, 512, 512))


import torch
from torch import nn
from torchsummary import summary

class Conv_Block(nn.Module):
    def __init__(self, in_channel, out_channel):
        super(Conv_Block, self).__init__()
        self.layer = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.LeakyReLU(),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.LeakyReLU()
        )

    def forward(self, x):
        return self.layer(x)

class DownSample(nn.Module):
    def __init__(self):
        super(DownSample, self).__init__()
        self.layer = nn.MaxPool2d(kernel_size=2, stride=2)  # 使用最大池化代替卷积

    def forward(self, x):
        return self.layer(x)

class UpSample(nn.Module):
    def __init__(self, channel):
        super(UpSample, self).__init__()
        self.conv = nn.ConvTranspose2d(channel, channel // 2, kernel_size=2, stride=2)  # 使用转置卷积

    def forward(self, x, feature_map):
        up = self.conv(x)  # 直接用转置卷积上采样
        return torch.cat((up, feature_map), dim=1)  # 拼接跳跃连接的特征图

class simple_UNet1(nn.Module):
    def __init__(self):
        super(simple_UNet1, self).__init__()
        self.c1 = Conv_Block(3, 32)
        self.d1 = DownSample()
        self.c2 = Conv_Block(32, 64)
        self.d2 = DownSample()
        self.c3 = Conv_Block(64, 128)
        self.d3 = DownSample()
        self.c4 = Conv_Block(128, 256)
        self.d4 = DownSample()
        self.c5 = Conv_Block(256, 512)
        self.u1 = UpSample(512)
        self.c6 = Conv_Block(512, 256)
        self.u2 = UpSample(256)
        self.c7 = Conv_Block(256, 128)
        self.u3 = UpSample(128)
        self.c8 = Conv_Block(128, 64)
        self.u4 = UpSample(64)
        self.c9 = Conv_Block(64, 32)
        self.out = nn.Conv2d(32, 1, kernel_size=1)
        self.th = nn.Sigmoid()

    def forward(self, x):
        r1 = self.c1(x)
        r2 = self.c2(self.d1(r1))
        r3 = self.c3(self.d2(r2))
        r4 = self.c4(self.d3(r3))
        r5 = self.c5(self.d4(r4))
        o1 = self.c6(self.u1(r5, r4))
        o2 = self.c7(self.u2(o1, r3))
        o3 = self.c8(self.u3(o2, r2))
        o4 = self.c9(self.u4(o3, r1))
        return self.th(self.out(o4))

# 初始化模型并迁移到正确的设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
fire_model = simple_UNet1().to(device)

# 输出模型的结构
summary(fire_model, (3, 512, 512))

