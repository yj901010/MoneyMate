<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-[#699BF7] mb-6">근처 은행 검색</h1>
    
    <!-- Search Bar -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="flex gap-4">
        <input 
          v-model="keyword"
          type="text"
          placeholder="지역 + 은행명을 입력하세요 (예: 강남 국민은행)"
          class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#699BF7]"
          @keyup.enter="searchPlaces"
        >
        <button 
          @click="searchPlaces"
          class="bg-[#699BF7] text-white px-6 py-2 rounded-lg hover:bg-[#5b8ce6] transition"
        >
          검색
        </button>
      </div>
    </div>

    <!-- Map and Products Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Map Section -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-md h-[600px]">
          <div id="map" class="w-full h-full rounded-lg"></div>
        </div>
      </div>

      <!-- Bank Products Section -->
      <div class="space-y-4">
        <div v-if="selectedBank" class="bg-white rounded-lg shadow-md p-4">
          <h3 class="text-lg font-bold text-[#699BF7] mb-4">{{ selectedBank }} 금리 정보</h3>
          
          <div v-if="loading" class="flex justify-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#699BF7]"></div>
          </div>

          <template v-else>
            <div v-for="product in bankProducts" 
                 :key="product.id"
                 class="mb-4 p-4 border rounded-lg hover:shadow-md transition"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h4 class="font-semibold">{{ product.productName }}</h4>
                  <p class="text-sm text-gray-500">{{ product.minMonth }}~{{ product.maxMonth }}개월</p>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-600">최고금리</p>
                  <p class="text-lg font-bold text-[#699BF7]">{{ product.maxMRate }}%</p>
                </div>
              </div>
              <div class="flex justify-between text-sm text-gray-600">
                <span>기본금리: {{ product.minRate }}%~{{ product.maxRate }}%</span>
                <button 
                  @click="showDetails(product)"
                  class="text-[#699BF7] hover:underline"
                >
                  상세보기
                </button>
              </div>
            </div>

            <div v-if="bankProducts.length === 0" class="text-center text-gray-500 py-4">
              등록된 상품이 없습니다.
            </div>
          </template>
        </div>
        
        <div v-else class="bg-white rounded-lg shadow-md p-4 text-center text-gray-500">
          은행을 선택하면 금리 정보가 표시됩니다.
        </div>
      </div>
    </div>

    <!-- Bank List Table -->
    <div class="mt-6">
      <div class="bg-gray-50 p-4 grid grid-cols-5 font-bold">
        <div>번호</div>
        <div>은행명</div>
        <div>주소1</div>
        <div>주소2</div>
        <div>전화번호</div>
      </div>
      <div id="placesList">
        <!-- Places will be dynamically added here -->
      </div>
      <div id="pagination" class="flex justify-center gap-2 mt-4">
        <!-- Pagination will be dynamically added here -->
      </div>
    </div>

    <!-- Product Details Modal -->
    <ProductDetailsModal
      v-if="selectedProduct"
      :product="selectedProduct"
      @close="selectedProduct = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFinanceStore } from '../stores/finance'
import ProductDetailsModal from '../components/ProductDetailsModal.vue'
const options = ref([])
const store = useFinanceStore()
const map = ref(null)
const ps = ref(null)
const infowindow = ref(null)
const markers = ref([])
const keyword = ref('')
const selectedBank = ref(null)
const selectedProduct = ref(null)
const loading = ref(false)

const bankProducts = computed(() => {
  if (!selectedBank.value) return []
  
  return store.products.filter(product => 
    product.bankName === selectedBank.value
  ).sort((a, b) => b.maxRate - a.maxRate)
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW'
  }).format(value)
}

const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve()
      return
    }
    const scriptSrc = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=6406bc8e1c6758394fcffcddffbb124d&libraries=services&autoload=false';
    const script = document.createElement('script');
    script.onload = () => {
      kakao.maps.load(() => {
        resolve(); // 지도 API 초기화 완료
      });
    };
    script.onerror = reject;
    script.src = scriptSrc;
    document.head.appendChild(script)
  })
}

