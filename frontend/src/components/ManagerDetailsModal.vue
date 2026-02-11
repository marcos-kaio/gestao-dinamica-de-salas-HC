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

const salvarTroca = async (alocacaoId: number, novaSalaId: string, forcar = false) => {
  if (!novaSalaId) return

  try {
    const res = await fetch(`http://localhost:8000/api/alocacao/${alocacaoId}/trocar`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ nova_sala_id: novaSalaId, forcar: forcar })
    })
    
    if (res.ok) {
      alert("Troca realizada com sucesso!")
      editandoId.value = null
      emit('updated')
    } else if (res.status === 409) {
      // Conflito detectado (sala ocupada)
      if (confirm("⚠️ AVISO: Esta sala já está ocupada por outro profissional.\n\nDeseja FORÇAR a alocação? Isso removerá o ocupante atual da sala.")) {
        // Tenta novamente com flag de força
        salvarTroca(alocacaoId, novaSalaId, true)
      } else {
        // Cancela a seleção visualmente se o usuário desistir
        iniciarEdicao(alocacaoId) 
      }
    } else {
      alert("Erro ao realizar a troca.")
    }
  } catch (e) {
    alert("Erro de conexão.")
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in" @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
      
      <!-- Header -->
      <div class="p-6 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">{{ data?.ambulatorio || 'Detalhes' }}</h2>
          <p class="text-sm text-gray-600">
            {{ data?.detalhes?.length || 0 }} alocações registradas
          </p>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-red-500 text-3xl font-light cursor-pointer">&times;</button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">
              <th class="pb-4 pl-2">Dia / Turno</th>
              <th class="pb-4">Profissional</th>
              <th class="pb-4">Sala Atual</th>
              <th class="pb-4 text-right pr-2">Ações</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="item in data?.detalhes || []" :key="item.alocacao_id" class="border-b border-gray-50 hover:bg-blue-50/50 transition-colors group">
              
              <!-- Dia/Turno -->
              <td class="py-4 pl-2 font-medium text-gray-600">
                <div class="flex items-center gap-2">
                  <span class="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs font-bold border border-gray-200">
                    {{ item.dia }}
                  </span>
                  <span class="text-xs text-gray-500">{{ item.turno }}</span>
                </div>
              </td>

              <!-- Médico -->
              <td class="py-4 text-gray-800 font-semibold">
                {{ item.medico }}
              </td>
              
              <!-- Sala (Visualização ou Edição) -->
              <td class="py-4">
                
                <!-- Modo Edição -->
                <div v-if="editandoId === item.alocacao_id" class="relative w-full max-w-md">
                  <select 
                    class="border border-blue-300 rounded-lg px-3 py-2 w-full text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none shadow-sm"
                    @change="salvarTroca(item.alocacao_id, ($event.target as HTMLSelectElement).value)"
                  >
                    <option disabled selected>Selecione uma nova sala...</option>
                    
                    <!-- Opções Livres -->
                    <optgroup label="✅ Salas Livres">
                      <option 
                        v-for="opt in salasDisponiveis.filter(s => !s.ocupada)" 
                        :key="opt.sala_id" 
                        :value="opt.sala_id"
                        class="text-gray-800"
                      >
                        {{ opt.nome }} {{ opt.recomendado ? '⭐ (Recomendada)' : '' }}
                      </option>
                    </optgroup>

                    <!-- Opções Ocupadas (Para Troca Forçada) -->
                    <optgroup label="⚠️ Salas Ocupadas (Requer Confirmação)">
                      <option 
                        v-for="opt in salasDisponiveis.filter(s => s.ocupada)" 
                        :key="opt.sala_id" 
                        :value="opt.sala_id"
                        class="text-red-600 bg-red-50"
                      >
                        {{ opt.nome }} — {{ opt.status }}
                      </option>
                    </optgroup>

                  </select>
                  
                  <div v-if="loadingSalas" class="absolute right-3 top-2.5">
                    <div class="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  </div>
                </div>

                <!-- Modo Visualização -->
                <div v-else class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-green-500 shadow-sm"></span>
                  <span class="font-bold text-gray-700">{{ item.sala }}</span>
                </div>
              </td>

              <!-- Botões -->
              <td class="py-4 text-right pr-2">
                <button 
                  v-if="editandoId !== item.alocacao_id"
                  @click="iniciarEdicao(item.alocacao_id)"
                  class="text-blue-600 hover:text-white hover:bg-blue-600 font-medium text-xs px-3 py-1.5 border border-blue-200 rounded-lg transition-all shadow-sm cursor-pointer"
                >
                  Mudar Sala
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

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
</style>