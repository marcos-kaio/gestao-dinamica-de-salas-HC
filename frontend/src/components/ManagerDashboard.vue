<script setup lang="ts">
import { ref } from 'vue'

const isLoading = ref(false)
const message = ref<{text: string, type: 'success'|'info'|'error'} | null>(null)

const API_URL = 'http://localhost:8000'

const callApi = async (endpoint: string, method: string = 'POST') => {
  isLoading.value = true
  message.value = { text: 'Processando...', type: 'info' }
  try {
    const response = await fetch(`${API_URL}${endpoint}`, { method })
    const data = await response.json()
    return data
  } catch (error) {
    console.error(error)
    message.value = { text: 'Erro de conexão com o servidor.', type: 'error' }
    return null
  } finally {
    isLoading.value = false
  }
}

const handleImportSalas = async () => {
  const res = await callApi('/api/setup/importar-salas')
  if (res) message.value = { text: `Salas importadas: ${res.salas_importadas || 'OK'}`, type: 'success' }
}

const handleImportGrades = async () => {
  const res = await callApi('/api/setup/importar-grades')
  if (res) message.value = { text: `Grades importadas: ${res.grades_importadas || 'OK'}`, type: 'success' }
}

const handleGenerateAllocation = async () => {
  const res = await callApi('/api/alocacao/gerar')
  if (res) message.value = { text: `Alocação gerada! Salas ocupadas automaticamente: ${res.salas_ocupadas_agora}`, type: 'success' }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-8 font-sans text-gray-900 flex flex-col items-center">
    
    <div class="w-full max-w-2xl">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900">Configuração do Sistema</h1>
        <p class="text-gray-500 mt-1">Ferramentas administrativas para importação e alocação em massa.</p>
      </header>

      <div v-if="message" class="mb-6 p-4 rounded-lg text-sm font-medium border"
           :class="{
             'bg-blue-50 text-blue-700 border-blue-200': message.type === 'info',
             'bg-green-50 text-green-700 border-green-200': message.type === 'success',
             'bg-red-50 text-red-700 border-red-200': message.type === 'error'
           }">
        {{ message.text }}
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <div class="space-y-6">
          
          <div class="flex items-start gap-4">
            <div class="bg-gray-100 p-3 rounded-lg text-gray-600">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900">1. Infraestrutura Física</h3>
              <p class="text-sm text-gray-500 mb-3">Reseta o banco de dados e importa a lista de salas do arquivo CSV.</p>
              <button @click="handleImportSalas" :disabled="isLoading" class="text-sm font-semibold text-blue-600 hover:underline disabled:opacity-50">
                Executar Importação de Salas
              </button>
            </div>
          </div>

          <div class="h-px bg-gray-100 w-full"></div>

          <div class="flex items-start gap-4">
            <div class="bg-gray-100 p-3 rounded-lg text-gray-600">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900">2. Demanda Médica (AGHU)</h3>
              <p class="text-sm text-gray-500 mb-3">Importa as grades de horários e profissionais do sistema hospitalar.</p>
              <button @click="handleImportGrades" :disabled="isLoading" class="text-sm font-semibold text-blue-600 hover:underline disabled:opacity-50">
                Executar Importação de Grades
              </button>
            </div>
          </div>

          <div class="h-px bg-gray-100 w-full"></div>

          <div class="flex items-start gap-4">
            <div class="bg-blue-50 p-3 rounded-lg text-blue-600">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900">3. Processamento de Alocação</h3>
              <p class="text-sm text-gray-500 mb-3">Roda o algoritmo de otimização e aplica as grades nas salas livres.</p>
              <button 
                @click="handleGenerateAllocation"
                :disabled="isLoading"
                class="px-4 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition shadow-sm disabled:opacity-50"
              >
                Gerar Alocação Automática
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>