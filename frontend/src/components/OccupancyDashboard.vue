<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

const dadosTempoReal = ref<any>(null)
const loading = ref(true)
let intervalo: any = null

const fetchDashboardRealTime = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/dashboard/agora')
    if (res.ok) {
      dadosTempoReal.value = await res.json()
    }
  } catch (e) {
    console.error("Erro ao buscar dados tempo real", e)
  } finally {
    loading.value = false
  }
}

// Agrupa as salas planas em cards por Especialidade/Ambulatório (Layout Antigo)
const ambulatoriosAgrupados = computed(() => {
  if (!dadosTempoReal.value) return []
  
  const grupos: Record<string, any> = {}
  
  dadosTempoReal.value.salas.forEach((sala: any) => {
    // Se estiver ocupada, usa a especialidade do ocupante
    // Se estiver livre, tenta usar a especialidade preferencial (se tivéssemos esse dado no flat list)
    // Como o endpoint realtime é focado em status, vamos agrupar por Bloco/Andar para salas livres ou manter "Geral"
    
    // Melhor abordagem: Agrupar pelo ocupante se houver, ou "Salas Livres/Manutenção" se não
    let chave = "Disponíveis / Outros"
    if (sala.status === 'OCUPADA' && sala.ocupante) {
      chave = sala.ocupante.especialidade || "Alocação Geral"
    } else if (sala.status === 'MANUTENCAO') {
      chave = "Manutenção"
    } else {
        // Salas livres: Tenta inferir pelo nome ou joga em Disponíveis
        chave = "Salas Disponíveis"
    }

    if (!grupos[chave]) {
      grupos[chave] = { nome: chave, salas: [], total: 0, ocupadas: 0 }
    }
    
    grupos[chave].salas.push(sala)
    grupos[chave].total++
    if (sala.status === 'OCUPADA') grupos[chave].ocupadas++
  })

  // Ordena alfabeticamente, deixando Disponíveis no topo
  return Object.values(grupos).sort((a: any, b: any) => {
      if(a.nome === 'Salas Disponíveis') return -1
      return a.nome.localeCompare(b.nome)
  })
})

onMounted(() => {
  fetchDashboardRealTime()
  intervalo = setInterval(fetchDashboardRealTime, 30000) // Atualiza a cada 30s
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
})
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    
    <!-- Cabeçalho (Mantido o novo com stats) -->
    <div class="mb-8 flex flex-col md:flex-row justify-between items-center gap-4 bg-white p-4 rounded-xl shadow-sm border border-gray-200">
      <div>
        <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
          Monitoramento em Tempo Real
        </h2>
        <p v-if="dadosTempoReal" class="text-sm text-gray-500 mt-1">
          Visão exata de: <strong class="text-blue-700">{{ dadosTempoReal.tempo.dia }} - {{ dadosTempoReal.tempo.turno }}</strong> ({{ dadosTempoReal.tempo.hora_legivel }})
        </p>
      </div>
      
      <div v-if="dadosTempoReal" class="flex gap-4">
        <div class="flex items-center gap-3 px-4 py-2 bg-blue-50 rounded-lg border border-blue-100">
          <div>
            <p class="text-xs text-blue-600 font-bold uppercase">Livres</p>
            <p class="text-center text-xl font-bold text-blue-900">{{ dadosTempoReal.estatisticas.livres }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3 px-2 py-2 bg-green-50 rounded-lg border border-green-100">
          <div>
            <p class="text-xs text-green-600 font-bold uppercase">Ocupadas</p>
            <p class="text-center text-xl font-bold text-green-900">{{ dadosTempoReal.estatisticas.ocupadas }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">
      <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
      Carregando mapa do hospital...
    </div>

    <!-- Grid de Cards (Estilo Antigo) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      
      <div 
        v-for="grupo in ambulatoriosAgrupados" 
        :key="grupo.nome"
        class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col hover:shadow-md transition-shadow"
      >
        <!-- Header do Card -->
        <div class="p-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
          <h3 class="font-bold text-gray-800 text-sm uppercase truncate pr-2" :title="grupo.nome">
            {{ grupo.nome }}
          </h3>
          <span class="text-[10px] font-bold px-2 py-1 rounded-full bg-white border border-gray-200 text-gray-600">
            {{ grupo.salas.length }} Salas
          </span>
        </div>

        <!-- Lista de Salas -->
        <div class="p-3 flex-1 overflow-y-auto max-h-48 custom-scrollbar">
          <ul class="space-y-2">
            <li 
              v-for="sala in grupo.salas" 
              :key="sala.sala_id" 
              class="flex justify-between items-center text-xs p-2 rounded bg-gray-50"
              :class="{'bg-red-50 text-red-700': sala.status === 'OCUPADA', 'bg-green-50 text-green-700': sala.status === 'LIVRE'}"
            >
              <div class="flex items-center gap-2">
                <span 
                  class="w-2 h-2 rounded-full"
                  :class="sala.status === 'LIVRE' ? 'bg-green-500' : (sala.status === 'OCUPADA' ? 'bg-red-500' : 'bg-yellow-500')"
                ></span>
                <span class="font-bold">{{ sala.nome }}</span>
              </div>
              
              <div v-if="sala.status === 'OCUPADA'" class="text-right truncate max-w-[100px]">
                <span class="block font-medium truncate">{{ sala.ocupante.medico }}</span>
              </div>
              <div v-else>
                <span class="opacity-60">{{ sala.status }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>