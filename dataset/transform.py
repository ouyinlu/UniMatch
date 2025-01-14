import random

import numpy as np
from PIL import Image, ImageOps, ImageFilter
import torch
from torchvision import transforms
from PIL import Image, ImageOps, ImageFilter, ImageEnhance


def crop(img, mask, size,ignore_value):
    w, h = img.size
    padw = size - w if w < size else 0
    padh = size - h if h < size else 0
    img = ImageOps.expand(img, border=(0, 0, padw, padh), fill=0)
    mask = ImageOps.expand(mask, border=(0, 0, padw, padh), fill=ignore_value)

    w, h = img.size
    x = random.randint(0, w - size)
    y = random.randint(0, h - size)
    img = img.crop((x, y, x + size, y + size))
    mask = mask.crop((x, y, x + size, y + size))

    return img, mask


def hflip(img, mask, p=0.5):
    if random.random() < p:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
    return img, mask

def bflip(img, mask, p=0.5):
    if random.random() < p:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        mask = mask.transpose(Image.FLIP_TOP_BOTTOM)
    return img, mask

def normalize(img, mask=None):
    img = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])(img)
    if mask is not None:
        mask = torch.from_numpy(np.array(mask)).long()
        return img, mask
    return img


def resize(img, mask, ratio_range):
    w, h = img.size
    long_side = random.randint(int(max(h, w) * ratio_range[0]), int(max(h, w) * ratio_range[1]))

    if h > w:
        oh = long_side
        ow = int(1.0 * w * long_side / h + 0.5)
    else:
        ow = long_side
        oh = int(1.0 * h * long_side / w + 0.5)

    img = img.resize((ow, oh), Image.BILINEAR)
    mask = mask.resize((ow, oh), Image.NEAREST)
    return img, mask


def blur(img, p=0.5):
    if random.random() < p:
        sigma = np.random.uniform(0.1, 2.0)
        img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
    return img



def obtain_cutmix_box(img_size, p=0.5, size_min=0.02, size_max=0.4, ratio_1=0.3, ratio_2=1/0.3):
    mask = torch.zeros(img_size, img_size)
    if random.random() > p:
        return mask

    size = np.random.uniform(size_min, size_max) * img_size * img_size
    while True:
        ratio = np.random.uniform(ratio_1, ratio_2)
        cutmix_w = int(np.sqrt(size / ratio))
        cutmix_h = int(np.sqrt(size * ratio))
        x = np.random.randint(0, img_size)
        y = np.random.randint(0, img_size)

        if x + cutmix_w <= img_size and y + cutmix_h <= img_size:
            break

    mask[y:y + cutmix_h, x:x + cutmix_w] = 1

    return mask


#添加的weak数据增强方式



#添加的strong数据增强方式

#不做操作
def img_aug_identity(img, scale=None):
    return img

#对图像进行自动对比度操作
def img_aug_autocontrast(img, scale=None):
    return ImageOps.autocontrast(img)

# 进行直方图均衡化操作
def img_aug_equalize(img, scale=None):
    return ImageOps.equalize(img)

#反转操作
def img_aug_invert(img, scale=None):
    return ImageOps.invert(img)

#高斯平滑
def img_aug_blur(img, scale=[0.1, 2.0]):
    assert scale[0] < scale[1]
    sigma = np.random.uniform(scale[0], scale[1])
    # print(f"sigma:{sigma}")
    return img.filter(ImageFilter.GaussianBlur(radius=sigma))

