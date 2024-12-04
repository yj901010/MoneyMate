<!-- src/components/charts/GoldChart.vue -->
<template>
  <div class="bg-white p-4 rounded-lg shadow-md">
    <div :class="chartContainerClass">
      <canvas ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import { 
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const props = defineProps({
  isMobileView: {
    type: Boolean,
    required: true
  }
});

const chartRef = ref(null);
const chartInstance = ref(null);
const chartContainerClass = ref("");

watch(() => props.isMobileView, (newVal) => {
  chartContainerClass.value = newVal ? "mobile-chart-container" : "desktop-chart-container";
}, { immediate: true });

const createChart = (labels, data) => {
  if (chartRef.value) {
    if (chartInstance.value) {
      chartInstance.value.destroy();
    }

    chartInstance.value = new Chart(chartRef.value.getContext('2d'), {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '금 시세',
          data,
          borderColor: '#FFC700',
          backgroundColor: 'rgba(255, 199, 0, 0.1)',
          borderWidth: 1,
          pointRadius: 0,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: '금 시세',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'MM/dd'
              }
            },
            ticks: {
              maxTicksLimit: 8,
              maxRotation: 45,
              minRotation: 45
            },
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: false,
            ticks: {
              callback: value => value.toLocaleString()
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          }
        }
      }
    });
  }
};

const fetchData = async () => {
  try {
    const apiUrl = "/api/chart/domestic/gold/M04020000/day?startDateTime=20240821000&endDateTime=202411210000";
    const response = await axios.get(apiUrl);
    
    const labels = response.data.map(item => item.localDate);
    const data = response.data.map(item => item.closePrice);
    
    createChart(labels, data);
  } catch (error) {
    console.error("Error fetching gold price data:", error);
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.mobile-chart-container {
  height: 250px;
  margin: 0 auto;
}

.desktop-chart-container {
  height: 400px;
  margin: 0 auto;
}
</style>