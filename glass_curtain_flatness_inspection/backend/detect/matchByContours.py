"""
该脚本用于读取玻璃幕墙图像，判断相邻玻璃反射图像边缘坐标范围是否匹配。
方法一：反射边缘轮廓比较
"""

import cv2
from .complexSplit import complexSplit
from .crop import crop_green_edges
from .edge import detect_reflected_edges


def match_two_edge(all_edges, adjacents, positions, idx, direction, tolerance=20):
    """
    该函数用于比较两个相邻玻璃的反射边缘是否一致。

    参数:
    - all_edges: 所有玻璃的边缘反射图像坐标。
    - adjacents: 当前玻璃的邻接关系。
    - positions: 所有玻璃的绝对位置。
    - idx:       当前玻璃的边缘反射图像坐标。
    - direction: 当前玻璃需要检测的边缘方向。
    - tolerance: 允许的误差范围，默认值为20

    返回值:
    - 反射边缘一致返回 True，不一致返回 False，没有邻接玻璃返回 None
    """

    # 计算反方西
    if direction == 'up':
        opposite_direction = 'down'
    elif direction == 'down':
        opposite_direction = 'up'
    elif direction == 'left':
        opposite_direction = 'right'
    elif direction == 'right':
        opposite_direction = 'left'
    else:
        return

    # 检查两个边缘是否有邻接
    for adjacent in adjacents[direction]:
        # 只检测坐标大于当前图像的，避免重复检测
        if adjacent > idx:
            # 打印当前窗户和邻接窗户边缘坐标（测试）
            # print(all_edges[idx])
            # print(all_edges[adjacent])

            # 当前图片反射图像存在direction边缘
            if len(all_edges[idx][direction]):
                # 邻接图片反射图像存在opposite_direction边缘
                if len(all_edges[adjacent][opposite_direction]):
                    # 比较两个邻接窗户的反射边缘相对横坐标
                    if direction == 'up' or direction == 'down':
                        # 现在只考虑边缘只有一组范围的情况，如果测试中发现可能有多段范围，再进行修改！！！
                        cur_edge_l, cur_edge_r = all_edges[idx][direction][0]
                        adj_edge_l, adj_edge_r = all_edges[adjacent][opposite_direction][0]
                        # 两个邻接窗户的横坐标
                        cur_cropped_x, _, _, _ = positions[idx]
                        adj_cropped_x, _, _, _ = positions[adjacent]
                        # 两个邻接窗户的反射边缘绝对横坐标
                        cur_l = cur_edge_l + cur_cropped_x
                        cur_r = cur_edge_r + cur_cropped_x
                        adj_l = adj_edge_l + adj_cropped_x
                        adj_r = adj_edge_r + adj_cropped_x
                        # 输出两个玻璃比较的反射边缘的范围
                        print(idx, "号玻璃的", direction, "反射边缘为：(", cur_l, ',', cur_r, ")")
                        print(adjacent, "号玻璃的", opposite_direction, "反射边缘为：(", adj_l, ',', adj_r, ")")
                        # 比较横坐标范围是否一致
                        if abs(cur_l - adj_l) < tolerance and abs(cur_r - adj_r) < tolerance:
                            print(idx, "号玻璃和", adjacent, "号玻璃反射边缘一致！")
                            return True
                        else:
                            print(idx, "号玻璃和", adjacent, "号玻璃反射边缘不一致！")
                            return False

                    # 比较两个邻接窗户的反射边缘相对纵坐标
                    else:
                        # 现在只考虑边缘只有一组范围的情况，如果测试中发现可能有多段范围，再进行修改！！！
                        cur_edge_u, cur_edge_d = all_edges[idx][direction][0]
                        adj_edge_u, adj_edge_d = all_edges[adjacent][opposite_direction][0]
                        # 两个邻接窗户的纵坐标
                        _, cur_cropped_y, _, _ = positions[idx]
                        _, adj_cropped_y, _, _ = positions[adjacent]
                        # 两个邻接窗户的反射边缘绝对横坐标
                        cur_u = cur_edge_u + cur_cropped_y
                        cur_d = cur_edge_d + cur_cropped_y
                        adj_u = adj_edge_u + adj_cropped_y
                        adj_d = adj_edge_d + adj_cropped_y
                        # 输出两个玻璃比较的反射边缘的范围
                        print(idx, "号玻璃的", direction, "反射边缘为：(", cur_u, ',', cur_d, ")")
                        print(adjacent, "号玻璃的", opposite_direction, "反射边缘为：(", adj_u, ',', adj_d, ")")
                        # 比较横坐标范围是否一致
                        if abs(cur_u - adj_u) < tolerance and abs(cur_d - adj_d) < tolerance:
                            print(idx, "号玻璃和", adjacent, "号玻璃反射边缘一致！")
                            return True
                        else:
                            print(idx, "号玻璃和", adjacent, "号玻璃反射边缘不一致！")
                            return False

                # 邻接图片反射图像不存在opposite_direction边缘
                else:
                    cur_edge_f, cur_edge_b = all_edges[idx][direction][0]
                    # 如果当前窗户边缘坐标范围小于误差允许
                    if abs(cur_edge_f - cur_edge_b) < tolerance:
                        return True
                    else:
                        return False

            # 当前图片反射图像不存在direction边缘
            else:
                # 邻接图片反射图像存在opposite_direction边缘
                if len(all_edges[adjacent][opposite_direction]):
                    adj_edge_f, adj_edge_b = all_edges[adjacent][opposite_direction][0]
                    # 如果邻接窗户边缘坐标范围小于误差允许
                    if abs(adj_edge_f - adj_edge_b) < tolerance:
                        return True
                    else:
                        return False

                # 邻接图片反射图像不存在opposite_direction边缘
                else:
                    return True
        return


def match_reflected_edges(image):
    # 获取分割后的玻璃图像并得到邻接关系字典
    cropped_images, cropped_positions, adjacency_dict = complexSplit(image)

    # 各玻璃的位置信息
    positions = []

    # 存储每个分割后图像的反射图像边缘坐标范围信息
    all_edges = {}

    for idx, img in enumerate(cropped_images):
        # 切除绿色边框
        cropped_img, relative_position = crop_green_edges(img)

        # 计算位置信息
        x, y = cropped_positions[idx]
        relative_x, relative_y, w, h = relative_position
        positions.append((x + relative_x, y + relative_y, w, h))

        # 获取反射图像边缘信息
        edges, _ = detect_reflected_edges(cropped_img)

        # 存储edges信息
        all_edges[idx] = edges

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
            result = match_two_edge(all_edges, adjacents, positions, idx, direction)
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

    labeled_image, results = match_reflected_edges(image)

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


