<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps<{
  show: boolean;
  allocation: any; 
  todasSalas: any[];
}>();

const emit = defineEmits(['close', 'confirm']);

const novaSalaId = ref("");
const motivo = ref("");
const loading = ref(false);

watch(() => props.show, (val) => {
  if (val) {
    novaSalaId.value = props.allocation?.sala_id || "";
    motivo.value = "";
    loading.value = false;
  }
});

const salasAgrupadas = computed(() => {
  const grupos: Record<string, any[]> = {};
  if (!props.todasSalas) return {};
  
  props.todasSalas.forEach(sala => {
    // Cria o nome do grupo: "Bloco A - 2º Andar"
    const key = `Bloco ${sala.bloco} - ${sala.andar}º Andar`;
    if (!grupos[key]) grupos[key] = [];
    grupos[key].push(sala);
  });

  // Ordena as chaves alfabeticamente para o menu ficar organizado
  return Object.keys(grupos).sort().reduce((obj, k) => { 
    obj[k] = grupos[k]; 
    return obj; 
  }, {} as any);
});

const salvar = () => {
  if (!novaSalaId.value) return;
  loading.value = true;
  
  emit('confirm', { 
    alocacaoId: props.allocation.id_alocacao, 
    novaSalaId: novaSalaId.value, 
    motivo: motivo.value 
  });
};
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in">
      
      <div class="bg-indigo-600 px-6 py-4 flex justify-between items-center text-white">
        <h3 class="font-bold text-lg">✏️ Trocar Sala</h3>
        <button @click="$emit('close')" class="hover:bg-indigo-700 rounded-full p-1 transition">✕</button>
      </div>

      <div class="p-6 space-y-6">
        
        <div class="bg-indigo-50 p-4 rounded-lg border border-indigo-100 text-center">
          <p class="text-xs text-indigo-500 font-bold uppercase tracking-wider mb-1">Especialidade</p>
          <p class="font-bold text-gray-800 text-xl">{{ allocation?.especialidade }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4 items-center">
          <div>
             <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Sala Atual</label>
             <div class="font-mono font-bold text-gray-600 bg-gray-100 p-2 rounded text-center border">
               {{ allocation?.sala }}
             </div>
          </div>
          <div class="text-center text-gray-300 text-xl">➔</div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mover para:</label>
          <select 
            v-model="novaSalaId" 
            class="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option disabled value="">Selecione nova sala...</option>
            
            <optgroup v-for="(salas, grupo) in salasAgrupadas" :key="grupo" :label="String(grupo)">
              <option v-for="sala in salas" :key="sala.id" :value="sala.id">
                {{ sala.nome_visual }} {{ sala.status_atual === 'OCUPADA' ? '(Ocupada)' : '' }}
              </option>
            </optgroup>

          </select>
        </div>
      </div>

      <div class="p-4 bg-gray-50 flex justify-end gap-2 border-t border-gray-100">
        <button 
          @click="$emit('close')" 
          class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          Cancelar
        </button>
        <button 
          @click="salvar" 
          :disabled="loading || !novaSalaId" 
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {{ loading ? 'Salvando...' : 'Confirmar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>