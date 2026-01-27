<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ManagerDetailsModal from './ManagerDetailsModal.vue'
import DataManagementModal from './DataManagementModal.vue'

interface ResumoAmbulatorio {
  ambulatorio: string;
  total_salas: number;
  localizacao: string[];
  lista_salas: string[];
  detalhes: any[];
}

const loading = ref(false)
const alocacaoResumo = ref<ResumoAmbulatorio[]>([])
const modalDetalhesAberto = ref(false)
const modalGestaoAberto = ref(false)
const itemSelecionado = ref<ResumoAmbulatorio | null>(null)

const API_URL = 'http://localhost:8000/api'

const carregarEstadoAtual = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_URL}/alocacao/resumo`)
    if (res.ok) {
      alocacaoResumo.value = await res.json()
    }
  } catch (err) {
    console.error("Erro", err)
  } finally {
    loading.value = false
  }
}

const gerarAlocacao = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_URL}/alocacao/gerar`, { method: 'POST' })
    const data = await response.json()
    if (data.resumo_executivo) alocacaoResumo.value = data.resumo_executivo
  } finally {
    loading.value = false
  }
}

const abrirDetalhes = (item: ResumoAmbulatorio) => {
  itemSelecionado.value = item
  modalDetalhesAberto.value = true
}

const aoAtualizar = () => {
  carregarEstadoAtual()
  modalDetalhesAberto.value = false
}

const aoConcluirGestao = () => {
  gerarAlocacao()
}

onMounted(() => { carregarEstadoAtual() })
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Painel de Gestão de Alocação</h1>
        <p class="text-gray-500 text-sm mt-1">Visão geral da ocupação e ferramentas de administração.</p>
      </div>
      
      <div class="flex gap-3">
        <button 
          @click="modalGestaoAberto = true" 
          class="flex items-center gap-2 bg-white text-gray-700 border border-gray-300 px-4 py-2.5 rounded-lg hover:bg-gray-50 hover:text-blue-600 transition font-medium shadow-sm"
        >
          ⚙️ Gerenciar Dados
        </button>

        <button 
          @click="gerarAlocacao" 
          :disabled="loading" 
          class="flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg hover:bg-blue-700 transition shadow-md disabled:opacity-70"
        >
          {{ loading ? 'Calculando...' : '⚡ Recalcular Alocação' }}
        </button>
      </div>
    </div>

    <div v-if="alocacaoResumo.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 animate-fade-in">
      <div 
        v-for="item in alocacaoResumo" 
        :key="item.ambulatorio"
        @click="abrirDetalhes(item)"
        class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md hover:border-blue-300 transition-all flex flex-col cursor-pointer group"
      >
        <div class="bg-gray-50/80 p-4 border-b border-gray-100 group-hover:bg-blue-50/50">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold text-gray-800 text-sm uppercase leading-tight truncate pr-2" :title="item.ambulatorio">{{ item.ambulatorio }}</h3>
              <span class="bg-white border border-gray-200 text-gray-600 text-[10px] font-bold px-2 py-1 rounded shrink-0">{{ item.total_salas }} SALAS</span>
            </div>
            <div class="flex flex-wrap gap-1">
               <span v-for="loc in item.localizacao" :key="loc" class="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-bold">📍 {{ loc }}</span>
            </div>
        </div>
        <div class="p-3 flex-1 bg-white relative">
            <p class="text-[10px] text-gray-400 font-bold uppercase mb-2">Salas:</p>
            <div class="overflow-y-auto max-h-32 custom-scrollbar">
                <ul class="space-y-1">
                    <li v-for="sala in item.lista_salas" :key="sala" class="text-xs text-gray-600 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span> {{ sala }}
                    </li>
                </ul>
            </div>
            <div class="absolute bottom-2 right-3 opacity-0 group-hover:opacity-100 transition-opacity text-blue-600">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
               </svg>
            </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="!loading" class="text-center py-20 text-gray-500">
      <p class="text-xl">Nenhuma alocação encontrada.</p>
      <p class="text-sm mt-2">Clique em "Gerenciar Dados" para importar uma grade.</p>
    </div>

    <!-- Modais -->
    <ManagerDetailsModal 
      v-if="modalDetalhesAberto" 
      :isOpen="modalDetalhesAberto" 
      :data="itemSelecionado" 
      @close="modalDetalhesAberto = false"
      @updated="aoAtualizar"
    />

    <DataManagementModal
      v-if="modalGestaoAberto"
      :isOpen="modalGestaoAberto"
      @close="modalGestaoAberto = false"
      @success="aoConcluirGestao"
    />

  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.animate-fade-in { animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
</style>