<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// --- Tipos ---

// Interface para o objeto retornado por /dashboard/agora (status em tempo real)
interface SalaStatus {
  sala_id: string;
  nome: string;
  bloco: string;
  andar: string;
  status: string;
  ocupante: any;
}

// Interface para o objeto retornado por /salas (detalhes estáticos)
interface SalaDetalhe {
  id: string;
  nome_visual: string;
  especialidade_preferencial: string;
}

// Interface unificada para o frontend
interface SalaBackend extends SalaStatus {
  especialidade_preferencial?: string; 
}

// Estados
const medicoNome = ref('')
const especialidade = ref('')

// Lista de seleção para o médico (Nomes amigáveis)
const especialidadesDisponiveis = [
  "CARDIOLOGIA", "PEDIATRIA", "ORTOPEDIA", "GINECOLOGIA", 
  "DERMATOLOGIA", "NEUROLOGIA", "GASTROENTEROLOGIA", 
  "CIRURGIA GERAL", "ONCOLOGIA", "NEFROLOGIA", "UROLOGIA",
  "OFTALMOLOGIA", "OTORRINOLARINGOLOGIA", "PSIQUIATRIA",
  "OTORRINO", "GINECO", "OBSTETRICIA" // Adicionando variações comuns na lista
]

// Mapa de Sinônimos para Normalização (Frontend)
const mapaSinonimos: Record<string, string> = {
  "OTORRINO": "OTORRINOLARINGOLOGIA",
  "GINECO": "GINECOLOGIA",
  "OBSTETRICIA": "GINECOLOGIA", // Muitas vezes compartilham
  "DERMATO": "DERMATOLOGIA",
  "NEURO": "NEUROLOGIA",
  "CARDIO": "CARDIOLOGIA",
  "PEDIATRIA GERAL": "PEDIATRIA",
  "CIRURGIA": "CIRURGIA GERAL"
}

const currentTab = ref<'checkin' | 'checkout' | 'history'>('checkin')
const checkinMode = ref<'auto' | 'manual' | null>(null)
const isLoading = ref(false)
const message = ref<{ text: string, type: 'success' | 'error' } | null>(null)

// Dados Brutos
const todasSalasCarregadas = ref<SalaBackend[]>([])
const history = ref<any[]>([]) 

const API_URL = 'http://localhost:8000/api'

// --- Helpers de Normalização ---

// Normaliza a entrada do usuário para bater com o cadastro oficial da sala
const normalizarEspecialidade = (texto: string): string => {
  if (!texto) return ""
  const upper = texto.toUpperCase().trim()
  // Retorna o sinônimo oficial ou o próprio texto se não houver mapeamento
  return mapaSinonimos[upper] || upper
}

// --- Computados (A Mágica da Recomendação) ---

const salasLivres = computed(() => {
  return todasSalasCarregadas.value.filter(s => s.status === 'LIVRE')
})

const salasOcupadas = computed(() => {
  return todasSalasCarregadas.value.filter(s => s.status === 'OCUPADA')
})

// Ordena as salas livres baseando-se na especialidade selecionada (com normalização)
const salasRecomendadas = computed(() => {
  const lista = [...salasLivres.value]
  
  // Normaliza o que o médico selecionou (Ex: "Otorrino" vira "OTORRINOLARINGOLOGIA")
  const espAlvo = normalizarEspecialidade(especialidade.value)

  if (!espAlvo) return lista 

  return lista.sort((a, b) => {
    // Normaliza a preferência da sala (Ex: "Otorrinolaringologia" vira upper)
    const prefA = (a.especialidade_preferencial || '').toUpperCase()
    const prefB = (b.especialidade_preferencial || '').toUpperCase()

    // Verifica se a especialidade alvo está contida na preferência da sala
    // Ex: "OTORRINOLARINGOLOGIA" está em "OTORRINOLARINGOLOGIA"? Sim.
    const matchA = prefA.includes(espAlvo) || espAlvo.includes(prefA)
    const matchB = prefB.includes(espAlvo) || espAlvo.includes(prefB)

    const scoreA = matchA ? 2 : (prefA === '' ? 1 : 0) // Salas genéricas (vazias) têm prioridade média
    const scoreB = matchB ? 2 : (prefB === '' ? 1 : 0)

    return scoreB - scoreA // Maior score primeiro
  })
})

