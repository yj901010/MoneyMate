<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import LoginModal from '../auth/LoginModal.vue';

const props = defineProps({
  isLoggedIn: Boolean
});

const emit = defineEmits(['logout']);
const router = useRouter();

const isOpen = ref(false); // 메뉴 열림 상태
const showLoginModal = ref(false);

const menuItems = [
  { name: '근처 은행 찾기', link: '/find-bank' },
  { name: '금리 비교', link: '/RateComparator' },
  { name: '게시판', link: '/article' },
  { name: '주가 예측', link: '/predict' }
];

// 메뉴 열고 닫기
const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

// 메뉴 닫기
const closeMenu = () => {
  isOpen.value = false;
};

// 외부 클릭 감지 로직
const handleOutsideClick = (event) => {
  const menu = document.querySelector('.menu-container');
  const menuButton = document.querySelector('.menu-button');

  // 메뉴와 메뉴 버튼을 제외한 영역 클릭 시 메뉴 닫기
  if (menu && !menu.contains(event.target) && menuButton && !menuButton.contains(event.target)) {
    closeMenu();
  }
};

// 프로필 버튼 클릭
const handleProfileClick = () => {
  if (props.isLoggedIn) {
    router.push('/profile');
  } else {
    showLoginModal.value = true;
  }
};

// 외부 클릭 이벤트 등록 및 해제
onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>

<template>
  <div>
    <!-- 네비게이션 바 -->
    <nav class="bg-[#699BF7] px-6 py-4 flex justify-between items-center fixed w-full top-0 z-20">
      <!-- 로고 -->
      <router-link to="/" class="text-[#FFC700] text-2xl font-bold hover:text-yellow-300">
        Money Mate
      </router-link>
      
      <!-- 메뉴 및 유저 조작 버튼 -->
      <div class="flex items-center gap-4">
        <!-- 로그인/로그아웃 버튼 -->
        <button
          v-if="isLoggedIn"
          @click="emit('logout')"
          class="text-white hover:text-[#FFC700] transition-colors duration-200"
        >
          Logout
        </button>
        <button
          v-else
          @click="showLoginModal = true"
          class="text-white hover:text-[#FFC700] transition-colors duration-200"
        >
          Login
        </button>

        <!-- 프로필 버튼 -->
        <button
          @click="handleProfileClick"
          class="text-white hover:text-[#FFC700] transition-colors duration-200"
        >
          My Profile
        </button>

        <!-- 메뉴 버튼 -->
        <button
          @click="toggleMenu"
          class="menu-button text-white hover:text-[#FFC700] transition-colors duration-200 px-4 py-2 rounded"
        >
          Menu
        </button>
      </div>
    </nav>

    <!-- 메뉴 항목 -->
    <div
      v-if="isOpen"
      class="menu-container fixed w-full bg-[#8CB3FA] top-16 z-10 transition-all duration-300 ease-in-out"
    >
      <div class="py-4">
        <router-link
          v-for="(item, index) in menuItems"
          :key="index"
          :to="item.link"
          @click="closeMenu"
          class="block py-3 text-white text-center hover:bg-[#699BF7] hover:text-[#FFC700] transition-colors duration-200"
        >
          {{ item.name }}
        </router-link>
      </div>
    </div>

    <!-- 로그인 모달 -->
    <LoginModal
      :is-open="showLoginModal"
      @close="showLoginModal = false"
    />
  </div>
</template>
