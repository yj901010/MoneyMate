<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 프로필 섹션 -->
    <ProfileHeader 
      :user="user" 
      @edit="navigateToEdit"
      @addProduct="openAddProductModal"
      @productRemoved="fetchUserProfile"
    />

    <AddProductModal 
      v-if="showAddProductModal"
      :is-open="showAddProductModal"
      @close="closeAddProductModal"
      @product-added="handleProductAdded"
    />

    <!-- 나의 투자 성향 섹션 -->
    <div class="mt-8 bg-white rounded-lg shadow-md p-6">
      <h2 class="text-xl font-bold mb-4">나의 투자 성향은?</h2>
      <div v-if="investmentStyle">
        <p class="text-gray-700">당신의 투자 성향: <strong>{{ investmentStyle.style }}</strong></p>
        <p class="text-gray-600 mt-2">{{ investmentStyle.feature }}</p>
        <p class="text-gray-600 mt-2">{{ investmentStyle.strategy }}</p>
        <button
          @click="showSurveyModal = true"
          class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          투자 성향 다시 파악하기
        </button>
      </div>
      <div v-else>
        <p class="text-gray-600 mb-4">투자 성향을 파악해보세요.</p>
        <button
          @click="showSurveyModal = true"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          투자 성향 파악하기
        </button>
      </div>
    </div>


    <!-- 투자 상품 추천 섹션 -->
    <div class="mt-8 bg-white rounded-lg shadow-md p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold">투자 상품 추천</h2>
          <p class="text-gray-600 text-sm mt-1">
            현재 투자 성향과 수입을 기반으로 맞춤형 포트폴리오를 추천받아보세요.
          </p>
        </div>
        <button
          @click="getRecommendation"
          :disabled="!user.income || !investmentStyle || isLoading"
          class="flex items-center gap-2 bg-[#699BF7] text-white px-6 py-3 rounded-lg hover:bg-[#5B8AE0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <!-- 로딩 중일 때 스피너 표시 -->
          <div v-if="isLoading" class="animate-spin rounded-full h-5 w-5 border-2 border-b-transparent border-white"></div>
          <!-- 로딩 중이 아닐 때 아이콘 표시 -->
          <span v-else class="material-icons-outlined text-xl">trending_up</span>
          {{ isLoading ? '분석중...' : '추천받기' }}
        </button>
      </div>

      <!-- 로딩 중 메시지 -->
      <div v-if="isLoading" class="text-center p-8">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-[#699BF7] border-b-transparent"></div>
          <p class="text-gray-600">투자 포트폴리오를 분석하고 있습니다...</p>
        </div>
      </div>

      <!-- 필수 정보 안내 -->
      <div v-if="!user.income || !investmentStyle" class="text-sm text-red-500 mt-2">
        <p v-if="!user.income">* 소득 정보를 입력해주세요.</p>
        <p v-if="!investmentStyle">* 투자 성향 설문을 완료해주세요.</p>
      </div>

      <!-- 이전 추천 내역 -->
      <div v-if="lastRecommendationDate && !isLoading" class="mt-4 p-4 bg-gray-50 rounded-lg">
        <div class="flex justify-between items-center">
          <p class="text-sm text-gray-500">
            마지막 추천 일자: {{ formatDate(lastRecommendationDate) }}
          </p>
          <button 
            @click="showLastRecommendation"
            class="text-sm text-[#699BF7] hover:text-[#5B8AE0]"
          >
            이전 추천 내역 보기
          </button>
        </div>
      </div>
    </div>

    <!-- 추천 카드 모달 -->
    <RecommendationCard
      v-if="showRecommendation"
      :portfolioItems="recommendationContent"
      @close="showRecommendation = false"
    />
    <!-- 설문조사 모달 -->
    <SurveyModal 
      v-if="showSurveyModal" 
      @close="closeSurveyModal" 
      @submitted="fetchUserProfile" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SurveyModal from '@/components/survey/SurveyModal.vue';
import AddProductModal from '@/components/auth/AddProductModal.vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import RecommendationCard from '@/components/auth/InvestmentRecommendation.vue';
import ProfileHeader from '@/components/auth/ProfileHeader.vue';

const router = useRouter();
const authStore = useAuthStore();
const API_URL = authStore.API_URL;

const isLoading = ref(false);

const user = ref({
  username: '',
  main_bank: '',
  subscribed_products: [],
  profile_image: '',
});

const investmentStyle = ref(null); // 투자 성향 정보
const showSurveyModal = ref(false);

const showRecommendation = ref(false);
const recommendationContent = ref('');
const lastRecommendationDate = ref(null);
const showAddProductModal = ref(false);

// income 포맷팅 함수
const formatIncome = (income) => {
  if (!income) return '정보 없음';
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0
  }).format(income * 10000); // DB에 저장된 값을 원 단위로 변환
};

// 이전 추천 내역 표시
const showLastRecommendation = () => {
  if (recommendationContent.value) {
    showRecommendation.value = true;
  }
};

const fetchUserProfile = async () => {
  try {
    const response = await axios.get(`${API_URL}/account/profile/`, {
      headers: {
        Authorization: `Token ${authStore.token}`,
      },
    });
    user.value = response.data;

    // 투자 성향 가져오기
    const styleResponse = await axios.get(`${API_URL}/chatbot/get-user-investment-style/`, {
      headers: {
        Authorization: `Token ${authStore.token}`,
      },
    });
    investmentStyle.value = styleResponse.data;

    // 마지막 추천 결과 가져오기
    await fetchLastPortfolio();
  } catch (error) {
    console.error('프로필 정보를 가져오는데 실패했습니다:', error);
  }
};

const navigateToEdit = () => {
  router.push('/profile/edit');
  console.log('프로필 수정 페이지로 이동');
};

const openAddProductModal = () => {
  console.log('Opening modal');
  showAddProductModal.value = true;
};

const closeAddProductModal = () => {
  showAddProductModal.value = false;
};

const handleProductAdded = async () => {
  await fetchUserProfile(); // 프로필 정보 새로고침
  closeAddProductModal();
};

const closeSurveyModal = () => {
  showSurveyModal.value = false;
};

const getRecommendation = async () => {
  try {
    if (!user.value.income || !investmentStyle.value) {
      console.error('필수 정보가 누락되었습니다.');
      return;
    }

    isLoading.value = true;

    const response = await axios.get(`${API_URL}/chatbot/make-portfolio/`, {
      headers: {
        Authorization: `Token ${authStore.token}`,
      },
    });
    
    console.log('API Response:', response.data); // 디버깅용

    if (response.data.portfolio) {
      recommendationContent.value = response.data.portfolio;
      showRecommendation.value = true;
      lastRecommendationDate.value = response.data.portfolio.created_at;
      console.log('Recommendation Content:', recommendationContent.value); // 디버깅용
    }
  } catch (error) {
    console.error('추천 정보를 가져오는데 실패했습니다:', error);
  } finally {
    isLoading.value = false;
  }
};

const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const fetchLastPortfolio = async () => {
  try {
    const response = await axios.get(`${API_URL}/chatbot/latest-portfolio/`, {
      headers: {
        Authorization: `Token ${authStore.token}`,
      },
    });
    
    if (response.data) {
      recommendationContent.value = response.data;
      lastRecommendationDate.value = response.data.created_at;
    }
  } catch (error) {
    console.error('최근 포트폴리오 정보를 가져오는데 실패했습니다:', error);
  }
};

onMounted(() => {
  fetchUserProfile();
});
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>