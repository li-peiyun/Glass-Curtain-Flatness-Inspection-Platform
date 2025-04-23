"""
该脚本用于读取玻璃幕墙图像，判断相邻玻璃反射图像边缘坐标范围是否匹配。
方法二：边缘色度比较
"""

import cv2
import numpy as np
from .complexSplit import complexSplit
from .crop import crop_green_edges


def match_edges_by_chroma(image1, image2, direction, offset=30, sample_points=100, chroma_threshold=0.5):
    """
    该函数用于比较两个相邻玻璃的反射边缘是否一致，通过比较色度信息。


    参数:
    - image1: 第一个玻璃的图像。
    - image2: 第二个玻璃的图像。
    - direction: 当前玻璃需要检测的边缘方向。
    - offset: 边缘偏移量，默认值为30。
    - sample_points: 在边缘上均匀选取的点数，默认值为100。
    - chroma_threshold: 无反射区域色度的阈值上限，默认值为0.5。

    返回值:
    - 反射边缘一致返回 True，不一致返回 False。
    """

    # 定义色度提取函数
    def extract_chroma(image, points):
        chroma_values = []
        for point in points:
            b, g, r = image[point[1], point[0]].astype(float)
            chroma = np.sqrt((r - g) ** 2 + (g - b) ** 2 + (b - r) ** 2)
            chroma_values.append(chroma)
        return chroma_values

    # 获取图像的边缘坐标
    height1, width1 = image1.shape[:2]
    height2, width2 = image2.shape[:2]

    # print("direction:", direction)

    if direction == 'up':
        # 获取上边缘
        edge1 = [(x, offset) for x in range(width1)]  # 上玻璃的下边缘向上偏移
        edge2 = [(x, height2 - offset - 1) for x in range(width2)]  # 下玻璃的上边缘向下偏移

    elif direction == 'down':
        # 获取下边缘
        edge1 = [(x, height1 - offset - 1) for x in range(width1)]  # 下玻璃的上边缘向下偏移
        edge2 = [(x, offset) for x in range(width2)]  # 上玻璃的下边缘向上偏移

    elif direction == 'left':
        # 获取左边缘
        edge1 = [(offset, y) for y in range(height1)]  # 左玻璃的右边缘向左偏移
        edge2 = [(width2 - offset - 1, y) for y in range(height2)]  # 右玻璃的左边缘向右偏移

    elif direction == 'right':
        # 获取右边缘
        edge1 = [(width1 - offset - 1, y) for y in range(height1)]  # 右玻璃的左边缘向右偏移
        edge2 = [(offset, y) for y in range(height2)]  # 左玻璃的右边缘向左偏移

    else:
        return None

    # 在边缘上均匀选取点
    step1 = max(1, len(edge1) // sample_points)
    step2 = max(1, len(edge2) // sample_points)
    sampled_points1 = edge1[::step1][:sample_points]
    sampled_points2 = edge2[::step2][:sample_points]

    # 提取色度信息
    chroma1 = extract_chroma(image1, sampled_points1)
    chroma2 = extract_chroma(image2, sampled_points2)

    # 比较色度信息
    matches = 0
    for (c1, c2), (p1, p2) in zip(zip(chroma1, chroma2), zip(sampled_points1, sampled_points2)):
        # 都为玻璃区域或都为反射区域
        if (c1 < chroma_threshold and c2 < chroma_threshold) or (c1 >= chroma_threshold and c2 >= chroma_threshold):
            matches += 1
            # print(f"色度一致: 点1 ({p1}) - 点2 ({p2}), 色度1: {c1}, 色度2: {c2}")
        # else:
        #     print(f"色度不一致: 点1 ({p1}) - 点2 ({p2}), 色度1: {c1}, 色度2: {c2}")

    if matches / sample_points > 0.9:  # 90% 以上的点色度一致
        return True, sampled_points1, sampled_points2
    else:
        return False, sampled_points1, sampled_points2


def match_two_edge(image, positions, adjacents, idx, direction, labeled_image=None):
    """
    该函数用于比较两个相邻玻璃的反射边缘是否一致。

    参数:
    - image: 原始图像。
    - positions: 所有玻璃的绝对位置。
    - adjacents: 当前玻璃的邻接关系。
    - idx:       当前玻璃的边缘反射图像坐标。
    - direction: 当前玻璃需要检测的边缘方向。
    - labeled_image: 标注后的图像，默认为 None。

    返回值:
    - 反射边缘一致返回 True，不一致返回 False，没有邻接玻璃返回 None
    """

    # 检查两个边缘是否有邻接
    for adjacent in adjacents[direction]:
        # 只检测坐标大于当前图像的，避免重复检测
        if adjacent > idx:
            # 获取当前玻璃和邻接玻璃的位置信息
            pos_x1, pos_y1, pos_w1, pos_h1 = positions[idx]
            pos_x2, pos_y2, pos_w2, pos_h2 = positions[adjacent]

            # 获取当前玻璃和邻接玻璃的图像
            cur_image = image[pos_y1:pos_y1 + pos_h1, pos_x1:pos_x1 + pos_w1]
            adj_image = image[pos_y2:pos_y2 + pos_h2, pos_x2:pos_x2 + pos_w2]

            # 比较色度信息
            result, sampled_points1, sampled_points2 = match_edges_by_chroma(cur_image, adj_image, direction)

            # 标注边缘线
            if labeled_image is not None:
                if direction == 'up':
                    for x, y in sampled_points1:
                        cv2.circle(labeled_image, (pos_x1 + x, pos_y1 + y), 6, (0, 255, 255), -1)  # 黄色点
                    for x, y in sampled_points2:
                        cv2.circle(labeled_image, (pos_x2 + x, pos_y2 + y), 6, (255, 0, 0), -1)  # 蓝色点
                elif direction == 'down':
                    for x, y in sampled_points1:
                        cv2.circle(labeled_image, (pos_x1 + x, pos_y1 + y), 6, (0, 255, 255), -1)  # 黄色点
                    for x, y in sampled_points2:
                        cv2.circle(labeled_image, (pos_x2 + x, pos_y2 + y), 6, (255, 0, 0), -1)  # 蓝色点
                elif direction == 'left':
                    for x, y in sampled_points1:
                        cv2.circle(labeled_image, (pos_x1 + x, pos_y1 + y), 6, (0, 255, 255), -1)  # 黄色点
                    for x, y in sampled_points2:
                        cv2.circle(labeled_image, (pos_x2 + x, pos_y2 + y), 6, (255, 0, 0), -1)  # 蓝色点
                elif direction == 'right':
                    for x, y in sampled_points1:
                        cv2.circle(labeled_image, (pos_x1 + x, pos_y1 + y), 6, (0, 255, 255), -1)  # 黄色点
                    for x, y in sampled_points2:
                        cv2.circle(labeled_image, (pos_x2 + x, pos_y2 + y), 6, (255, 0, 0), -1)  # 蓝色点

            # 显示标注后的图像
            # if labeled_image is not None:
            #     window_name = f'Comparing Edge {idx} and {adjacent} ({direction})'
            #     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            #     cv2.resizeWindow(window_name, 800, 600)
            #     cv2.imshow(window_name, labeled_image)
            #     cv2.waitKey(0)
            #     cv2.destroyWindow(window_name)

            if result is True:
                # print(idx, "号玻璃和", adjacent, "号玻璃反射边缘一致！")
                return True
            else:
                # print(idx, "号玻璃和", adjacent, "号玻璃反射边缘不一致！")
                return False

    return None


def match_reflected_edges_by_chroma(image):
    # 获取分割后的玻璃图像并得到邻接关系字典
    cropped_images, cropped_positions, adjacency_dict = complexSplit(image)

    # 各玻璃的位置信息
    positions = []

    for idx, img in enumerate(cropped_images):
        # 切除绿色边框
        cropped_img, relative_position = crop_green_edges(img)

        # 计算位置信息
        x, y = cropped_positions[idx]
        relative_x, relative_y, w, h = relative_position
        positions.append((x + relative_x, y + relative_y, w, h))

    # 比较相邻图像的反射图像边缘坐标范围是否一致
    results = []
    labeled_image = image.copy()

    for idx in range(len(adjacency_dict)):
        # 得到该图像的邻接关系
        adjacents = adjacency_dict[idx]

        # 邻接方向
        directions = ['up', 'down', 'left', 'right']

        # 检测各方向邻接玻璃反射边缘是否一致
        for direction in directions:
            result = match_two_edge(image, positions, adjacents, idx, direction, labeled_image=labeled_image)
            # 存在邻接关系
            if result is True or result is False:
                # 反射边缘一致
                if result is True:
                    results.append((idx, adjacents[direction][0], True))
                # 反射边缘不一致
                else:
                    results.append((idx, adjacents[direction][0], False))

                # 标注当前玻璃
                pos_x, pos_y, pos_w, pos_h = positions[idx]
                cv2.rectangle(labeled_image, (pos_x, pos_y), (pos_x + pos_w, pos_y + pos_h), (255, 255, 100), 16)
                # 计算当前玻璃边框的中心位置
                center_x = pos_x + pos_w // 2
                center_y = pos_y + pos_h // 2
                text_size, _ = cv2.getTextSize(str(idx), cv2.FONT_HERSHEY_SIMPLEX, 4, 10)
                text_width, text_height = text_size
                cv2.putText(labeled_image, str(idx), (center_x - text_width // 2, center_y + text_height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 100), 10, cv2.LINE_AA)

        # 标注相邻玻璃
        for direction in directions:
            if direction in adjacents and adjacents[direction]:
                adjacent = adjacents[direction][0]
                if adjacent > idx:
                    adj_x, adj_y, adj_w, adj_h = positions[adjacent]
                    cv2.rectangle(labeled_image, (adj_x, adj_y), (adj_x + adj_w, adj_y + adj_h), (255, 255, 100), 16)
                    # 计算相邻玻璃边框的中心位置
                    adj_center_x = adj_x + adj_w // 2
                    adj_center_y = adj_y + adj_h // 2
                    text_size, _ = cv2.getTextSize(str(adjacent), cv2.FONT_HERSHEY_SIMPLEX, 4, 10)
                    text_width, text_height = text_size
                    cv2.putText(labeled_image, str(adjacent), (adj_center_x - text_width // 2, adj_center_y + text_height // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 100), 10, cv2.LINE_AA)

    return labeled_image, results


if __name__ == "__main__":
    file_path = "../output/preprocess.png"
    image = cv2.imread(file_path)

    labeled_image, results = match_reflected_edges_by_chroma(image)

    # 显示标注后的图像
    window_name = 'match'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    cv2.imshow(window_name, labeled_image)
    cv2.waitKey(0)

    # 打印每对玻璃反射边缘是否一致的信息
    for idx1, idx2, is_match in results:
        if is_match:
            print(f"第 {idx1} 号和第 {idx2} 号玻璃反射边缘一致")
        else:
            print(f"第 {idx1} 号和第 {idx2} 号玻璃反射边缘不一致")
