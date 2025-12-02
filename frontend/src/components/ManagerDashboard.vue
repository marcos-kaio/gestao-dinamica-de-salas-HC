<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ManagerDetailsModal from './ManagerDetailsModal.vue'

interface ResumoAmbulatorio {
  ambulatorio: string;
  total_salas: number;
  localizacao: string[];
  lista_salas: string[];
}

const allocationSummary = ref<ResumoAmbulatorio[]>([])
const isLoading = ref(false)

// Estado para controlar o modal de detalhes
const isDetailsModalOpen = ref(false)
const selectedAllocation = ref<ResumoAmbulatorio | null>(null)

const API_URL = 'http://localhost:8000'

const callApi = async (endpoint: string, method: string = 'POST') => {
  isLoading.value = true
  try {
    const response = await fetch(`${API_URL}${endpoint}`, { method })
    const data = await response.json()
    return data
  } catch (error) {
    console.error(error)
    alert('Erro ao conectar com o servidor')
  } finally {
    isLoading.value = false
  }
}

const fetchCurrentAllocation = async () => {
  const res = await callApi('/api/alocacao/resumo', 'GET')
  
  if (res && res.resumo_ambulatorios) {
    console.log("Dados de Alocação Recebidos:", res.resumo_ambulatorios) // Debug: Veja no Console do navegador (F12)
    allocationSummary.value = res.resumo_ambulatorios
  }
}

onMounted(() => {
  fetchCurrentAllocation()
})

const handleImportSalas = async () => {
  const res = await callApi('/api/setup/importar-salas')
  if (res) alert(`Importação de Salas: ${JSON.stringify(res)}`)
  fetchCurrentAllocation() // Atualiza a tela após importar
}

const handleImportGrades = async () => {
  const res = await callApi('/api/setup/importar-grades')
  if (res) alert(`Importação de Grades: ${JSON.stringify(res)}`)
}

const handleGenerateAllocation = async () => {
  const res = await callApi('/api/alocacao/gerar')
  if (res && res.resumo_executivo) {
    allocationSummary.value = res.resumo_executivo
  }
}

const openDetails = (item: ResumoAmbulatorio) => {
  selectedAllocation.value = item
  isDetailsModalOpen.value = true
}

const closeDetails = () => {
  isDetailsModalOpen.value = false
  setTimeout(() => selectedAllocation.value = null, 200)
}

const formatLocation = (loc: string) => {
  const match = loc.match(/Bloco\s+(.+)\s+-\s+(\d+)/)
  if (match) {
    const bloco = match[1]
    const andar = match[2]
    const andarFormatado = andar === '0' ? 'Térreo' : `${andar}º Andar`
    return `Bloco ${bloco} - ${andarFormatado}`
  }
  return loc
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
    
    <header class="mb-10">
      <h1 class="text-3xl font-bold text-gray-900">Painel do Gestor</h1>
      <p class="text-gray-500 mt-1">Gerenciamento de Importação e Alocação de Salas (GDS)</p>
    </header>

    <div class="mb-12 flex flex-wrap gap-4 rounded-xl bg-white p-6 shadow-sm border border-gray-100">
      <button 
        @click="handleImportSalas"
        :disabled="isLoading"
        class="cursor-pointer flex items-center gap-2 rounded-lg bg-indigo-50 px-5 py-3 text-sm font-semibold text-indigo-700 hover:bg-indigo-100 transition disabled:opacity-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
        1. Importar Salas (CSV)
      </button>

      <button 
        @click="handleImportGrades"
        :disabled="isLoading"
        class="cursor-pointer flex items-center gap-2 rounded-lg bg-purple-50 px-5 py-3 text-sm font-semibold text-purple-700 hover:bg-purple-100 transition disabled:opacity-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
        2. Importar Grades (AGHU)
      </button>

      <div class="h-auto w-px bg-gray-300 mx-2"></div>

      <button 
        @click="handleGenerateAllocation"
        :disabled="isLoading"
        class="cursor-pointer flex items-center gap-2 rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white hover:bg-emerald-700 shadow-md hover:shadow-lg transition disabled:opacity-50"
      >
        <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
        3. Gerar Alocação Inteligente
      </button>
    </div>

    <div v-if="allocationSummary.length > 0">
      <h2 class="text-xl font-semibold text-gray-800 mb-6">Resultado da Alocação por Especialidade</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="item in allocationSummary" 
          :key="item.ambulatorio"
          @click="openDetails(item)"
          class="group relative flex flex-col rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-lg hover:border-blue-300 cursor-pointer"
        >
          <div class="p-6 flex flex-col h-full">
            <div class="flex items-start justify-between mb-4">
              <div class="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                {{ item.ambulatorio }}
              </div>
              <!-- CORREÇÃO AQUI: Uso de operador ?? para garantir exibição de 0 se vier null/undefined -->
              <span class="text-2xl font-bold text-gray-900">
                {{ item.total_salas ?? 0 }} 
                <span class="text-sm font-normal text-gray-500">salas</span>
              </span>
            </div>

            <div class="mt-auto">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Localização</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li v-for="loc in item.localizacao" :key="loc" class="flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  {{ formatLocation(loc) }}
                </li>
              </ul>
            </div>
            
            <div class="mt-4 flex justify-end pt-2 border-t border-gray-50">
              <span class="text-xs font-medium text-blue-600 group-hover:underline flex items-center gap-1">
                Ver detalhes
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!isLoading" class="mt-20 flex flex-col items-center justify-center text-center">
      <div class="rounded-full bg-gray-100 p-6 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">Nenhuma alocação gerada</h3>
      <p class="text-gray-500 max-w-md mt-2">Importe as salas e as grades médicas, depois clique em "Gerar Alocação" para visualizar o planejamento.</p>
    </div>

    <ManagerDetailsModal 
      :is-open="isDetailsModalOpen"
      :data="selectedAllocation"
      @close="closeDetails"
    />

  </div>
</template>