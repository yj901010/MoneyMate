<!-- src/views/PostDetail.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div class="bg-white rounded-lg shadow-md p-6">
      <!-- Loading and Error States -->
      <div v-if="store.loading" class="text-center text-gray-500">로딩 중...</div>
      <div v-if="store.error" class="text-center text-red-500">오류가 발생했습니다.</div>

      <!-- Post Content -->
      <div v-if="store.currentArticle" class="post-details">
        <!-- Post Header -->
        <div class="border-b pb-4">
          <h1 class="text-2xl font-bold mb-4">{{ store.currentArticle.title }}</h1>
          <div class="flex justify-between text-gray-600">
            <div class="flex space-x-4">
              <span>작성자: {{ store.currentArticle.author }}</span>
              <span>작성일: {{ formatDate(store.currentArticle.created_at) }}</span>
              <span>조회수: {{ store.currentArticle.visit_count }}</span>
            </div>
            <div class="space-x-2">
              <button 
                v-if="isAuthor"
                @click="handleEdit" 
                class="text-[#699BF7] hover:text-[#5b8ce6]"
              >
                수정
              </button>
              <button 
                v-if="isAuthor"
                @click="handleDelete" 
                class="text-red-500 hover:text-red-600"
              >
                삭제
              </button>
            </div>
          </div>
        </div>

        <!-- Post Content -->
        <div class="py-6 min-h-[200px] whitespace-pre-wrap">
          {{ store.currentArticle.content }}
        </div>

        <!-- Comments Section -->
        <div class="border-t pt-6">
          <h2 class="text-xl font-bold mb-4">댓글 {{ store.currentArticle.comments?.length || 0 }}개</h2>
          
          <!-- Comment Form -->
          <div class="mb-6">
            <textarea
              v-model="newComment"
              placeholder="댓글을 입력하세요"
              class="w-full border rounded p-2 min-h-[100px]"
            ></textarea>
            <div class="flex justify-end mt-2">
              <button 
                @click="submitComment"
                class="bg-[#699BF7] text-white px-4 py-2 rounded hover:bg-[#5b8ce6]"
              >
                댓글 작성
              </button>
            </div>
          </div>

          <!-- Comments List -->
          <div class="space-y-4">
            <div 
              v-for="comment in store.currentArticle.comments" 
              :key="comment.id"
              class="border-b last:border-b-0 pb-4"
            >

              <div class="flex justify-between mb-2">
                <div class="font-bold">{{ comment.user }}</div>
                <div class="text-gray-600 text-sm space-x-2">
                  <span>{{ formatDate(comment.created_at) }}</span>
                  <div v-if="comment.user === authStore.usernameValue" class="inline-block">
                    <button 
                      @click="handleCommentEdit(comment)"
                      class="text-[#699BF7] hover:text-[#5b8ce6] mx-2"
                    >
                      수정
                    </button>
                    <button 
                      @click="deleteComment(comment.id)"
                      class="text-red-500 hover:text-red-600"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
              <!-- 댓글 수정 폼 -->
              <div v-if="editingComment?.id === comment.id" class="mt-2">
                <textarea
                  v-model="editingComment.content"
                  class="w-full border rounded p-2 min-h-[60px]"
                ></textarea>
                <div class="flex justify-end mt-2 space-x-2">
                  <button 
                    @click="updateComment(comment.id)"
                    class="bg-[#699BF7] text-white px-3 py-1 rounded hover:bg-[#5b8ce6]"
                  >
                    확인
                  </button>
                  <button 
                    @click="cancelEdit"
                    class="bg-gray-400 text-white px-3 py-1 rounded hover:bg-gray-500"
                  >
                    취소
                  </button>
                </div>
              </div>
              <!-- 일반 댓글 내용 -->
              <div v-else class="text-gray-700">{{ comment.content }}</div>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-6 pt-4 border-t">
          <button 
            @click="router.push('/article')"
            class="px-4 py-2 border rounded hover:bg-gray-100"
          >
            목록으로
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useArticleStore } from '@/stores/articleStore';
import { useAuthStore } from '@/stores/authStore';
import apiClient from '@/plugins/axios'; // Axios 인스턴스 임포트

const router = useRouter();
const route = useRoute();
const store = useArticleStore();
const authStore = useAuthStore();
const newComment = ref('');

// author가 현재 사용자와 동일한지 확인
const isAuthor = computed(() => store.currentArticle?.author === authStore.usernameValue);

// 날짜 형식 변환 함수
const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

// 게시글 가져오기 함수
const fetchPost = async () => {
  try {
    await store.fetchArticle(route.params.id);
  } catch (error) {
    console.error('Error fetching post:', error);
    alert('게시글을 불러오는데 실패했습니다.');
    router.push('/article');
  }
};

// 게시글 수정 핸들러
const handleEdit = () => {
  router.push(`/article/${store.currentArticle.id}/modify`);
};

// 게시글 삭제 핸들러
const handleDelete = async () => {
  if (confirm('정말 삭제하시겠습니까?')) {
    try {
      await apiClient.delete(
        `/article/${store.currentArticle.id}/delete/`,
        {
          headers: {
            Authorization: `Token ${authStore.token}`
          },
          // withCredentials는 Axios 인스턴스에서 이미 설정됨
        }
      );
      alert('게시글이 삭제되었습니다.');
      router.push('/article');
    } catch (error) {
      console.error('Error deleting post:', error);
      alert('게시글 삭제에 실패했습니다.');
    }
  }
};

const submitComment = async () => {
    try {
        if (!newComment.value.trim()) {
            alert('댓글 내용을 입력해주세요.');
            return;
        }

        await store.createComment(
            store.currentArticle.id,
            newComment.value
        );
        
        newComment.value = '';
    } catch (error) {
        console.error('Error submitting comment:', error);
        alert('댓글 작성에 실패했습니다.');
    }
};

// 댓글 삭제 핸들러
const deleteComment = async (commentId) => {
  if (confirm('댓글을 삭제하시겠습니까?')) {
    try {
      await apiClient.delete(
        `/article/${store.currentArticle.id}/comments/${commentId}/delete/`,
        {
          headers: {
            Authorization: `Token ${authStore.token}`
          },
          // withCredentials는 Axios 인스턴스에서 이미 설정됨
        }
      );
      
      // 댓글 삭제 후 게시글 새로고침
      await fetchPost();
    } catch (error) {
      console.error('Error deleting comment:', error);
      alert('댓글 삭제에 실패했습니다.');
    }
  }
};

// 댓글 수정을 위한 상태
const editingComment = ref(null);

// 댓글 수정 시작
const handleCommentEdit = (comment) => {
  editingComment.value = {
    id: comment.id,
    content: comment.content
  };
};

// 댓글 수정 취소
const cancelEdit = () => {
  editingComment.value = null;
};

// 댓글 수정 저장
const updateComment = async (commentId) => {
  try {
    await apiClient.put(
      `/article/${store.currentArticle.id}/comments/${commentId}/update/`,
      {
        content: editingComment.value.content
      },
      {
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      }
    );
    
    // 댓글 수정 후 게시글 새로고침
    await fetchPost();
    // 수정 모드 종료
    editingComment.value = null;
  } catch (error) {
    console.error('Error updating comment:', error);
    alert('댓글 수정에 실패했습니다.');
  }
};

// 컴포넌트 마운트 시 게시글 가져오기
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    router.push('/');
    return;
  }
  await fetchPost();
  console.log('Comments:', store.currentArticle.comments);
});
</script>