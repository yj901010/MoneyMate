import { ref } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';
import { useRouter } from 'vue-router';
export const useAuthStore = defineStore('user', () => {
  const API_URL = 'http://localhost:8000';
  const token = ref(null);
  const isAuthenticated = ref(false);
  const usernameValue = ref(null);
  const router = useRouter();

  // 쿠키에 토큰을 저장하는 함수
  const setToken = (tokenValue) => {
    document.cookie = `token=${tokenValue}; path=/; max-age=3600`;
    token.value = tokenValue;
    isAuthenticated.value = true; // 로그인 상태 변경
  };

  // 쿠키에서 토큰을 읽는 함수
  const getTokenFromCookie = () => {
    const match = document.cookie.match(/(?:^| )token=([^;]+)(?=;|$)/);
    if (match) {
      token.value = match[1];
      isAuthenticated.value = true;
    } else {
      isAuthenticated.value = false;
    }
  };

  // 로컬 스토리지에서 username을 가져오는 함수
  const getUsernameFromLocalStorage = () => {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
      usernameValue.value = storedUsername;
    }
  };

  // 로그인 함수 수정
  const logIn = async function (payload) {
    const { username, password } = payload;
    
    try {
      const res = await axios.post(`${API_URL}/accounts/login/`, { username, password });
      const { key } = res.data;
      usernameValue.value = username;
      localStorage.setItem('username', username);
      setToken(key);
      window.location.reload();
    } catch (err) {
      alert('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.');
      console.error('로그인 실패:', err);
    }
  };

  // 회원가입 요청을 보내는 함수
  const register = async function (payload) {
    try {
      // FormData의 내용을 로그로 확인 (디버깅 용도)
      console.log('서버로 전송되는 데이터:');
      for (let pair of payload.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
      }
      
      const response = await axios.post(
        `${API_URL}/accounts/signup/`,
        payload,
        {
          // 'Content-Type': 'multipart/form-data' 헤더를 제거하여 axios가 자동으로 설정하게 함
        }
      );
      
      console.log('회원가입 완료:', response.data);
      alert('회원가입이 완료되었습니다.');
      
      usernameValue.value = payload.get('username');
      // 회원가입 후 자동 로그인
      await logIn({
        username: payload.get('username'),
        password: payload.get('password1')
      });
      
      return true;
    } catch (err) {
      console.error('회원가입 실패:', err);
      console.error('에러 상세:', err.response?.data);
      
      let errorMessage = '회원가입에 실패했습니다.\n';
      
      if (err.response?.data) {
        // 서버에서 반환한 에러 메시지 처리
        Object.keys(err.response.data).forEach(key => {
          const messages = err.response.data[key];
          if (Array.isArray(messages)) {
            messages.forEach(msg => {
              errorMessage += `${key}: ${msg} \n`;
            });
          } else {
            errorMessage += `${key}: ${messages} \n`;
          }
        });
      }
      
      alert(errorMessage);
      return false;
    }
  };

  // 로그아웃 처리 (쿠키에서 토큰 삭제)
  const logOut = async function () {
    try {
      const res = await axios.post(`${API_URL}/accounts/logout/`);
      document.cookie = 'token=; path=/; max-age=0';
      token.value = null;
      isAuthenticated.value = false; // 로그인 상태 변경
      usernameValue.value = null;
      alert('로그아웃 되었습니다.');
      console.log('로그아웃 완료:', res.data);
    } catch (err) {
      alert('로그아웃 중 오류가 발생했습니다.');
      console.error('로그아웃 실패:', err);
    }
  };

  const getUserProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/accounts/user/`, {
        headers: {
          Authorization: `Token ${token.value}`,
        },
      });
      return response;
    } catch (error) {
      console.error('프로필 가져오기 실패:', error.response?.data || error.message);
      throw error;
    }
  };
  
  const formatPhoneNumber = (phone) => {
    // 하이픈 제거
    const cleaned = phone.replace(/-/g, '');
  
    // 앞자리가 '0'으로 시작하면 '+82'로 교체
    if (cleaned.startsWith('0')) {
      return '+82' + cleaned.slice(1);
    }
    return cleaned;
  };
  
  const updateUser = async (formData) => {
    try {
      // 전화번호 변환 처리
      const phone = formData.get('phone'); // formData에서 phone 값을 가져옴
      if (phone) {
        const formattedPhone = formatPhoneNumber(phone);
        formData.set('phone', formattedPhone); // 변환된 전화번호를 다시 formData에 설정
      }
  
      const response = await axios.patch(`${API_URL}/account/edit/`, formData, {
        headers: {
          Authorization: `Token ${token.value}`,
          'Content-Type': 'multipart/form-data',
        },
      });
  
      console.log('프로필 업데이트 성공:', response.data);
      router.push('/profile');
      return response.data;
    } catch (error) {
      console.error('프로필 업데이트 실패:', error.response?.data || error.message);
      throw error;
    }
  };
  

  // 페이지 로드 시 쿠키에서 토큰 읽기
  getTokenFromCookie();
  getUsernameFromLocalStorage();

  return { API_URL, logIn, register, logOut, token, isAuthenticated, getTokenFromCookie, setToken, usernameValue, getUsernameFromLocalStorage, updateUser, getUserProfile };
}, { persist: true });
