<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-md overflow-hidden">
      <div class="bg-[#699BF7] p-4">
        <h3 class="text-lg font-bold text-white">맞춤 투자 포트폴리오 추천</h3>
      </div>
      
      <div class="p-6">
        <!-- 투자 종류 섹션 -->
        <div class="mb-6" v-if="portfolioItems?.types?.length > 0">
          <h4 class="text-lg font-bold mb-3">투자 종류</h4>
          <ul class="list-decimal pl-5 space-y-1">
            <li v-for="item in portfolioItems.types" :key="item.id" class="text-gray-700">
              {{ item.name }}
            </li>
          </ul>
        </div>

        <!-- 추천 상품 섹션 -->
        <div class="mb-6" v-if="portfolioItems?.products?.length > 0">
          <h4 class="text-lg font-bold mb-3">수익 좋은 상품 추천</h4>
          <ul class="list-decimal pl-5 space-y-1">
            <li v-for="item in portfolioItems.products" :key="item.id" class="text-gray-700">
              {{ item.name }}
            </li>
          </ul>
        </div>

        <!-- 투자 비율 섹션 -->
        <div class="mb-6" v-if="portfolioItems?.ratios?.length > 0">
          <h4 class="text-lg font-bold mb-3">투자 비율</h4>
          <div class="flex flex-col md:flex-row items-center gap-6">
            <!-- 원형 차트 -->
            <div class="w-64 h-64">
              <canvas ref="pieChart"></canvas>
            </div>
            <!-- 범례 -->
            <div class="flex flex-col gap-2">
              <div v-for="item in portfolioItems.ratios" :key="item.id" class="flex items-center gap-2">
                <div 
                  class="w-4 h-4 rounded-full" 
                  :style="{ backgroundColor: getChartColor(item.name) }"
                ></div>
                <span class="text-sm text-gray-700">{{ item.name }}: {{ item.ratio }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end">
          <button 
            class="px-4 py-2 bg-[#699BF7] text-white rounded hover:bg-[#5B8AE0] transition-colors"
            @click="$emit('close')"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

const props = defineProps({
  portfolioItems: {
    type: Object,
    required: true,
    default: () => ({
      types: [],
      products: [],
      ratios: []
    })
  }
});

// 디버깅을 위한 watch
watch(() => props.portfolioItems, (newValue) => {
  console.log('portfolioItems changed:', newValue);
}, { deep: true });

const pieChart = ref(null);
let chart = null;

const chartColors = [
  '#699BF7',
  '#4F7BE5',
  '#7DADFF',
  '#3563D9',
  '#90C2FF',
];

const getChartColor = (name) => {
  if (!props.portfolioItems?.ratios) return chartColors[0];
  const index = props.portfolioItems.ratios.findIndex(item => item.name === name);
  return chartColors[index % chartColors.length];
};

const createChart = () => {
  if (!pieChart.value || !props.portfolioItems?.ratios?.length) return;
  
  if (chart) {
    chart.destroy();
  }

  const ctx = pieChart.value.getContext('2d');
  const labels = props.portfolioItems.ratios.map(item => item.name);
  const data = props.portfolioItems.ratios.map(item => item.ratio);

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: labels.map((_, index) => chartColors[index % chartColors.length]),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
};

onMounted(() => {
  console.log('Component mounted with data:', props.portfolioItems);
  if (props.portfolioItems?.ratios?.length > 0) {
    createChart();
  }
});

watch(() => props.portfolioItems, () => {
  console.log('Portfolio items updated:', props.portfolioItems);
  if (props.portfolioItems?.ratios?.length > 0) {
    createChart();
  }
}, { deep: true });

defineEmits(['close']);
</script>