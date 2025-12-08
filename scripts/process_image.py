#!/usr/bin/env python3
"""
每日图片处理脚本
从 owspace.com 获取当日图片，处理后保存到 images/latest.jpg
"""

import os
import requests
from datetime import datetime, timezone, timedelta
from PIL import Image
from io import BytesIO


def get_today_image_url():
    """根据当前 UTC 日期生成图片 URL"""
    now = datetime.now(timezone.utc) + timedelta(days=1)
    year = now.strftime("%Y")
    month_day = now.strftime("%m%d")
    url = f"https://img.owspace.com/Public/uploads/Download/{year}/{month_day}.jpg"
    return url


def download_image(url):
    """下载图片并返回 PIL Image 对象"""
    print(f"正在下载图片: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    img = Image.open(BytesIO(response.content))
    print(f"下载成功，原始尺寸: {img.size[0]} x {img.size[1]}")
    return img


def process_image(img, output_width=300, output_height=400,
                  left_right_crop=60, top_bottom_crop=68):
    """
    处理图片：裁剪边缘并缩放到指定尺寸，空白处填充白色
    
    参数:
        img: PIL Image 对象
        output_width: 输出图片宽度
        output_height: 输出图片高度
        left_right_crop: 左右各裁剪的像素数 (默认60)
        top_bottom_crop: 上下各裁剪的像素数 (默认68)
    """
    original_width, original_height = img.size
    
    print(f"原始尺寸: {original_width} x {original_height}")
    print(f"目标尺寸: {output_width} x {output_height}")
    
    # 裁剪图片 (左, 上, 右, 下)
    crop_box = (
        left_right_crop,  # 左边裁剪
        top_bottom_crop,  # 上边裁剪
        original_width - left_right_crop,  # 右边裁剪
        original_height - top_bottom_crop  # 下边裁剪
    )
    
    cropped_img = img.crop(crop_box)
    cropped_width, cropped_height = cropped_img.size
    
    print(f"裁剪后尺寸: {cropped_width} x {cropped_height}")
    
    # 创建白色背景画布（指定输出尺寸）
    result = Image.new('RGB', (output_width, output_height), 'white')
    
    # 计算缩放比例，确保裁剪后的图片能完全放入输出尺寸
    scale_x = output_width / cropped_width
    scale_y = output_height / cropped_height
    scale = min(scale_x, scale_y)  # 使用较小的比例，确保不超出边界
    
    # 缩放裁剪后的图片
    new_width = int(cropped_width * scale)
    new_height = int(cropped_height * scale)
    scaled_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    print(f"缩放后尺寸: {new_width} x {new_height}")
    
    # 计算居中位置
    x = (output_width - new_width) // 2
    y = (output_height - new_height) // 2
    
    # 将缩放后的图片粘贴到白色背景上（居中）
    result.paste(scaled_img, (x, y))

    # 在旋转之前，将第45-50行的黑色像素变为红色
    pixels = result.load()
    for row in range(45, 215):  # 第45-50行（索引从0开始，所以是44-49）
        if row < result.height:  # 确保不超出图片高度
            for col in range(result.width):
                r, g, b = pixels[col, row]
                # 判断是否为黑色（接近黑色的像素）
                if r < 50 and g < 50 and b < 50:
                    pixels[col, row] = (255, 0, 0)  # 红色

    # 旋转90度（逆时针）
    result = result.rotate(90, expand=True)
    print(f"旋转后尺寸: {result.size[0]} x {result.size[1]}")
    
    return result


def main():
    # 确保输出目录存在
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    output_dir = os.path.join(repo_root, "images")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "latest.jpg")
    
    try:
        # 获取当日图片 URL
        url = get_today_image_url()
        
        # 下载图片
        img = download_image(url)
        
        # 处理图片
        result = process_image(
            img,
            output_width=300,
            output_height=400,
            left_right_crop=60,
            top_bottom_crop=68
        )
        
        # 保存结果
        result.save(output_path, quality=99)
        print(f"处理完成，保存至: {output_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"下载图片失败: {e}")
        raise
    except Exception as e:
        print(f"处理出错: {e}")
        raise


if __name__ == "__main__":
    main()

