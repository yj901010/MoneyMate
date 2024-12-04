<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useFinanceStore } from '@/stores/finance';
import { useRouter } from 'vue-router';

// 기본 이미지 import (경로를 프로젝트에 맞게 조정하세요)
import default1 from '@/assets/default1.jpg';
import default2 from '@/assets/default2.jpg';
import default3 from '@/assets/default3.jpg';
import default4 from '@/assets/default4.jpg';
import default5 from '@/assets/default5.jpg';

const router = useRouter();
const authStore = useAuthStore();
const financeStore = useFinanceStore();

const registerForm = ref({
  username: '',
  password1: '',
  password2: '',
  email: '',
  first_name: '',
  last_name: '',
  profile_image: null,
  subscribed_products: [],
  birth: '',
  phone: '',
  income: '',
  job: '',
  main_bank: ''
});

const selectedProducts = ref([]);

// 이미지 미리보기 URL
const imagePreview = ref('');

// 선택된 기본 이미지 ID를 추적하기 위한 변수
const selectedDefaultImage = ref(null);

// 기본 이미지 목록
const defaultImages = [
  { id: 'default1', src: default1 },
  { id: 'default2', src: default2 },
  { id: 'default3', src: default3 },
  { id: 'default4', src: default4 },
  { id: 'default5', src: default5 },
];

// 프로필 이미지 업로드 처리
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    registerForm.value.profile_image = file;
    imagePreview.value = URL.createObjectURL(file);
    selectedDefaultImage.value = null; // 기본 이미지 선택 해제
  } else {
    registerForm.value.profile_image = null;
    imagePreview.value = '';
  }
};

// 기본 이미지 선택 처리
const selectDefaultImage = async (imageSrc, imageId) => {
  try {
    const response = await fetch(imageSrc);
    if (!response.ok) {
      throw new Error('이미지를 불러올 수 없습니다.');
    }
    const blob = await response.blob();
    const file = new File([blob], 'default-profile.jpg', { type: blob.type });
    registerForm.value.profile_image = file;
    imagePreview.value = URL.createObjectURL(file);
    selectedDefaultImage.value = imageId; // 선택된 기본 이미지 ID 설정
  } catch (error) {
    console.error('기본 이미지 로딩 오류:', error);
    alert('기본 이미지를 불러오는 데 문제가 발생했습니다.');
  }
};

// 상품 선택/해제 처리
const toggleProduct = (product) => {
  const index = selectedProducts.value.findIndex(p => p.id === product.id);
  if (index === -1) {
    // 새로운 상품 추가
    selectedProducts.value.push({
      id: product.id,  // fin_prdt_cd
      fin_prdt_nm: product.fin_prdt_nm,
      kor_co_nm: product.kor_co_nm
    });
  } else {
    // 기존 상품 제거
    selectedProducts.value.splice(index, 1);
  }
  // subscribed_products 업데이트
  registerForm.value.subscribed_products = selectedProducts.value.map(p => p.id);
};

// 회원가입 처리
const handleRegister = async () => {
  try {
    console.log(registerForm.value);
    // 비밀번호 일치 여부 확인
    if (registerForm.value.password1 !== registerForm.value.password2) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }

    // 전화번호 형식 확인
    const phoneRegex = /^01([0|1|6|7|8|9])?([0-9]{3,4})?([0-9]{4})$/;
    if (!phoneRegex.test(registerForm.value.phone)) {
      alert('올바른 전화번호 형식이 아닙니다.');
      return;
    }

    // 프로필 이미지 필수 선택 처리 (업로드 또는 기본 이미지 선택)
    if (!registerForm.value.profile_image) {
      alert('프로필 이미지를 업로드하거나 기본 이미지 중 하나를 선택해주세요.');
      return;
    }

    const formData = new FormData();
    const formattedPhone = `+82${registerForm.value.phone.slice(1)}`;

    // subscribed_products를 제외한 다른 필드들 추가
    Object.keys(registerForm.value).forEach(key => {
      if (key === 'subscribed_products') {
        return; // subscribed_products는 따로 처리
      }

      if (key === 'profile_image' && registerForm.value[key]) {
        formData.append(key, registerForm.value[key]);
      } else if (key === 'phone') {
        formData.append(key, formattedPhone);
      } else if (key === 'income') {
        formData.append(key, registerForm.value[key] ? parseFloat(registerForm.value[key]) : '');
      } else {
        formData.append(key, registerForm.value[key]);
      }
    });

    // subscribed_products를 문자열 배열로 변환하여 추가 (parseInt 제거)
    selectedProducts.value.forEach(product => {
      formData.append('subscribed_products', product.id);
    });

    // FormData 내용 확인 (디버깅 용도)
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }

    // 회원가입 요청
    const success = await authStore.register(formData);
    if (success) {
      router.push('/');
    }
  } catch (error) {
    console.error('회원가입 처리 중 오류:', error);
    alert('회원가입 처리 중 오류가 발생했습니다.');
  }
};

