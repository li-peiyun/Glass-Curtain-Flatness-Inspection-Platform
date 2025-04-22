import cv2
from run import preprocess_image
# from detect.matchByContours import match_reflected_edges
from detect.matchByChroma import match_reflected_edges


# 主要平整度检测函数
def main_detect(image_name):
    pre_result_image = preprocess_image(image_name)
    labeled_image, results = match_reflected_edges(pre_result_image)

    return labeled_image, results


if __name__ == "__main__":
    # 设置图片名称
    image_name = "test1.png"
    labeled_image, results = main_detect(image_name)

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