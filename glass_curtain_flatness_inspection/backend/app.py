from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from flask_cors import CORS
from FlatnessDetect import main_detect  # 导入main_detect函数

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

        # 调用main_detect函数进行图片处理
        labeled_image, results = main_detect(filename)

        # 保存处理后的图片
        processed_file_path = os.path.join(PROCESSED_FOLDER, filename)
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
            'processedImage': f'http://localhost:5000/processed/{filename}',
            'results': result_list
        })


@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
