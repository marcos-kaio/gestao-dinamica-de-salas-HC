<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// --- Tipos ---
interface SalaBackend {
  sala_id: string;
  nome: string;
  bloco: string;
  andar: string;
  status: string;
  ocupante: any;
  especialidade_preferencial?: string;
}

interface SalaDetalhe {
  id: string;
  nome_visual: string;
  especialidade_preferencial: string;
}

// Estados
const medicoNome = ref('')
const especialidade = ref('')
const especialidadesDisponiveis = [
  "CARDIOLOGIA", "PEDIATRIA", "ORTOPEDIA", "GINECOLOGIA", 
  "DERMATOLOGIA", "NEUROLOGIA", "GASTROENTEROLOGIA", 
  "CIRURGIA GERAL", "ONCOLOGIA", "NEFROLOGIA", "UROLOGIA",
  "OFTALMOLOGIA", "OTORRINOLARINGOLOGIA", "PSIQUIATRIA",
  "OTORRINO", "GINECO"
]

const mapaSinonimos: Record<string, string> = {
  "OTORRINO": "OTORRINOLARINGOLOGIA",
  "GINECO": "GINECOLOGIA",
  "OBSTETRICIA": "GINECOLOGIA",
  "DERMATO": "DERMATOLOGIA",
  "NEURO": "NEUROLOGIA",
  "CARDIO": "CARDIOLOGIA",
  "PEDIATRIA GERAL": "PEDIATRIA",
  "CIRURGIA": "CIRURGIA GERAL"
}

const currentTab = ref<'checkin' | 'checkout'>('checkin')
const checkinMode = ref<'auto' | 'manual' | null>(null)
const isLoading = ref(false)
const message = ref<{ text: string, type: 'success' | 'error' } | null>(null)

const todasSalasCarregadas = ref<SalaBackend[]>([])

const API_URL = 'http://localhost:8000/api'

// --- Helpers ---
const normalizarEspecialidade = (texto: string): string => {
  if (!texto) return ""
  const upper = texto.toUpperCase().trim()
  return mapaSinonimos[upper] || upper
}

// --- Computados ---
const salasLivres = computed(() => todasSalasCarregadas.value.filter(s => s.status === 'LIVRE'))
const salasOcupadas = computed(() => todasSalasCarregadas.value.filter(s => s.status === 'OCUPADA'))

const salasRecomendadas = computed(() => {
  const lista = [...salasLivres.value]
  const espAlvo = normalizarEspecialidade(especialidade.value)
  if (!espAlvo) return lista 

  return lista.sort((a, b) => {
    const prefA = (a.especialidade_preferencial || '').toUpperCase()
    const prefB = (b.especialidade_preferencial || '').toUpperCase()
    const matchA = prefA.includes(espAlvo) || espAlvo.includes(prefA)
    const matchB = prefB.includes(espAlvo) || espAlvo.includes(prefB)
    const scoreA = matchA ? 2 : (prefA === '' ? 1 : 0)
    const scoreB = matchB ? 2 : (prefB === '' ? 1 : 0)
    return scoreB - scoreA
  })
})

const isRecomendada = (sala: SalaBackend) => {
  if (!especialidade.value) return false
  const espAlvo = normalizarEspecialidade(especialidade.value)
  const pref = (sala.especialidade_preferencial || '').toUpperCase()
  return pref.includes(espAlvo) || (espAlvo.length > 3 && espAlvo.includes(pref))
}

// --- API ---

const fetchSalasTempoReal = async () => {
  isLoading.value = true
  try {
    const [resStatus, resDetalhes] = await Promise.all([
      fetch(`${API_URL}/dashboard/agora`),
      fetch(`${API_URL}/salas`)
    ])

    const dataStatus = await resStatus.json()
    const dataDetalhes: SalaDetalhe[] = await resDetalhes.json()
    const mapaDetalhes = new Map(dataDetalhes.map((s) => [s.id, s]))

    const salasStatusList: any[] = dataStatus.salas;
    todasSalasCarregadas.value = salasStatusList.map((salaStatus) => ({
      ...salaStatus,
      especialidade_preferencial: mapaDetalhes.get(salaStatus.sala_id)?.especialidade_preferencial || ''
    }))
  } catch (e) {
    console.error(e)
    message.value = { text: "Erro de conexão.", type: 'error' }
  } finally {
    isLoading.value = false
  }
}

