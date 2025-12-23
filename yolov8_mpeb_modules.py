import torch
import torch.nn as nn
from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.block import Bottleneck

class SELayer(nn.Module):
    def __init__(self, channel, reduction=4):
        super(SELayer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Hardsigmoid(inplace=True),
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y

class MobileNetBlock(nn.Module):
    def __init__(self, c1, c2, k, s, er, se, act=0):
        super().__init__()
        self.use_res_connect = s == 1 and c1 == c2
        hidden_dim = int(round(c1 * er))
        layers = []
        if er != 1:
            layers.append(Conv(c1, hidden_dim, 1, 1, None, g=1, act=nn.ReLU() if act==0 else nn.Hardsigmoid()))
        layers.append(Conv(hidden_dim, hidden_dim, k, s, g=hidden_dim, act=nn.ReLU() if act==0 else nn.Hardsigmoid()))
        if se:
            layers.append(SELayer(hidden_dim))
        layers.append(Conv(hidden_dim, c2, 1, 1, None, g=1, act=False))
        self.conv = nn.Sequential(*layers)

    def forward(self, x):
        return x + self.conv(x) if self.use_res_connect else self.conv(x)

class EMA(nn.Module):
    def __init__(self, channels, factor=32):
        super(EMA, self).__init__()
        self.groups = factor
        if channels < self.groups: self.groups = channels
        while self.groups > 0 and channels % self.groups != 0: self.groups -= 1
        if self.groups < 1: self.groups = 1
        self.softmax = nn.Softmax(dim=-1)
        self.agp = nn.AdaptiveAvgPool2d((1, 1))
        self.pool_h = nn.AdaptiveAvgPool2d((None, 1))
        self.pool_w = nn.AdaptiveAvgPool2d((1, None))
        self.gn = nn.GroupNorm(channels // self.groups, channels // self.groups)
        self.conv1x1 = nn.Conv2d(channels // self.groups, channels // self.groups, kernel_size=1, stride=1, padding=0)
        self.conv3x3 = nn.Conv2d(channels // self.groups, channels // self.groups, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        b, c, h, w = x.size()
        group_x = x.reshape(b * self.groups, -1, h, w)
        x_h = self.pool_h(group_x)
        x_w = self.pool_w(group_x).permute(0, 1, 3, 2)
        hw = self.conv1x1(torch.cat([x_h, x_w], dim=2))
        x_h, x_w = torch.split(hw, [h, w], dim=2)
        x1 = self.gn(group_x * x_h.sigmoid() * x_w.permute(0, 1, 3, 2).sigmoid())
        x2 = self.conv3x3(group_x)
        x11 = self.softmax(self.agp(x1).reshape(b * self.groups, -1, 1).permute(0, 2, 1))
        x12 = x2.reshape(b * self.groups, c // self.groups, -1)
        x21 = self.softmax(self.agp(x2).reshape(b * self.groups, -1, 1).permute(0, 2, 1))
        x22 = x1.reshape(b * self.groups, c // self.groups, -1)
        weights = (torch.matmul(x11, x12) + torch.matmul(x21, x22)).reshape(b * self.groups, 1, h, w)
        return (group_x * weights.sigmoid()).reshape(b, c, h, w)

class C2f_EMA(nn.Module):
    def __init__(self, c1, c2, n=1, shortcut=False, g=1, e=0.5):
        super().__init__()
        self.c = int(c2 * e)
        self.cv1 = Conv(c1, 2 * self.c, 1, 1)
        self.cv2 = Conv((2 + n) * self.c, c2, 1)
        self.m = nn.ModuleList(Bottleneck(self.c, self.c, shortcut, g, k=((3, 3), (3, 3)), e=1.0) for _ in range(n))
        self.ema = EMA((2 + n) * self.c)

    def forward(self, x):
        y = list(self.cv1(x).chunk(2, 1))
        y.extend(m(y[-1]) for m in self.m)
        z = torch.cat(y, 1)
        z = self.ema(z)
        return self.cv2(z)

class BiFPN_Concat(nn.Module):
    def __init__(self, dimension=1):
        super().__init__()
        self.d = dimension
        self.w = nn.Parameter(torch.ones(5, dtype=torch.float32), requires_grad=True)
        self.epsilon = 1e-4

    def forward(self, x):
        if isinstance(x, list):
            n = len(x)
            weights = self.w[:n].relu()
            weights = weights / (weights.sum() + self.epsilon)
            return torch.cat([x[i] * weights[i] for i in range(n)], self.d)
        else:
            return x
