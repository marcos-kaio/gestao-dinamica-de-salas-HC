<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  data: any,
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'updated'])

const editandoId = ref<number | null>(null)
const salasDisponiveis = ref<any[]>([])
const loadingSalas = ref(false)

const iniciarEdicao = async (alocacaoId: number) => {
  editandoId.value = alocacaoId
  loadingSalas.value = true
  salasDisponiveis.value = []
  
  try {
    const res = await fetch(`http://localhost:8000/api/alocacao/${alocacaoId}/opcoes`)
    if(res.ok) {
      salasDisponiveis.value = await res.json()
    }
  } finally {
    loadingSalas.value = false
  }
}

const salvarTroca = async (alocacaoId: number, novaSalaId: string) => {
  try {
    const res = await fetch(`http://localhost:8000/api/alocacao/${alocacaoId}/trocar`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ nova_sala_id: novaSalaId })
    })
    
    if(res.ok) {
      editandoId.value = null
      emit('updated')
    }
  } catch (e) {
    alert("Erro ao salvar troca")
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
      
      <!-- Header -->
      <div class="p-6 border-b flex justify-between items-center bg-gray-50 rounded-t-lg">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">{{ data?.ambulatorio || 'Detalhes' }}</h2>
          <p class="text-sm text-gray-600">
            {{ data?.detalhes?.length || 0 }} alocações registradas
          </p>
        </div>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700 cursor-pointer text-2xl">&times;</button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs font-bold text-gray-500 uppercase border-b">
              <th class="pb-3 w-1/4">Dia/Turno</th>
              <th class="pb-3 w-1/3">Profissional</th>
              <th class="pb-3 w-1/4">Sala</th>
              <th class="pb-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="item in data?.detalhes" :key="item.alocacao_id" class="border-b hover:bg-gray-50 group">
              <td class="py-3 font-medium text-gray-700">
                <span class="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs border border-blue-100">
                  {{ item.dia }} - {{ item.turno }}
                </span>
              </td>
              <td class="py-3 text-gray-800 font-medium truncate max-w-[200px]" :title="item.medico">
                {{ item.medico }}
              </td>
              
              <td class="py-3">
                <div v-if="editandoId === item.alocacao_id" class="relative">
                  <select 
                    class="border rounded px-2 py-1 w-full text-xs bg-white focus:ring-2 focus:ring-blue-500"
                    @change="salvarTroca(item.alocacao_id, ($event.target as HTMLSelectElement).value)"
                  >
                    <option disabled selected>Selecione...</option>
                    <option v-for="opt in salasDisponiveis" :key="opt.sala_id" :value="opt.sala_id">
                      {{ opt.nome }} {{ opt.recomendado ? '⭐' : '' }}
                    </option>
                  </select>
                  <div v-if="loadingSalas" class="text-[10px] text-gray-400 mt-1">Carregando salas...</div>
                </div>
                <div v-else class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-green-500"></span>
                  {{ item.sala }}
                </div>
              </td>

              <td class="py-3 text-right">
                <button 
                  v-if="editandoId !== item.alocacao_id"
                  @click="iniciarEdicao(item.alocacao_id)"
                  class="text-blue-600 hover:text-blue-800 font-medium cursor-pointer text-xs px-3 py-1 border border-blue-200 rounded hover:bg-blue-50 transition"
                >
                  Trocar
                </button>
                <button 
                  v-else 
                  @click="editandoId = null"
                  class="text-gray-500 hover:text-gray-700 text-xs underline cursor-pointer ml-2"
                >
                  Cancelar
                </button>
              </td>
            </tr>
            <tr v-if="!data?.detalhes || data.detalhes.length === 0">
              <td colspan="4" class="text-center py-8 text-gray-500">
                Nenhuma alocação encontrada para este ambulatório.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>