const requestCheckIn = async (salaId: string, nomeSala: string) => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/checkin`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        medico_nome: medicoNome.value,
        especialidade: especialidade.value,
        sala_id: salaId
      })
    })

    if (res.ok) {
      message.value = { text: `✅ Check-in confirmado na sala ${nomeSala}!`, type: 'success' }
      // Sucesso: Muda para aba de checkout para ver a sala ocupada
      checkinMode.value = null
      currentTab.value = 'checkout'
      await fetchSalasTempoReal()
    } else {
      const err = await res.json()
      message.value = { text: `Erro: ${err.detail}`, type: 'error' }
    }
  } catch (e) {
    message.value = { text: "Falha na requisição de check-in.", type: 'error' }
  } finally {
    isLoading.value = false
  }
}

const handleSmartCheckin = async () => {
  if (!medicoNome.value || !especialidade.value) {
    alert("Preencha Nome e Especialidade.")
    return
  }
  const melhorSala = salasRecomendadas.value[0]
  if (melhorSala) {
    await requestCheckIn(melhorSala.sala_id, melhorSala.nome)
  } else {
    message.value = { text: "Nenhuma sala livre disponível agora.", type: 'error' }
  }
}

const handleManualCheckin = async (salaId: string) => {
  if (!medicoNome.value) {
    alert("Identifique-se primeiro.")
    return
  }
  const sala = todasSalasCarregadas.value.find(s => s.sala_id === salaId)
  if (sala) await requestCheckIn(salaId, sala.nome)
}

const handleCheckout = async (salaId: string) => {
  if(!confirm("Liberar esta sala agora?")) return;
  
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/checkout/${salaId}`, { method: 'POST' })
    if (res.ok) {
      message.value = { text: "Sala liberada com sucesso!", type: 'success' }
      await fetchSalasTempoReal()
    } else {
      message.value = { text: "Erro ao liberar sala.", type: 'error' }
    }
  } catch (e) {
    message.value = { text: "Erro de conexão.", type: 'error' }
  } finally {
    isLoading.value = false
  }
}

const formatAndar = (andar: string) => {
    if (!andar) return ''
    return (andar === '0' || andar.toLowerCase().includes('térreo')) ? 'Térreo' : `${andar}º Andar`
}

