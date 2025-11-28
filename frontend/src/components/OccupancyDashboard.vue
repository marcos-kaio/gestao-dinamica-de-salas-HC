<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AllocationDetailsModal from '../components/AllocationDetailsModal.vue'

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

const dashboardData = ref<ResumoAmbulatorio[]>([])
const lastUpdate = ref<string>('')
const isDetailsModalOpen = ref(false)
const selectedAllocation = ref<ResumoAmbulatorio | null>(null)

let pollingInterval: number | null = null;
const API_URL = 'http://localhost:8000'

const fetchDashboardRealTime = async () => {
  try {
    const res = await fetch(`${API_URL}/api/salas`)
    const salas = await res.json()
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
  } catch (e) {
    console.error(e)
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
    <header class="bg-indigo-600 text-white p-6 shadow-md rounded-b-3xl mb-8">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold">Monitoramento de Ocupação</h1>
          <p class="text-indigo-100 text-sm">Visão em tempo real dos ambulatórios</p>
        </div>
        <div class="bg-indigo-700/50 backdrop-blur-sm px-4 py-2 rounded-full flex items-center gap-2 text-xs font-medium border border-indigo-500/30">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
          </span>
          <span class="text-indigo-50">Sincronizado às {{ lastUpdate }}</span>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4">
      <div v-if="dashboardData.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div 
          v-for="item in dashboardData" 
          :key="item.ambulatorio"
          @click="openDetails(item)"
          class="group bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition cursor-pointer relative overflow-hidden"
        >
          <div class="absolute left-0 top-0 bottom-0 w-1 transition-colors" 
               :class="item.salas_ocupadas > 0 ? 'bg-indigo-500' : 'bg-gray-200'"></div>

          <div class="pl-2 flex flex-col h-full">
            <div class="flex justify-between items-start mb-3">
              <div class="pr-2">
                <h4 class="font-bold text-gray-900 line-clamp-1" :title="item.ambulatorio">{{ item.ambulatorio }}</h4>
                <p class="text-xs text-gray-500 mt-1 flex flex-wrap gap-1">
                   <span v-for="loc in formatLocation(item.localizacao)" :key="loc" class="bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100">{{ loc }}</span>
                </p>
              </div>
              <div class="text-right shrink-0">
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
                      class="bg-indigo-500 h-2 rounded-full transition-all duration-500 group-hover:bg-indigo-400" 
                      :style="{ width: `${(item.salas_ocupadas / item.total_salas) * 100}%` }"
                  ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-20 text-gray-500">
        Nenhum dado encontrado. O gestor precisa importar a infraestrutura.
      </div>
    </main>

    <AllocationDetailsModal 
      :is-open="isDetailsModalOpen"
      :data="selectedAllocation"
      @close="closeDetails"
    />
  </div>
</template>