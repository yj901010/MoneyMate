<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="closeModal"></div>
 
    <div class="relative min-h-screen flex items-center justify-center p-4">
      <div class="relative bg-white rounded-xl shadow-lg w-full max-w-4xl p-6">
        <!-- Header -->
        <div class="flex items-center justify-between border-b pb-4">
          <h3 class="text-xl font-semibold text-gray-800">예적금 추가</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times"></i>
          </button>
        </div>
 
        <!-- Content Area -->
        <div class="py-4 h-[600px]">
          <!-- Search and Filter - Full Width -->
          <div class="mb-4">
            <div class="flex gap-4 mb-4">
              <div class="flex-grow">
                <input 
                  type="text" 
                  v-model="searchQuery"
                  placeholder="상품명 검색..."
                  class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <select 
                v-model="selectedBank"
                class="w-48 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체 은행</option>
                <option v-for="bank in uniqueBanks" :key="bank" :value="bank">
                  {{ bank }}
                </option>
              </select>
            </div>
          </div>
 
          <!-- Content Columns -->
          <div class="flex gap-4 h-[500px]">
            <!-- Left Column: Product Selection -->
            <div class="flex-1 flex flex-col">
              <div class="flex-1 overflow-y-auto pr-2">
                <div class="space-y-3">
                  <div v-for="product in filteredProducts" 
                       :key="product.id"
                       @click="toggleProduct(product)"
                       :class="[
                         'p-4 border rounded-lg transition-colors cursor-pointer',
                         isSelected(product) 
                           ? 'bg-blue-50 border-blue-300' 
                           : 'hover:bg-gray-50'
                       ]"
                  >
                    <div class="flex items-center justify-between">
                      <div class="flex-1">
                        <div class="flex items-center">
                          <i 
                            :class="[
                              'fas mr-2',
                              isSelected(product) 
                                ? 'fa-check-circle text-blue-500' 
                                : 'fa-circle text-gray-300'
                            ]"
                          ></i>
                          <div>
                            <h4 class="font-medium text-gray-800">{{ product.productName }}</h4>
                            <p class="text-sm text-gray-600">{{ product.bankName }}</p>
                          </div>
                        </div>
                      </div>
                      <div class="text-right">
                        <p class="text-sm font-medium text-blue-600">{{ product.maxRate }}%</p>
                        <p class="text-xs text-gray-500">{{ product.maxMonth }}개월</p>
                      </div>
                    </div>
                  </div>
                </div>
 
                <!-- Empty State -->
                <div v-if="filteredProducts.length === 0" class="text-center py-8 text-gray-500">
                  검색 결과가 없습니다.
                </div>
              </div>
            </div>
 
            <!-- Right Column: Selected Products -->
            <div class="w-96 flex flex-col border-l pl-4">
              <h4 class="font-medium text-gray-800 mb-2 flex justify-between items-center">
                <span>선택한 상품 ({{ selectedProducts.length }})</span>
                <button 
                  v-if="selectedProducts.length > 0"
                  @click="selectedProducts = []"
                  class="text-sm text-gray-500 hover:text-gray-700"
                >
                  전체 해제
                </button>
              </h4>
              <div class="flex-1 overflow-y-auto pr-2">
                <div class="space-y-2">
                  <div v-for="p in selectedProducts" 
                       :key="p.id" 
                       class="bg-blue-50 p-3 rounded-lg">
                    <div class="flex justify-between items-start">
                      <div class="flex-1">
                        <p class="font-medium text-gray-800">{{ p.productName }}</p>
                        <p class="text-sm text-gray-600">
                          {{ p.bankName }} | 
                          {{ p.maxRate }}% | 
                          {{ p.maxMonth }}개월
                        </p>
                      </div>
                      <button 
                        @click.stop="removeProduct(p)"
                        class="text-red-500 hover:text-red-600 ml-2"
                      >
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
 
              <!-- Add Button -->
              <div class="pt-4 border-t mt-4">
                <button 
                  @click="addSelectedProducts"
                  :disabled="selectedProducts.length === 0"
                  class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  선택한 상품 추가하기 ({{ selectedProducts.length }}개)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
 </template>
 
 <script setup>
 import { ref, computed, onMounted } from 'vue';
 import { useFinanceStore } from '@/stores/finance';
 
 const store = useFinanceStore();
 
 const props = defineProps({
  isOpen: Boolean
 });
 
 const emit = defineEmits(['close', 'productAdded']);
 
 const searchQuery = ref('');
 const selectedBank = ref('');
 const selectedProducts = ref([]);
 
 // 상품이 선택되었는지 확인하는 함수
 const isSelected = (product) => {
  return selectedProducts.value.some(p => p.id === product.id);
 };
 
// 필터링된 상품 목록
const filteredProducts = computed(() => {
  return store.products.filter(product => {
    // 검색어 매칭
    const matchesSearch = product.productName.toLowerCase()
      .includes(searchQuery.value.toLowerCase());
    
    // 은행 매칭
    const matchesBank = !selectedBank.value || product.bankName === selectedBank.value;
    
    // 이미 구독한 상품인지 확인
    const isNotSubscribed = !store.userSubscribedProducts.some(
      subProduct => subProduct.fin_prdt_cd === product.id
    );

    // 모든 조건을 만족하는 상품만 반환
    return matchesSearch && matchesBank && isNotSubscribed;
  });
});
 
 // 상품 선택/해제 토글
 const toggleProduct = (product) => {
  const index = selectedProducts.value.findIndex(p => p.id === product.id);
  if (index === -1) {
    selectedProducts.value.push(product);
  } else {
    selectedProducts.value.splice(index, 1);
  }
 };
 
 // 선택한 상품 제거
 const removeProduct = (product) => {
  const index = selectedProducts.value.findIndex(p => p.id === product.id);
  if (index !== -1) {
    selectedProducts.value.splice(index, 1);
  }
 };
 
 // 선택한 상품들 추가
 const addSelectedProducts = async () => {
  if (selectedProducts.value.length === 0) return;
 
  try {
    for (const product of selectedProducts.value) {
      await store.addProductToAccount(product.id); // 스토어 액션 사용
    }
    
    emit('productAdded');
    closeModal();
  } catch (error) {
    console.error('상품 추가에 실패했습니다:', error);
  }
 };
 
 const closeModal = () => {
  selectedProducts.value = [];
  searchQuery.value = '';
  selectedBank.value = '';
  emit('close');
 };

 const uniqueBanks = computed(() => {
    const bankSet = new Set();
    store.products.forEach(product => {
      bankSet.add(product.bankName); // 모든 은행 이름 추가
    });
    return Array.from(bankSet); // 고유한 은행 이름 배열 반환
  });
 
 onMounted(async () => {
  if (props.isOpen) {
    await store.fetchUserSubscribedProducts();
    await store.fetchProducts();
  }
 });
 </script>
