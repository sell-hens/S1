# ====================Begin===================
import warnings
warnings.filterwarnings("ignore", message=".*pretrained.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*weights.*", category=UserWarning)
import torch
import os
import glob
from torchvision import transforms, models
from PIL import Image

# ==================== 1. 图片加载 ====================
''' 图片路径'''
img_dir = "img"
img_paths = sorted(glob.glob(os.path.join(img_dir, "*")))

#  请在此处编写代码，实现使用预训练 ResNet18 模型对图像进行分类
# ====================Begin===================

# ==================== 2. 图像预处理 ====================
# 预训练模型 ResNet18 期望 224x224, RGB, 并进行标准化
'''定义三个转换到Compose方法'''
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406],
                        std=[0.229,0.224,0.225])
])

# ==================== 3. 模型加载 ====================
model = models.resnet18(pretrained=True)
model.eval()#测试状态  #进入状态

# ==================== 4. ImageNet 标签映射====================
labels = []
with open("imagenet_classes.txt")as f:
    labels = [line.strip() for line in f.readlines()]#获取标签

# ==================== 5. 批量图片推理 ====================
for img_path in img_paths:#逐个处理
    img = Image.open(img_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0)#添加batch维度
    with torch.no_grad():#不进行反向传播调整参数
        output = model(img_tensor)#传入model模型进行传递获取返回值
        pred_class = torch.argmax(output,dim=1).item()#寻找最可能性分类概率（不确定度）
        pred_label = labels[pred_class]

    print(f"{img_path} --> Predicted class: {pred_label}")

# ====================End===================

