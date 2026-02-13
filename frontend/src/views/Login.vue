<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)

    const res = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      body: formData
    })

    if (!res.ok) throw new Error('Credenciais inválidas')

    const data = await res.json()
    authStore.setToken(data.access_token)
    router.push('/') // Redireciona para o Dashboard
  } catch (err) {
    error.value = 'Usuário ou senha incorretos'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8 border border-gray-200">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-700">GDS</h1>
        <p class="text-gray-500 mt-2">Gestão Dinâmica de Salas - HC</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Usuário</label>
          <input 
            v-model="username" 
            type="text" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="Digite seu usuário"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
          <input 
            v-model="password" 
            type="password" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="Digite sua senha"
            required
          />
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-200">
          {{ error }}
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 transition font-medium shadow-sm disabled:opacity-70 flex justify-center cursor-pointer"
        >
          <span v-if="loading">Entrando...</span>
          <span v-else>Entrar</span>
        </button>
      </form>
      
      <div class="mt-6 text-center text-xs text-gray-400">
        &copy; Hospital das Clínicas UFPE
      </div>
    </div>
  </div>
</template>