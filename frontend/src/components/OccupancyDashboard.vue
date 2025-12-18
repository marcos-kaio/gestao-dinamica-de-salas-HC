<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AllocationDetailsModal from '../components/AllocationDetailsModal.vue'

interface SalaStatus {
  id: string;
  numero: string;
  status: 'LIVRE' | 'OCUPADA' | 'MANUTENCAO';
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

const dashboardData = ref<ResumoAmbulatorio[]>([])
const lastUpdate = ref<string>('')
const isDetailsModalOpen = ref(false)
const selectedAllocation = ref<ResumoAmbulatorio | null>(null)

const API_URL = 'http://localhost:8000'
let pollingInterval: number | null = null;

const fetchDashboardRealTime = async () => {
  try {
    const res = await fetch(`${API_URL}/api/salas`)
    const salas = await res.json()
    if (!salas) return

    const agrupamento = new Map<string, ResumoAmbulatorio>()

    salas.forEach((sala: any) => {
      const esp = (sala.status_atual === 'OCUPADA' && sala.ocupante_atual) 
          ? 'Em Atendimento' // Simplificação para demo, idealmente usaria a especialidade da alocação
          : (sala.especialidade_preferencial || 'Clínica Médica');

      if (!agrupamento.has(esp)) {
        agrupamento.set(esp, {
          ambulatorio: esp,
          total_salas: 0,
          salas_ocupadas: 0,
          localizacao: [],
          lista_salas_detalhada: []
        })
      }

      const grupo = agrupamento.get(esp)!
      grupo.total_salas++
      if (sala.status_atual === 'OCUPADA') grupo.salas_ocupadas++
      
      const loc = `Bloco ${sala.bloco} - ${sala.andar}`
      if (!grupo.localizacao.includes(loc)) grupo.localizacao.push(loc)

      grupo.lista_salas_detalhada.push({
        id: sala.id,
        numero: sala.nome_visual,
        status: sala.status_atual === 'EM_MANUTENCAO' ? 'MANUTENCAO' : sala.status_atual,
        ocupante: sala.ocupante_atual,
        horario: null,
        andar: sala.andar,
        bloco: sala.bloco
      })
    })

    dashboardData.value = Array.from(agrupamento.values()).sort((a, b) => b.total_salas - a.total_salas)
    lastUpdate.value = new Date().toLocaleTimeString('pt-BR')

  } catch (error) {
    console.error("Erro no polling:", error)
  }
}

onMounted(() => {
  fetchDashboardRealTime()
  pollingInterval = setInterval(fetchDashboardRealTime, 5000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})

const openDetails = (item: ResumoAmbulatorio) => {
  selectedAllocation.value = item
  isDetailsModalOpen.value = true
}

const closeDetails = () => {
  isDetailsModalOpen.value = false
  setTimeout(() => selectedAllocation.value = null, 200)
}

const formatLocation = (locs: string[]) => {
  if (!locs || locs.length === 0) return []
  return locs.map(loc => {
    const match = loc.match(/Bloco\s+(.+)\s+-\s+(\d+)/)
    return match ? `Bloco ${match[1]} • ${match[2] === '0' ? 'Térreo' : match[2] + 'º Andar'}` : loc
  })
}
</script>

<template>
  <div class="animate-fade-in">
    <div class="mb-8 flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div>
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          Monitoramento em Tempo Real
        </h2>
        <p class="text-slate-500 text-sm mt-1 ml-5">Status operacional das salas ambulatoriais</p>
      </div>
      <div class="text-right">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Última Atualização</div>
        <div class="text-xl font-mono font-medium text-slate-700">{{ lastUpdate || '--:--:--' }}</div>
      </div>
    </div>

    <div v-if="dashboardData.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div v-for="item in dashboardData" :key="item.ambulatorio" @click="openDetails(item)" class="group bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-500/50 transition-all cursor-pointer overflow-hidden flex flex-col h-full">
        <div class="h-1 w-full bg-indigo-500"></div>
        <div class="p-5 flex-1 flex flex-col">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1 pr-2">
              <h4 class="font-bold text-slate-800 text-base leading-tight line-clamp-1" :title="item.ambulatorio">{{ item.ambulatorio }}</h4>
              <p class="text-[11px] text-slate-500 mt-1 truncate font-medium">{{ formatLocation(item.localizacao)[0] }}</p>
            </div>
            <div class="text-right shrink-0">
               <div class="text-2xl font-bold text-slate-800 leading-none">{{ item.salas_ocupadas }}</div>
               <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wide mt-0.5">Ativos</div>
            </div>
          </div>

          <div class="mt-auto">
            <div class="flex justify-between text-[10px] font-bold uppercase text-slate-400 mb-1.5">
                <span>Taxa de Ocupação</span>
                <span>{{ Math.round((item.salas_ocupadas / item.total_salas) * 100) || 0 }}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500 bg-indigo-500" :style="{ width: `${(item.salas_ocupadas / item.total_salas) * 100}%` }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="flex flex-col items-center justify-center py-20 text-slate-400">
      <svg class="w-12 h-12 mb-4 animate-pulse text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      <span class="text-sm font-medium">Conectando ao servidor...</span>
    </div>

    <AllocationDetailsModal :is-open="isDetailsModalOpen" :data="selectedAllocation" @close="closeDetails" />
  </div>
</template>