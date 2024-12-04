<template>
  <div class="bg-white p-4 rounded-lg shadow-md">
    <div class="chart-container">
      <canvas ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
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
import zoomPlugin from "chartjs-plugin-zoom"; // 줌/팬 기능 플러그인
import Papa from "papaparse";

// Chart.js 등록
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

const props = defineProps({
  symbol: {
    type: String,
    required: true,
    validator: (value) => ["KOSPI", "KOSDAQ"].includes(value),
  },
});

const chartRef = ref(null);
const chartInstance = ref(null);

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  try {
    const month = dateStr.slice(6, 8);
    const day = dateStr.slice(8, 10);
    return `${month}/${day}`;
  } catch (error) {
    console.error("Date parsing error:", error);
    return "";
  }
};

const processData = (rawData) => {
  const filteredData = rawData.slice(3).filter((item) => {
    const strItem = String(item).trim();
    return strItem !== "";
  });
  filteredData.pop();

  return {
    labels: filteredData.map((entry) => formatDate(entry[0])),
    openPrices: filteredData.map((entry) =>
      Number(parseFloat(entry[1]).toFixed(2))
    ),
    highPrices: filteredData.map((entry) =>
      Number(parseFloat(entry[2]).toFixed(2))
    ),
    lowPrices: filteredData.map((entry) =>
      Number(parseFloat(entry[3]).toFixed(2))
    ),
    closePrices: filteredData.map((entry) =>
      Number(parseFloat(entry[4]).toFixed(2))
    ),
  };
};

const renderChart = (labels, openPrices, highPrices, lowPrices, closePrices) => {
  if (chartRef.value) {
    if (chartInstance.value) {
      chartInstance.value.destroy();
    }

    chartInstance.value = new Chart(chartRef.value.getContext("2d"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "시가",
            data: openPrices,
            borderColor: "#699BF7",
            borderWidth: 1,
            tension: 0.1,
            fill: false,
            pointRadius: 0,
          },
          {
            label: "고가",
            data: highPrices,
            borderColor: "#4CAF50",
            borderWidth: 1,
            tension: 0.1,
            fill: false,
            pointRadius: 0,
          },
          {
            label: "저가",
            data: lowPrices,
            borderColor: "#F44336",
            borderWidth: 1,
            tension: 0.1,
            fill: false,
            pointRadius: 0,
          },
          {
            label: "종가",
            data: closePrices,
            borderColor: "#FFC700",
            borderWidth: 1,
            tension: 0.1,
            fill: false,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 20,
          },
        },
        plugins: {
          title: {
            display: true,
            text: `${props.symbol} 지수`,
            font: {
              size: 16,
              weight: "bold",
            },
          },
          legend: {
            display: true,
            position: "top",
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
          zoom: {
            pan: {
              enabled: true,
              mode: "x",
            },
            zoom: {
              wheel: {
                enabled: true,
              },
              pinch: {
                enabled: true,
              },
              mode: "x",
            },
          },
        },
        scales: {
          x: {
            display: true,
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
              autoSkip: true,
              maxTicksLimit: 8,
            },
          },
          y: {
            display: true,
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
        },
      },
    });
  }
};

const fetchData = async () => {
  try {
    const today = new Date();
    const endDate = today.toISOString().slice(0, 10).replace(/-/g, "");
    const startDate = new Date(today.setMonth(today.getMonth() - 3))
      .toISOString()
      .slice(0, 10)
      .replace(/-/g, "");

    const url = `/api/front-api/external/chart/domestic/info?symbol=${props.symbol}&requestType=1&startTime=${startDate}&endTime=${endDate}&timeframe=day`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const textData = await response.text();
    const parsedData = Papa.parse(textData, {
      delimiter: ",",
      skipEmptyLines: true,
      header: false,
    });

    const { labels, openPrices, highPrices, lowPrices, closePrices } =
      processData(parsedData.data);
    renderChart(labels, openPrices, highPrices, lowPrices, closePrices);
  } catch (error) {
    console.error("Error fetching or processing data:", error);
  }
};

watch(
  () => props.symbol,
  () => {
    fetchData();
  }
);

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
}
</style>
