<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <!-- 검색 섹션 -->
    <div class="mb-6">
      <div class="relative">
        <input
          v-model="Name"
          type="text"
          placeholder="종목명을 입력하세요"
          class="w-full border rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="handleInput"
        />
        <!-- 자동완성 목록 -->
        <ul
          v-if="suggestions.length > 0"
          class="absolute z-10 bg-white border mt-1 w-full rounded-lg shadow-lg max-h-48 overflow-y-auto"
        >
          <li
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="selectSuggestion(suggestion)"
            class="p-2 hover:bg-blue-100 cursor-pointer"
          >
            {{ suggestion }}
          </li>
        </ul>
        <button
          @click="searchName"
          class="absolute right-3 top-1/2 transform -translate-y-1/2 bg-blue-500 text-white px-5 py-2 rounded-full hover:bg-blue-600 transition"
          :disabled="isLoading"
        >
          {{ isLoading ? '검색중...' : '검색' }}
        </button>
      </div>
    </div>

    <!-- 차트 섹션 -->
    <div v-show="!isLoading && store.graphData && store.graphData.length > 0" class="chart-container">
      <div id="chartWrapper" class="w-full h-full">
        <canvas ref="chartRef"></canvas>
      </div>
    </div>

    <!-- 로딩 스피너 -->
    <div v-if="isLoading" class="flex justify-center items-center h-40">
      <q-spinner-ball color="primary" size="10em" />
    </div>

    <!-- 안내 문구 -->
    <div v-else-if="!store.graphData || store.graphData.length === 0" class="text-center p-6 text-gray-500">
      종목을 검색하여 그래프를 확인하세요
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from "vue";
import { deepStore } from "../stores/deepStore";
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import { tickerCode } from "../data/joosickData";
import { QSpinnerBall } from "quasar";

// Chart.js 플러그인 등록
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  zoomPlugin
);

const chartRef = ref(null);
const chartInstance = ref(null);
const isLoading = ref(false);
const Name = ref("");
const store = deepStore();
const suggestions = ref([]); // 자동완성 데이터

// 날짜 포맷 함수
const formatDate = (dateStr) => {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  } catch (error) {
    console.error("날짜 포맷 오류:", error);
    return "";
  }
};

// 기존 차트 제거
const destroyChart = () => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }
};

// 차트 생성 함수
const createChart = async (retryCount = 0) => {
  const maxRetries = 5;
  const retryDelay = 100;

  try {
    await nextTick();

    if (!chartRef.value) {
      if (retryCount < maxRetries) {
        console.log(`Canvas not ready, retrying... (${retryCount + 1}/${maxRetries})`);
        setTimeout(() => createChart(retryCount + 1), retryDelay);
        return;
      }
      throw new Error("Canvas element not found after max retries");
    }

    const ctx = chartRef.value.getContext("2d");

    // 기존 차트 정리
    destroyChart();

    const labels = store.graphData.map((item) => formatDate(item.date));
    const data = store.graphData.map((item) => item.predictedClose);

    chartInstance.value = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "예측 종가",
            data,
            borderColor: "#699BF7",
            borderWidth: 2,
            tension: 0.1,
            fill: false,
            pointRadius: 1,
            pointHoverRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `${Name.value} 예측 종가`,
            padding: 20,
          },
          tooltip: {
            enabled: true, // 마우스 오버로 자동 표시
          },
          zoom: {
            zoom: {
              wheel: {
                enabled: true,
              },
              pinch: {
                enabled: true,
              },
              mode: "x",
            },
            pan: {
              enabled: true,
              mode: "x",
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
            },
          },
          y: {
            ticks: {
              callback: (value) => `${value.toLocaleString()}원`,
            },
          },
        },
      },
    });
  } catch (error) {
    console.error("차트 생성 중 오류:", error);
  }
};

// 검색어 입력 처리 (자동완성)
const handleInput = () => {
  const query = Name.value.toLowerCase();
  suggestions.value = Object.keys(tickerCode).filter((key) =>
    key.toLowerCase().includes(query)
  );
};

// 자동완성 선택
const selectSuggestion = (suggestion) => {
  Name.value = suggestion;
  suggestions.value = [];
};

// 검색 기능
const searchName = async () => {
  if (!Name.value) {
    alert("종목명을 입력해주세요");
    return;
  }

  const stockCode = tickerCode[Name.value];
  if (!stockCode) {
    alert("존재하지 않는 종목입니다");
    return;
  }

  isLoading.value = true;
  destroyChart();

  try {
    await store.loaddata(stockCode);

    setTimeout(() => {
      createChart();
      isLoading.value = false;
    }, 300);
  } catch (error) {
    console.error("데이터 로드 실패:", error);
    alert("데이터를 불러오는데 실패했습니다");
    isLoading.value = false;
  }
};

// 컴포넌트 마운트 시 차트 초기화
onMounted(() => {
  if (store.graphData && store.graphData.length > 0) {
    createChart();
  }
});

// 데이터 변경 감지
watch(
  () => store.graphData,
  (newData) => {
    if (newData && newData.length > 0) {
      setTimeout(() => {
        createChart();
      }, 300);
    }
  },
  { deep: true }
);

// 컴포넌트 언마운트 시 차트 제거
onUnmounted(() => {
  destroyChart();
});
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
  background: linear-gradient(to bottom, #ffffff, #f8fbff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(105, 155, 247, 0.1);
}

#chartWrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
</style>
