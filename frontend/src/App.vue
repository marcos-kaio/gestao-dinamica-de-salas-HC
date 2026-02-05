<script setup lang="ts">
import { ref } from 'vue'
import OccupancyDashboard from './components/OccupancyDashboard.vue'
import ManagerDashboard from './components/ManagerDashboard.vue'
import DoctorPortal from './components/DoctorPortal.vue'

const currentView = ref('dashboard') // 'dashboard', 'manager', 'portal'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
    <!-- Navbar -->
    <nav class="bg-blue-800 text-white shadow-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="font-bold text-xl tracking-tight">
            Gestão Dinâmica de Salas - HC UFPE
          </div>
          <div class="flex space-x-1">
            <button 
              @click="currentView = 'dashboard'"
              :class="currentView === 'dashboard' ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
              class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200"
            >
              Visão Geral
            </button>
            <button 
              @click="currentView = 'manager'"
              :class="currentView === 'manager' ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
              class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200"
            >
              Gestão
            </button>
            <button 
              @click="currentView = 'portal'"
              :class="currentView === 'portal' ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
              class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200"
            >
              Portal Médico
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="flex-1 w-full max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div v-if="currentView === 'dashboard'">
        <OccupancyDashboard />
      </div>
      <div v-else-if="currentView === 'manager'">
        <ManagerDashboard />
      </div>
      <div v-else>
        <DoctorPortal />
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <p class="text-center text-gray-500 text-sm">
          © 2026 Hospital das Clínicas UFPE - Gestão Dinâmica de Salas
        </p>
      </div>
    </footer>
  </div>
</template>