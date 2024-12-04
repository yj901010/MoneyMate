<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-[#699BF7] mb-6">금리 비교</h1>
    
    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">은행</label>
          <select 
            v-model="filters.bankCode"
            class="w-full border rounded-lg p-2"
          >
            <option value="">전체</option>
            <option v-for="bank in store.banks" :key="bank.code" :value="bank.name">
              {{ bank.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">가입기간 (개월)</label>
          <select 
            v-model="filters.period"
            class="w-full border rounded-lg p-2"
          >
            <option value="">전체</option>
            <option v-for="period in periods" :key="period" :value="period">
              {{ period }}개월
            </option>
          </select>
        </div>
      </div>

      <div class="mt-4 flex justify-end">
        <button 
          @click="handleSearch"
          class="bg-[#699BF7] text-white px-6 py-2 rounded-lg hover:bg-[#5b8ce6]"
        >
          검색
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#699BF7] mx-auto"></div>
    </div>

    <!-- Results -->
    <template v-else>
      <!-- Chart -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-lg font-bold mb-4">금리 비교</h2>
        <canvas ref="chartContainer" class="h-[400px] w-full"></canvas>
      </div>

      <!-- Products Table -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">은행</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상품명</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">가입기간</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기본금리</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">최고금리</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상세정보</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">{{ product.bankName }}</td>
                <td class="px-6 py-4">{{ product.productName }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ product.minMonth }}~{{ product.maxMonth }}개월</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ product.minRate }}%~</td>
                <td class="px-6 py-4 whitespace-nowrap font-semibold text-[#699BF7]">
                  {{ product.maxMRate }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <button 
                    @click="showDetails(product)"
                    class="text-[#699BF7] hover:text-[#5b8ce6]"
                  >
                    상세보기
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Details Modal -->
    <ProductDetailsModal
      v-if="store.selectedProduct"
      :product="store.selectedProduct"
      @close="store.clearSelectedProduct()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useFinanceStore } from '../stores/finance'
import ProductDetailsModal from '../components/ProductDetailsModal.vue'
import { Chart } from 'chart.js/auto'

const store = useFinanceStore()
const chartContainer = ref(null)
const chartInstance = ref(null)

const filters = ref({
  bankCode: '',
  period: null
})

const periods = [6, 12, 24, 36]

const filteredProducts = computed(() => 
  store.filterProducts(filters.value.bankCode, filters.value.period)
)

const handleSearch = () => {
  updateChart()
}

const showDetails = (product) => {
  store.setSelectedProduct(product)
}

const updateChart = () => {
  if (!chartContainer.value) return
  
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const displayProducts = filteredProducts.value.slice(0, 10)

  chartInstance.value = new Chart(chartContainer.value, {
    type: 'bar',
    data: {
      labels: displayProducts.map(p => `${p.bankName}\n${p.productName}`),
      datasets: [
        {
          label: '기본금리',
          data: displayProducts.map(p => p.minRate),
          backgroundColor: '#699BF7'
        },
        {
          label: '최고금리',
          data: displayProducts.map(p => p.maxRate),
          backgroundColor: '#FFC700'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `${context.dataset.label}: ${context.raw}%`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `${value}%`
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

watch(filters, () => {
  updateChart()
}, { deep: true })

onMounted(async () => {
  await store.fetchBanks()
  await store.fetchProducts()
  updateChart()
})
</script>

<style scoped>
canvas {
  max-height: 400px;
}
</style>
