<template>
  <div class="w-96 bg-white rounded-lg shadow-xl p-4">
    <h3 class="text-lg font-semibold text-center">환율 계산기</h3>
    <div v-if="isLoading" class="text-center text-gray-500">Loading...</div>
    <div v-else-if="errorMessage" class="text-center text-red-500">
      {{ errorMessage }}
    </div>
    <div v-else>
      <div class="flex justify-between items-center mt-4">
        <!-- From Currency -->
        <div class="flex items-center">
          <img :src="`/src/assets/img/nation/${currencyToCountryCode[fromCurrencyCode]}.png`" :alt="fromCurrencyCode" class="w-6 h-6 mr-2" />
          <span>{{ fromCurrencyName }} ({{ fromCurrencyCode }})</span>
        </div>
        <input
          type="number"
          v-model.number="amountFrom"
          @input="convertCurrency"
          class="border rounded px-3 py-1 w-20 text-right"
        />
      </div>
      <!-- Swap Button -->
      <div class="text-center my-2">
        <button @click="swapCurrencies" class="text-xl">=</button>
      </div>
      <div class="flex justify-between items-center">
        <!-- To Currency -->
        <div class="flex items-center">
          <img :src="`/src/assets/img/nation/${currencyToCountryCode[toCurrencyCode]}.png`" :alt="toCurrencyCode" class="w-6 h-6 mr-2" />
          <span>{{ toCurrencyName }} ({{ toCurrencyCode }})</span>
        </div>
        <input
          type="number"
          v-model.number="amountTo"
          disabled
          class="border rounded px-3 py-1 w-20 text-right bg-gray-100"
        />
      </div>

      <!-- 환율 옵션 -->
      <div class="mt-4">
        <label class="block mb-2 font-semibold text-sm">환율 옵션:</label>
        <select v-model="rateType" @change="convertCurrency" class="w-full border rounded px-3 py-2">
          <option value="deal_bas_r">매매 기준율</option>
          <option value="tts">송금 보낼 때</option>
          <option value="ttb">송금 받을 때</option>
        </select>
      </div>

      <!-- 통화 선택 -->
      <div class="mt-4">
        <label class="block mb-2 font-semibold text-sm">From Currency:</label>
        <select v-model="fromCurrencyCode" @change="updateCurrencyInfo" class="w-full border rounded px-3 py-2">
          <option v-for="(rate, code) in exchangeRateStore.rates" :key="code" :value="code">
            {{ rate.cur_nm }} ({{ code }})
          </option>
        </select>
      </div>
      <div class="mt-4">
        <label class="block mb-2 font-semibold text-sm">To Currency:</label>
        <select v-model="toCurrencyCode" @change="updateCurrencyInfo" class="w-full border rounded px-3 py-2">
          <option v-for="(rate, code) in exchangeRateStore.rates" :key="code" :value="code">
            {{ rate.cur_nm }} ({{ code }})
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useExchangeRateStore } from '@/stores/exchangeRateStore';
import { currencyToCountryCode } from '@/data/currencyMapping';

// 상태 관리
const rateType = ref('deal_bas_r'); // 기본 환율 옵션
const amountFrom = ref(1); // 기본 값
const amountTo = ref(0); // 계산된 값
const isLoading = ref(true); // 로딩 상태
const errorMessage = ref(null); // 오류 메시지

// 스토어
const exchangeRateStore = useExchangeRateStore();

// 통화 선택
const fromCurrencyCode = ref('USD');
const toCurrencyCode = ref('KRW');

const fromCurrencyName = ref('');
const toCurrencyName = ref('');

// 환율 계산
const convertCurrency = () => {
  const fromRate = exchangeRateStore.getRate(fromCurrencyCode.value, rateType.value);
  const toRate = exchangeRateStore.getRate(toCurrencyCode.value, rateType.value);

  if (fromRate && toRate) {
    const amountInKRW = amountFrom.value * fromRate;
    amountTo.value = (amountInKRW / toRate).toFixed(2);
  } else {
    amountTo.value = 0;
  }
};

// 통화 정보 업데이트
const updateCurrencyInfo = () => {
  const fromRate = exchangeRateStore.rates[fromCurrencyCode.value];
  const toRate = exchangeRateStore.rates[toCurrencyCode.value];

  fromCurrencyName.value = fromRate ? fromRate.cur_nm : '';
  toCurrencyName.value = toRate ? toRate.cur_nm : '';

  convertCurrency();
};

// 통화 스왑
const swapCurrencies = () => {
  const tempCode = fromCurrencyCode.value;
  fromCurrencyCode.value = toCurrencyCode.value;
  toCurrencyCode.value = tempCode;

  const tempName = fromCurrencyName.value;
  fromCurrencyName.value = toCurrencyName.value;
  toCurrencyName.value = tempName;

  convertCurrency();
};

// 초기 데이터 로드
onMounted(async () => {
  try {
    await exchangeRateStore.loadRates(); // API로 환율 데이터 로드
    updateCurrencyInfo(); // 통화 정보 업데이트
    isLoading.value = false;
    convertCurrency(); // 환율 계산
  } catch (error) {
    errorMessage.value = '환율 데이터를 가져오는 데 실패했습니다.';
    isLoading.value = false;
  }
});
</script>
