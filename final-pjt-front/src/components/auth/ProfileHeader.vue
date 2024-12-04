<!-- ProfileHeader.vue -->
<template>
  <div class="w-full">
    <!-- Main profile card -->
    <div class="bg-white rounded-xl shadow-lg p-6">
      <!-- Profile header section -->
      <div class="flex items-start space-x-6">
        <!-- Profile image -->
        <div class="relative flex-shrink-0">
          <div class="w-24 h-24 rounded-full overflow-hidden">
            <img 
              :src="profileImage"
              :alt="user?.username"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

        <!-- User info -->
        <div class="flex-grow">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-800">{{ user?.username }}</h2>
            <button @click="$emit('edit')"
                    class="flex items-center text-gray-600 hover:text-gray-800 transition-colors">
              <span class="mr-1">수정하기</span>
              <i class="fas fa-pencil-alt text-sm"></i>
            </button>
          </div>
          
          <div class="mt-2 space-y-1">
            <p class="text-gray-600">
              주거래 은행: {{ user?.main_bank || '정보 없음' }}
            </p>
            <p class="text-gray-600">
              연 수입: {{ formatIncome(user?.income) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Products section -->
      <div class="mt-6">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-800">가입한 예적금 목록</h3>
          <button @click="handleAddProduct"
                  class="flex items-center text-gray-600 hover:text-gray-800 transition-colors">
            <span class="mr-1">예적금 추가하기</span>
            <i class="fas fa-plus-circle text-sm"></i>
          </button>
        </div>
        <div v-if="user?.subscribed_products?.length" class="space-y-2">
          <div v-for="product in user.subscribed_products" 
              :key="product.id"
              class="p-3 bg-gray-50 rounded-lg font-medium group relative hover:bg-gray-100 transition-colors">
            <div class="flex justify-between items-center">
              <span>{{ product.fin_prdt_nm }}</span>
              <button 
                @click="removeSubscribedProduct(product)"
                class="text-gray-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 flex items-center gap-1"
              >
                <span class="text-sm">해지하기</span>
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500">
          가입한 예적금이 없습니다.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import AddProductModal from '@/components/auth/AddProductModal.vue';
import { useFinanceStore } from '@/stores/finance';
const store = useFinanceStore();

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['edit', 'addProduct']);

const profileImage = computed(() => {
  return props.user?.profile_image || '/default-profile.jpg';
});

const formatIncome = (income) => {
  if (!income) return '정보 없음';
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0
  }).format(income * 10000);
};

const handleAddProduct = () => {
  console.log('예적금 추가하기 버튼 클릭됨');
  emit('addProduct');  // defineEmits 대신 emit 사용
};

// 상품 해지 함수 추가
const removeSubscribedProduct = async (product) => {
  if (confirm(`'${product.fin_prdt_nm}' 상품을 정말 해지하시겠습니까?`)) {
    try {
      await store.removeProductFromAccount(product.fin_prdt_cd);
      // 성공적으로 삭제되면 부모 컴포넌트에 알림
      emit('productRemoved');
    } catch (error) {
      console.error('상품 해지에 실패했습니다:', error);
    }
  }
};
</script>