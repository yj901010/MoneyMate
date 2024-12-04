import { defineStore } from 'pinia';
import { surveyData } from '@/data/surveyData.js';

export const useSurveyStore = defineStore('survey', {
  state: () => ({
    questions: surveyData, // 설문 질문 데이터
    currentQuestionIndex: 0, // 현재 질문 인덱스
    answers: Array(surveyData.length).fill(undefined), // 질문별 답변 상태 초기화
    result: null, // 최종 투자 성향 결과
    showResultModal: false, // 결과 모달 표시 여부
  }),
  getters: {
    isSurveyComplete(state) {
      // 모든 질문에 대한 답변 완료 여부를 확인 (3번 문제 제외)
      return state.answers.every((answer, index) => {
        if (index === 2) {
          // 3번 문제는 건너뜀
          return true;
        }
        return answer !== undefined; // 다른 질문은 답변이 있어야 함
      });
    },
    getFinalResult(state) {
      // 최종 결과를 반환
      return state.result || '결과를 계산 중입니다.';
    },
  },
  actions: {
    saveAnswer(index) {
      console.log(`Saving answer index=${index} for question ${this.currentQuestionIndex}`);
      if (this.questions[this.currentQuestionIndex].type === 'single') {
        this.answers[this.currentQuestionIndex] = index; // 단일 선택 답변 저장
      } else if (this.questions[this.currentQuestionIndex].type === 'multiple') {
        if (!Array.isArray(this.answers[this.currentQuestionIndex])) {
          this.answers[this.currentQuestionIndex] = [];
        }
        const existingIndex = this.answers[this.currentQuestionIndex].indexOf(index);
        if (existingIndex === -1) {
          this.answers[this.currentQuestionIndex].push(index); // 다중 선택에 추가
        } else {
          this.answers[this.currentQuestionIndex].splice(existingIndex, 1); // 이미 선택된 경우 제거
        }
      }
      console.log('Updated answers:', this.answers);
    },
    nextQuestion() {
      console.log('Moving to next question');
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
      console.log('Current question index:', this.currentQuestionIndex);
    },
    prevQuestion() {
      console.log('Moving to previous question');
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
      console.log('Current question index:', this.currentQuestionIndex);
    },
    calculateScore() {
      console.log('Calculating total score');
      let totalScore = 0;

      this.answers.forEach((answer, questionIndex) => {
        const question = this.questions[questionIndex];

        if (questionIndex === 2 && answer === undefined) {
          // 3번 문제 (index 2)가 선택되지 않은 경우 기본 점수는 0
          console.log('Skipping question 3 (index 2), no answer provided');
          return;
        }

        if (Array.isArray(answer)) {
          // 다중 선택 점수 계산
          totalScore += answer.reduce((acc, index) => acc + (question.options[index]?.points || 0), 0);
        } else if (typeof answer === 'number') {
          // 단일 선택 점수 계산
          totalScore += question.options[answer]?.points || 0;
        }
      });

      console.log('Total score:', totalScore);

      if (totalScore <= 20) this.result = '안정형';
      else if (totalScore <= 40) this.result = '안정추구형';
      else if (totalScore <= 60) this.result = '위험중립형';
      else if (totalScore <= 80) this.result = '적극투자형';
      else this.result = '공격투자형';

      console.log('Investment style:', this.result);
    },
    showResult() {
      // 모든 필수 답변이 완료되었는지 확인 (3번 문제 제외)
      if (this.isSurveyComplete) {
        this.showResultModal = true;
        console.log(`Final result: ${this.result}`);
      } else {
        alert('필수 질문에 답변을 완료해주세요.');
      }
    },
    hideResult() {
      this.showResultModal = false;
    },
    resetSurvey() {
      console.log('Resetting survey');
      this.currentQuestionIndex = 0;
      this.answers = Array(this.questions.length).fill(undefined); // 초기화 시 모든 문항의 상태를 undefined로 설정
      this.result = null;
      this.showResultModal = false;
    },
    closeSurvey() {
      console.log('Closing survey');
      this.currentQuestionIndex = 0;
      this.answers = Array(this.questions.length).fill(undefined);
      this.result = null; // 결과 초기화는 필요하지 않음
      this.showResultModal = false;
    },
    resetSurvey() {
      console.log('Resetting survey');
      this.currentQuestionIndex = 0;
      this.answers = Array(this.questions.length).fill(undefined);
      this.result = null;
      this.showResultModal = false;
    },
  },
});
