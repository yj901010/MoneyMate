<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useArticleStore } from '@/stores/articleStore';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const store = useArticleStore();
const authStore = useAuthStore();

const isEditing = computed(() => !!route.params.id);
const title = ref('');
const content = ref('');

onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.');
    router.push('/');
    return;
  }
  
  if (isEditing.value) {
    fetchPostData(route.params.id);
  }
});

const fetchPostData = (postId) => {
  const post = store.articles.find((article) => article.id === parseInt(postId));
  if (post) {
    title.value = post.title;
    content.value = post.content;
  } else {
    store.axiosInstance.get(`/article/${postId}/modify/`)
      .then((response) => {
        title.value = response.data.title;
        content.value = response.data.content;
      })
      .catch((error) => {
        console.error('Error fetching post data:', error);
        if (error.response?.status === 401) {
          alert('로그인이 필요한 서비스입니다.');
          router.push('/');
        }
      });
  }
};

const handleSubmit = async () => {
  try {
    if (!authStore.isAuthenticated) {
      alert('로그인이 필요한 서비스입니다.');
      router.push('/');
      return;
    }

    const payload = {
      title: title.value,
      content: content.value,
    };

    const headers = {
      'Authorization': `Token ${authStore.token}`
    };

    if (isEditing.value) {
      await axios.put(
        `${store.API_URL}/article/${route.params.id}/modify/`, 
        payload,
        { headers }
      );
      alert('게시글이 수정되었습니다.');
    } else {
      await axios.post(
        `${store.API_URL}/article/create/`, 
        payload,
        { headers }
      );
      alert('게시글이 작성되었습니다.');
    }

    router.push('/article');
  } catch (error) {
    console.error('Error submitting post:', error);
    if (error.response?.status === 401) {
      alert('로그인이 필요한 서비스입니다.');
    } else {
      alert('게시글 작성/수정 중 오류가 발생했습니다.');
    }
  }
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="bg-white rounded-lg shadow-md p-6">
      <h1 class="text-2xl font-bold text-[#699BF7] mb-6">
        {{ isEditing ? '게시글 수정' : '새 게시글 작성' }}
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block mb-2">제목</label>
          <input v-model="title" type="text" class="w-full border rounded p-2" required />
        </div>

        <div>
          <label class="block mb-2">내용</label>
          <textarea
            v-model="content"
            class="w-full border rounded p-2 min-h-[300px]"
            required
          ></textarea>
        </div>

        <div class="flex justify-end gap-4">
          <button
            type="button"
            @click="router.back()"
            class="px-4 py-2 border rounded hover:bg-gray-100"
          >
            취소
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-[#699BF7] text-white rounded hover:bg-[#5b8ce6]"
          >
            {{ isEditing ? '수정하기' : '작성하기' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>