<template>
  <div id="app">
    <ImageUploader />
  </div>
</template>

<script>
import ImageUploader from './components/ImageUploader.vue';

export default {
  name: 'App',
  components: {
    ImageUploader
  }
};
</script>

<style>
/* 全局样式 */
body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #333; /* 深灰色背景 */
  color: #fff; /* 白色文字 */
  font-family: Arial, sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%; /* 确保#app容器占满整个视口宽度 */
  box-sizing: border-box;
}
</style>
