<!-- src/components/dashboard/MarketDashboard.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="space-y-8">
        <StockChart symbol="KOSPI" />
        <StockChart symbol="KOSDAQ" />
        <GoldChart :isMobileView="isMobileView" />
      </div>
      <div>
        <NewsList />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import StockChart from '../charts/StockChart.vue'
import GoldChart from '../charts/GoldChart.vue'
import NewsList from '../news/NewsList.vue'

const isMobileView = ref(window.innerWidth < 768)

const handleResize = () => {
  isMobileView.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>