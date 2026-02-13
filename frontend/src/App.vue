<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const auth = useAuthStore()

// Verifica se a rota atual pede para esconder o layout (ex: Login)
const showLayout = computed(() => !route.meta.hideLayout && auth.isAuthenticated)

// Helper para estilo do menu ativo
const isActive = (path: string) => route.path === path
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
    
    <!-- Navbar (Só aparece se estiver logado) -->
    <nav v-if="showLayout" class="bg-blue-800 text-white shadow-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="font-bold text-xl tracking-tight flex items-center gap-2">
            Gestão Dinâmica de Salas - HC UFPE
          </div>
          
          <div class="flex items-center gap-4">
            <div class="flex space-x-1">
              <router-link 
                to="/ocupacao"
                :class="isActive('/ocupacao') ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
                class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200 decoration-0"
              >
                Visão Geral
              </router-link>
              
              <router-link 
                to="/gestao"
                :class="isActive('/gestao') ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
                class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200 decoration-0"
              >
                Gestão
              </router-link>
              
              <router-link 
                to="/portal"
                :class="isActive('/portal') ? 'bg-blue-900 text-white shadow-inner' : 'text-blue-100 hover:bg-blue-700 hover:text-white'"
                class="px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-all duration-200 decoration-0"
              >
                Portal Médico
              </router-link>
            </div>

            <!-- Divisor -->
            <div class="h-6 w-px bg-blue-700/50"></div>

            <!-- Botão Sair -->
            <button 
              @click="auth.logout()"
              class="flex items-center gap-2 text-blue-200 hover:text-white text-sm font-medium px-3 py-2 rounded hover:bg-blue-700 transition cursor-pointer"
              title="Sair do Sistema"
            >
              <span>Sair</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <!-- Se for Login, ocupa a tela toda. Se não, usa margens padrão do dashboard -->
    <main :class="showLayout ? 'flex-1 w-full max-w-7xl mx-auto py-6 sm:px-6 lg:px-8' : 'flex-1 w-full'">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer (Só aparece se estiver logado) -->
    <footer v-if="showLayout" class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <p class="text-center text-gray-500 text-sm">
          © 2026 Hospital das Clínicas UFPE - Gestão Dinâmica de Salas
        </p>
      </div>
    </footer>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>