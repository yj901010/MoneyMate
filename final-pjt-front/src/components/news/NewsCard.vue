<template>
  <div class="flex gap-4 p-4 border-b hover:bg-gray-50 transition-colors">
    <div class="w-full">
      <a :href="news.link" target="_blank" class="hover:text-blue-600">
        <h3 class="font-bold mb-2" v-html="news.title"></h3>
      </a>
      <p class="text-sm text-gray-600" v-html="news.description"></p>
      <p class="text-xs text-gray-400 mt-2">{{ formatDate(news.pubDate) }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  news: {
    type: Object,
    required: true
  }
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>