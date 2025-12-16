{
type: file
filePath: frontend/src/components/DoctorPortal.vue
content:
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Tipos baseados no Backend (models.py e schemas)
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

// Estados do Formulário do Médico
const medicoNome = ref('')
const especialidade = ref('')
const especialidadesDisponiveis = [
  "Neurologia", "Cardiologia", "Ortopedia", "Pediatria", 
  "Ginecologia", "Dermatologia", "Oncologia", "Psiquiatria",
  "Oftalmo", "Otorrino", "Urologia", "Cirurgia Geral"
]

// Controle de Interface
const currentTab = ref<'checkin' | 'checkout'>('checkin')
const viewMode = ref<'auto' | 'manual'>('auto')
const isLoading = ref(false)
const message = ref<{ text: string, type: 'success' | 'error' } | null>(null)

// Dados
const salasLivres = ref<Sala[]>([])
const salasOcupadas = ref<Sala[]>([])

const API_URL = 'http://localhost:8000'

// --- Funções de API ---

const fetchSalasOciosas = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas/ociosas`)
    const data = await res.json()
    salasLivres.value = data.salas || []
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const fetchTodasSalas = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas`)
    const data: Sala[] = await res.json()
    // Filtra apenas as ocupadas para a tela de Checkout
    salasOcupadas.value = data.filter(s => s.status_atual === 'OCUPADA')
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

// 1. Check-in Inteligente (Automático)
const handleSmartCheckin = async () => {
  if (!medicoNome.value || !especialidade.value) {
    message.value = { text: "Preencha seu nome e especialidade", type: 'error' }
    return
  }

  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas/checkin/inteligente`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        medico_nome: medicoNome.value,
        especialidade: especialidade.value
      })
    })

    const data = await res.json()

    if (!res.ok) throw new Error(data.detail || 'Erro ao realizar check-in')

    message.value = { 
      text: `Sucesso! Sala ${data.sala_alocada.numero} alocada para você. (${data.analise_logistica})`, 
      type: 'success' 
    }
    // Limpa campos após sucesso e muda para aba checkout
    setTimeout(() => {
        currentTab.value = 'checkout'
        fetchTodasSalas()
    }, 2000)

  } catch (err: any) {
    message.value = { text: err.message, type: 'error' }
  } finally {
    isLoading.value = false
  }
}

// 2. Check-in Manual (Selecionando da lista)
const handleManualCheckin = async (salaId: string) => {
  if (!medicoNome.value) {
    alert("Por favor, identifique-se com seu nome antes de ocupar uma sala.")
    return
  }

  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas/${salaId}/checkin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ medico_nome: medicoNome.value })
    })

    if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail)
    }

    message.value = { text: `Check-in realizado com sucesso na sala ${salaId}`, type: 'success' }
    fetchSalasOciosas() // Atualiza lista
  } catch (err: any) {
    message.value = { text: err.message, type: 'error' }
  } finally {
    isLoading.value = false
  }
}

// 3. Checkout
const handleCheckout = async (salaId: string) => {
  if(!confirm("Deseja realmente liberar esta sala?")) return;

  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/api/salas/${salaId}/checkout`, { method: 'POST' })
    if (!res.ok) throw new Error('Erro ao realizar checkout')
    
    message.value = { text: "Sala liberada com sucesso!", type: 'success' }
    fetchTodasSalas() // Atualiza lista
  } catch (err: any) {
    message.value = { text: err.message, type: 'error' }
  } finally {
    isLoading.value = false
  }
}

// Lógica de Ordenação e Filtragem para "Salas Próximas"
const salasLivresOrdenadas = computed(() => {
  if (!especialidade.value) return salasLivres.value

  // Clona o array para não mutar o original
  const lista = [...salasLivres.value]
  
  // Ordena: Primeiro as que contêm a especialidade preferencial, depois as outras
  return lista.sort((a, b) => {
    const esp = especialidade.value.toLowerCase()
    const prefA = (a.especialidade_preferencial || '').toLowerCase().includes(esp)
    const prefB = (b.especialidade_preferencial || '').toLowerCase().includes(esp)

    if (prefA && !prefB) return -1
    if (!prefA && prefB) return 1
    return 0
  })
})

const formatAndar = (andar: string) => {
    return (andar === '0' || andar.toLowerCase().includes('térreo')) ? 'Térreo' : `${andar}º Andar`
}