onMounted(async () => {
  await financeStore.fetchBanks();
  await financeStore.fetchProducts();
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-[#699BF7] mb-6">회원가입</h1>
    <div class="bg-white rounded-lg shadow-md p-6">
      <form @submit.prevent="handleRegister" class="space-y-4" enctype="multipart/form-data">
        <!-- 프로필 이미지 업로드 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">프로필 이미지 업로드</label>
          <input
            type="file"
            accept="image/*"
            @change="handleImageUpload"
            class="mt-1 block w-full"
          />
          <img v-if="imagePreview" :src="imagePreview" class="mt-2 h-32 w-32 object-cover rounded-full" />
        </div>

        <!-- 기본 이미지 선택 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">기본 이미지 선택</label>
          <div class="flex space-x-2">
            <div v-for="image in defaultImages" :key="image.id" class="flex flex-col items-center">
              <img
                :src="image.src"
                alt="Default Image"
                class="h-24 w-24 object-cover rounded-full cursor-pointer border-2"
                @click="selectDefaultImage(image.src, image.id)"
                :class="{
                  'border-blue-500': selectedDefaultImage === image.id
                }"
              />
              <span class="text-sm mt-1">기본{{ image.id.slice(-1) }}</span>
            </div>
          </div>
        </div>

        <!-- 아이디 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">아이디</label>
          <input
            type="text"
            v-model="registerForm.username"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 비밀번호 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">비밀번호</label>
          <input
            type="password"
            v-model="registerForm.password1"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">비밀번호 확인</label>
          <input
            type="password"
            v-model="registerForm.password2"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 이메일 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">이메일</label>
          <input
            type="email"
            v-model="registerForm.email"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 이름 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">이름</label>
          <input
            type="text"
            v-model="registerForm.first_name"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 성 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">성</label>
          <input
            type="text"
            v-model="registerForm.last_name"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 생년월일 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">생년월일</label>
          <input
            type="date"
            v-model="registerForm.birth"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 전화번호 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">전화번호</label>
          <input
            type="tel"
            v-model="registerForm.phone"
            required
            placeholder="01012345678"
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 소득 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">소득</label>
          <input
            type="number"
            v-model="registerForm.income"
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 직업 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">직업</label>
          <input
            type="text"
            v-model="registerForm.job"
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>

        <!-- 주 거래 은행 -->
        <div>
          <label class="block text-sm font-medium text-gray-700">주 거래 은행</label>
          <select
            v-model="registerForm.main_bank"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 p-2"
          >
            <option value="">은행을 선택하세요</option>
            <option v-for="bank in financeStore.banks" :key="bank.code" :value="bank.code">
              {{ bank.name }}
            </option>
          </select>
        </div>

        <!-- 가입한 상품 선택 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">가입한 상품 선택</label>
          <div class="space-y-2 max-h-60 overflow-y-auto">
            <div v-for="product in financeStore.availableProducts" :key="product.id" 
                class="flex items-center justify-between p-2 border rounded hover:bg-gray-50"
                :class="{ 'bg-blue-50': selectedProducts.some(p => p.id === product.id) }">
              <div>
                <span class="font-medium">{{ product.fin_prdt_nm }}</span>
                <span class="text-sm text-gray-500 ml-2">({{ product.kor_co_nm }})</span>
              </div>
              <button 
                type="button"
                @click="toggleProduct(product)"
                class="px-3 py-1 rounded text-sm"
                :class="selectedProducts.some(p => p.id === product.id) ? 
                  'bg-red-500 text-white hover:bg-red-600' : 'bg-blue-500 text-white hover:bg-blue-600'"
              >
                {{ selectedProducts.some(p => p.id === product.id) ? '취소' : '선택' }}
              </button>
            </div>
          </div>
          <div v-if="selectedProducts.length > 0" class="mt-2">
            <p class="text-sm font-medium text-gray-700">선택된 상품:</p>
            <div class="flex flex-wrap gap-2 mt-1">
              <span 
                v-for="product in selectedProducts" 
                :key="product.id"
                class="inline-flex items-center px-2 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {{ product.fin_prdt_nm }}
                <button 
                  @click="toggleProduct(product)" 
                  class="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            </div>
          </div>
        </div>

        <!-- 취소 및 회원가입 버튼 -->
        <div class="flex gap-4">
          <button 
            type="button" 
            @click="router.push('/')"
            class="flex-1 px-4 py-2 border rounded hover:bg-gray-100"
          >
            취소
          </button>
          <button 
            type="submit"
            class="flex-1 bg-[#699BF7] text-white py-2 rounded-md hover:bg-blue-600"
          >
            회원가입
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
