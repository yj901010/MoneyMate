<!-- src/components/news/NewsList.vue -->
<template>
  <div class="bg-white rounded-lg shadow-md">
    <h2 class="text-lg font-bold p-4 border-b">최신 뉴스</h2>
    <div class="divide-y">
      <NewsCard
        v-for="news in newsList"
        :key="news.link"
        :news="news"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import NewsCard from './NewsCard.vue'

const newsList = ref([])

const fetchNews = async () => {
  try {
    const response = await axios.get('http://localhost:8000/finlife/news/')
    newsList.value = response.data.items
  } catch (error) {
    console.error('뉴스를 불러오는데 실패했습니다:', error)
  }
}

onMounted(() => {
  fetchNews()
})
</script>

