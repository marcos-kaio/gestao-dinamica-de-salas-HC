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
  <div class="manager-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-text">
          <div class="header-badge">ADMIN</div>
          <h1 class="page-title">Painel de Gestão</h1>
          <p class="page-subtitle">Configure alocações e gerencie recursos do sistema</p>
        </div>
        
        <div class="header-actions">
          <button 
            @click="modalGestaoAberto = true" 
            class="action-btn secondary"
          >
            <span class="btn-icon">⚙️</span>
            <span class="btn-text">Gerenciar Dados</span>
          </button>

          <button 
            @click="gerarAlocacao" 
            :disabled="loading" 
            class="action-btn primary"
          >
            <span class="btn-icon">⚡</span>
            <span class="btn-text">{{ loading ? 'Calculando...' : 'Recalcular' }}</span>
            <div v-if="loading" class="btn-loader"></div>
          </button>
        </div>
      </div>
    </div>

    <!-- Grid de Ambulatórios -->
    <div v-if="alocacaoResumo.length > 0" class="ambulatorios-grid">
      <div 
        v-for="(item, index) in alocacaoResumo" 
        :key="item.ambulatorio"
        @click="abrirDetalhes(item)"
        class="ambulatorio-card"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <div class="card-header">
          <div class="card-top">
            <h3 class="card-title" :title="item.ambulatorio">{{ item.ambulatorio }}</h3>
            <div class="card-count">
              <span class="count-number">{{ item.total_salas }}</span>
              <span class="count-label">SALAS</span>
            </div>
          </div>
          
          <div class="location-tags">
            <span v-for="loc in item.localizacao" :key="loc" class="location-tag">
              📍 {{ loc }}
            </span>
          </div>
        </div>

        <div class="card-body">
          <div class="salas-preview">
            <div 
              v-for="sala in item.lista_salas.slice(0, 6)" 
              :key="sala" 
              class="sala-chip"
            >
              {{ sala }}
            </div>
            <div v-if="item.lista_salas.length > 6" class="sala-chip more">
              +{{ item.lista_salas.length - 6 }}
            </div>
          </div>
        </div>

        <div class="card-footer">
          <span class="footer-action">
            <span class="action-text">Editar Alocações</span>
            <span class="action-arrow">→</span>
          </span>
        </div>
        
        <div class="card-glow"></div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3 class="empty-title">Nenhuma alocação encontrada</h3>
      <p class="empty-text">Clique em "Gerenciar Dados" para importar uma grade</p>
      <button @click="modalGestaoAberto = true" class="empty-button">
        Começar Agora
      </button>
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
.manager-dashboard {
  animation: fade-in 0.5s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Header */
.dashboard-header {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 24px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.header-text {
  flex: 1;
}

.header-badge {
  display: inline-block;
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.page-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #fff 0%, rgba(148, 163, 184, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: rgba(148, 163, 184, 0.7);
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  font-family: 'Rajdhani', sans-serif;
}

.action-btn.secondary {
  background: rgba(30, 41, 59, 0.8);
  color: rgba(148, 163, 184, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.action-btn.secondary:hover {
  background: rgba(30, 41, 59, 1);
  color: white;
  border-color: rgba(14, 165, 233, 0.4);
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
}

.action-btn.primary {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border: 1px solid rgba(14, 165, 233, 0.5);
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3);
}

.action-btn.primary:hover:not(:disabled) {
  box-shadow: 0 6px 30px rgba(14, 165, 233, 0.5);
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-loader {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Grid */
.ambulatorios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.ambulatorio-card {
  position: relative;
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(14, 165, 233, 0.15);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: card-slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

@keyframes card-slide-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ambulatorio-card:hover {
  border-color: rgba(14, 165, 233, 0.4);
  box-shadow: 0 10px 40px rgba(14, 165, 233, 0.25);
  transform: translateY(-8px);
}

.ambulatorio-card:hover .card-glow {
  opacity: 0.3;
}

.card-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.2), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.card-header {
  background: rgba(15, 23, 42, 0.6);
  padding: 1.5rem;
  border-bottom: 1px solid rgba(14, 165, 233, 0.1);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.02em;
  line-height: 1.3;
  text-transform: uppercase;
  flex: 1;
}

.card-count {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(14, 165, 233, 0.15);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

.count-number {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0ea5e9;
}

.count-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.6);
  letter-spacing: 0.05em;
}

.location-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.location-tag {
  background: rgba(6, 182, 212, 0.15);
  color: rgba(6, 182, 212, 0.9);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(6, 182, 212, 0.2);
}

.card-body {
  padding: 1.25rem;
}

.salas-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sala-chip {
  background: rgba(15, 23, 42, 0.6);
  color: rgba(148, 163, 184, 0.9);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.sala-chip.more {
  background: rgba(14, 165, 233, 0.15);
  color: rgba(14, 165, 233, 0.9);
  border-color: rgba(14, 165, 233, 0.3);
  font-family: 'Orbitron', sans-serif;
}

.card-footer {
  padding: 1rem 1.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-top: 1px solid rgba(14, 165, 233, 0.1);
}

.footer-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(14, 165, 233, 0.9);
  font-weight: 600;
  font-size: 0.9rem;
}

.action-arrow {
  font-size: 1.2rem;
  transition: transform 0.3s;
}

.ambulatorio-card:hover .action-arrow {
  transform: translateX(4px);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
}

.empty-text {
  color: rgba(148, 163, 184, 0.7);
  margin-bottom: 2rem;
}

.empty-button {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3);
}

.empty-button:hover {
  box-shadow: 0 6px 30px rgba(14, 165, 233, 0.5);
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .ambulatorios-grid {
    grid-template-columns: 1fr;
  }
}
</style>