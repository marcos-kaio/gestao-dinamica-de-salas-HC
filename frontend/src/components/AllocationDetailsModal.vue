<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

// 1. Atualizar a Interface para casar com o Dashboard
interface SalaStatus {
  id: string;
  numero: string;
  status: 'LIVRE' | 'OCUPADA' | 'MANUTENCAO'; // Adicionado MANUTENCAO
  ocupante: string | null;
  horario: string | null;
  andar: string;
  bloco: string;
  especialidade_original?: string; // Opcional, para evitar erros se não vier
}

interface ResumoAmbulatorio {
  ambulatorio: string;
  total_salas: number;
  salas_ocupadas: number;
  localizacao: string[];
  lista_salas_detalhada: SalaStatus[];
}

defineProps<{
  isOpen: boolean;
  data: ResumoAmbulatorio | null;
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div v-if="isOpen && data" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity p-4">
    
    <div class="w-full max-w-4xl rounded-xl bg-white shadow-2xl overflow-hidden animate-scale-in flex flex-col max-h-[90vh]">
      
      <div class="p-6 border-b border-gray-100 shrink-0">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-3">
             <div class="rounded-full bg-blue-50 px-4 py-1.5 text-sm font-bold text-blue-600">
                {{ data.ambulatorio }}
             </div>
             <span class="text-sm text-gray-500">{{ data.salas_ocupadas }} ocupadas de {{ data.total_salas }} totais</span>
          </div>
          <button @click="handleClose" class="text-gray-400 hover:text-gray-600 transition cursor-pointer">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>

      <div class="p-6 bg-gray-50/50 overflow-y-auto">
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <div 
            v-for="sala in data.lista_salas_detalhada" 
            :key="sala.id"
            class="flex flex-col p-4 rounded-lg border shadow-sm transition-all"
            :class="{
              'bg-white border-red-200 shadow-red-100': sala.status === 'OCUPADA',
              'bg-white border-green-200 shadow-green-50': sala.status === 'LIVRE',
              'bg-gray-100 border-gray-300 opacity-80': sala.status === 'MANUTENCAO'
            }"
          >
            <div class="flex justify-between items-start mb-2">
                <span class="font-bold text-lg text-gray-800">{{ sala.numero }}</span>
                
                <span 
                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide"
                    :class="{
                      'bg-red-100 text-red-700': sala.status === 'OCUPADA',
                      'bg-green-100 text-green-700': sala.status === 'LIVRE',
                      'bg-gray-200 text-gray-600': sala.status === 'MANUTENCAO'
                    }"
                >
                    {{ sala.status }}
                </span>
            </div>

            <div class="text-sm">
                <div v-if="sala.status === 'OCUPADA'" class="text-gray-700">
                    <p class="font-semibold text-red-600 truncate" :title="sala.ocupante || ''">
                        👤 {{ sala.ocupante || 'Médico' }}
                    </p>
                    <p class="text-xs text-gray-400 mt-1">Check-in às {{ sala.horario }}</p>
                </div>
                <div v-else-if="sala.status === 'MANUTENCAO'" class="text-gray-500 italic flex items-center gap-1">
                    🚧 Em Manutenção
                </div>
                <div v-else class="text-gray-400 italic">
                    Disponível
                </div>
            </div>

            <div class="mt-3 pt-2 border-t border-gray-100 text-xs text-gray-400 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                Bloco {{ sala.bloco }} - {{ sala.andar }}
            </div>
          </div>
        </div>

      </div>

      <div class="bg-gray-50 p-4 border-t border-gray-200 flex justify-end">
        <button 
          @click="handleClose"
          class="rounded-lg border border-gray-300 bg-white px-6 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition cursor-pointer"
        >
          Fechar Detalhes
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