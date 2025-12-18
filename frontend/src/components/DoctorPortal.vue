<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Sala {
  id: string;
  nome_visual: string;
  bloco: string;
  andar: string;
  especialidade_preferencial: string;
  status_atual: string;
  ocupante_atual: string | null;
  features: string[];
}

const medicoNome = ref('')
const especialidade = ref('')
const especialidadesDisponiveis = [
  "Neurologia", "Cardiologia", "Ortopedia", "Pediatria", 
  "Ginecologia", "Dermatologia", "Oncologia", "Psiquiatria"
]

const currentTab = ref<'checkin' | 'checkout'>('checkin')
const viewMode = ref<'auto' | 'manual'>('auto')
const isLoading = ref(false)
const message = ref<{ text: string, type: 'success' | 'error' } | null>(null)
const salasLivres = ref<Sala[]>([])
const salasOcupadas = ref<Sala[]>([])
const API_URL = 'http://localhost:8000'

const fetchSalasOciosas = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas/ociosas?especialidade=${especialidade.value}`)
    salasLivres.value = await res.json()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const fetchSalasOcupadas = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas`)
    const todas = await res.json()
    salasOcupadas.value = todas.filter((s: Sala) => s.status_atual === 'OCUPADA')
  } catch (e) { console.error(e) } finally { isLoading.value = false }
}

onMounted(() => {
  fetchSalasOcupadas()
})

const handleCheckin = async (salaId: string) => {
  if (!medicoNome.value) {
    message.value = { text: "Por favor, identifique-se.", type: 'error' }
    return
  }
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/checkin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sala_id: salaId, medico_nome: medicoNome.value, especialidade: especialidade.value })
    })
    if (res.ok) {
      message.value = { text: "Check-in realizado com sucesso!", type: 'success' }
      medicoNome.value = ''
      salasLivres.value = []
      fetchSalasOcupadas()
    } else {
      message.value = { text: "Erro ao realizar check-in.", type: 'error' }
    }
  } catch (e) { message.value = { text: "Erro de conexão.", type: 'error' } } finally { isLoading.value = false }
}

const handleCheckout = async (salaId: string) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/checkout/${salaId}`, { method: 'POST' })
    if (res.ok) {
      message.value = { text: "Check-out confirmado. Sala liberada.", type: 'success' }
      fetchSalasOcupadas()
    }
  } catch (e) { console.error(e) } finally { isLoading.value = false }
}

const formatAndar = (andar: string) => (andar === '0' ? 'Térreo' : `${andar}º Andar`)
</script>

<template>
  <div class="max-w-3xl mx-auto animate-fade-in">
    
    <!-- Cabeçalho -->
    <div class="mb-8 text-center">
      <h2 class="text-2xl font-bold text-slate-800">Acesso Médico</h2>
      <p class="text-slate-500 text-sm">Registre sua entrada e saída das salas de atendimento.</p>
    </div>

    <!-- Navegação de Abas -->
    <div class="bg-white p-1 rounded-xl border border-slate-200 shadow-sm flex mb-8">
      <button 
        @click="currentTab = 'checkin'"
        class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
        :class="currentTab === 'checkin' ? 'bg-[#003B71] text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'"
      >
        Realizar Check-in
      </button>
      <button 
        @click="currentTab = 'checkout'; fetchSalasOcupadas()"
        class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
        :class="currentTab === 'checkout' ? 'bg-[#003B71] text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'"
      >
        Realizar Check-out
      </button>
    </div>

    <!-- Mensagens de Alerta -->
    <div v-if="message" class="mb-6 p-4 rounded-lg text-sm font-medium flex items-center gap-2" :class="message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-red-50 text-red-700 border border-red-100'">
      <span v-if="message.type === 'success'">✅</span><span v-else>⚠️</span>
      {{ message.text }}
      <button @click="message = null" class="ml-auto opacity-50 hover:opacity-100">&times;</button>
    </div>

    <!-- CHECK-IN -->
    <div v-if="currentTab === 'checkin'" class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Seu Nome</label>
          <input v-model="medicoNome" type="text" placeholder="Dr(a). Exemplo" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:border-[#003B71] focus:ring-2 focus:ring-[#003B71]/10 outline-none transition-all font-medium text-slate-800">
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Especialidade</label>
          <select v-model="especialidade" class="w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-200 focus:border-[#003B71] focus:ring-2 focus:ring-[#003B71]/10 outline-none transition-all font-medium text-slate-800 appearance-none">
            <option value="" disabled selected>Selecione...</option>
            <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">{{ esp }}</option>
          </select>
        </div>
      </div>

      <div class="mb-6">
        <button @click="fetchSalasOciosas" :disabled="!especialidade || isLoading" class="w-full py-3 bg-[#003B71] hover:bg-[#002a52] text-white font-bold rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
          <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <span v-else class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
          Buscar Salas Disponíveis
        </button>
      </div>

      <div v-if="salasLivres.length > 0" class="space-y-3">
        <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Salas Recomendadas</h3>
        <div v-for="sala in salasLivres" :key="sala.id" class="flex flex-col sm:flex-row items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-xl hover:border-emerald-400 transition-colors gap-4">
          <div class="flex items-center gap-4 w-full sm:w-auto">
            <div class="h-10 w-10 bg-white rounded-lg flex items-center justify-center font-bold text-[#003B71] border border-slate-200 shadow-sm shrink-0">
              {{ sala.nome_visual.replace(/\D/g, '') }}
            </div>
            <div>
              <div class="font-bold text-slate-800">{{ sala.nome_visual }}</div>
              <div class="text-xs text-slate-500 font-medium">Bloco {{ sala.bloco }} • {{ formatAndar(sala.andar) }}</div>
            </div>
          </div>
          <button @click="handleCheckin(sala.id)" class="w-full sm:w-auto px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg shadow-sm transition-colors">
            Confirmar Ocupação
          </button>
        </div>
      </div>
    </div>

    <!-- CHECK-OUT -->
    <div v-if="currentTab === 'checkout'" class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8">
      <div v-if="salasOcupadas.length === 0" class="text-center py-12">
        <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <p class="text-slate-500 font-medium">Nenhuma sala ocupada no momento.</p>
      </div>
      <div v-else class="space-y-3">
        <div v-for="sala in salasOcupadas" :key="sala.id" class="flex flex-col sm:flex-row items-center justify-between p-4 bg-white border border-l-4 border-slate-200 border-l-red-500 rounded-r-xl shadow-sm gap-4">
          <div class="w-full">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-lg font-bold text-slate-800">{{ sala.nome_visual }}</span>
              <span class="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded border border-slate-200">{{ formatAndar(sala.andar) }}</span>
            </div>
            <p class="text-sm text-slate-600">Ocupante: <span class="font-bold text-slate-800">{{ sala.ocupante_atual }}</span></p>
          </div>
          <button @click="handleCheckout(sala.id)" class="w-full sm:w-auto px-5 py-2 bg-red-50 text-red-600 border border-red-100 text-sm font-bold rounded-lg hover:bg-red-100 transition-colors">
            Liberar Sala
          </button>
        </div>
      </div>
    </div>

  </div>
</template>