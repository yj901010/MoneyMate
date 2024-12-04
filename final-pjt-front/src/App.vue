<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import Navbar from '@/components/layout/Navbar.vue';
import ChatBot from '@/components/layout/chatbot.vue';
import CurrencyConverter from '@/components/layout/CurrencyConverter.vue';

const router = useRouter();
const authStore = useAuthStore();

const isLoggedIn = computed(() => authStore.isAuthenticated);

const handleLogout = () => {
  authStore.logOut();
  router.push('/');
};

onMounted(() => {
  authStore.getTokenFromCookie();
});

const isChatBotOpen = ref(false);
const isCurrencyConverterOpen = ref(false);

const toggleChatBot = () => {
  isChatBotOpen.value = !isChatBotOpen.value;
  if (isChatBotOpen.value) {
    isCurrencyConverterOpen.value = false;
  }
};

const toggleCurrencyConverter = () => {
  isCurrencyConverterOpen.value = !isCurrencyConverterOpen.value;
  if (isCurrencyConverterOpen.value) {
    isChatBotOpen.value = false;
  }
};

const handleOutsideClick = (event) => {
  if (
    !event.target.closest('.chatbot-container') &&
    !event.target.closest('.currency-converter-container') &&
    !event.target.closest('.chatbot-button') &&
    !event.target.closest('.currency-converter-button')
  ) {
    isChatBotOpen.value = false;
    isCurrencyConverterOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>

<template>
  <div>
    <Navbar :is-logged-in="isLoggedIn" @logout="handleLogout" />
    <main class="pt-16">
      <router-view></router-view>
    </main>

    <!-- 챗봇 및 컨버터 버튼 -->
    <div class="fixed bottom-6 right-6 flex space-x-4">
      <button
        @click.stop="toggleChatBot"
        class="bg-[#699BF7] p-4 rounded-full shadow-lg hover:bg-blue-500 text-white chatbot-button"
      >
        <svg
          v-if="!isChatBotOpen"
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
      <button
        @click.stop="toggleCurrencyConverter"
        class="bg-[#699BF7] p-4 rounded-full shadow-lg hover:bg-blue-500 text-white currency-converter-button"
      >
        <svg
          v-if="!isCurrencyConverterOpen"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 6v6m0 0v6m0-6h6m-6 0H6"
          />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- 컴포넌트들 -->
    <div
      v-if="isChatBotOpen"
      class="fixed bottom-24 right-6 chatbot-container"
    >
      <ChatBot />
    </div>
    <div
      v-if="isCurrencyConverterOpen"
      class="fixed bottom-24 right-6 currency-converter-container"
    >
      <CurrencyConverter />
    </div>
  </div>
</template>
