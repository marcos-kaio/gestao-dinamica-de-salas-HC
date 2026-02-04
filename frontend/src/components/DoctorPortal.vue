<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

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

const normalizarEspecialidade = (texto: string): string => {
  if (!texto) return ""
  const upper = texto.toUpperCase().trim()
  return mapaSinonimos[upper] || upper
}

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
  <div class="doctor-portal">
    <!-- Header -->
    <div class="portal-header">
      <div class="header-badge">MÉDICO</div>
      <h1 class="page-title">Portal do Profissional</h1>
      <p class="page-subtitle">Sistema de Check-in Inteligente</p>
    </div>

    <!-- Identificação -->
    <div class="identification-card">
      <div class="card-icon">👨‍⚕️</div>
      <h2 class="card-title">IDENTIFICAÇÃO OBRIGATÓRIA</h2>
      
      <div class="input-grid">
        <div class="input-wrapper">
          <label class="input-label">Seu Nome</label>
          <input 
            v-model="medicoNome" 
            type="text" 
            placeholder="Ex: Dr. Carlos Silva" 
            class="custom-input"
          >
        </div>
        
        <div class="input-wrapper">
          <label class="input-label">Especialidade</label>
          <select v-model="especialidade" class="custom-select">
            <option value="" disabled selected>Selecione...</option>
            <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">
              {{ esp }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Feedback Message -->
    <transition name="slide-down">
      <div v-if="message" :class="['message-banner', message.type]">
        <span class="message-text">{{ message.text }}</span>
        <button @click="message = null" class="message-close">✕</button>
      </div>
    </transition>

    <!-- Tabs -->
    <div class="tabs-container">
      <button 
        @click="currentTab = 'checkin'; checkinMode = null; fetchSalasTempoReal()" 
        :class="['tab-button', currentTab === 'checkin' && 'active']"
      >
        <span class="tab-icon">➕</span>
        <span class="tab-text">Check-in</span>
      </button>
      
      <button 
        @click="currentTab = 'checkout'; fetchSalasTempoReal()" 
        :class="['tab-button', currentTab === 'checkout' && 'active']"
      >
        <span class="tab-icon">🚪</span>
        <span class="tab-text">Checkout</span>
      </button>
    </div>

    <!-- Check-in Content -->
    <div v-if="currentTab === 'checkin'" class="tab-content">
      <div v-if="!checkinMode" class="mode-selection">
        <div @click="handleSmartCheckin" class="mode-card smart">
          <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
          </div>
          <div class="mode-icon">🤖</div>
          <h3 class="mode-title">Check-in Inteligente</h3>
          <p class="mode-description">
            Alocação automática para {{ especialidade || 'sua especialidade' }}
          </p>
        </div>

        <div @click="checkinMode = 'manual'; fetchSalasTempoReal()" class="mode-card manual">
          <div class="mode-icon">👆</div>
          <h3 class="mode-title">Check-in Manual</h3>
          <p class="mode-description">Escolha sua sala na lista</p>
        </div>
      </div>

      <div v-if="checkinMode === 'manual'" class="manual-selection">
        <div class="selection-header">
          <button @click="checkinMode = null" class="back-button">
            ← Voltar
          </button>
          <span class="available-count">{{ salasLivres.length }} salas livres</span>
        </div>

        <div v-if="isLoading" class="loading-text">Carregando...</div>
        <div v-else-if="salasLivres.length === 0" class="no-rooms">
          🚫 Nenhuma sala livre no momento
        </div>
        
        <div v-else class="salas-grid">
          <div 
            v-for="sala in salasRecomendadas" 
            :key="sala.sala_id" 
            :class="['sala-card', isRecomendada(sala) && 'recommended']"
          >
            <div v-if="isRecomendada(sala)" class="recommended-badge">⭐ RECOMENDADA</div>
            
            <div class="sala-header">
              <div class="sala-info">
                <span class="sala-name">{{ sala.nome }}</span>
                <span class="sala-location">
                  Bloco {{ sala.bloco }} • {{ formatAndar(sala.andar) }}
                </span>
                <span v-if="sala.especialidade_preferencial" class="sala-specialty">
                  {{ sala.especialidade_preferencial }}
                </span>
              </div>
              <div class="status-badge available">LIVRE</div>
            </div>

            <button @click="handleManualCheckin(sala.sala_id)" class="select-button">
              Ocupar esta Sala
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Checkout Content -->
    <div v-if="currentTab === 'checkout'" class="tab-content">
      <div v-if="isLoading" class="loading-text">Carregando...</div>
      <div v-else-if="salasOcupadas.length === 0" class="no-rooms">
        Nenhuma sala ocupada no momento
      </div>
      
      <div v-else class="occupied-list">
        <div v-for="sala in salasOcupadas" :key="sala.sala_id" class="occupied-card">
          <div class="occupied-info">
            <h3 class="occupied-name">{{ sala.nome }}</h3>
            <p class="occupied-doctor">
              Ocupante: <strong>{{ sala.ocupante?.medico || 'Desconhecido' }}</strong>
            </p>
            <p class="occupied-specialty">{{ sala.ocupante?.especialidade }}</p>
          </div>
          
          <button @click="handleCheckout(sala.sala_id)" class="checkout-button">
            Liberar Sala
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.doctor-portal {
  max-width: 1200px;
  margin: 0 auto;
  animation: fade-in 0.5s ease-out;
}

/* Header */
.portal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-badge {
  display: inline-block;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.page-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, rgba(148, 163, 184, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: rgba(148, 163, 184, 0.7);
  font-size: 1rem;
}

/* Identification Card */
.identification-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: rgba(148, 163, 184, 0.8);
  margin-bottom: 1.5rem;
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.9);
}

