"""
该脚本用于计算反射图像在各边缘上的位置坐标。
"""

import cv2
import matplotlib.pyplot as plt


def detect_reflected_edges(image):
    """
    该函数用于裁剪掉分割图像中可能存在的绿色窗框部分。

    参数:
    - image: 分割且切除绿色边框后的图像。

    返回值:
    - edges: 反射图像在各边缘的坐标范围字典
    - image: 包含轮廓的图像。
    """

    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # otsu图像分割为前景和背景
    ret1, th1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

    # 找到图像的轮廓
    contours, _ = cv2.findContours(th1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 记录反射图像的边缘坐标
    edges = {'up': [], 'left': [], 'down': [], 'right': []}

    # 遍历轮廓
    for contour in contours:
        # 初始化边缘点
        up_points = []
        down_points = []
        left_points = []
        right_points = []

        for point in contour[:, 0]:  # 遍历轮廓上的点
            x, y = point[0], point[1]

            # 判断边缘方向
            if y == 0:
                up_points.append(x)
            elif y == image.shape[0] - 1:
                down_points.append(x)
            if x == 0:
                left_points.append(y)
            elif x == image.shape[1] - 1:
                right_points.append(y)

        # 更新边缘范围
        if up_points:
            min_x, max_x = min(up_points), max(up_points)
            if max_x - min_x >= 4:
                edges['up'].append((min_x, max_x))
        if left_points:
            min_y, max_y = min(left_points), max(left_points)
            if max_y - min_y >= 4:
                edges['left'].append((min_y, max_y))
        if down_points:
            min_x, max_x = min(down_points), max(down_points)
            if max_x - min_x >= 4:
                edges['down'].append((min_x, max_x))
        if right_points:
            min_y, max_y = min(right_points), max(right_points)
            if max_y - min_y >= 4:
                edges['right'].append((min_y, max_y))

    # 绘制轮廓
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

    return edges, image


# 测试
if __name__ == "__main__":
    image_path = 'crop/c1.png'
    # 读取图片文件
    image = cv2.imread(image_path)

    edges, image_with_contours = detect_reflected_edges(image)

    # 打印边缘信息
    print("|      | 反射图像边缘  |")
    print("| ---- | ------------- |")
    print(f"| 上   | {edges['up']}       |")
    print(f"| 左   | {edges['left']}       |")
    print(f"| 下   | {edges['down']}       |")
    print(f"| 右   | {edges['right']}       |")

    # 显示包含轮廓的图像
    plt.figure(figsize=(10, 5))
    plt.imshow(cv2.cvtColor(image_with_contours, cv2.COLOR_BGR2RGB))
    plt.title('Image with Contours')
    plt.axis('off')
    plt.show()
