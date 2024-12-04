import { defineStore } from 'pinia';
import axios from 'axios';

export const useExchangeRateStore = defineStore('exchangeRate', {
  state: () => ({
    rates: {},
  }),
  actions: {
    async loadRates() {
      try {
        const response = await axios.get('http://localhost:8000/finlife/getchanges/');
        const rateData = response.data;
        rateData.forEach((item) => {
          const curUnit = item.cur_unit;
          this.rates[curUnit] = {
            ttb: parseFloat(item.ttb),
            tts: parseFloat(item.tts),
            deal_bas_r: parseFloat(item.deal_bas_r),
            cur_nm: item.cur_nm,
          };
        });
      } catch (error) {
        console.error('Failed to load rates:', error);
        throw error;
      }
    },
    getRate(curUnit, rateType) {
      if (this.rates[curUnit]) {
        return this.rates[curUnit][rateType];
      }
      return null;
    },
  },
});
