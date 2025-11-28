<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

// Interface dos dados que vêm do Dashboard
interface ResumoAmbulatorio {
  ambulatorio: string;
  total_salas: number;
  localizacao: string[];
  lista_salas: string[];
}

defineProps<{
  isOpen: boolean;
  data: ResumoAmbulatorio | null;
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

// Função de formatação de localização 
const formatLocation = (loc: string) => {
  const match = loc.match(/Bloco\s+(.+)\s+-\s+(\d+)/)
  if (match) {
    const bloco = match[1]
    const andar = match[2]
    const andarFormatado = andar === '0' ? 'Térreo' : `${andar}º Andar`
    return `Bloco ${bloco} - ${andarFormatado}`
  }
  return loc
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div v-if="isOpen && data" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity p-4">
    
    <div class="w-full max-w-2xl rounded-xl bg-white shadow-2xl overflow-hidden animate-scale-in">
      
      <div class="p-6 border-b border-gray-100">
        <div class="flex items-center justify-between mb-6">
          <div class="rounded-full bg-blue-50 px-4 py-1.5 text-sm font-bold text-blue-600">
            {{ data.ambulatorio }}
          </div>
          
          <div class="text-2xl font-bold text-gray-900">
            {{ data.total_salas }} <span class="text-sm font-normal text-gray-500">salas</span>
          </div>
        </div>

        <div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">LOCALIZAÇÃO</p>
          <ul class="text-sm text-gray-600 space-y-2">
            <li v-for="loc in data.localizacao" :key="loc" class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="font-medium">{{ formatLocation(loc) }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="flex justify-center -mt-3">
        <div class="bg-white p-1 rounded-full border border-gray-100 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <div class="p-6 bg-gray-50/50">
        <p class="text-sm font-semibold text-gray-600 mb-4">Salas Alocadas:</p>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <div 
            v-for="sala in data.lista_salas" 
            :key="sala"
            class="flex items-center justify-center rounded-lg border border-gray-200 bg-white py-2 px-3 text-sm font-medium text-gray-700 shadow-sm hover:border-blue-300 transition-colors cursor-default"
          >
            {{ sala }}
          </div>
        </div>
      </div>

      <div class="bg-gray-50 p-4 border-t border-gray-200 flex justify-end">
        <button 
          @click="handleClose"
          class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 transition"
        >
          Fechar
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>