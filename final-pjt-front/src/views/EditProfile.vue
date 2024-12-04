<template>
  <div class="container mx-auto px-4 py-8">
    <h2 class="text-2xl font-bold mb-4">회원정보 수정</h2>
    <form @submit.prevent="handleUpdate" class="bg-white p-6 rounded-lg shadow-md space-y-4">
      <!-- 프로필 이미지 -->
      <div>
        <label class="block text-sm font-medium mb-1">프로필 이미지</label>
        <div class="flex items-center space-x-4">
          <img
            v-if="previewImage || profileImageUrl"
            :src="previewImage || profileImageUrl"
            alt="프로필 이미지"
            class="w-16 h-16 rounded-full object-cover border"
          />
          <input type="file" @change="handleImageUpload" class="border border-gray-300 rounded-lg p-2" />
        </div>
      </div>
      <!-- 이메일 -->
      <div>
        <label class="block text-sm font-medium mb-1">이메일</label>
        <input v-model="email" type="email" class="border border-gray-300 rounded-lg w-full p-2" />
      </div>
      <!-- 소득 -->
      <div>
        <label class="block text-sm font-medium mb-1">소득</label>
        <input v-model="income" type="number" class="border border-gray-300 rounded-lg w-full p-2" />
      </div>
      <!-- 직업 -->
      <div>
        <label class="block text-sm font-medium mb-1">직업</label>
        <input v-model="job" type="text" class="border border-gray-300 rounded-lg w-full p-2" />
      </div>
      <!-- 전화번호 -->
      <div>
        <label class="block text-sm font-medium mb-1">전화번호</label>
        <input v-model="phone" type="text" class="border border-gray-300 rounded-lg w-full p-2" />
      </div>
      <!-- 주거래 은행 -->
      <div class="relative">
        <label class="block text-sm font-medium mb-1">주거래 은행</label>
        <div class="relative">
          <button
            @click="toggleDropdown"
            type="button"
            class="border border-gray-300 rounded-lg w-full p-2 bg-white text-left"
          >
            {{ mainBank || '은행 선택' }}
          </button>
          <ul
            v-if="showDropdown"
            class="absolute z-10 bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-auto w-full"
          >
            <li
              v-for="(bank, index) in visibleBanks"
              :key="index"
              @click="selectBank(bank)"
              class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
            >
              {{ bank }}
            </li>
          </ul>
        </div>
      </div>
      <!-- 수정 버튼 -->
      <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        수정하기
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';

const authStore = useAuthStore();

const email = ref('');
const income = ref('');
const job = ref('');
const phone = ref('');
const mainBank = ref('');
const profileImage = ref(null);
const profileImageUrl = ref('');
const previewImage = ref(null);

const bankList = ref([]);
const visibleBanks = ref([]);
const showDropdown = ref(false);

// 프로필 데이터 초기화
const initializeProfile = async () => {
  try {
    const response = await authStore.getUserProfile();
    const { email: userEmail, income: userIncome, job: userJob, phone: userPhone, main_bank, profile_image } =
      response.data;

    email.value = userEmail;
    income.value = userIncome;
    job.value = userJob;
    phone.value = userPhone;
    mainBank.value = main_bank;
    profileImageUrl.value = profile_image;
  } catch (error) {
    console.error('프로필 데이터를 불러오는 중 오류 발생:', error.response?.data || error.message);
  }
};

// 은행 목록 가져오기
const fetchBankList = async () => {
  try {
    const response = await axios.get('http://localhost:8000/finlife/getBankName/');
    bankList.value = response.data;
    visibleBanks.value = bankList.value.slice(0, 10);
  } catch (error) {
    console.error('은행 목록을 불러오는 중 오류 발생:', error.response?.data || error.message);
  }
};

// 드롭다운 토글
const toggleDropdown = (event) => {
  showDropdown.value = !showDropdown.value;
  event.stopPropagation(); // 드롭다운 클릭 시 다른 이벤트 중단
};

// 드롭다운 외부 클릭 감지
const handleOutsideClick = (event) => {
  if (!event.target.closest('.relative')) {
    showDropdown.value = false;
  }
};

// 은행 선택 처리
const selectBank = (bank) => {
  mainBank.value = bank;
  showDropdown.value = false;
};

// 이미지 업로드 처리
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  profileImage.value = file;
  previewImage.value = URL.createObjectURL(file);
};

// 회원정보 업데이트 처리
const handleUpdate = async () => {
  const formData = new FormData();
  formData.append('email', email.value);
  formData.append('income', income.value);
  formData.append('job', job.value);
  formData.append('phone', phone.value);
  formData.append('main_bank', mainBank.value);
  if (profileImage.value) {
    formData.append('profile_image', profileImage.value);
  }

  try {
    await authStore.updateUser(formData);
    alert('회원정보가 성공적으로 수정되었습니다.');
  } catch (error) {
    console.error('회원정보 수정 중 오류 발생:', error.response?.data || error.message);
    alert('회원정보 수정에 실패했습니다.');
  }
};

// 컴포넌트 마운트/언마운트 시 이벤트 등록/제거
onMounted(() => {
  initializeProfile();
  fetchBankList();
  document.addEventListener('click', handleOutsideClick);
});
onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>