// Hooks
onMounted(() => {
  fetchSalasOciosas()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 pb-20">
    
    <header class="bg-teal-600 text-white p-6 shadow-md rounded-b-3xl mb-8">
      <h1 class="text-2xl font-bold">Portal do Profissional</h1>
      <p class="text-teal-100 text-sm">Realize Check-in e Check-out de consultórios</p>
    </header>

    <main class="max-w-3xl mx-auto px-4">
        
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
        <h2 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-wide">Sua Identificação</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Profissional</label>
                <input 
                    v-model="medicoNome"
                    type="text" 
                    placeholder="Ex: Dr. Carlos Silva"
                    class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition"
                >
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Especialidade</label>
                <select 
                    v-model="especialidade"
                    class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-teal-500 bg-white outline-none"
                    @change="fetchSalasOciosas" 
                >
                    <option value="" disabled selected>Selecione...</option>
                    <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">{{ esp }}</option>
                </select>
            </div>
        </div>
      </div>

      <div v-if="message" :class="`mb-6 p-4 rounded-lg text-sm font-medium ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`">
        {{ message.text }}
        <button @click="message = null" class="float-right font-bold ml-2">&times;</button>
      </div>

      <div class="flex p-1 bg-gray-200 rounded-xl mb-6">
        <button 
            @click="currentTab = 'checkin'; fetchSalasOciosas()"
            :class="`flex-1 py-2.5 text-sm font-medium rounded-lg transition ${currentTab === 'checkin' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`"
        >
            Encontrar Sala (Check-in)
        </button>
        <button 
            @click="currentTab = 'checkout'; fetchTodasSalas()"
            :class="`flex-1 py-2.5 text-sm font-medium rounded-lg transition ${currentTab === 'checkout' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`"
        >
            Minhas Salas (Check-out)
        </button>
      </div>

      <div v-if="currentTab === 'checkin'">
        
        <div class="flex gap-4 mb-6">
            <label class="flex items-center gap-2 cursor-pointer p-3 border rounded-lg bg-white flex-1 hover:border-teal-400 transition" :class="{'ring-2 ring-teal-500 border-teal-500': viewMode === 'auto'}">
                <input type="radio" v-model="viewMode" value="auto" class="hidden">
                <div class="bg-teal-100 p-2 rounded-full text-teal-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <div>
                    <span class="block font-bold text-gray-900">Automático</span>
                    <span class="text-xs text-gray-500">O sistema escolhe a melhor sala</span>
                </div>
            </label>

            <label class="flex items-center gap-2 cursor-pointer p-3 border rounded-lg bg-white flex-1 hover:border-teal-400 transition" :class="{'ring-2 ring-teal-500 border-teal-500': viewMode === 'manual'}">
                <input type="radio" v-model="viewMode" value="manual" class="hidden">
                <div class="bg-blue-100 p-2 rounded-full text-blue-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
                </div>
                <div>
                    <span class="block font-bold text-gray-900">Lista Manual</span>
                    <span class="text-xs text-gray-500">Escolha na lista de ociosas</span>
                </div>
            </label>
        </div>

        <div v-if="viewMode === 'auto'" class="text-center py-8 bg-white rounded-xl border border-gray-200 shadow-sm">
            <div class="mb-4 inline-block p-4 bg-teal-50 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">Check-in Inteligente</h3>
            <p class="text-gray-500 max-w-sm mx-auto mb-6">Encontraremos a sala disponível mais próxima do bloco da sua especialidade.</p>
            
            <button 
                @click="handleSmartCheckin"
                :disabled="isLoading || !medicoNome || !especialidade"
                class="bg-teal-600 text-white px-8 py-3 rounded-lg font-bold shadow-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform active:scale-95"
            >
                <span v-if="!isLoading">Solicitar Sala Agora</span>
                <span v-else>Processando...</span>
            </button>
        </div>

        <div v-else>
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-gray-800">
                    Salas Livres 
                    <span class="text-sm font-normal text-gray-500">({{ salasLivres.length }} disponíveis)</span>
                </h3>
                <button @click="fetchSalasOciosas" class="text-teal-600 text-sm hover:underline">Atualizar</button>
            </div>

            <div v-if="isLoading" class="text-center py-10 text-gray-400">Carregando salas...</div>
            
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div 
                    v-for="sala in salasLivresOrdenadas" 
                    :key="sala.id"
                    class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition relative overflow-hidden"
                >
                    <div v-if="especialidade && sala.especialidade_preferencial && sala.especialidade_preferencial.toLowerCase().includes(especialidade.toLowerCase())" class="absolute top-0 right-0 bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-bl-lg">
                        Recomendada
                    </div>

                    <div class="flex justify-between items-start">
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-lg font-bold text-gray-900">{{ sala.nome_visual }}</span>
                                <span class="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-600 border border-gray-200">{{ formatAndar(sala.andar) }} - Bloco {{ sala.bloco }}</span>
                            </div>
                            <p class="text-sm text-gray-500 mb-3">
                                <span class="font-medium text-gray-700">Pref:</span> {{ sala.especialidade_preferencial || 'Geral' }}
                            </p>
                        </div>
                    </div>
                    
                    <button 
                        @click="handleManualCheckin(sala.id)"
                        class="w-full mt-2 py-2 bg-white border border-teal-600 text-teal-600 rounded-lg text-sm font-bold hover:bg-teal-50 transition"
                    >
                        Ocupar Sala
                    </button>
                </div>
            </div>
        </div>

      </div>

      <div v-if="currentTab === 'checkout'">
        <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-gray-800">Salas Ocupadas Atualmente</h3>
            <button @click="fetchTodasSalas" class="text-blue-600 text-sm hover:underline">Atualizar</button>
        </div>

        <div v-if="isLoading" class="text-center py-10 text-gray-400">Carregando ocupação...</div>

        <div v-else-if="salasOcupadas.length === 0" class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
            <p class="text-gray-500">Nenhuma sala ocupada no momento.</p>
        </div>

        <div v-else class="space-y-3">
            <div 
                v-for="sala in salasOcupadas" 
                :key="sala.id"
                class="bg-white p-4 rounded-xl border-l-4 border-l-red-500 shadow-sm flex flex-col sm:flex-row justify-between items-center gap-4"
            >
                <div>
                    <div class="flex items-center gap-3">
                        <span class="text-xl font-bold text-gray-900">{{ sala.nome_visual }}</span>
                        <span class="text-sm text-gray-500">{{ formatAndar(sala.andar) }}</span>
                    </div>
                    <p class="text-sm text-gray-600 mt-1">
                        Ocupante: <span class="font-bold text-gray-800">{{ sala.ocupante_atual }}</span>
                    </p>
                </div>
                
                <button 
                    @click="handleCheckout(sala.id)"
                    class="px-4 py-2 bg-red-50 text-red-700 text-sm font-bold rounded-lg hover:bg-red-100 transition whitespace-nowrap"
                >
                    Liberar Sala (Check-out)
                </button>
            </div>
        </div>
      </div>

    </main>
  </div>
</template>
}