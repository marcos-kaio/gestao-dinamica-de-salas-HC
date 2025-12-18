<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface SalaStatus {
  id: string;
  numero: string;
  status: 'LIVRE' | 'OCUPADA' | 'MANUTENCAO';
  ocupante: string | null;
  horario: string | null;
  andar: string;
  bloco: string;
  especialidade_original?: string;
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
  <div v-if="isOpen && data" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="handleClose"></div>
    
    <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-scale-in border border-slate-200">
      
      <!-- Cabeçalho Roxo/Indigo para Diferenciar do Gestor -->
      <div class="bg-indigo-600 p-6 text-white flex justify-between items-start shrink-0 relative overflow-hidden">
        <svg class="absolute -right-6 -bottom-8 w-32 h-32 text-white/10 pointer-events-none" fill="currentColor" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
        <div class="relative z-10">
          <span class="block text-indigo-200 text-xs font-bold uppercase tracking-wider mb-1">Status em Tempo Real</span>
          <h2 class="text-2xl font-bold leading-tight">{{ data.ambulatorio }}</h2>
        </div>
        <button @click="handleClose" class="relative z-10 text-white/70 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="bg-slate-50 px-6 py-3 border-b border-slate-200 flex items-center justify-between shrink-0">
        <div class="flex gap-4">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-red-500"></span> <span class="text-xs font-bold text-slate-600">Ocupado</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span> <span class="text-xs font-bold text-slate-600">Livre</span>
          </div>
        </div>
        <div class="text-xs font-bold text-slate-500 uppercase">{{ data.salas_ocupadas }} / {{ data.total_salas }} Salas em Uso</div>
      </div>

      <div class="p-6 overflow-y-auto bg-slate-50/50">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <div v-for="sala in data.lista_salas_detalhada" :key="sala.id" class="bg-white rounded-lg border shadow-sm p-4 flex flex-col relative overflow-hidden transition-all" :class="sala.status === 'OCUPADA' ? 'border-red-200' : 'border-emerald-200'">
            
            <div class="absolute top-0 left-0 w-1 h-full" :class="sala.status === 'OCUPADA' ? 'bg-red-500' : 'bg-emerald-500'"></div>
            
            <div class="flex justify-between items-start mb-2 pl-3">
              <span class="text-lg font-bold text-slate-800">{{ sala.numero }}</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wide" :class="sala.status === 'OCUPADA' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'">
                {{ sala.status === 'OCUPADA' ? 'Ocupada' : 'Livre' }}
              </span>
            </div>

            <div class="pl-3 mt-auto">
              <div v-if="sala.status === 'OCUPADA'" class="text-xs text-slate-600">
                <span class="block text-slate-400 text-[9px] uppercase font-bold">Responsável</span>
                <span class="font-semibold">{{ sala.ocupante || 'Não informado' }}</span>
              </div>
              <div v-else class="text-xs text-slate-400 italic">Disponível para alocação</div>
              
              <div class="mt-3 pt-2 border-t border-slate-50 flex items-center text-[10px] text-slate-400 font-medium">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                Bloco {{ sala.bloco }} • {{ sala.andar }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white p-4 border-t border-slate-200 flex justify-end shrink-0">
        <button @click="handleClose" class="px-5 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 text-sm font-medium hover:bg-slate-50 transition-colors">Fechar Monitoramento</button>
      </div>
    </div>
  </div>
</template>