// Verifica se uma sala é recomendada para mostrar o badge
const isRecomendada = (sala: SalaBackend) => {
  if (!especialidade.value) return false
  
  const espAlvo = normalizarEspecialidade(especialidade.value)
  const pref = (sala.especialidade_preferencial || '').toUpperCase()
  
  // Match bidirecional para pegar casos parciais
  return pref.includes(espAlvo) || (espAlvo.length > 3 && espAlvo.includes(pref))
}

// --- Funções de API ---

const fetchSalasTempoReal = async () => {
  isLoading.value = true
  try {
    const [resStatus, resDetalhes] = await Promise.all([
      fetch(`${API_URL}/dashboard/agora`),
      fetch(`${API_URL}/salas`)
    ])

    const dataStatus = await resStatus.json()
    const dataDetalhes: SalaDetalhe[] = await resDetalhes.json()

    const mapaDetalhes = new Map<string, SalaDetalhe>(dataDetalhes.map((s) => [s.id, s]))

    const salasStatusList: SalaStatus[] = dataStatus.salas;
    
    todasSalasCarregadas.value = salasStatusList.map((salaStatus) => ({
      ...salaStatus,
      especialidade_preferencial: mapaDetalhes.get(salaStatus.sala_id)?.especialidade_preferencial || ''
    }))

  } catch (e) {
    console.error("Erro ao buscar dados:", e)
    message.value = { text: "Erro de conexão com o servidor.", type: 'error' }
  } finally {
    isLoading.value = false
  }
}

// --- Ações ---

// 1. Check-in Inteligente (Automático)
const handleSmartCheckin = async () => {
  if (!medicoNome.value || !especialidade.value) {
    alert("Por favor, preencha seu Nome e Especialidade.")
    return
  }

  isLoading.value = true
  
  setTimeout(() => {
    const melhorSala = salasRecomendadas.value[0]
    
    if (melhorSala) {
       const motivo = isRecomendada(melhorSala) ? "Compatibilidade de Especialidade" : "Disponibilidade Geral"
       
       message.value = { 
        text: `✅ Sala Alocada: ${melhorSala.nome} (${melhorSala.bloco}). Critério: ${motivo}.`, 
        type: 'success' 
      }
      
      registrarHistorico(melhorSala.nome)
      
      checkinMode.value = null
      currentTab.value = 'history'
      fetchSalasTempoReal()
    } else {
       message.value = { text: "⚠️ Não há salas livres no momento.", type: 'error' }
    }
    isLoading.value = false
  }, 1200)
}

// 2. Check-in Manual
const handleManualCheckin = async (salaId: string) => {
  if (!medicoNome.value) {
    alert("Por favor, identifique-se com seu nome.")
    return
  }

  const sala = todasSalasCarregadas.value.find(s => s.sala_id === salaId)
  if (!sala) return

  isLoading.value = true
  setTimeout(() => {
      message.value = { text: `Check-in realizado: ${sala.nome}`, type: 'success' }
      registrarHistorico(sala.nome)
      
      fetchSalasTempoReal()
      checkinMode.value = null
      currentTab.value = 'history'
      isLoading.value = false
  }, 600)
}

// 3. Checkout
const handleCheckout = async (salaId: string) => {
  if(!confirm("Liberar esta sala?")) return;
  isLoading.value = true
  setTimeout(() => {
    message.value = { text: "Sala liberada com sucesso!", type: 'success' }
    const item = history.value.find(h => h.status === 'Ativo')
    if(item) item.status = 'Finalizado'
    
    fetchSalasTempoReal()
    isLoading.value = false
  }, 600)
}

