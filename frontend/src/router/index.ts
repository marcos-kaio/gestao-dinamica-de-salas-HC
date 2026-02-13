import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import OccupancyDashboard from '../components/OccupancyDashboard.vue'
import ManagerDashboard from '../components/ManagerDashboard.vue'
import DoctorPortal from '../components/DoctorPortal.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true, hideLayout: true } // hideLayout usado no App.vue
  },
  {
    path: '/',
    redirect: '/ocupacao' // Redireciona a raiz para a primeira aba
  },
  {
    path: '/ocupacao',
    name: 'Ocupacao',
    component: OccupancyDashboard
  },
  {
    path: '/gestao',
    name: 'Gestao',
    component: ManagerDashboard
  },
  {
    path: '/portal',
    name: 'PortalMedico',
    component: DoctorPortal
  }
]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (!to.meta.public && !authStore.isAuthenticated) {
    return next('/login')
  }
  
  if (to.path === '/login' && authStore.isAuthenticated) {
    return next('/')
  }

  next()
})

export default router