"""
该脚本用于裁剪掉图像中可能存在的绿色窗框部分，方便计算反射边缘坐标。
"""

import cv2
import numpy as np


def crop_green_edges(image):
    """
    该函数用于裁剪掉分割图像中可能存在的绿色窗框部分。

    参数:
    - image: 分割后的图像。

    返回值:
    - cropped_image: 裁剪掉绿色窗框的图像。
    - relative_position: 相对位置信息 (relative_x, relative_y, w, h)。
    """

    # # 将图像转换为HSV色彩空间
    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #
    # # 定义绿色范围
    # lower_green = np.array([35, 50, 50])
    # upper_green = np.array([85, 255, 255])
    #
    # # 创建掩码
    # mask = cv2.inRange(hsv, lower_green, upper_green)

    # 找到绿色边缘的坐标
    up_edge = 0
    down_edge = image.shape[0]
    left_edge = 0
    right_edge = image.shape[1]

    # # 上边缘
    # for i in range(int(0.1 * image.shape[0])):
    #     if np.any(mask[i]):
    #         up_edge = i
    #
    # # 下边缘
    # for i in range(image.shape[0]-1, int(0.9 * image.shape[0]), -1):
    #     if np.any(mask[i]):
    #         down_edge = i
    #
    # # 左边缘
    # for i in range(int(0.08 * image.shape[1])):
    #     if np.any(mask[:, i]):
    #         left_edge = i
    #
    # # 右边缘
    # for i in range(image.shape[1]-1, int(0.92 * image.shape[1]), -1):
    #     if np.any(mask[:, i]):
    #         right_edge = i

    # 偏移参数
    vertical_offset_percent = 0.11
    horizontal_offset_percent = 0.06
    # 垂直方向偏移
    vertical_offset = int((down_edge - up_edge) * vertical_offset_percent)
    # 水平方向偏移
    horizontal_offset = int((right_edge - left_edge) * horizontal_offset_percent)

    # 裁剪图像
    cropped_image = image[up_edge + vertical_offset:down_edge - vertical_offset,
                    left_edge + horizontal_offset:right_edge - horizontal_offset]

    # 相对位置信息
    relative_x = left_edge + horizontal_offset
    relative_y = up_edge + vertical_offset
    w = right_edge - left_edge - 2 * horizontal_offset
    h = down_edge - up_edge - 2 * vertical_offset
    relative_position = (relative_x, relative_y, w, h)

    return cropped_image, relative_position


# 测试
if __name__ == "__main__":
    image_path = 'split/s2.png'
    image = cv2.imread(image_path)

    cropped_image, relative_position = crop_green_edges(image)

    # 显示裁剪后的图像
    cv2.namedWindow('cropped image', cv2.WINDOW_NORMAL)
    cv2.imshow("cropped image", cropped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 打印相对位置信息
    print("相对位置信息：")
    print(relative_position)
