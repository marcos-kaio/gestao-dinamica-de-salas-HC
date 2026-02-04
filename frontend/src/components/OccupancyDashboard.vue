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

const ambulatoriosAgrupados = computed(() => {
  if (!dadosTempoReal.value) return []
  
  const grupos: Record<string, any> = {}
  
  dadosTempoReal.value.salas.forEach((sala: any) => {
    let chave = "Disponíveis / Outros"
    if (sala.status === 'OCUPADA' && sala.ocupante) {
      chave = sala.ocupante.especialidade || "Alocação Geral"
    } else if (sala.status === 'MANUTENCAO') {
      chave = "Manutenção"
    } else {
        chave = "Salas Disponíveis"
    }

    if (!grupos[chave]) {
      grupos[chave] = { nome: chave, salas: [], total: 0, ocupadas: 0 }
    }
    
    grupos[chave].salas.push(sala)
    grupos[chave].total++
    if (sala.status === 'OCUPADA') grupos[chave].ocupadas++
  })

  return Object.values(grupos).sort((a: any, b: any) => {
      if(a.nome === 'Salas Disponíveis') return -1
      return a.nome.localeCompare(b.nome)
  })
})

onMounted(() => {
  fetchDashboardRealTime()
  intervalo = setInterval(fetchDashboardRealTime, 30000)
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
})
</script>

<template>
  <div class="dashboard">
    <!-- Header com Estatísticas -->
    <div class="dashboard-header">
      <div class="header-info">
        <div class="live-indicator">
          <span class="live-dot"></span>
          <span class="live-text">MONITORAMENTO AO VIVO</span>
        </div>
        <h1 class="dashboard-title">Mapa em Tempo Real</h1>
        <p v-if="dadosTempoReal" class="dashboard-subtitle">
          <span class="time-badge">{{ dadosTempoReal.tempo.dia }}</span>
          <span class="divider">•</span>
          <span class="time-badge">{{ dadosTempoReal.tempo.turno }}</span>
          <span class="divider">•</span>
          <span class="time-info">{{ dadosTempoReal.tempo.hora_legivel }}</span>
        </p>
      </div>
      
      <div v-if="dadosTempoReal" class="stats-container">
        <div class="stat-card available">
          <div class="stat-icon">✓</div>
          <div class="stat-content">
            <span class="stat-label">Livres</span>
            <span class="stat-value">{{ dadosTempoReal.estatisticas.livres }}</span>
          </div>
          <div class="stat-glow"></div>
        </div>
        
        <div class="stat-card occupied">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <span class="stat-label">Ocupadas</span>
            <span class="stat-value">{{ dadosTempoReal.estatisticas.ocupadas }}</span>
          </div>
          <div class="stat-glow"></div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loader">
        <div class="loader-ring"></div>
        <div class="loader-ring"></div>
        <div class="loader-ring"></div>
      </div>
      <p class="loading-text">Sincronizando com o hospital...</p>
    </div>

    <!-- Grid de Ambulatórios -->
    <div v-else class="ambulatorios-grid">
      <div 
        v-for="(grupo, index) in ambulatoriosAgrupados" 
        :key="grupo.nome"
        class="ambulatorio-card"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <div class="card-header">
          <div class="card-title-wrapper">
            <h3 class="card-title" :title="grupo.nome">{{ grupo.nome }}</h3>
            <div class="card-badge">
              <span class="badge-count">{{ grupo.salas.length }}</span>
              <span class="badge-label">SALAS</span>
            </div>
          </div>
          <div class="occupancy-indicator">
            <div class="occupancy-bar">
              <div 
                class="occupancy-fill" 
                :style="{ width: `${(grupo.ocupadas / grupo.total) * 100}%` }"
              ></div>
            </div>
            <span class="occupancy-text">{{ grupo.ocupadas }}/{{ grupo.total }}</span>
          </div>
        </div>

        <div class="salas-list">
          <div 
            v-for="sala in grupo.salas" 
            :key="sala.sala_id" 
            :class="['sala-item', `status-${sala.status.toLowerCase()}`]"
          >
            <div class="sala-status-indicator"></div>
            <div class="sala-info">
              <span class="sala-nome">{{ sala.nome }}</span>
              <span v-if="sala.status === 'OCUPADA'" class="sala-ocupante">
                {{ sala.ocupante.medico }}
              </span>
              <span v-else class="sala-status">{{ sala.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  animation: fade-slide-in 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fade-slide-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header */
.dashboard-header {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 24px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3),
              0 0 0 1px rgba(14, 165, 233, 0.1),
              inset 0 1px 0 rgba(148, 163, 184, 0.1);
}

.header-info {
  flex: 1;
}

.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.live-dot {
  width: 10px;
  height: 10px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 20px #10b981;
  animation: pulse-dot 2s ease-in-out infinite;
}

.live-text {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: rgba(16, 185, 129, 0.9);
  text-transform: uppercase;
}

.dashboard-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, rgba(148, 163, 184, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.dashboard-subtitle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(148, 163, 184, 0.7);
  font-size: 0.9rem;
}

.time-badge {
  background: rgba(14, 165, 233, 0.15);
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  color: rgba(14, 165, 233, 0.9);
}

.divider {
  color: rgba(148, 163, 184, 0.3);
}

.time-info {
  font-weight: 500;
}

/* Stats Cards */
.stats-container {
  display: flex;
  gap: 1rem;
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 16px;
  border: 1px solid;
  background: rgba(30, 41, 59, 0.5);
  backdrop-filter: blur(10px);
  min-width: 150px;
  overflow: hidden;
}

.stat-card.available {
  border-color: rgba(16, 185, 129, 0.3);
}

.stat-card.occupied {
  border-color: rgba(239, 68, 68, 0.3);
}

.stat-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 10px currentColor);
}

