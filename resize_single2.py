from PIL import Image, ImageDraw

def process_image(input_path, output_path, output_width, output_height, 
                  left_right_crop=60, top_bottom_crop=68):
    """
    处理图片：裁剪边缘并缩放到指定尺寸，空白处填充白色
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        output_width: 输出图片宽度
        output_height: 输出图片高度
        left_right_crop: 左右各裁剪的像素数 (默认60)
        top_bottom_crop: 上下各裁剪的像素数 (默认68)
    """
    # 打开图片
    img = Image.open(input_path)
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
    
    print(f"已将第45-50行的黑色像素替换为红色")

    # 旋转90度（逆时针）
    result = result.rotate(90, expand=True)
    print(f"旋转后尺寸: {result.size[0]} x {result.size[1]}")
    
    # 保存结果
    result.save(output_path, quality=99)
    print(f"处理完成，保存至: {output_path}")
    
    return result


# 使用示例
if __name__ == "__main__":
    # 修改这里的参数
    input_image = "../1208.jpg"      # 输入图片路径
    output_image = "output.jpg"    # 输出图片路径
    target_width = 300             # 输出宽度
    target_height = 400            # 输出高度
    
    try:
        process_image(
            input_image, 
            output_image, 
            output_width=target_width,
            output_height=target_height,
            left_right_crop=60, 
            top_bottom_crop=68
        )
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_image}'")
    except Exception as e:
        print(f"处理出错: {e}")
