// src/plugins/axios.js

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // 백엔드 API 주소
  withCredentials: true,             // 쿠키 전송 설정
  headers: {
    'Content-Type': 'application/json',
    // 필요한 다른 헤더들
  },
});

export default apiClient;