.stat-card.available .stat-icon {
  color: #10b981;
}

.stat-card.occupied .stat-icon {
  color: #ef4444;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.7);
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
}

.stat-glow {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  border-radius: 16px;
  transition: opacity 0.3s;
}

.stat-card.available .stat-glow {
  background: radial-gradient(circle at center, #10b981 0%, transparent 70%);
}

.stat-card.occupied .stat-glow {
  background: radial-gradient(circle at center, #ef4444 0%, transparent 70%);
}

.stat-card:hover .stat-glow {
  opacity: 0.2;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem;
  gap: 2rem;
}

.loader {
  position: relative;
  width: 80px;
  height: 80px;
}

.loader-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 1.5s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.loader-ring:nth-child(2) {
  animation-delay: -0.3s;
  border-top-color: #06b6d4;
}

.loader-ring:nth-child(3) {
  animation-delay: -0.6s;
  border-top-color: #10b981;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: rgba(148, 163, 184, 0.7);
  font-size: 1rem;
  font-weight: 600;
}

/* Grid de Ambulatórios */
.ambulatorios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.ambulatorio-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.15);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: card-appear 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

@keyframes card-appear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.ambulatorio-card:hover {
  border-color: rgba(14, 165, 233, 0.4);
  box-shadow: 0 8px 30px rgba(14, 165, 233, 0.2),
              0 0 0 1px rgba(14, 165, 233, 0.2);
  transform: translateY(-4px);
}

.card-header {
  background: rgba(15, 23, 42, 0.6);
  padding: 1.25rem;
  border-bottom: 1px solid rgba(14, 165, 233, 0.1);
}

.card-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  line-height: 1.3;
  flex: 1;
}

.card-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(14, 165, 233, 0.15);
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

.badge-count {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0ea5e9;
}

.badge-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.6);
  letter-spacing: 0.05em;
}

.occupancy-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.occupancy-bar {
  flex: 1;
  height: 6px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.occupancy-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #06b6d4);
  border-radius: 10px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(14, 165, 233, 0.5);
}

.occupancy-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.8);
  font-family: 'Orbitron', sans-serif;
}

/* Lista de Salas */
.salas-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
}

.salas-list::-webkit-scrollbar {
  width: 6px;
}

.salas-list::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 10px;
}

.salas-list::-webkit-scrollbar-thumb {
  background: rgba(14, 165, 233, 0.3);
  border-radius: 10px;
}

.salas-list::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

.sala-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid;
  transition: all 0.2s;
}

.sala-item.status-livre {
  border-color: rgba(16, 185, 129, 0.2);
}

.sala-item.status-ocupada {
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.05);
}

.sala-item.status-manutencao {
  border-color: rgba(245, 158, 11, 0.2);
  opacity: 0.7;
}

.sala-status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-livre .sala-status-indicator {
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}

.status-ocupada .sala-status-indicator {
  background: #ef4444;
  box-shadow: 0 0 10px #ef4444;
}

.status-manutencao .sala-status-indicator {
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b;
}

.sala-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  flex: 1;
  min-width: 0;
}

.sala-nome {
  font-weight: 700;
  font-size: 0.9rem;
  color: white;
}

.sala-ocupante {
  font-size: 0.8rem;
  color: rgba(239, 68, 68, 0.9);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sala-status {
  font-size: 0.75rem;
  color: rgba(148, 163, 184, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
  }
  
  .stats-container {
    width: 100%;
    justify-content: space-between;
  }
  
  .ambulatorios-grid {
    grid-template-columns: 1fr;
  }
}
</style>