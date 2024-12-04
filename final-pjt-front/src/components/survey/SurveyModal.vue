<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white w-11/12 max-w-lg rounded-lg shadow-lg p-6 relative">
      <!-- 닫기 버튼 -->
      <button
        @click="$emit('close')"
        class="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
      >
        ✖
      </button>
      <!-- 설문 질문 -->
      <h2 class="text-2xl font-bold mb-4 text-center">{{ currentQuestion.question }}</h2>
      <ul class="space-y-2">
        <li
          v-for="(option, index) in currentQuestion.options"
          :key="index"
          @click="handleOptionClick(option, index)"
          class="py-3 px-4 border rounded-lg cursor-pointer hover:bg-gray-100"
          :class="{
            'bg-blue-500 text-white': isOptionSelected(index),
            'border-gray-300': !isOptionSelected(index),
            'border-blue-500': isOptionSelected(index)
          }"
        >
          {{ option.text }}
        </li>
      </ul>
      <!-- 네비게이션 버튼 -->
      <div class="flex justify-between mt-6">
        <button
          @click="prevQuestion"
          class="px-6 py-2 rounded-lg bg-gray-500 text-white hover:bg-gray-600"
          :disabled="currentQuestionIndex === 0"
        >
          이전
        </button>
        <button
          @click="nextOrSubmit"
          class="px-6 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
        >
          {{ isLastQuestion ? '결과 저장하기' : '다음' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useSurveyStore } from '@/stores/surveyStore';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

// 상태 관리
const surveyStore = useSurveyStore();
const authStore = useAuthStore();

const emit = defineEmits(['close', 'submitted']); // 'submitted' 이벤트 추가

// 현재 질문과 상태
const currentQuestionIndex = computed(() => surveyStore.currentQuestionIndex);
const currentQuestion = computed(() => surveyStore.questions[currentQuestionIndex.value]);
const isLastQuestion = computed(() => currentQuestionIndex.value === surveyStore.questions.length - 1);

const selectedAnswerIndex = ref(null);

// 옵션 선택 여부 확인
const isOptionSelected = (index) => {
  const answers = surveyStore.answers[currentQuestionIndex.value];
  if (currentQuestion.value.type === 'single') {
    return answers === index; // 단일 선택
  } else if (currentQuestion.value.type === 'multiple') {
    return Array.isArray(answers) && answers.includes(index); // 다중 선택
  }
  return false;
};

// 옵션 클릭
const handleOptionClick = (option, index) => {
  if (currentQuestion.value.type === 'single') {
    selectedAnswerIndex.value = index;
    surveyStore.saveAnswer(index);
  } else if (currentQuestion.value.type === 'multiple') {
    const answers = surveyStore.answers[currentQuestionIndex.value] || [];
    const existingIndex = answers.indexOf(index);
    if (existingIndex === -1) {
      answers.push(index);
    } else {
      answers.splice(existingIndex, 1);
    }
    surveyStore.answers[currentQuestionIndex.value] = answers;
  }
};

// 이전 질문
const prevQuestion = () => {
  selectedAnswerIndex.value = null;
  surveyStore.prevQuestion();
};

// 다음 질문 또는 제출
const nextOrSubmit = async () => {
  if (currentQuestion.value.type === 'single' && selectedAnswerIndex.value === null) {
    alert('답변을 선택해주세요.');
    return;
  }

  if (isLastQuestion.value) {
    surveyStore.calculateScore(); // 점수 계산

    try {
      const payload = {
        style: surveyStore.result, // 최종 계산된 투자 성향
      };

      const response = await axios.post('http://localhost:8000/chatbot/save-user-investment-style/', payload, {
        headers: {
          Authorization: `Token ${authStore.token}`, // 인증 토큰
        },
      });

      console.log('저장 성공:', response.data);

      // 저장 완료 후 부모 컴포넌트에 알림
      emit('submitted'); // 프로필 갱신 요청
      alert(response.data.message); // 결과 메시지 표시
      emit('close'); // 모달 닫기
    } catch (error) {
      console.error('저장 실패:', error.response?.data || error.message);
      alert('저장 중 오류가 발생했습니다.');
    }
  } else {
    selectedAnswerIndex.value = null;
    surveyStore.nextQuestion();
  }
};
</script>
