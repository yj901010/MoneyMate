import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/views/MainPage.vue'
// import SignUpPage from '@/views/SignUpPage.vue'
import InterestRateComparatorPage from '@/views/InterestRateComparatorPage.vue'
import ArticleView from '@/views/ArticleView.vue'
import PostDetail from '@/views/PostDetail.vue'
import CreateView from '@/views/CreateView.vue'
import BankSearch from '@/views/BankSearch.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import ProfileView from '@/views/ProfileView.vue'
import EditProfile from '@/views/EditProfile.vue'
import PredictView from '@/views/PredictView.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'MainPage',
      component: MainPage,
    },
    // {
    //   path: '/signup',
    //   name: 'SignUp',
    //   component: SignUpPage,
    // },
    {
      path: '/RateComparator',
      name: 'RateComparator',
      component: InterestRateComparatorPage,
    },
    {
      path: '/article',
      name: 'ArticleView',
      component: ArticleView,
    },
    {
      path: '/article/:id',
      name: 'PostDetail',
      component: PostDetail,
    },
    {
      path: '/article/:id/modify',  // 게시글 수정 라우트 추가
      name: 'articleEdit',
      component: CreateView
    },
    {
      path: '/article/create',
      name: 'CreateView',
      component: CreateView,
    },
    {
      path: '/find-bank',
      name: 'BankSearch',
      component: BankSearch,
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterPage
    },
    {
      path: '/profile',
      name: 'ProfileView',
      component: ProfileView
    },
    {
      path: '/profile/edit',
      name: 'EditProfile',
      component: EditProfile
    },
    {
      path: '/predict',
      name: 'PredictView',
      component: PredictView
    },
  ],
})

export default router