onMounted(() => {
  fetchSalasTempoReal()
})
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen font-sans animate-fade-in">
    
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Portal do Profissional</h1>
        <p class="text-gray-500 text-sm mt-1">Gestão de Alocação em Tempo Real</p>
      </div>
    </div>

    <main class="max-w-4xl mx-auto px-4">
      
      <!-- Identificação -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-8 transition-shadow hover:shadow-md">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xl">🪪</span>
          <h2 class="text-xs font-bold text-gray-400 uppercase tracking-wide">Identificação Obrigatória</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Nome do profissional de saúde</label>
                <input v-model="medicoNome" type="text" placeholder="Ex: Dr. Carlos Silva" class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-blue-500 outline-none transition bg-gray-50 focus:bg-white">
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Especialidade</label>
                <select v-model="especialidade" class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-blue-500 bg-white outline-none cursor-pointer">
                    <option value="" disabled selected>Selecione...</option>
                    <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">{{ esp }}</option>
                </select>
            </div>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="message" class="mb-6 animate-slide-down">
        <div :class="`p-4 rounded-lg text-sm font-medium flex justify-between items-center ${message.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'}`">
          <span>{{ message.text }}</span>
          <button @click="message = null" class="font-bold text-lg leading-none opacity-50 hover:opacity-100">&times;</button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex p-1 bg-gray-200 rounded-xl mb-8 shadow-inner">
        <button @click="currentTab = 'checkin'; checkinMode = null; fetchSalasTempoReal()" :class="`flex-1 py-3 text-sm font-bold rounded-lg cursor-pointer transition ${currentTab === 'checkin' ? 'bg-white text-blue-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`">Realizar Check-in</button>
        <button @click="currentTab = 'checkout'; fetchSalasTempoReal()" :class="`flex-1 py-3 text-sm font-bold rounded-lg cursor-pointer transition ${currentTab === 'checkout' ? 'bg-white text-blue-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`">Checkout / Salas Ocupadas</button>
      </div>

      <!-- CHECK-IN -->
      <div v-if="currentTab === 'checkin'">
        <div v-if="!checkinMode" class="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
            <div @click="handleSmartCheckin" class="group relative overflow-hidden bg-linear-to-br from-blue-500 to-blue-700 rounded-2xl p-8 cursor-pointer shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 h-48 flex flex-col items-center justify-center text-center border border-blue-600">
                <div v-if="isLoading" class="absolute inset-0 bg-blue-800/80 flex items-center justify-center z-20 backdrop-blur-sm">
                    <div class="animate-spin h-8 w-8 border-4 border-white border-t-transparent rounded-full"></div>
                </div>
                <span class="text-5xl mb-4">🤖</span>
                <h3 class="text-2xl font-bold text-white">Check-in Inteligente</h3>
                <p class="text-blue-100 mt-2 text-sm">Aloca automaticamente a melhor sala para {{ especialidade || 'sua especialidade' }}.</p>
            </div>
            <div @click="checkinMode = 'manual'; fetchSalasTempoReal()" class="group bg-white rounded-2xl p-8 cursor-pointer border-2 border-dashed border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-all h-48 flex flex-col items-center justify-center text-center">
                <span class="text-5xl mb-4 text-gray-400 group-hover:text-blue-500">👆</span>
                <h3 class="text-2xl font-bold text-gray-700 group-hover:text-blue-700">Check-in Manual</h3>
                <p class="text-gray-500 mt-2 text-sm">Escolha na lista.</p>
            </div>
        </div>

        <div v-if="checkinMode === 'manual'" class="animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <button @click="checkinMode = null" class="text-gray-500 hover:text-blue-600 font-bold flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200 cursor-pointer">← Voltar</button>
                <span class="text-sm text-gray-500 font-medium">{{ salasLivres.length }} salas livres</span>
            </div>
            <div v-if="isLoading" class="text-center py-12">Carregando...</div>
            <div v-else-if="salasLivres.length === 0" class="text-center py-12 bg-white rounded-xl border border-gray-200">🚫 Nenhuma sala livre.</div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="sala in salasRecomendadas" :key="sala.sala_id" class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition group relative overflow-hidden" :class="{'border-blue-500 ring-1 ring-blue-500 bg-blue-50/30': isRecomendada(sala)}">
                    <div v-if="isRecomendada(sala)" class="absolute top-0 right-0 bg-blue-500 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg shadow-sm z-10">⭐ RECOMENDADA</div>
                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <span class="text-lg font-bold text-gray-800">{{ sala.nome }}</span>
                            <div class="text-xs text-gray-500 mt-1 flex flex-col gap-1">
                                <span>Bloco {{ sala.bloco }} • {{ formatAndar(sala.andar) }}</span>
                                <span v-if="sala.especialidade_preferencial" class="text-blue-700 bg-blue-50 px-1.5 rounded w-fit">Pref: {{ sala.especialidade_preferencial }}</span>
                            </div>
                        </div>
                        <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded border border-green-200">LIVRE</span>
                    </div>
                    <button @click="handleManualCheckin(sala.sala_id)" class="w-full py-2.5 bg-white border border-blue-600 text-blue-700 rounded-lg text-sm font-bold hover:bg-blue-600 hover:text-white cursor-pointer transition shadow-sm">Ocupar esta Sala</button>
                </div>
            </div>
        </div>
      </div>

      <!-- CHECKOUT -->
      <div v-if="currentTab === 'checkout'" class="animate-fade-in">
        <div v-if="isLoading" class="text-center py-10">Carregando...</div>
        <div v-else-if="salasOcupadas.length === 0" class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300 text-gray-500">Nenhuma sala ocupada.</div>
        <div v-else class="space-y-3">
            <div v-for="sala in salasOcupadas" :key="sala.sala_id" class="bg-white p-4 rounded-xl border-l-4 border-l-red-500 shadow-sm flex justify-between items-center">
                <div>
                    <h3 class="font-bold text-gray-800">{{ sala.nome }}</h3>
                    <p class="text-sm text-gray-600">Ocupante: <strong class="text-gray-900">{{ sala.ocupante?.medico || 'Desconhecido' }}</strong></p>
                    <p class="text-xs text-gray-400">{{ sala.ocupante?.especialidade }}</p>
                </div>
                <button @click="handleCheckout(sala.sala_id)" class="px-4 py-2 bg-red-50 text-red-600 text-sm font-bold rounded-lg hover:bg-red-100 border border-red-100 transition">Liberar</button>
            </div>
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
.animate-slide-down { animation: slideDown 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>