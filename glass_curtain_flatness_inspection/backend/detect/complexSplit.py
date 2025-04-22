"""
      额外的分割方法尝试：
      1. 先进行垂直线分割
      2. 进行水平线分割
      垂直线分割需要避免相邻边框的影响 → 目前来看阈值为180的效果比较好

      函数说明：
      add_column : 进行邻接矩阵的形成

      filter_close_lines(line,min_distance)
        传入检测到的线的集合和线之间的最小距离，进行筛选
        ** mark ：如果分割有问题，就调整 min_distance **

     find_lines(image, orientation='vertical', line_length=100, line_gap=5, min_distance = 180)
        根据图像和查找方向【水平 / 垂直】，返回对应的直线
        min_distance和filter_close_lines的传参对应的

    crop_images_by_orientation()
        裁剪得到图像
"""


import cv2
import numpy as np
import matplotlib.pyplot as plt


def add_column(matrix, new_col):
    if matrix.size == 0:
        # 如果矩阵是空的，初始化矩阵为第一列
        matrix = np.array(new_col).reshape(-1, 1)
    else:
        # 如果矩阵已经有数据，按列堆叠
        new_col = np.array(new_col).reshape(-1, 1)
        matrix = np.hstack((matrix, new_col))

    return matrix


# 过滤掉接近的边线
def filter_close_lines(lines, min_distance):
    """过滤掉距离过近的垂直线"""
    if not lines:
        return []

    # 首先按位置排序
    sorted_lines = sorted(lines)

    # 过滤过近的线
    filtered_lines = [sorted_lines[0]]  # 添加第一条线
    for line in sorted_lines[1:]:
        if line - filtered_lines[-1] >= min_distance:
            filtered_lines.append(line)
    return filtered_lines


# 按照水平和竖直，利用Canny检测去查找边缘线
def find_lines(image, orientation='vertical', line_length=100, line_gap=5, min_distance = 180):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 根据方向调整霍夫变换的角度范围
    theta = np.pi / 180 if orientation == 'vertical' else np.pi / 2

    lines = cv2.HoughLinesP(edges, 1, theta, 80, minLineLength=line_length, maxLineGap=line_gap)

    line_positions = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if orientation == 'vertical' and abs(x2 - x1) < 10:  # 垂直线
                line_positions.append((x1 + x2) // 2)
            elif orientation == 'horizontal' and abs(y2 - y1) < 10:  # 水平线
                line_positions.append((y1 + y2) // 2)

    # 排序并过滤掉过于接近的线
    return sorted(filter_close_lines(line_positions, min_distance))


# 裁剪得到对应的图片，并进行返回
def crop_images_by_orientation(image, line_positions, orientation):
    cropped_images = []
    start = 0

    for pos in line_positions:
        if orientation == 'vertical':
            cropped_images.append(image[:, start:pos])
        elif orientation == 'horizontal':
            cropped_images.append(image[start:pos, :])
        start = pos

    # 添加最后一个区域
    if orientation == 'vertical':
        cropped_images.append(image[:, start:])
    elif orientation == 'horizontal':
        cropped_images.append(image[start:, :])

    return cropped_images


# 多层次的复杂分割函数实现
def complexSplit(image):
    """
    该函数用于将玻璃幕墙图像分割为一扇扇窗户。

    参数:
    - image: 玻璃幕墙图像（已完成反射分割和边框检测）。

    返回值:
    - cropped_images: 裁剪后的窗户图像列表。
    - cropped_positions: 裁剪后的窗户位置信息 (x, y) 列表。
    - adjacency_dict: 图片的邻接关系字典列表。
    """
    # 先进行垂直分割
    vertical_lines = find_lines(image, 'vertical', min_distance=1800)

    # 打印垂直分割线
    # print(vertical_lines)

    # 得到列数
    col = len(vertical_lines) - 1

    # 裁剪图像
    vertically_cropped_images = crop_images_by_orientation(image, vertical_lines, 'vertical')

    # 移除掉两侧的图像
    if len(vertically_cropped_images) >= 2:
        vertically_cropped_images.pop(0)
        vertically_cropped_images.pop(-1)

    # 存储所有分割后的图片
    cropped_images = []

    # 存储每个分割后玻璃的位置信息，格式(x, y)
    cropped_positions = []

    # 存储每个分割后玻璃的邻接关系
    adjacency_dict = []

    # 对每个垂直分割的部分应用水平分割
    for col_idx, v_img in enumerate(vertically_cropped_images):
        # 该列玻璃的x和w
        x = vertical_lines[col_idx]

        # 得到水平分割线
        horizontal_lines = find_lines(v_img, 'horizontal', min_distance=500)

        # 打印水平分割线
        # print(horizontal_lines)

        # 得到行数
        row = len(horizontal_lines) - 1

        horizontally_cropped_images = crop_images_by_orientation(v_img, horizontal_lines, 'horizontal')

        # 移除两端的图像
        if len(horizontally_cropped_images) >= 2:
            horizontally_cropped_images.pop(0)
            horizontally_cropped_images.pop(-1)

        # 将得到的裁剪后的图片保存
        for row_idx, h_img in enumerate(horizontally_cropped_images):
            # 当前图片在总裁剪图片列表中的下标
            idx = len(cropped_images)

            # 将该分割后图片添加进cropped_images
            cropped_images.append(h_img)

            # 得到该玻璃的y和h
            y = horizontal_lines[row_idx]

            # 将该分割后图片的位置信息添加进cropped_positions
            cropped_positions.append((x, y))
            # print(cropped_positions[idx])

            # 该分割后图片的邻接关系
            adjacency = {'left': [], 'right': [], 'up': [], 'down': []}
            # 左邻接
            if col_idx > 0:
                adjacency['left'].append(idx - row)
            # 右邻接
            if col_idx < col - 1:
                adjacency['right'].append(idx + row)
            # 上邻接
            if row_idx > 0:
                adjacency['up'].append(idx - 1)
            # 下邻接
            if row_idx < row - 1:
                adjacency['down'].append(idx + 1)
            # 将该分割后图片的邻接关系添加进adjacency_dict
            adjacency_dict.append(adjacency)
            # print(adjacency_dict[idx])

    return cropped_images, cropped_positions, adjacency_dict


if __name__ == "__main__":
    file_path = "data/test1.png"
    image = cv2.imread(file_path)

    # 分割图片
    cropped_images, cropped_positions, adjacency_dict = complexSplit(image)

    for idx, img in enumerate(cropped_images):
        print("第", idx, "张分割照片：")
        cv2.imshow("split", img)
        print("位置信息：", cropped_positions[idx])
        print("邻接关系：", adjacency_dict[idx])
        cv2.waitKey(0)





