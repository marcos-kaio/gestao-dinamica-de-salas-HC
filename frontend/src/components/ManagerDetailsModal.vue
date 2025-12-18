<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

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

const formatLocation = (loc: string) => {
  const match = loc.match(/Bloco\s+(.+)\s+-\s+(\d+)/)
  if (match) {
    return `Bloco ${match[1]} • ${match[2] === '0' ? 'Térreo' : match[2] + 'º Andar'}`
  }
  return loc
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div v-if="isOpen && data" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="handleClose"></div>
    <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-scale-in border border-slate-200">
      <div class="bg-[#003B71] p-6 text-white flex justify-between items-start shrink-0 relative overflow-hidden">
        <svg class="absolute -right-6 -bottom-8 w-32 h-32 text-white/5 pointer-events-none" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8.5 12H9v-2.5H6.5v-1.5H9V8.5h1.5v2.5h2.5v1.5h-2.5V15z"/></svg>
        <div class="relative z-10 pr-8">
          <span class="block text-blue-200 text-xs font-bold uppercase tracking-wider mb-1">Especialidade</span>
          <h2 class="text-2xl font-bold leading-tight">{{ data.ambulatorio }}</h2>
        </div>
        <button @click="handleClose" class="relative z-10 text-white/70 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      <div class="bg-slate-50 px-6 py-3 border-b border-slate-200 flex items-center gap-3 shrink-0">
        <span class="text-xs font-bold text-slate-500 uppercase tracking-wide">Total Alocado:</span>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-[#003B71] border border-blue-200">{{ data.total_salas ?? 0 }} salas</span>
      </div>
      <div class="p-6 overflow-y-auto">
        <div class="mb-8">
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg> Localização Principal
          </h4>
          <div class="flex flex-wrap gap-2">
            <div v-for="loc in data.localizacao" :key="loc" class="flex items-center bg-white border border-slate-200 px-3 py-2 rounded-lg text-sm text-slate-700 shadow-sm">
              <span class="w-1.5 h-1.5 rounded-full bg-[#003B71] mr-2"></span> {{ formatLocation(loc) }}
            </div>
          </div>
        </div>
        <div>
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg> Salas Vinculadas
          </h4>
          <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            <div v-for="sala in data.lista_salas" :key="sala" class="flex items-center justify-center py-2.5 px-1 bg-white border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:border-[#003B71] hover:text-[#003B71] hover:bg-blue-50 transition-all cursor-default shadow-sm">{{ sala }}</div>
          </div>
        </div>
      </div>
      <div class="bg-slate-50 p-4 border-t border-slate-200 flex justify-end shrink-0">
        <button @click="handleClose" class="px-5 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 text-sm font-medium hover:bg-slate-100 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-200">Fechar</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-scale-in { animation: scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.96) translateY(8px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>