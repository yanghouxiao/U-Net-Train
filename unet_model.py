import torch
from torch import nn
from torchsummary import summary
from torch.nn import functional as F

class Conv_Block(nn.Module):
    def __init__(self, in_channel, out_channel):
        super(Conv_Block, self).__init__()
        self.layer = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False),
            nn.BatchNorm2d(out_channel),
            nn.Dropout(0.5),
            nn.LeakyReLU(),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False),
            nn.BatchNorm2d(out_channel),
            nn.Dropout(0.5),
            nn.LeakyReLU()
        )

    def forward(self, x):
        return self.layer(x)


class DownSample(nn.Module):
    def __init__(self, channel):
        super(DownSample, self).__init__()
        self.layer = nn.Sequential(
            nn.Conv2d(channel, channel, kernel_size=3, stride=2, padding=1, padding_mode='reflect', bias=0),  #这个2维卷积替代了最大池化
            nn.BatchNorm2d(channel),
            nn.LeakyReLU()
        )

    def forward(self, x):
        return self.layer(x)


class UpSample(nn.Module):
    def __init__(self, channel):
        super(UpSample, self).__init__()
        self.layer = nn.Conv2d(channel, channel//2, kernel_size=1, stride=1)

    def forward(self, x, feature_map):
        up = F.interpolate(x, scale_factor=2, mode='nearest')  #用最近邻插值代替转置卷积上采样
        out = self.layer(up)
        return torch.cat((out, feature_map), dim=1)


class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        self.c1 = Conv_Block(3, 64)
        self.d1 = DownSample(64)
        self.c2 = Conv_Block(64, 128)
        self.d2 = DownSample(128)
        self.c3 = Conv_Block(128, 256)
        self.d3 = DownSample(256)
        self.c4 = Conv_Block(256, 512)
        self.d4 = DownSample(512)
        self.c5 = Conv_Block(512, 1024)
        self.u1 = UpSample(1024)
        self.c6 = Conv_Block(1024, 512)
        self.u2 = UpSample(512)
        self.c7 = Conv_Block(512, 256)
        self.u3 = UpSample(256)
        self.c8 = Conv_Block(256, 128)
        self.u4 = UpSample(128)
        self.c9 = Conv_Block(128, 64)
        self.out = nn.Conv2d(64, 1, kernel_size=3, stride=1, padding=1)
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

# if __name__ == '__main__':
#     x = torch.randn(2, 3, 512, 512)
#     net = UNet()
#     print(net(x).shape)

# 初始化模型并迁移到正确的设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
fire_model = UNet().to(device)

# 输出模型的结构
summary(fire_model, (3, 512, 512))  # Correct input size (3 channels, 512x512)

