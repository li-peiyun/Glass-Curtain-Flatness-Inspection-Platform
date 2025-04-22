<template>
  <div class="app-container">
    <header>
      <h1>玻璃幕墙平整度检查</h1>
    </header>
    <main>
      <div v-if="!imageUrl && !isLoading" class="initial-section">
        <div class="upload-section">
          <input type="file" @change="onFileChange" accept="image/*">
          <button @click="uploadImage" :disabled="!file">上传图片</button>
        </div>
      </div>
      <div v-if="imageUrl && !processedImageUrl && !isLoading" class="preview-section">
        <div class="upload-section">
          <input type="file" @change="onFileChange" accept="image/*">
          <button @click="uploadImage" :disabled="!file">上传图片</button>
        </div>
        <img :src="imageUrl" alt="Uploaded Image" width="300" @click="openModal(imageUrl)" class="zoomable">
      </div>
      <div v-if="isLoading" class="loading-section">
        <h3>处理中...</h3>
        <div class="loader"></div>
      </div>
      <div v-if="processedImageUrl && !isLoading" class="result-section">
        <div class="left-column">
          <div class="image-section">
            <img :src="imageUrl" alt="Uploaded Image" width="300" @click="openModal(imageUrl)" class="zoomable">
          </div>
          <div class="processed-image-section">
            <img :src="processedImageUrl" alt="Processed Image" width="600" @click="openModal(processedImageUrl)" class="zoomable">
          </div>
        </div>
        <div class="right-column">
          <div class="table-container">
            <table>
              <thead>
              <tr>
                <th>玻璃反射边缘对</th>
                <th>是否一致</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(result, index) in paginatedResults" :key="index">
                <td>{{ result.edgePair }}</td>
                <td>{{ result.isMatch ? '一致' : '不一致' }}</td>
              </tr>
              </tbody>
            </table>
            <div class="pagination">
              <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
            </div>
          </div>
          <button @click="resetUpload" class="retry-button-bottom">再测一张</button>
        </div>
      </div>
    </main>
    <!-- 图片放大模态框 -->
    <div v-if="showModal" class="modal" @click="closeModal">
      <div ref="imageContainer">
        <img :src="modalImageUrl" alt="Enlarged Image" class="enlarged-image">
      </div>
    </div>
  </div>
</template>

<script>
import Viewer from 'viewerjs';
import 'viewerjs/dist/viewer.css';

export default {
  data() {
    return {
      file: null,
      imageUrl: '',
      processedImageUrl: '',
      results: [],
      isLoading: false,
      currentPage: 1,
      resultsPerPage: 12, // 每页显示12条信息
      showModal: false,
      modalImageUrl: '',
      viewer: null
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.results.length / this.resultsPerPage);
    },
    paginatedResults() {
      const start = (this.currentPage - 1) * this.resultsPerPage;
      const end = start + this.resultsPerPage;
      return this.results.slice(start, end);
    }
  },
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      this.file = file;
      this.imageUrl = URL.createObjectURL(file);
    },
    async uploadImage() {
      if (!this.file) return; // 如果没有文件，不进行上传

      this.isLoading = true; // 开始加载
      this.processedImageUrl = '';
      this.results = [];
      this.currentPage = 1; // 重置页码

      const formData = new FormData();
      formData.append('image', this.file);

      try {
        const response = await fetch('http://localhost:5000/process-image', {
          method: 'POST',
          body: formData
        });
        const result = await response.json();
        this.processedImageUrl = result.processedImage;
        this.results = result.results; // 直接使用返回的JSON数据
      } catch (error) {
        console.error('Error uploading image:', error);
      } finally {
        this.isLoading = false; // 结束加载
      }
    },
    resetUpload() {
      this.file = null;
      this.imageUrl = '';
      this.processedImageUrl = '';
      this.results = [];
      this.isLoading = false;
      this.currentPage = 1; // 重置页码
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
    openModal(imageUrl) {
      this.modalImageUrl = imageUrl;
      this.showModal = true;
      this.$nextTick(() => {
        if (this.viewer) {
          this.viewer.destroy();
        }
        this.viewer = new Viewer(this.$refs.imageContainer, {
          inline: true,
          backdrop: true, // 启用背景模糊效果
          viewed() {
            this.viewer.zoomTo(1);
          }
        });
      });
    },
    closeModal() {
      this.showModal = false;
      if (this.viewer) {
        this.viewer.destroy();
      }
    }
  },
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.destroy();
    }
  }
};
</script>

<style scoped>
/* 添加一些样式以美化页面 */
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding: 20px; /* 设置内边距 */
}

header {
  width: 100%;
  text-align: center;
  padding: 10px 0;
  margin-bottom: 20px; /* 确保主体部分显示在标题下方 */
}

header h1 {
  color: inherit; /* 继承父元素的颜色 */
}

main {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80%; /* 设置主体内容的宽度为总页面宽度的80% */
  box-sizing: border-box;
}

.initial-section,
.preview-section,
.loading-section,
.result-section {
  width: 100%;
  box-sizing: border-box;
  text-align: center;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-section input[type="file"] {
  margin-bottom: 10px;
  background-color: #444;
  color: #fff;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
}

.upload-section button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.upload-section button:disabled {
  background-color: #777;
  cursor: not-allowed;
}

.upload-section button:hover:not(:disabled) {
  background-color: #45a049;
}

.preview-section img {
  margin-bottom: 20px;
  border: 2px solid #444;
  border-radius: 4px;
  background-color: #444;
}

.loading-section {
  text-align: center;
}

/* 加载图标样式 */
.loader {
  border: 16px solid #444; /* 深灰色 */
  border-top: 16px solid #4CAF50; /* 绿色 */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 表格样式 */
.right-column {
  flex: 1;
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
}

.table-container {
  width: 100%;
  border: 1px solid #555;
  border-radius: 4px;
  background-color: #444;
  padding: 10px;
  box-sizing: border-box;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0;
  background-color: #444;
  color: #fff;
  border: none;
}

th, td {
  border: 1px solid #555;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #555;
}

tr:nth-child(even) {
  background-color: #444;
}

tr:nth-child(odd) {
  background-color: #333;
}

tr:hover {
  background-color: #555;
}

.result-section {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
  box-sizing: border-box;
}

.left-column {
  flex: 1;
  margin-right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center; /* 左侧图片居中对齐 */
}

.image-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-section img {
  margin-bottom: 20px;
  cursor: zoom-in; /* 显示放大镜符号 */
}

.retry-button-bottom {
  margin-top: 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button-bottom:hover {
  background-color: #45a049;
}

.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.pagination button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background-color: #777;
  cursor: not-allowed;
}

.pagination span {
  margin: 0 10px;
}

.processed-image-section {
  display: flex;
  flex-direction: column;
  align-items: center; /* 处理后的图片居中对齐 */
}

.processed-image-section img {
  cursor: zoom-in; /* 显示放大镜符号 */
}

/* 模态框样式 */
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: transparent; /* 透明背景 */
  z-index: 1000;
}

.enlarged-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保持图片比例并完整显示 */
}
</style>
