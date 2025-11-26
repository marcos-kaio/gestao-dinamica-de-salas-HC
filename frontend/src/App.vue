<script setup lang="ts">
import { ref } from 'vue'
import ManagerDashboard from './components/ManagerDashboard.vue'
import OccupancyDashboard from './components/OccupancyDashboard.vue'
import DoctorPortal from './components/DoctorPortal.vue'

// Define os possíveis estados da navegação
type ViewState = 'home' | 'manager' | 'occupancy' | 'doctor'

const currentView = ref<ViewState>('home')

const navigateTo = (view: ViewState) => {
  currentView.value = view
}
</script>

<template>
  <div v-if="currentView === 'home'" class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8 font-sans">
    
    <div class="text-center max-w-2xl mb-12">
      <div class="mb-6 flex justify-center">
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Gestão Dinâmica de Salas</h1>
      <p class="text-lg text-gray-600">Hospital das Clínicas - UFPE</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl">
      
      <div 
        @click="navigateTo('manager')"
        class="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-300 transform hover:-translate-y-1"
      >
        <div class="bg-blue-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-100 transition">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Área Administrativa</h2>
        <p class="text-sm text-gray-500">Importação de dados do AGHU e execução manual dos algoritmos de alocação.</p>
      </div>

      <div 
        @click="navigateTo('occupancy')"
        class="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-xl hover:border-indigo-300 transition-all duration-300 transform hover:-translate-y-1"
      >
        <div class="bg-indigo-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Monitoramento</h2>
        <p class="text-sm text-gray-500">Dashboard em tempo real da ocupação das salas e ambulatórios.</p>
      </div>

      <div 
        @click="navigateTo('doctor')"
        class="group cursor-pointer bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-xl hover:border-teal-300 transition-all duration-300 transform hover:-translate-y-1"
      >
        <div class="bg-teal-50 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-teal-100 transition">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Portal do Profissional</h2>
        <p class="text-sm text-gray-500">Área para médicos, residentes e enfermeiros realizarem check-in e check-out.</p>
      </div>

    </div>
    
    <footer class="mt-16 text-sm text-gray-400">
      &copy; 2025 Hospital das Clínicas - UFPE
    </footer>
  </div>

  <div v-else-if="currentView === 'manager'">
    <button @click="navigateTo('home')" class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-blue-800 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-blue-700 transition hover:scale-105">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
      Menu Principal
    </button>
    <ManagerDashboard />
  </div>

  <div v-else-if="currentView === 'occupancy'">
    <button @click="navigateTo('home')" class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-indigo-800 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-indigo-700 transition hover:scale-105">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
      Menu Principal
    </button>
    <OccupancyDashboard />
  </div>

  <div v-else-if="currentView === 'doctor'">
    <button @click="navigateTo('home')" class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-teal-800 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-teal-700 transition hover:scale-105">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
      Menu Principal
    </button>
    <DoctorPortal />
  </div>
</template>