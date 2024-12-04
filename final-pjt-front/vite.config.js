import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/kakao': {
        target: 'https://dapi.kakao.com', // 카카오 지도 API 서버 주소
        changeOrigin: true, // 대상 서버로부터 다른 도메인을 허용
        rewrite: (path) => path.replace(/^\/kakao/, ''), // '/kakao'를 제거하여 실제 API 경로로 변경
      },
      '/api/chart': {
        target: 'https://api.stock.naver.com', // 실제 API 서버 주소
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chart/, '/chart'), // '/api/chart'를 '/chart'로 바꿔서 실제 API 경로로 리다이렉트
      },
      // /api로 시작하는 모든 요청을 m.stock.naver.com API로 프록시
      '/api': {
        target: 'https://m.stock.naver.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // '/api'를 제거하고 실제 API 경로로 리다이렉션
      },
      
    },
  },
})