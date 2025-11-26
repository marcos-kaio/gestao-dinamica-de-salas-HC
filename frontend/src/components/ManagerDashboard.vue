<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AllocationDetailsModal from '../components/AllocationDetailsModal.vue'

// --- Interfaces de Dados ---
interface SalaStatus {
  id: string;
  numero: string;
  status: 'LIVRE' | 'OCUPADA';
  ocupante: string | null;
  horario: string | null;
  andar: string;
  bloco: string;
}

interface ResumoAmbulatorio {
  ambulatorio: string;
  total_salas: number;
  salas_ocupadas: number;
  localizacao: string[];
  lista_salas_detalhada: SalaStatus[];
}

// --- Estados ---
const dashboardData = ref<ResumoAmbulatorio[]>([])
const isLoading = ref(false)
const lastUpdate = ref<string>('')

// Modal
const isDetailsModalOpen = ref(false)
const selectedAllocation = ref<ResumoAmbulatorio | null>(null)

// Polling
let pollingInterval: number | null = null;
const API_URL = 'http://localhost:8000'

// --- API & Lógica ---

const callApi = async (endpoint: string, method: string = 'GET') => {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, { method })
    return await response.json()
  } catch (error) {
    console.error(`Erro em ${endpoint}:`, error)
    return null
  }
}

const fetchDashboardRealTime = async () => {
  const salas = await callApi('/api/salas')
  if (!salas) return

  const agrupamento = new Map<string, ResumoAmbulatorio>()

  salas.forEach((sala: any) => {
    const especialidade = sala.especialidade_preferencial || "Salas Gerais"
    
    if (!agrupamento.has(especialidade)) {
      agrupamento.set(especialidade, {
        ambulatorio: especialidade,
        total_salas: 0,
        salas_ocupadas: 0,
        localizacao: [],
        lista_salas_detalhada: []
      })
    }

    const grupo = agrupamento.get(especialidade)!
    grupo.total_salas++
    if (sala.status_atual === 'OCUPADA') grupo.salas_ocupadas++

    const loc = `Bloco ${sala.bloco} - ${sala.andar}º Andar`
    if (!grupo.localizacao.includes(loc)) grupo.localizacao.push(loc)

    grupo.lista_salas_detalhada.push({
      id: sala.id,
      numero: sala.nome_visual,
      status: sala.status_atual,
      ocupante: sala.ocupante_atual,
      horario: sala.horario_entrada,
      andar: sala.andar,
      bloco: sala.bloco
    })
  })

  dashboardData.value = Array.from(agrupamento.values()).sort((a, b) => b.total_salas - a.total_salas)
  lastUpdate.value = new Date().toLocaleTimeString()
}

// Ações
const handleImportSalas = async () => {
  isLoading.value = true
  await callApi('/api/setup/importar-salas', 'POST')
  await fetchDashboardRealTime()
  isLoading.value = false
}

const handleImportGrades = async () => {
  isLoading.value = true
  await callApi('/api/setup/importar-grades', 'POST')
  isLoading.value = false
}

const handleGenerateAllocation = async () => {
  isLoading.value = true
  await callApi('/api/alocacao/gerar', 'POST')
  await fetchDashboardRealTime()
  isLoading.value = false
}

const openDetails = (item: ResumoAmbulatorio) => {
  selectedAllocation.value = item
  isDetailsModalOpen.value = true
}

const closeDetails = () => {
  isDetailsModalOpen.value = false
  setTimeout(() => selectedAllocation.value = null, 200)
}

const formatLocation = (locs: string[]) => {
  if (locs.length <= 2) return locs
  return [...locs.slice(0, 2), `+${locs.length - 2} locais`]
}

onMounted(() => {
  fetchDashboardRealTime()
  pollingInterval = setInterval(fetchDashboardRealTime, 3000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 pb-20">
    
    <header class="bg-teal-600 text-white p-6 shadow-md rounded-b-3xl mb-8">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold">Painel do Gestor</h1>
          <p class="text-teal-100 text-sm">Monitoramento e Alocação de Recursos</p>
        </div>
        
        <div class="bg-teal-700/50 backdrop-blur-sm px-4 py-2 rounded-full flex items-center gap-2 text-xs font-medium border border-teal-500/30">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
          </span>
          <span class="text-teal-50">Sincronizado às {{ lastUpdate }}</span>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4">

      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-8">
        <h2 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-wide">Ferramentas de Gestão</h2>
        
        <div class="flex flex-wrap gap-4">
          <button 
            @click="handleImportSalas"
            :disabled="isLoading"
            class="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 hover:text-teal-600 transition disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
            Importar Salas
          </button>

          <button 
            @click="handleImportGrades"
            :disabled="isLoading"
            class="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 hover:text-teal-600 transition disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            Importar Grades
          </button>

          <div class="hidden md:block w-px bg-gray-200 mx-2"></div>

          <button 
            @click="handleGenerateAllocation"
            :disabled="isLoading"
            class="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-teal-600 text-white font-bold hover:bg-teal-700 shadow-md shadow-teal-200 transition transform active:scale-95 disabled:opacity-50"
          >
            <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
            <span v-else>Processando...</span>
            Recalcular Alocação
          </button>
        </div>
      </div>

      <div v-if="dashboardData.length > 0">
        <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
          Visão Geral por Especialidade
          <span class="text-xs font-normal bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{{ dashboardData.length }} áreas</span>
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div 
            v-for="item in dashboardData" 
            :key="item.ambulatorio"
            @click="openDetails(item)"
            class="group bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md hover:border-teal-300 transition cursor-pointer relative overflow-hidden"
          >
            <div class="absolute left-0 top-0 bottom-0 w-1 transition-colors" 
                 :class="item.salas_ocupadas > 0 ? 'bg-teal-500' : 'bg-gray-200'"></div>

            <div class="pl-2 flex flex-col h-full">
              <div class="flex justify-between items-start mb-3">
                <div class="pr-2">
                  <h4 class="font-bold text-gray-900 line-clamp-1" :title="item.ambulatorio">{{ item.ambulatorio }}</h4>
                  <p class="text-xs text-gray-500 mt-1 flex flex-wrap gap-1">
                     <span v-for="loc in formatLocation(item.localizacao)" :key="loc" class="bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100">{{ loc }}</span>
                  </p>
                </div>
                
                <div class="text-right flex-shrink-0">
                   <span class="text-2xl font-bold text-gray-800">{{ item.salas_ocupadas }}</span>
                   <span class="text-sm text-gray-400 font-medium">/{{ item.total_salas }}</span>
                </div>
              </div>

              <div class="mt-auto pt-4">
                <div class="flex justify-between text-[10px] font-bold uppercase text-gray-400 mb-1">
                    <span>Ocupação</span>
                    <span>{{ Math.round((item.salas_ocupadas / item.total_salas) * 100) }}%</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div 
                        class="bg-teal-500 h-2 rounded-full transition-all duration-500 group-hover:bg-teal-400" 
                        :style="{ width: `${(item.salas_ocupadas / item.total_salas) * 100}%` }"
                    ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!isLoading" class="mt-20 flex flex-col items-center justify-center text-center">
        <div class="bg-gray-50 p-6 rounded-full mb-4">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Nenhum dado encontrado</h3>
        <p class="text-gray-500 mt-2 max-w-sm">Importe as salas e as grades para começar a visualizar o painel.</p>
      </div>

    </main>

    <AllocationDetailsModal 
      :is-open="isDetailsModalOpen"
      :data="selectedAllocation"
      @close="closeDetails"
    />
  </div>
</template>