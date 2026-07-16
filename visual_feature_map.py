import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

# =========================
# 1. 模型定义
# =========================
class scenesize_model(nn.Module):
    def __init__(self, num_classes=3):
        super(scenesize_model, self).__init__()
        self.backbone = models.resnet18(weights=None)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.backbone(x)

# =========================
# 2. 加载模型
# =========================
model = scenesize_model(num_classes=3)
model_path = r'D:\Python\Text\unet\train\size_pt\size_model_8.pt'
model.load_state_dict(torch.load(model_path, weights_only=True))
model.eval()

# =========================
# 3. 加载图片
# =========================
image_path = r'scene_size_judgment_dataset/train/mid_scene/fire_image_1_00323.jpg'
image = Image.open(image_path).convert('RGB')

transform = transforms.Compose([
    transforms.Resize((640, 640)),
    transforms.ToTensor(),
])

input_tensor = transform(image).unsqueeze(0)

# =========================
# 4. Grad-CAM 核心函数
# =========================
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.feature_maps = None
        self.gradients = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.feature_maps = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(self, input_tensor, class_idx=None):
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()

        self.model.zero_grad()
        class_score = output[0, class_idx]
        class_score.backward()

        gradients = self.gradients.detach().cpu().numpy()[0]  # [C, H, W]
        feature_maps = self.feature_maps.detach().cpu().numpy()[0]  # [C, H, W]

        weights = np.mean(gradients, axis=(1, 2))  # 每个通道的平均权重
        cam = np.zeros(feature_maps.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            cam += w * feature_maps[i]

        cam = np.maximum(cam, 0)  # ReLU
        cam = cv2.resize(cam, (640, 640))  # 调整为输入图片大小
        cam = cam - np.min(cam)
        cam = cam / np.max(cam)
        return cam, class_idx

# =========================
# 5. 执行 Grad-CAM
# =========================
target_layer = model.backbone.layer4
grad_cam = GradCAM(model, target_layer)
cam, predicted_class = grad_cam.generate_cam(input_tensor)

# =========================
# 6. 显示原图 + 热力图对比
# =========================
def show_cam_with_original(img, mask, predicted_class):
    # 调整原图尺寸，确保和热力图一致
    img_resized = img.resize((640, 640))
    img_np = np.array(img_resized).astype(np.float32) / 255.0

    heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
    heatmap = np.float32(heatmap) / 255
    cam = heatmap + img_np
    cam = cam / np.max(cam)

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(img_np)
    plt.title('Original Image')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cam)
    plt.title(f'Grad-CAM Heatmap (Predicted Class: {predicted_class})')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

# =========================
# 7. 执行显示
# =========================
show_cam_with_original(image, cam, predicted_class)
