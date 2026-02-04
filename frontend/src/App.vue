<script setup lang="ts">
import { ref } from 'vue'
import OccupancyDashboard from './components/OccupancyDashboard.vue'
import ManagerDashboard from './components/ManagerDashboard.vue'
import DoctorPortal from './components/DoctorPortal.vue'

const currentView = ref('dashboard')
</script>

<template>
  <div class="app-container">
    <!-- Animated Background -->
    <div class="bg-pattern"></div>
    <div class="gradient-overlay"></div>
    
    <!-- Navbar -->
    <nav class="nav-container">
      <div class="nav-content">
        <div class="nav-brand">
          <div class="pulse-indicator"></div>
          <div class="brand-text">
            <span class="brand-primary">HC UFPE</span>
            <span class="brand-secondary">Sistema de Gestão Inteligente</span>
          </div>
        </div>
        
        <div class="nav-tabs">
          <button 
            @click="currentView = 'dashboard'"
            :class="['nav-tab', currentView === 'dashboard' && 'active']"
          >
            <span class="tab-icon">📊</span>
            <span class="tab-label">Dashboard</span>
            <div v-if="currentView === 'dashboard'" class="tab-indicator"></div>
          </button>
          
          <button 
            @click="currentView = 'manager'"
            :class="['nav-tab', currentView === 'manager' && 'active']"
          >
            <span class="tab-icon">⚙️</span>
            <span class="tab-label">Gestão</span>
            <div v-if="currentView === 'manager'" class="tab-indicator"></div>
          </button>
          
          <button 
            @click="currentView = 'portal'"
            :class="['nav-tab', currentView === 'portal' && 'active']"
          >
            <span class="tab-icon">👨‍⚕️</span>
            <span class="tab-label">Portal Médico</span>
            <div v-if="currentView === 'portal'" class="tab-indicator"></div>
          </button>
        </div>
      </div>
    </nav>

    <!-- Content with Smooth Transitions -->
    <main class="main-content">
      <transition name="view-transition" mode="out-in">
        <OccupancyDashboard v-if="currentView === 'dashboard'" key="dashboard" />
        <ManagerDashboard v-else-if="currentView === 'manager'" key="manager" />
        <DoctorPortal v-else key="portal" />
      </transition>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <span class="footer-text">Hospital das Clínicas UFPE © 2026</span>
        <div class="footer-status">
          <span class="status-dot"></span>
          <span class="status-text">Sistema Online</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
  --electric-blue: #0ea5e9;
  --medical-cyan: #06b6d4;
  --deep-navy: #0f172a;
  --soft-slate: #1e293b;
  --medical-green: #10b981;
  --warning-amber: #f59e0b;
  --danger-red: #ef4444;
}

.app-container {
  min-height: 100vh;
  background: var(--deep-navy);
  position: relative;
  overflow-x: hidden;
  font-family: 'Rajdhani', sans-serif;
}

/* Animated Background Pattern */
.bg-pattern {
  position: fixed;
  inset: 0;
  background-image: 
    repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(14, 165, 233, 0.03) 2px, rgba(14, 165, 233, 0.03) 4px),
    repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(6, 182, 212, 0.03) 2px, rgba(6, 182, 212, 0.03) 4px);
  animation: grid-flow 20s linear infinite;
  pointer-events: none;
  z-index: 0;
}

.gradient-overlay {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 20% 50%, rgba(14, 165, 233, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.08) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

@keyframes grid-flow {
  0% { transform: translate(0, 0); }
  100% { transform: translate(4px, 4px); }
}

/* Navigation */
.nav-container {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(14, 165, 233, 0.2);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3),
              0 0 0 1px rgba(14, 165, 233, 0.1);
}

.nav-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pulse-indicator {
  width: 12px;
  height: 12px;
  background: var(--medical-cyan);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 0 20px var(--medical-cyan);
  animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-ring {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.brand-primary {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.05em;
}

.brand-secondary {
  font-size: 0.75rem;
  color: rgba(148, 163, 184, 0.8);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* Navigation Tabs */
.nav-tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(30, 41, 59, 0.5);
  padding: 0.5rem;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.nav-tab {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: rgba(148, 163, 184, 0.7);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.nav-tab:hover {
  color: rgba(148, 163, 184, 1);
  background: rgba(148, 163, 184, 0.05);
}

.nav-tab.active {
  color: white;
  background: rgba(14, 165, 233, 0.15);
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.3),
              inset 0 0 20px rgba(14, 165, 233, 0.1);
}

.tab-icon {
  font-size: 1.2rem;
  filter: grayscale(0.3);
  transition: filter 0.3s;
}

.nav-tab.active .tab-icon {
  filter: grayscale(0);
}

.tab-label {
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.05em;
}

.tab-indicator {
  position: absolute;
  bottom: -0.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: 30%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--electric-blue), transparent);
  animation: indicator-pulse 2s ease-in-out infinite;
}

@keyframes indicator-pulse {
  0%, 100% { opacity: 0.5; width: 30%; }
  50% { opacity: 1; width: 60%; }
}

/* Main Content */
.main-content {
  position: relative;
  z-index: 1;
  min-height: calc(100vh - 180px);
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
}

/* View Transitions */
.view-transition-enter-active,
.view-transition-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-transition-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.view-transition-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.98);
}

/* Footer */
.footer {
  position: relative;
  z-index: 1;
  background: rgba(15, 23, 42, 0.8);
  border-top: 1px solid rgba(14, 165, 233, 0.1);
  backdrop-filter: blur(10px);
}

.footer-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-text {
  color: rgba(148, 163, 184, 0.6);
  font-size: 0.875rem;
  font-weight: 500;
}

.footer-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--medical-green);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--medical-green);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  color: rgba(148, 163, 184, 0.8);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-content {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .nav-tabs {
    width: 100%;
    flex-direction: column;
  }
  
  .nav-tab {
    justify-content: center;
  }
  
  .brand-secondary {
    display: none;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>