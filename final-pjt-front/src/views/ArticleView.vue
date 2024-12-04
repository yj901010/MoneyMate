<!-- ArticleView.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div class="bg-white rounded-lg shadow-md p-6">
      <!-- Board Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-[#699BF7]">자유게시판</h1>
        <button
          @click="handleWrite"
          class="bg-[#699BF7] text-white px-4 py-2 rounded hover:bg-[#5b8ce6] transition"
        >
          글쓰기
        </button>
      </div>

      <!-- Search Bar -->
      <div class="flex gap-4 mb-6">
        <select v-model="searchType" class="border rounded p-2">
          <option value="title">제목</option>
          <option value="content">내용</option>
          <option value="author">작성자</option>
        </select>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="검색어를 입력하세요"
          class="flex-1 border rounded p-2"
        />
        <button
          @click="handleSearch"
          class="bg-[#699BF7] text-white px-4 rounded hover:bg-[#5b8ce6] transition"
        >
          검색
        </button>
      </div>

      <!-- Loading and Error States -->
      <div v-if="store.loading" class="text-center text-gray-500">로딩 중...</div>
      <div v-if="store.error" class="text-center text-red-500">오류가 발생했습니다.</div>

      <!-- Board Table -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left">번호</th>
              <th class="px-6 py-3 text-left">제목</th>
              <th class="px-6 py-3 text-left">작성자</th>
              <th class="px-6 py-3 text-left">작성일</th>
              <th class="px-6 py-3 text-left">조회</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr
              v-for="post in posts"
              :key="post.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="goToPost(post.id)"
            >
              <td class="px-6 py-4">{{ post.id }}</td>
              <td class="px-6 py-4">
                {{ post.title }}
                <span v-if="post.comment_count" class="text-[#699BF7] ml-2">
                  [{{ post.comment_count }}]
                </span>
              </td>
              <td class="px-6 py-4">{{ post.author }}</td>
              <td class="px-6 py-4">{{ formatDate(post.created_at) }}</td>
              <td class="px-6 py-4">{{ post.visit_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center mt-6 gap-2">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="handlePageChange(page)"
          :class="[
            'px-3 py-1 rounded',
            currentPage === page
              ? 'bg-[#699BF7] text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          ]"
        >
          {{ page }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useArticleStore } from '@/stores/articleStore';
import { useAuthStore } from '@/stores/authStore';

const router = useRouter();
const store = useArticleStore();
const authStore = useAuthStore();

const searchType = ref('title');
const searchQuery = ref('');
const currentPage = ref(1);
const postsPerPage = 10;
const totalPages = computed(() => Math.ceil(store.articles.length / postsPerPage));

const posts = computed(() => {
  const startIndex = (currentPage.value - 1) * postsPerPage;
  const endIndex = startIndex + postsPerPage;
  return store.sortedArticles.slice(startIndex, endIndex);
});

const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    router.push('/');
    return;
  }
  store.getArticles();
});

const handleSearch = () => {
  // TODO: Implement search logic
};

const handleWrite = () => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    return;
  }
  router.push('/article/create');
};

const goToPost = (id) => {
  router.push(`/article/${id}`);
};

const handlePageChange = (page) => {
  currentPage.value = page;
};
</script>
