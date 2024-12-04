<script setup>
import { ref, watch } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const props = defineProps({
  isOpen: Boolean
});
const emit = defineEmits(['close']);

const currentTab = ref('Login'); // 기본 화면: 로그인
const loginForm = ref({
  username: '',
  password: ''
});
const emailForRecovery = ref(''); // 이메일 입력 상태
const recoveryMessage = ref(''); // 복구 메시지
const isRecovering = ref(false); // 복구 요청 상태
const csrfToken = ref(''); // CSRF 토큰 저장

const authStore = useAuthStore();

const closeModal = () => {
  resetFields(); // 입력값 초기화
  emit('close');
};

// 입력값 초기화
const resetFields = () => {
  currentTab.value = 'Login';
  loginForm.value.username = '';
  loginForm.value.password = '';
  emailForRecovery.value = '';
  recoveryMessage.value = '';
  isRecovering.value = false;
};

// CSRF 토큰 가져오기
const fetchCSRFToken = async () => {
  try {
    console.log('CSRF 토큰 가져오는 중...');
    const response = await axios.get('http://localhost:8000/account/get-csrf-token/');
    csrfToken.value = response.data.csrftoken;
    console.log('CSRF 토큰 가져오기 성공:', csrfToken.value);
  } catch (error) {
    console.error('CSRF 토큰 가져오기 실패:', error);
  }
};

// 로그인 처리
const handleLogin = async () => {
  try {
    console.log('로그인 시도 중...');
    await authStore.logIn(loginForm.value);
    console.log('로그인 성공');
    closeModal();
  } catch (error) {
    console.error('로그인 실패:', error);
  }
};

// 아이디 찾기 API 호출
const findId = async () => {
  if (!emailForRecovery.value.trim()) {
    recoveryMessage.value = '이메일을 입력해주세요.';
    return;
  }

  try {
    console.log('아이디 찾기 요청 시작...');
    isRecovering.value = true;

    const formData = new URLSearchParams();
    formData.append('email', emailForRecovery.value);

    const response = await axios.post('http://localhost:8000/account/find-id/', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    recoveryMessage.value = `회원님의 아이디는: ${response.data.User_Id}`;
    console.log('아이디 찾기 성공:', response.data);
  } catch (error) {
    recoveryMessage.value = '아이디를 찾을 수 없습니다. 이메일을 확인해주세요.';
    console.error('아이디 찾기 실패:', error);
  } finally {
    isRecovering.value = false;
  }
};

const getCSRFToken = () => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='));
  if (!cookieValue) {
    console.error('CSRF 토큰을 찾을 수 없습니다.');
    return null; // 반환값이 없을 경우 null 반환
  }
  return cookieValue.split('=')[1];
};

const resetPassword = async () => {
  if (!emailForRecovery.value.trim()) {
    recoveryMessage.value = '이메일을 입력해주세요.';
    return;
  }

  try {
    isRecovering.value = true;
    const csrfToken = getCSRFToken(); // CSRF 토큰 가져오기
  
    if (!csrfToken) {
      recoveryMessage.value = 'CSRF 토큰이 누락되었습니다.';
      return;
    }

    console.log('CSRF 토큰:', csrfToken);

    const response = await axios.post(
      'http://localhost:8000/account/password_reset/',
      { email: emailForRecovery.value },
      {
        headers: {
          'X-CSRFToken': csrfToken,
        },
        withCredentials: true, // 쿠키 전송 포함
      }
    );

    recoveryMessage.value = '비밀번호 재설정 링크가 이메일로 전송되었습니다.';
  } catch (error) {
    recoveryMessage.value = '비밀번호 재설정 요청에 실패했습니다.';
    console.error('비밀번호 재설정 실패:', error.response || error);
  } finally {
    isRecovering.value = false;
  }
};

// 회원가입 페이지로 이동
const handleRegisterClick = () => {
  closeModal();
  router.push('/register');
};

