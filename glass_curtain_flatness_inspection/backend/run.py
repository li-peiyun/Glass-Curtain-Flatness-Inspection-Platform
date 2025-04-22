import subprocess
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


# 结构胶检测
def detect_border(image_path, save_dir="output"):
    # 提取文件名（不包含扩展名）
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    # 构建结果保存路径
    result_path = os.path.join(save_dir, f"{base_filename}.png")

    # 构建推理命令
    command = f"python deploy/python/infer.py --config inference_model/deploy.yaml --image_path {image_path} --save_dir {save_dir}"

    try:
        subprocess.run(command, shell=True, check=True)
        print("Inference completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during inference: {e}")

    border_image = cv2.imread(result_path)

    # 返回结果保存路径
    return border_image


# 反射景物提取
def detect_reflected(image_path):
    # 读取图片文件
    image = cv2.imread(image_path)

    # cv2.COLOR_BGR2GRAY 将BGR格式转换成灰度图片
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # otsu图像分割为前景和背景
    ret1, th1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

    # 提取反射（背景）部分
    reflect_image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(th1))

    # 返回反射提取图片
    return reflect_image


# 处理图片的主要函数
def preprocess_image(image_name):
    # 设置图片路径
    image_path = os.path.join("uploads", image_name)

    # 结构胶检测，返回结果图片路径
    border_image = detect_border(image_path)

    # 玻璃反射景物提取
    reflect_image = detect_reflected(image_path)

    # 读取原始图像和检测结果图像
    original_image = cv2.imread(image_path)

    # 将图像转换为HSV颜色空间
    hsv = cv2.cvtColor(border_image, cv2.COLOR_BGR2HSV)

    # 设定绿色的HSV范围
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # 根据阈值获取绿色区域的掩码
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # 找到绿色区域的轮廓
    contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 创建新图像，将检测结果覆盖在原始图像上
    overlay_result_on_original = np.copy(reflect_image)
    overlay_result_on_original[border_image[:, :, 1] > 0] = border_image[border_image[:, :, 1] > 0]

    # 返回处理后的图片
    return overlay_result_on_original


# 测试部分
if __name__ == "__main__":
    # 设置图片名称
    image_name = "test1.png"

    # 处理图片
    result_image = preprocess_image(image_name)

    # 显示处理后的图片
    cv2.namedWindow('detected image', cv2.WINDOW_NORMAL)
    cv2.imshow("detected image", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
