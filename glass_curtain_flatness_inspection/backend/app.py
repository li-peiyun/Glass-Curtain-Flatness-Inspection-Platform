from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from flask_cors import CORS
from FlatnessDetect import main_detect_by_chroma, main_detect_by_contours  # 导入两个处理函数
import uuid

app = Flask(__name__)
CORS(app)  # 允许所有来源的请求，可以根据需要进行更细粒度的控制
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # 获取用户选择的方法
        method = request.form.get('method', 'chroma')  # 默认使用采样色度比较法

        # 根据选择的方法调用相应的处理函数
        if method == 'chroma':
            labeled_image, results = main_detect_by_chroma(filename)
        elif method == 'contours':
            labeled_image, results = main_detect_by_contours(filename)
        else:
            return jsonify({'error': 'Invalid method'}), 400

        # 生成唯一的处理后文件名
        processed_filename = f"{uuid.uuid4()}-{filename}"
        processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        cv2.imwrite(processed_file_path, labeled_image)

        # 构建结果列表
        result_list = []
        for idx1, idx2, is_match in results:
            result_list.append({
                'edgePair': f"第 {idx1} 号和第 {idx2} 号玻璃反射边缘",
                'isMatch': is_match
            })

        # 返回处理后的图片路径和结果列表
        return jsonify({
            'processedImage': f'http://localhost:5000/processed/{processed_filename}',
            'results': result_list
        })


@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