.custom-input,
.custom-select {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 0.9rem 1.2rem;
  color: white;
  font-size: 1rem;
  transition: all 0.3s;
  font-family: 'Rajdhani', sans-serif;
}

.custom-input:focus,
.custom-select:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.custom-select {
  cursor: pointer;
}

/* Message Banner */
.message-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: 14px;
  margin-bottom: 2rem;
  font-weight: 600;
  animation: slide-down 0.3s ease-out;
}

.message-banner.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.message-banner.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.message-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.message-close:hover {
  opacity: 1;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 1rem;
  background: rgba(30, 41, 59, 0.6);
  padding: 0.75rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: rgba(148, 163, 184, 0.7);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-button:hover {
  background: rgba(148, 163, 184, 0.05);
  color: white;
}

.tab-button.active {
  background: rgba(14, 165, 233, 0.15);
  color: white;
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
}

.tab-icon {
  font-size: 1.3rem;
}

/* Mode Selection */
.mode-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.mode-card {
  position: relative;
  padding: 3rem 2rem;
  border-radius: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.mode-card.smart {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%);
  border: 2px solid rgba(14, 165, 233, 0.4);
}

.mode-card.manual {
  background: rgba(30, 41, 59, 0.6);
  border: 2px dashed rgba(148, 163, 184, 0.3);
}

.mode-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}

.mode-card.smart:hover {
  border-color: rgba(14, 165, 233, 0.6);
  box-shadow: 0 20px 50px rgba(14, 165, 233, 0.3);
}

.mode-card.manual:hover {
  border-color: rgba(148, 163, 184, 0.5);
  background: rgba(30, 41, 59, 0.8);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(14, 165, 233, 0.3);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.mode-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.mode-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
}

.mode-description {
  color: rgba(148, 163, 184, 0.8);
  font-size: 0.95rem;
}

/* Manual Selection */
.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-button {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: rgba(148, 163, 184, 0.9);
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(30, 41, 59, 1);
  border-color: rgba(14, 165, 233, 0.4);
  color: white;
}

.available-count {
  color: rgba(148, 163, 184, 0.8);
  font-weight: 600;
}

.salas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.sala-card {
  position: relative;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.sala-card.recommended {
  border-color: rgba(14, 165, 233, 0.5);
  background: rgba(14, 165, 233, 0.08);
}

.sala-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.recommended-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.4rem 0.8rem;
  border-radius: 0 16px 0 12px;
}

.sala-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.sala-info {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.sala-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
}

.sala-location {
  font-size: 0.85rem;
  color: rgba(148, 163, 184, 0.7);
}

.sala-specialty {
  font-size: 0.8rem;
  color: rgba(6, 182, 212, 0.9);
  background: rgba(6, 182, 212, 0.15);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  width: fit-content;
}

.status-badge {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-badge.available {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.select-button {
  width: 100%;
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(14, 165, 233, 0.4);
  color: #0ea5e9;
  padding: 1rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.select-button:hover {
  background: linear-gradient(135deg, #0ea5e9, #06b6d4);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
}

/* Occupied List */
.occupied-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.occupied-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.6);
  border-left: 4px solid #ef4444;
  border-radius: 16px;
  padding: 1.5rem;
  gap: 2rem;
}

.occupied-info {
  flex: 1;
}

.occupied-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.occupied-doctor {
  color: rgba(148, 163, 184, 0.8);
  margin-bottom: 0.25rem;
}

.occupied-doctor strong {
  color: white;
}

.occupied-specialty {
  color: rgba(148, 163, 184, 0.6);
  font-size: 0.9rem;
}

.checkout-button {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 0.9rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.checkout-button:hover {
  background: #ef4444;
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

/* Utilities */
.loading-text {
  text-align: center;
  padding: 3rem;
  color: rgba(148, 163, 184, 0.7);
  font-size: 1.1rem;
}

.no-rooms {
  text-align: center;
  padding: 4rem;
  font-size: 1.2rem;
  color: rgba(148, 163, 184, 0.6);
  background: rgba(30, 41, 59, 0.4);
  border: 1px dashed rgba(148, 163, 184, 0.2);
  border-radius: 16px;
}

/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .input-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs-container {
    flex-direction: column;
  }
  
  .mode-selection {
    grid-template-columns: 1fr;
  }
  
  .occupied-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .checkout-button {
    width: 100%;
  }
}
</style>