// Auxiliar
const registrarHistorico = (nomeSala: string) => {
  history.value.unshift({
    id: Date.now(),
    room: nomeSala,
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'}),
    status: 'Ativo'
  })
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
    
    <!-- Header: Estilo unificado com as outras telas -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Portal do Profissional</h1>
        <p class="text-gray-500 text-sm mt-1">Gestão de Alocação em Tempo Real</p>
      </div>
    </div>

    <main class="max-w-4xl mx-auto px-4">
      
      <!-- Identificação (Sempre visível) -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-8 transition-shadow hover:shadow-md">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xl">🪪</span>
          <h2 class="text-xs font-bold text-gray-400 uppercase tracking-wide">Identificação Obrigatória</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Seu Nome</label>
                <input 
                    v-model="medicoNome"
                    type="text" 
                    placeholder="Ex: Dr. Carlos Silva"
                    class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-blue-500 outline-none transition bg-gray-50 focus:bg-white"
                >
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">Especialidade (Para Recomendação)</label>
                <select 
                    v-model="especialidade"
                    class="w-full rounded-lg border-gray-300 border p-3 focus:ring-2 focus:ring-blue-500 bg-white outline-none"
                >
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

      <!-- Tabs Navegação -->
      <div class="flex p-1 bg-gray-200 rounded-xl mb-8 shadow-inner">
        <button 
            @click="currentTab = 'checkin'; checkinMode = null; fetchSalasTempoReal()"
            :class="`flex-1 py-3 text-sm font-bold rounded-lg transition ${currentTab === 'checkin' ? 'bg-white text-blue-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`"
        >
            Realizar Check-in
        </button>
        <button 
            @click="currentTab = 'checkout'; fetchSalasTempoReal()"
            :class="`flex-1 py-3 text-sm font-bold rounded-lg transition ${currentTab === 'checkout' ? 'bg-white text-blue-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`"
        >
            Checkout / Salas Ocupadas
        </button>
        <button 
            @click="currentTab = 'history'"
            :class="`flex-1 py-3 text-sm font-bold rounded-lg transition ${currentTab === 'history' ? 'bg-white text-blue-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`"
        >
            Meu Histórico
        </button>
      </div>

      <!-- CONTEÚDO CHECK-IN -->
      <div v-if="currentTab === 'checkin'">
        
        <!-- Seleção de Modo (Cards Grandes) -->
        <div v-if="!checkinMode" class="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
            
            <!-- Card Automático -->
            <div 
                @click="handleSmartCheckin"
                class="group relative overflow-hidden bg-linear-to-br from-blue-500 to-blue-700 rounded-2xl p-8 cursor-pointer shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 h-48 flex flex-col items-center justify-center text-center border border-blue-600"
            >
                <div v-if="isLoading" class="absolute inset-0 bg-blue-800/80 flex items-center justify-center z-20 backdrop-blur-sm">
                    <div class="flex flex-col items-center text-white">
                        <div class="animate-spin h-8 w-8 border-4 border-white border-t-transparent rounded-full mb-2"></div>
                        <span class="text-sm font-bold">Buscando melhor sala...</span>
                    </div>
                </div>
                <span class="text-5xl mb-4 group-hover:scale-110 transition-transform filter drop-shadow-md">🤖</span>
                <h3 class="text-2xl font-bold text-white">Check-in Inteligente</h3>
                <p class="text-blue-100 mt-2 text-sm">
                  O sistema encontra automaticamente a sala livre mais adequada para 
                  <strong v-if="especialidade" class="text-white underline decoration-wavy">{{ especialidade }}</strong>
                  <span v-else>sua especialidade</span>.
                </p>
            </div>

            <!-- Card Manual -->
            <div 
                @click="checkinMode = 'manual'; fetchSalasTempoReal()"
                class="group bg-white rounded-2xl p-8 cursor-pointer border-2 border-dashed border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-all h-48 flex flex-col items-center justify-center text-center"
            >
                <span class="text-5xl mb-4 text-gray-400 group-hover:text-blue-500 transition-colors">👆</span>
                <h3 class="text-2xl font-bold text-gray-700 group-hover:text-blue-700">Check-in Manual</h3>
                <p class="text-gray-500 mt-2 text-sm">Visualize a lista completa e escolha sua sala.</p>
            </div>
        </div>

        <!-- Modo Manual (Lista Ordenada) -->
        <div v-if="checkinMode === 'manual'" class="animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <button @click="checkinMode = null" class="text-gray-500 hover:text-blue-600 font-bold flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                    ← Voltar
                </button>
                <span class="text-sm text-gray-500 font-medium">{{ salasLivres.length }} salas livres</span>
            </div>

            <div v-if="isLoading" class="text-center py-12">
                <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3"></div>
                <p class="text-gray-500">Atualizando disponibilidade...</p>
            </div>

            <div v-else-if="salasLivres.length === 0" class="text-center py-12 bg-white rounded-xl border border-gray-200">
                <p class="text-3xl mb-2">🚫</p>
                <p class="text-gray-600 font-medium">Nenhuma sala livre encontrada neste momento.</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div 
                    v-for="sala in salasRecomendadas" 
                    :key="sala.sala_id"
                    class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition group relative overflow-hidden"
                    :class="{'border-blue-500 ring-1 ring-blue-500 bg-blue-50/30': isRecomendada(sala)}"
                >
                    <!-- Badge de Recomendação -->
                    <div v-if="isRecomendada(sala)" class="absolute top-0 right-0 bg-blue-500 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg shadow-sm z-10">
                        ⭐ RECOMENDADA
                    </div>

                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <span class="text-lg font-bold text-gray-800">{{ sala.nome }}</span>
                            <div class="text-xs text-gray-500 mt-1 flex flex-col gap-1">
                                <span>Bloco {{ sala.bloco }} • {{ formatAndar(sala.andar) }}</span>
                                <span v-if="sala.especialidade_preferencial" class="text-blue-700 bg-blue-50 px-1.5 rounded w-fit">
                                  Pref: {{ sala.especialidade_preferencial }}
                                </span>
                            </div>
                        </div>
                        <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded border border-green-200">LIVRE</span>
                    </div>
                    
                    <button 
                        @click="handleManualCheckin(sala.sala_id)"
                        class="w-full py-2.5 bg-white border border-blue-600 text-blue-700 rounded-lg text-sm font-bold hover:bg-blue-600 hover:text-white transition shadow-sm"
                    >
                        Ocupar esta Sala
                    </button>
                </div>
            </div>
        </div>

      </div>

      <!-- CONTEÚDO CHECKOUT -->
      <div v-if="currentTab === 'checkout'" class="animate-fade-in">
        <div v-if="isLoading" class="text-center py-10 text-gray-400">Carregando...</div>
        
        <div v-else-if="salasOcupadas.length === 0" class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
            <p class="text-gray-500">Nenhuma sala ocupada no momento.</p>
        </div>

        <div v-else class="space-y-3">
            <div v-for="sala in salasOcupadas" :key="sala.sala_id" class="bg-white p-4 rounded-xl border-l-4 border-l-red-500 shadow-sm flex justify-between items-center">
                <div>
                    <h3 class="font-bold text-gray-800">{{ sala.nome }}</h3>
                    <p class="text-sm text-gray-600">Ocupante: <strong class="text-gray-900">{{ sala.ocupante?.medico || 'Desconhecido' }}</strong></p>
                    <p class="text-xs text-gray-400">{{ sala.ocupante?.especialidade }}</p>
                </div>
                <button @click="handleCheckout(sala.sala_id)" class="px-4 py-2 bg-red-50 text-red-600 text-sm font-bold rounded-lg hover:bg-red-100 border border-red-100 transition">
                    Liberar
                </button>
            </div>
        </div>
      </div>

      <!-- CONTEÚDO HISTÓRICO -->
      <div v-if="currentTab === 'history'" class="animate-fade-in bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table class="w-full text-left text-sm">
              <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
                  <tr>
                      <th class="p-4">Data</th>
                      <th class="p-4">Sala</th>
                      <th class="p-4">Status</th>
                  </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in history" :key="item.id">
                      <td class="p-4">{{ item.date }} <br><span class="text-xs text-gray-400">{{ item.time }}</span></td>
                      <td class="p-4 font-bold text-blue-700">{{ item.room }}</td>
                      <td class="p-4">
                          <span class="px-2 py-1 rounded text-xs font-bold" :class="item.status === 'Ativo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
                              {{ item.status }}
                          </span>
                      </td>
                  </tr>
                  <tr v-if="history.length === 0">
                      <td colspan="3" class="p-6 text-center text-gray-400">Sem histórico recente.</td>
                  </tr>
              </tbody>
          </table>
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