// 탭 변경 시 필드 초기화
const switchTab = (tabName) => {
  resetFields(); // 필드 초기화
  currentTab.value = tabName;
};

// 모달 닫힐 때 입력값 초기화
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      console.log('모달 열림 - CSRF 토큰 가져오기 시작');
      fetchCSRFToken();
    } else {
      console.log('모달 닫힘 - 입력값 초기화');
      resetFields();
    }
  }
);
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen">
      <div class="fixed inset-0 bg-black opacity-50" @click="closeModal"></div>
      <div class="relative bg-white rounded-lg w-full max-w-md p-6">
        <!-- 헤더 -->
        <h2 class="text-xl font-bold text-center mb-6">
          {{ currentTab === 'Login' ? '로그인' : currentTab === 'FindId' ? '아이디 찾기' : '비밀번호 찾기' }}
        </h2>

        <!-- 로그인 -->
        <div v-if="currentTab === 'Login'">
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">아이디</label>
              <input
                type="text"
                v-model="loginForm.username"
                class="mt-1 block w-full rounded-md border border-gray-300 p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">비밀번호</label>
              <input
                type="password"
                v-model="loginForm.password"
                class="mt-1 block w-full rounded-md border border-gray-300 p-2"
              />
            </div>
            <button type="submit" class="w-full bg-[#699BF7] text-white py-2 rounded-md hover:bg-blue-600">
              로그인
            </button>
          </form>
          <div class="text-sm mt-4 text-gray-500 text-center">
            <span @click="switchTab('FindId')" class="cursor-pointer text-[#699BF7] hover:underline">
              아이디 찾기
            </span>
            &nbsp;|&nbsp;
            <span @click="switchTab('FindPassword')" class="cursor-pointer text-[#699BF7] hover:underline">
              비밀번호 찾기
            </span>
            &nbsp;|&nbsp;
            <span @click="handleRegisterClick" class="cursor-pointer text-[#699BF7] hover:underline">
              회원가입
            </span>
          </div>
        </div>

        <!-- 아이디 찾기 -->
        <div v-else-if="currentTab === 'FindId'">
          <p class="text-gray-700 text-sm mb-4">가입 시 사용한 이메일을 입력해주세요.</p>
          <input
            type="email"
            v-model="emailForRecovery"
            placeholder="이메일"
            class="mt-1 block w-full rounded-md border border-gray-300 p-2 mb-4"
          />
          <button
            @click="findId"
            :disabled="isRecovering"
            class="w-full bg-green-500 text-white py-2 rounded-md hover:bg-green-600 disabled:opacity-50"
          >
            아이디 찾기
          </button>
          <p v-if="recoveryMessage" class="mt-4 text-sm text-gray-700">
            {{ recoveryMessage }}
          </p>
          <p class="mt-4 text-center text-sm text-gray-500">
            <span @click="switchTab('Login')" class="cursor-pointer text-[#699BF7] hover:underline">
              로그인 화면으로 돌아가기
            </span>
          </p>
        </div>

        <!-- 비밀번호 찾기 -->
        <div v-else-if="currentTab === 'FindPassword'">
          <p class="text-gray-700 text-sm mb-4">가입 시 사용한 이메일을 입력해주세요.</p>
          <input
            type="email"
            v-model="emailForRecovery"
            placeholder="이메일"
            class="mt-1 block w-full rounded-md border border-gray-300 p-2 mb-4"
          />
          <button
            @click="resetPassword"
            :disabled="isRecovering"
            class="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
          >
            비밀번호 재설정
          </button>
          <p v-if="recoveryMessage" class="mt-4 text-sm text-gray-700">
            {{ recoveryMessage }}
          </p>
          <p class="mt-4 text-center text-sm text-gray-500">
            <span @click="switchTab('Login')" class="cursor-pointer text-[#699BF7] hover:underline">
              로그인 화면으로 돌아가기
            </span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
