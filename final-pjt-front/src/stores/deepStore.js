import { defineStore } from 'pinia';
import axios from 'axios';
export const deepStore = defineStore('deepStore', {
  state: () => ({
    graphData: [], // 그래프 데이터 저장
    r2: null, // r2 값 저장
  }),
  actions: {
    async loaddata(tickerCode) {
      try {
        
        const response = await axios.get(`http://localhost:8000/predict/get-predict/${tickerCode}`);
        const data = response.data;
        this.graphData = data.graph_data.map((item) => ({
          date: new Date(item.Date),
          predictedClose: item['Predicted Close'],
        }));
        this.r2 = data.r2;
      } catch (error) {
        console.error('데이터를 불러오는 데 실패했습니다:', error);
        throw error;
      }
    },
  },
});