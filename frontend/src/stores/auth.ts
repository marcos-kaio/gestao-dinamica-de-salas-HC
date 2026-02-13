import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('gds_token'))
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('gds_token', newToken)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('gds_token')
    
    window.location.href = '/login' 
  }

  return { token, user, isAuthenticated, setToken, logout }
})