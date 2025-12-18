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
  <div class="min-h-screen bg-slate-50 font-sans text-slate-800 flex flex-col">
    
    <!-- Faixa Institucional -->
    <div class="h-1.5 w-full bg-[#003B71]"></div>

    <!-- Navbar Interna (Aparece apenas quando NÃO está na Home) -->
    <header v-if="currentView !== 'home'" class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        <!-- Logo Compacta na Navbar -->
        <div class="flex items-center gap-3 cursor-pointer group" @click="navigateTo('home')">
          <div class="h-9 w-9 bg-[#003B71] rounded flex items-center justify-center text-white font-black text-xs shadow-sm group-hover:bg-[#002a52] transition-colors">
            HC
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-bold text-slate-800 leading-none">Gestão de Salas</span>
            <span class="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Hospital das Clínicas</span>
          </div>
        </div>
        
        <button 
          @click="navigateTo('home')"
          class="text-xs font-semibold text-slate-500 hover:text-[#003B71] hover:bg-slate-50 px-3 py-1.5 rounded transition-all flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          Menu Principal
        </button>
      </div>
    </header>

    <main class="flex-1 flex flex-col">
      
      <!-- 1. Menu Principal (Portal de Entrada) -->
      <div v-if="currentView === 'home'" class="flex-1 flex flex-col items-center justify-center p-6 animate-fade-in bg-gradient-to-b from-slate-100 to-slate-50">
        
        <div class="text-center mb-12">
          <!-- LOGO PRINCIPAL EM DESTAQUE -->
          <div class="inline-flex items-center justify-center p-5 bg-white rounded-2xl shadow-sm border border-slate-200 mb-8 gap-5 transform hover:scale-105 transition-transform duration-500">
            <div class="flex flex-col items-end">
              <span class="text-4xl font-black text-[#003B71] leading-none tracking-tighter">HC</span>
              <span class="text-xs font-bold text-slate-400 tracking-widest">UFPE</span>
            </div>
            <div class="h-12 w-px bg-slate-200"></div>
            <div class="text-left">
              <h1 class="text-sm font-bold text-slate-700 uppercase leading-tight tracking-wide">Gestão Dinâmica<br><span class="text-[#003B71]">de Salas</span></h1>
            </div>
          </div>

          <h2 class="text-3xl font-bold text-slate-900 tracking-tight mb-2">Portal Integrado</h2>
          <p class="text-slate-500 max-w-md mx-auto">Selecione um módulo para acessar as ferramentas de gestão e operação.</p>
        </div>

        <!-- Grid de Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl px-4">
          
          <!-- Card Gestor -->
          <div @click="navigateTo('manager')" class="group cursor-pointer bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-[#003B71]/40 transition-all duration-300 relative overflow-hidden flex flex-col">
            <div class="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-10 transition-opacity">
              <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>
            </div>
            <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-[#003B71] group-hover:text-white transition-colors text-[#003B71] shadow-sm">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2 group-hover:text-[#003B71] transition-colors">Painel do Gestor</h3>
            <p class="text-sm text-slate-500 leading-relaxed mb-6 flex-1">Importação de dados, gestão da infraestrutura e execução da alocação inteligente.</p>
            <span class="text-xs font-bold text-[#003B71] uppercase tracking-wide flex items-center gap-1 group-hover:gap-2 transition-all">Acessar <span class="text-lg leading-none">&rarr;</span></span>
          </div>

          <!-- Card Ocupação -->
          <div @click="navigateTo('occupancy')" class="group cursor-pointer bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-indigo-500/40 transition-all duration-300 relative overflow-hidden flex flex-col">
            <div class="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-10 transition-opacity">
              <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
            </div>
            <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-colors text-indigo-600 shadow-sm">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2 group-hover:text-indigo-700 transition-colors">Monitoramento</h3>
            <p class="text-sm text-slate-500 leading-relaxed mb-6 flex-1">Visualização em tempo real da ocupação das salas e status dos ambulatórios.</p>
            <span class="text-xs font-bold text-indigo-600 uppercase tracking-wide flex items-center gap-1 group-hover:gap-2 transition-all">Acessar <span class="text-lg leading-none">&rarr;</span></span>
          </div>

          <!-- Card Médico -->
          <div @click="navigateTo('doctor')" class="group cursor-pointer bg-white p-8 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-emerald-500/40 transition-all duration-300 relative overflow-hidden flex flex-col">
            <div class="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-10 transition-opacity">
              <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8.5 12H9v-2.5H6.5v-1.5H9V8.5h1.5v2.5h2.5v1.5h-2.5V15z"/></svg>
            </div>
            <div class="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-emerald-600 group-hover:text-white transition-colors text-emerald-600 shadow-sm">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-2 group-hover:text-emerald-700 transition-colors">Portal do Médico</h3>
            <p class="text-sm text-slate-500 leading-relaxed mb-6 flex-1">Área exclusiva para corpo clínico. Check-in, check-out e consulta de escalas.</p>
            <span class="text-xs font-bold text-emerald-600 uppercase tracking-wide flex items-center gap-1 group-hover:gap-2 transition-all">Acessar <span class="text-lg leading-none">&rarr;</span></span>
          </div>

        </div>

        <footer class="mt-auto pt-20 text-center pb-6">
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            © 2025 Hospital das Clínicas - UFPE / Ebserh
          </p>
        </footer>
      </div>

      <!-- Telas Internas -->
      <div v-else class="flex-1 max-w-7xl mx-auto w-full p-6 sm:p-8 animate-fade-in">
        <ManagerDashboard v-if="currentView === 'manager'" />
        <OccupancyDashboard v-if="currentView === 'occupancy'" />
        <DoctorPortal v-if="currentView === 'doctor'" />
      </div>

    </main>
  </div>
</template>

<style>
.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>