const searchPlaces = () => {
  if (!ps.value) return

  ps.value.keywordSearch(keyword.value, (data, status, pagination) => {
    if (status === kakao.maps.services.Status.OK) {
      const filteredData = data.filter(place => 
        place.category_name.includes('은행') && 
        place.place_name.includes(keyword.value.split(' ')[1] || '')
      )
      
      if (filteredData.length > 0) {
      
        displayPlaces(filteredData)
        displayPagination(pagination)
      } else {
        alert('검색 결과가 존재하지 않습니다.')
      }
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
      alert('검색 결과가 존재하지 않습니다.')
    } else if (status === kakao.maps.services.Status.ERROR) {
      alert('검색 결과 중 오류가 발생했습니다.')
    }
  })
}

const displayPlaces = (places) => {
  const listEl = document.getElementById('placesList')
  const bounds = new kakao.maps.LatLngBounds()

  while (listEl.hasChildNodes()) {
    listEl.removeChild(listEl.lastChild)
  }
  removeMarkers()

  places.forEach((place, index) => {
    const placePosition = new kakao.maps.LatLng(place.y, place.x)
    const marker = addMarker(placePosition, index, place)
    const itemEl = getListItem(index, place)
    
    bounds.extend(placePosition)

    kakao.maps.event.addListener(marker, 'click', () => {
      displayInfowindow(marker, place)
    })

    itemEl.onclick = () => {
      map.value.setCenter(placePosition)
      displayInfowindow(marker, place)
      
    }

    listEl.appendChild(itemEl)
  })

  map.value.setBounds(bounds)
}

const addMarker = (position, idx) => {
  const marker = new kakao.maps.Marker({
    position: position
  })
  marker.setMap(map.value)
  markers.value.push(marker)
  return marker
}

const removeMarkers = () => {
  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []
}

const getListItem = (index, place) => {
  const el = document.createElement('div')
  el.className = 'bg-white p-4 grid grid-cols-5 border-b hover:bg-gray-50 cursor-pointer'
  
  let itemStr = `
    <div>${index + 1}</div>
    <div>${place.place_name}</div>
    <div>${place.road_address_name || ''}</div>
    <div>${place.address_name}</div>
    <div>${place.phone}</div>
  `
  el.innerHTML = itemStr
  return el
}

const displayInfowindow = (marker, place) => {
  const content = `
    <div class="p-4">
      <h5 class="font-bold">${place.place_name}</h5>
      <p>${place.road_address_name}</p>
      <p>${place.address_name}</p>
      <p>${place.phone}</p>
    </div>
  `
  infowindow.value.setContent(content)
  infowindow.value.open(map.value, marker)
  
  selectedBank.value = place.place_name.split(' ')[0]
}

const displayPagination = (pagination) => {
  const paginationEl = document.getElementById('pagination')
  paginationEl.innerHTML = ''

  for (let i = 1; i <= pagination.last; i++) {
    const el = document.createElement('a')
    el.href = "#"
    el.className = i === pagination.current 
      ? 'px-3 py-1 bg-[#699BF7] text-white rounded'
      : 'px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded'
    el.innerHTML = i

    if (i !== pagination.current) {
      el.onclick = () => pagination.gotoPage(i)
    }

    paginationEl.appendChild(el)
  }
}

const showDetails = (product) => {
  selectedProduct.value = product
}

onMounted(async () => {
  try {
    await loadKakaoMapScript()
    const container = document.getElementById('map')
    const options = {
      center: new kakao.maps.LatLng(35.2054, 126.8115),
      level: 3
    }
    map.value = new kakao.maps.Map(container, options)
    ps.value = new kakao.maps.services.Places()
    infowindow.value = new kakao.maps.InfoWindow({ zIndex: 1 })

    // 금리 정보 로드
    await store.fetchProducts()
  } catch (error) {
    console.error('Error:', error)
  }
})


</script>

<style scoped>
.map {
  width: 100%;
  height: 100%;
}
</style>