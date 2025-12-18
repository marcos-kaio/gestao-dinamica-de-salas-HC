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
    allocationSummary.value = res.resumo_ambulatorios
  }
}

onMounted(() => {
  fetchCurrentAllocation()
})

const handleImportSalas = async () => {
  await callApi('/api/setup/importar-salas')
  fetchCurrentAllocation()
}

const handleImportGrades = async () => {
  await callApi('/api/setup/importar-grades')
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
    return `Bloco ${match[1]} • ${match[2] === '0' ? 'Térreo' : match[2] + 'º Andar'}`
  }
  return loc
}
</script>

<template>
  <div class="animate-fade-in">
    
    <div class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Painel de Alocação</h2>
        <p class="text-slate-500 text-sm mt-1">Gerenciamento da distribuição de salas por especialidade.</p>
      </div>
    </div>

    <!-- Toolbar Unificada -->
    <div class="bg-white p-1.5 rounded-xl border border-slate-200 shadow-sm mb-10 flex flex-col md:flex-row gap-2">
      <div class="flex-1 flex gap-2">
        <button @click="handleImportSalas" :disabled="isLoading" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-[#003B71] transition-all disabled:opacity-50">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg> Importar Salas
        </button>
        <div class="w-px bg-slate-100 my-2 hidden md:block"></div>
        <button @click="handleImportGrades" :disabled="isLoading" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-[#003B71] transition-all disabled:opacity-50">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg> Importar Grades
        </button>
      </div>
      <button @click="handleGenerateAllocation" :disabled="isLoading" class="w-full md:w-auto px-6 py-2.5 bg-[#003B71] hover:bg-[#002a52] text-white text-sm font-bold rounded-lg shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-80">
        <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
        <svg v-else class="animate-spin w-5 h-5 text-white/50" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        {{ isLoading ? 'Processando...' : 'Executar Alocação Inteligente' }}
      </button>
    </div>

    <!-- Resultados -->
    <div v-if="allocationSummary.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="item in allocationSummary" :key="item.ambulatorio" @click="openDetails(item)" class="group cursor-pointer bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-[#003B71]/50 transition-all duration-200 flex flex-col h-full overflow-hidden">
        <div class="h-1 w-full bg-slate-100 group-hover:bg-[#003B71] transition-colors"></div>
        <div class="p-5 flex-1 flex flex-col">
          <div class="flex justify-between items-start mb-3 gap-2">
            <h3 class="font-bold text-slate-800 text-base leading-tight group-hover:text-[#003B71] transition-colors line-clamp-2" :title="item.ambulatorio">{{ item.ambulatorio }}</h3>
            <span class="shrink-0 bg-slate-50 text-slate-600 text-[11px] font-bold px-2 py-1 rounded border border-slate-100 min-w-[24px] text-center">{{ item.total_salas ?? 0 }}</span>
          </div>
          <div class="mt-auto pt-4 space-y-2 border-t border-slate-50">
            <div v-for="loc in item.localizacao.slice(0, 2)" :key="loc" class="flex items-center text-xs text-slate-500 font-medium">
              <svg class="w-3.5 h-3.5 mr-2 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              <span class="truncate">{{ formatLocation(loc) }}</span>
            </div>
            <div v-if="item.localizacao.length > 2" class="text-[10px] text-slate-400 pl-6 font-medium">+{{ item.localizacao.length - 2 }} outros locais</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!isLoading" class="border-2 border-dashed border-slate-200 rounded-xl p-16 flex flex-col items-center justify-center text-center bg-slate-50/30">
      <div class="bg-white p-4 rounded-full shadow-sm mb-4">
        <svg class="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
      </div>
      <h3 class="text-lg font-bold text-slate-700">Nenhuma alocação disponível</h3>
      <p class="text-slate-500 max-w-sm mt-2 text-sm">Utilize a barra de ferramentas acima para importar dados do sistema ou gerar um novo planejamento.</p>
    </div>

    <ManagerDetailsModal :is-open="isDetailsModalOpen" :data="selectedAllocation" @close="closeDetails" />
  </div>
</template>