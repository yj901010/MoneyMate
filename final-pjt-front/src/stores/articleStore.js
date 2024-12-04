// src/stores/articleStore.js

import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '@/plugins/axios'; // Axios 인스턴스 임포트
import { useAuthStore } from '@/stores/authStore';

export const useArticleStore = defineStore('article', () => {
  const authStore = useAuthStore();
  const articles = ref([]);
  const currentArticle = ref(null);
  const API_URL = 'http://127.0.0.1:8000';
  
  const loading = ref(false);
  const error = ref(null);

  // 로컬 스토리지에서 조회한 게시글을 로드
  const viewedArticles = ref(new Set(JSON.parse(localStorage.getItem('viewedArticles') || '[]')));

  // 게시글 목록 가져오기
  const getArticles = async () => {
    const headers = {
      'Authorization': `Token ${authStore.token}`
    };

    loading.value = true;
    error.value = null;

    try {
      const res = await apiClient.get('/article/list/', { headers });
      articles.value = res.data;
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        alert('로그인이 필요한 서비스입니다.');
      } else {
        alert('게시글을 가져오는 중 오류가 발생했습니다.');
      }
      error.value = err;
    } finally {
      loading.value = false;
    }
  };

  // 단일 게시글 가져오기 및 조회수 증가
  const fetchArticle = async (articleId) => {
    // 이미 조회한 게시글이라면 게시글 목록에서 가져오기
    if (viewedArticles.value.has(articleId)) {
      const cachedArticle = articles.value.find(a => a.id === articleId);
      if (cachedArticle) {
        currentArticle.value = cachedArticle;
        return currentArticle.value;
      }
    }

    const headers = {
      'Authorization': `Token ${authStore.token}`
    };

    loading.value = true;
    error.value = null;

    try {
      const res = await apiClient.get(`/article/${articleId}/`, { headers });
      currentArticle.value = res.data;

      // 조회한 게시글 ID를 추가하고 로컬 스토리지에 저장
      viewedArticles.value.add(articleId);
      localStorage.setItem('viewedArticles', JSON.stringify([...viewedArticles.value]));
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        alert('게시글을 찾을 수 없습니다.');
      } else if (err.response?.status === 401) {
        alert('로그인이 필요한 서비스입니다.');
      } else {
        alert('게시글을 가져오는 중 오류가 발생했습니다.');
      }
      error.value = err;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const createComment = async (articleId, content) => {
    try {
        await apiClient.post(
            `/article/${articleId}/comments/create/`,
            { content },
            {
                headers: {
                    Authorization: `Token ${authStore.token}`
                }
            }
        );
        // 댓글 작성 후 게시글 새로고침
        await fetchArticle(articleId);
    } catch (error) {
        console.error('Error creating comment:', error);
        throw error;
    }
};

  // 게시글 목록을 컴퓨티드 프로퍼티로 정렬 또는 필터링 가능
  const sortedArticles = computed(() => {
    return [...articles.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  });

  return { 
    articles, 
    currentArticle, 
    API_URL, 
    getArticles, 
    fetchArticle, 
    loading, 
    error, 
    sortedArticles,
    createComment
  };
}, { persist: true });