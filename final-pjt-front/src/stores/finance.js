import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './authStore'

const BASE_URL = 'http://localhost:8000'

export const useFinanceStore = defineStore('finance', {
  state: () => ({
    banks: [],
    products: [],
    selectedProduct: null,
    productOptions: [],
    loading: false,
    error: null,
    userSubscribedProducts: []
  }),

  getters: {
    sortedProducts: (state) => {
      return [...state.products].sort((a, b) => b.maxRate - a.maxRate)
    },
    
    availableProducts: (state) => {
      return state.products.map(product => ({
        id: product.id,  // fin_prdt_cd
        fin_prdt_nm: product.productName,
        kor_co_nm: product.bankName
      }))
    },

    // 새로운 getter 추가: 구독하지 않은 상품만 필터링
    availableNewProducts: (state) => {
      return state.products.filter(product => 
        !state.userSubscribedProducts.some(
          subProduct => subProduct.fin_prdt_cd === product.id
        )
      )
    },

    // 검색과 필터링을 위한 새로운 getter
    filteredAvailableProducts: (state) => (searchQuery, bankCode) => {
      return state.products
        .filter(product => 
          // 이미 구독한 상품 제외
          !state.userSubscribedProducts.some(
            subProduct => subProduct.fin_prdt_cd === product.id
          ) &&
          // 검색어 필터링
          product.productName.toLowerCase().includes(searchQuery.toLowerCase()) &&
          // 은행 필터링
          (!bankCode || product.bankName === bankCode)
        )
    }
  },

  actions: {
    async findRates(productId) {
      try {
        const response = await axios.get(`${BASE_URL}/finlife/${productId}/top_rate_month/`)
        console.log(response)
        this.rates_months = {
          maxRate: response.data.max_rate,
          minRate: response.data.min_rate,
          minMonth:response.data.min_month,
          maxMonth:response.data.max_month,
        }
        return this.rates_months
      } catch (error) {
        this.error = '은행 목록을 불러오는데 실패했습니다.'
        console.error('Error fetching banks:', error)
      }
    },
    async fetchBanks() {
      try {
        const response = await axios.get(`${BASE_URL}/finlife/getBankName/`)
        this.banks = response.data.map(bankName => ({
          code: bankName,
          name: bankName
        }))
      } catch (error) {
        this.error = '은행 목록을 불러오는데 실패했습니다.'
        console.error('Error fetching banks:', error)
      }
    },

    async fetchUserSubscribedProducts() {
      const authStore = useAuthStore();
      try {
        const response = await axios.get(`${BASE_URL}/account/profile/`, {
          headers: {
            Authorization: `Token ${authStore.token}`,
          },
        });
        this.userSubscribedProducts = response.data.subscribed_products || [];
      } catch (error) {
        console.error('Error fetching user products:', error);
        this.userSubscribedProducts = [];
      }
    },

    async fetchProducts() {
      this.loading = true
      try {
        // 1. 상품 목록 가져오기
        const response = await axios.get(`${BASE_URL}/finlife/deposit-products/`)
        const products = response.data
        
        // 2. 각 상품에 대해 추가 정보를 가져오기
        const productsWithDetails = await Promise.all(products.map(async (item) => {
          // 첫 번째 API로부터 상품 기본 정보 가져오기
          const product = {
            id: item.fin_prdt_cd,
            bankName: item.kor_co_nm,
            productName: item.fin_prdt_nm,
            joinWay: item.join_way,
            joinMember: item.join_member,
            etcNote: item.etc_note,
            joinDeny: item.join_deny,
            spclCnd: item.spcl_cnd,  // `spcl_cnd` 필드는 두 번째 API에서 가져옴
          }
    
          // 3. 각 상품에 대해 두 번째 API 호출하여 추가 정보 가져오기
          try {
            const optionResponse = await axios.get(`${BASE_URL}/finlife/${item.fin_prdt_cd}/top_rate_month/`)
            console.log('옵션 응답',optionResponse.data)
            product.maxRate = parseFloat(optionResponse.data.max_rate || 0),
            product.minRate = parseFloat(optionResponse.data.min_rate || 0),
            product.maxMRate = parseFloat(optionResponse.data.max_Mrate || 0),
            product.maxMonth = parseFloat(optionResponse.data.max_month || 0),
            product.minMonth = parseFloat(optionResponse.data.min_month || 0)
          } catch (error) {
            console.error(`Error fetching options for product ${item.fin_prdt_cd}:`, error)
            product.spclCnd = '정보 없음';  // 옵션 정보가 없으면 기본값으로 설정
          }
          console.log(product)
          return product
        }))
    
        this.products = productsWithDetails
    
      } catch (error) {
        this.error = '상품 정보를 불러오는데 실패했습니다.'
        console.error('Error fetching products:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchProductOptions(productId) {
      try {
        const response = await axios.get(`${BASE_URL}/finlife/deposit-products-options/${productId}/`)
        this.productOptions = response.data
        return response.data
      } catch (error) {
        this.error = '상품 옵션을 불러오는데 실패했습니다.'
        console.error('Error fetching product options:', error)
      }
    },

    setSelectedProduct(product) {
      this.selectedProduct = product
    },

    clearSelectedProduct() {
      this.selectedProduct = null
    },

    filterProducts(bankCode, period) {
      return this.products.filter(product => 
        (!bankCode || product.bankName === bankCode) &&
        (!period || (product.minMonth <= parseInt(period) && product.maxMonth >= parseInt(period)))
      )
    },

    async addProductToAccount(productId) {
      const authStore = useAuthStore();
      try {
        const response = await axios.post(
          `${BASE_URL}/account/add-product/`,
          { product_id: productId },
          {
            headers: {
              Authorization: `Token ${authStore.token}`, // 인증 토큰 포함
            },
          }
        );
        console.log('상품 추가 성공:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error adding product to account:', error.response?.data || error.message);
        throw error; // 호출한 쪽에서 처리할 수 있도록 예외를 다시 던짐
      }
    },

    async removeProductFromAccount(productId) {
      const authStore = useAuthStore();
      try {
        const response = await axios.delete(
          `${BASE_URL}/account/remove-product/`,
          {
            headers: {
              Authorization: `Token ${authStore.token}`,
            },
            data: { product_id: productId }
          }
        );
        console.log('상품 해지 성공:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error removing product from account:', error.response?.data || error.message);
        throw error;
      }
    }
    
  }
})