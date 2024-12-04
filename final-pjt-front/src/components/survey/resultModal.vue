<template>
  <div v-if="showModal" class="fixed inset-0 bg-gray-800 bg-opacity-50 flex justify-center items-center">
    <div class="bg-white rounded-lg shadow-lg w-4/5 md:w-1/2 p-6">
      <h2 class="text-xl font-bold mb-4">설문 결과</h2>
      <p class="text-gray-700">당신의 투자 성향: <strong>{{ investmentStyle }}</strong></p>
      <p class="text-gray-600 mt-4">
        {{ styleDescription }}
      </p>
      <button 
        @click="$emit('close')" 
        class="mt-6 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        닫기
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useSurveyStore } from '@/stores/surveyStore';

const surveyStore = useSurveyStore();

const showModal = computed(() => surveyStore.showResultModal);
const investmentStyle = computed(() => surveyStore.result);

const styleDescription = computed(() => {
  switch (investmentStyle.value) {
    case '안정형':
      return '안정적인 수익을 추구하며 위험을 최소화하는 투자 성향입니다.';
    case '안정추구형':
      return '안전성을 우선시하며 소폭의 위험을 감수할 수 있는 성향입니다.';
    case '위험중립형':
      return '위험과 수익의 균형을 맞추는 투자 성향입니다.';
    case '적극투자형':
      return '수익을 목표로 일정 수준의 위험을 감수할 수 있는 성향입니다.';
    case '공격투자형':
      return '높은 수익을 추구하며 큰 위험도 감수할 수 있는 성향입니다.';
    default:
      return '설문 결과를 확인하세요.';
  }
});

const closeModal = () => {
  surveyStore.hideResult();
};
</script>