# 对比度增强
def img_aug_contrast(img, scale=[0.05, 0.95]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    v = max_v - v
    # # print(f"final:{v}")
    # v = np.random.uniform(scale[0], scale[1])
    return ImageEnhance.Contrast(img).enhance(v)

# 亮度增强
def img_aug_brightness(img, scale=[0.05, 0.95]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    v = max_v - v
    # print(f"final:{v}")
    return ImageEnhance.Brightness(img).enhance(v)

# 颜色增强
def img_aug_color(img, scale=[0.05, 0.95]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    v = max_v - v
    # print(f"final:{v}")
    return ImageEnhance.Color(img).enhance(v)

#锐化
def img_aug_sharpness(img, scale=[0.05, 0.95]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    v = max_v - v
    # print(f"final:{v}")
    return ImageEnhance.Sharpness(img).enhance(v)


def img_aug_hue(img, scale=[0, 0.5]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    v += min_v
    if np.random.random() < 0.5:
        hue_factor = -v
    else:
        hue_factor = v
    # print(f"Final-V:{hue_factor}")
    input_mode = img.mode
    if input_mode in {"L", "1", "I", "F"}:
        return img
    h, s, v = img.convert("HSV").split()
    np_h = np.array(h, dtype=np.uint8)
    # uint8 addition take cares of rotation across boundaries
    with np.errstate(over="ignore"):
        np_h += np.uint8(hue_factor * 255)
    h = Image.fromarray(np_h, "L")
    img = Image.merge("HSV", (h, s, v)).convert(input_mode)
    return img


# 减少图像颜色深度
def img_aug_posterize(img, scale=[4, 8]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    # print(min_v, max_v, v)
    v = int(np.ceil(v))
    v = max(1, v)
    v = max_v - v
    # print(f"final:{v}")
    return ImageOps.posterize(img, v)

# 图像中的像素颜色值反转
def img_aug_solarize(img, scale=[1, 256]):
    min_v, max_v = min(scale), max(scale)
    v = float(max_v - min_v)*random.random()
    # print(min_v, max_v, v)
    v = int(np.ceil(v))
    v = max(1, v)
    v = max_v - v
    # print(f"final:{v}")
    return ImageOps.solarize(img, v)

# 随机灰度化
def ima_aug_RandomGrayscale(img,scale = None):
    img = transforms.RandomGrayscale(p=0.2)(img)
    return img
#边界增强
def img_aug_edge_enhence(img,scale = None):
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    return img


#图像旋转
def Rotate(img, mask, p=0.5):
        return img, mask

def Rotate_90(img, mask, p=0.5):
    if random.random() < p:
        v = 90
        return img.rotate(v), mask.rotate(v)
    else:
        return img, mask

def Rotate_180(img, mask, p=0.5):
    if random.random() < p:
        v = 180
        return img.rotate(v), mask.rotate(v)
    else:
        return img, mask

def Rotate_270(img, mask, p=0.5):
    if random.random() < p:
        v = 270
        return img.rotate(v), mask.rotate(v)
    else:
        return img, mask

def ima_aug_geometric_transformation(img, mask):
    # img, mask = bflip(img, mask, p=0.1)
    img, mask = Rotate(img, mask, p=0.5)
    img, mask = Rotate_90(img, mask, p=0.5)
    img, mask = Rotate_180(img, mask, p=0.5)
    img, mask = Rotate_270(img, mask, p=0.5)
    # img, mask = shearX(img, mask, p=0.5)
    # img, mask = translateX(img, mask, p=0.5)

    return img, mask

def get_augment_list(flag_using_wide=False):  
    if flag_using_wide:
        l = [
        #不做操作
        (img_aug_identity, None),
        #对图像进行自动对比度操作
        (img_aug_autocontrast, None), 
        # 进行直方图均衡化操作
        (img_aug_equalize, None),
        #高斯平滑
        (img_aug_blur, [0.1, 2.0]),
        #对比度增强
        (img_aug_contrast, [0.1, 1.8]),
        #亮度增强
        (img_aug_brightness, [0.1, 1.8]),
        #颜色增强
        (img_aug_color, [0.1, 1.8]),
        #锐化
        (img_aug_sharpness, [0.1, 1.8]),
        #减少颜色深度
        (img_aug_posterize, [2, 8]),
        # 像素颜色值反转
        (img_aug_solarize, [1, 256]),

        (img_aug_hue, [0, 0.5]),
        #边界增强
        (img_aug_edge_enhence, None),
        #灰度化
        (ima_aug_RandomGrayscale, None)
        ]
    else:
             l = [
        #不做操作
        (img_aug_identity, None),
        #对图像进行自动对比度操作
        (img_aug_autocontrast, None), 
        # 进行直方图均衡化操作
        (img_aug_equalize, None),
        #高斯平滑
        # (img_aug_blur, [0.1, 2.0]),
        #对比度增强
        (img_aug_contrast, [0.1, 1.8]),
        #亮度增强
        (img_aug_brightness, [0.1, 1.8]),
        #颜色增强
        (img_aug_color, [0.1, 1.8]),
        #锐化
        (img_aug_sharpness, [0.1, 1.8]),
        #减少颜色深度
        (img_aug_posterize, [2, 8]),
        # 像素颜色值反转
        (img_aug_solarize, [1, 256]),
        
        (img_aug_hue, [0, 0.5]),
        #边界增强
        (img_aug_edge_enhence, None),
        #灰度化
        (ima_aug_RandomGrayscale, None)
        ]
    return l

    
def agumentation(img,num_augs = 3,flag_using_random_num=False,flag_using_wide= False, augment_list = None):
    if flag_using_random_num:
        max_num = np.random.randint(1, high=num_augs + 1)
    else:
        max_num = num_augs
    augment_list = get_augment_list(flag_using_wide)
    ops = random.choices(augment_list, k=max_num)
    for op, scales in ops:
        # print("="*20, str(op))
        img = op(img, scales)
    return img
