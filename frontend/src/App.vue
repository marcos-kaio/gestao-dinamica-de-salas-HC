<script setup lang="ts">
import { ref } from 'vue'
import ManagerDashboard from './components/ManagerDashboard.vue'

// Define os possíveis estados da navegação
type ViewState = 'home' | 'manager' | 'future'

const currentView = ref<ViewState>('home')

// Função para navegar
const navigateTo = (view: ViewState) => {
  currentView.value = view
}
</script>

<template>
  <!-- 1. Tela Inicial (Menu Principal) -->
  <div v-if="currentView === 'home'" class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8 font-sans">
    
    <div class="text-center max-w-2xl mb-12">
      <div class="mb-6 flex justify-center">
        <div class="bg-blue-100 p-4 rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Gestão Dinâmica de Salas (HC)</h1>
      <p class="text-lg text-gray-600">Bem-vindo ao sistema de otimização de recursos ambulatoriais. Selecione o módulo que deseja acessar.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
      
      <!-- Botão 1: Painel do Gestor -->
      <div 
        @click="navigateTo('manager')"
        class="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-8 shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-300 transform hover:-translate-y-1"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-blue-50 p-3 rounded-lg group-hover:bg-blue-100 transition">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-300 group-hover:text-blue-500 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Painel do Gestor</h2>
        <p class="text-gray-500">Importe dados do AGHU, gerencie a infraestrutura e gere alocações inteligentes automaticamente.</p>
      </div>

      <!-- Botão 2: Futuro Módulo -->
      <div 
        @click="navigateTo('future')"
        class="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-8 shadow-sm hover:shadow-xl hover:border-purple-300 transition-all duration-300 transform hover:-translate-y-1"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-purple-50 p-3 rounded-lg group-hover:bg-purple-100 transition">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-300 group-hover:text-purple-500 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Portal do Médico</h2>
        <p class="text-gray-500">Em breve: Área para médicos e residentes visualizarem suas escalas e realizarem check-in.</p>
      </div>

    </div>
    
    <footer class="mt-16 text-sm text-gray-400">
      &copy; 2025 Hospital das Clínicas - UFPE
    </footer>
  </div>

  <!-- 2. Tela do Painel do Gestor -->
  <div v-else-if="currentView === 'manager'">
    <!-- Botão Voltar Flutuante -->
    <button 
      @click="navigateTo('home')" 
      class="fixed bottom-6 right-6 z-50 cursor-pointer flex items-center gap-2 rounded-full bg-gray-800 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-gray-700 transition hover:scale-105"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Voltar ao Início
    </button>
    
    <ManagerDashboard />
  </div>

  <!-- 3. Tela Futura (Placeholder) -->
  <div v-else-if="currentView === 'future'" class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
    <div class="text-center">
      <div class="inline-flex bg-purple-100 p-6 rounded-full mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      </div>
      <h2 class="text-3xl font-bold text-gray-900 mb-2">Em Construção</h2>
      <p class="text-gray-500 mb-8 max-w-md mx-auto">Este módulo está sendo desenvolvido e estará disponível nas próximas atualizações do sistema.</p>
      
      <button 
        @click="navigateTo('home')" 
        class="cursor-pointer rounded-lg border border-gray-300 bg-white px-6 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition"
      >
        Voltar para o Menu
      </button>
    </div>
  </div>
</template>