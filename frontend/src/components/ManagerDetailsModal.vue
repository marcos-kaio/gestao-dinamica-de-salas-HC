<script setup lang="ts">
import { ref, computed } from 'vue';
import ManualEditModal from './ManualEditModal.vue';

// Definição das Props
const props = defineProps<{
  isOpen: boolean;
  data: any; 
  detailedList: any[]; 
}>();

const emit = defineEmits(['close', 'refresh']);

const showEdit = ref(false);
const itemEditing = ref(null);
const allRooms = ref([]);

// Calcula quantas salas únicas existem na lista atual para exibir no cabeçalho
const totalUniqueRooms = computed(() => {
  if (!props.detailedList) return 0;
  const unique = new Set(props.detailedList.map(i => i.sala));
  return unique.size;
});

const handleEdit = async (item: any) => {
  itemEditing.value = item;
  if (allRooms.value.length === 0) {
    try {
      const res = await fetch('http://localhost:8000/api/salas');
      allRooms.value = await res.json();
    } catch(e) { console.error(e); }
  }
  showEdit.value = true;
};

const confirmEdit = async (payload: any) => {
  try {
    const res = await fetch(`http://localhost:8000/api/alocacoes/${payload.alocacaoId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nova_sala_id: payload.novaSalaId })
    });
    if (res.ok) {
      showEdit.value = false;
      emit('refresh');
      emit('close');
    } else {
      alert("Erro ao editar.");
    }
  } catch (e) { alert("Erro de conexão"); }
};

// Cores para os turnos ficarem visuais
const getTurnoColor = (turno: string) => {
  if (turno === 'MANHA') return 'bg-orange-100 text-orange-700 border-orange-200';
  if (turno === 'TARDE') return 'bg-blue-100 text-blue-700 border-blue-200';
  if (turno === 'NOITE') return 'bg-indigo-100 text-indigo-700 border-indigo-200';
  return 'bg-gray-100 text-gray-600';
}
</script>

<template>
  <div v-if="isOpen && data" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade">
    
    <div class="w-full max-w-4xl rounded-xl bg-white shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <div class="p-6 border-b border-gray-100 flex justify-between items-start bg-white">
        <div>
           <div class="flex items-center gap-2 mb-2">
             <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700 uppercase tracking-wide">
               {{ data.ambulatorio }}
             </span>
           </div>
           
           <h2 class="text-2xl font-bold text-gray-900">
             {{ totalUniqueRooms }} salas físicas
             <span class="text-base font-normal text-gray-400">
               ({{ detailedList.length }} horários alocados)
             </span>
           </h2>
           
           <p class="text-sm text-gray-500 mt-1">
             Cada bloco abaixo representa um turno de atendimento. Clique para mover.
           </p>
        </div>
        
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 p-2 text-3xl leading-none transition">
          &times;
        </button>
      </div>

      <div class="p-6 bg-gray-50 overflow-y-auto custom-scroll grow">
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          
          <button 
            v-for="item in detailedList" 
            :key="item.id_alocacao"
            @click="handleEdit(item)"
            class="group relative flex flex-col items-center justify-between p-3 rounded-xl border-2 border-white bg-white shadow-sm hover:border-indigo-500 hover:shadow-md transition-all cursor-pointer h-32"
          >
            <div class="w-full flex justify-center mb-1">
              <span :class="`text-[10px] font-bold px-2 py-0.5 rounded border ${getTurnoColor(item.turno)} uppercase tracking-tighter`">
                {{ item.dia }} • {{ item.turno }}
              </span>
            </div>

            <div class="flex flex-col items-center">
              <span class="text-xl font-bold text-gray-800">{{ item.sala }}</span>
              <span class="text-[10px] text-gray-400 mt-1">
                {{ item.andar === '0' ? 'Térreo' : item.andar + 'º Andar' }}
              </span>
            </div>

            <div class="opacity-0 group-hover:opacity-100 transition-opacity mt-1">
              <span class="text-xs font-bold text-indigo-600 flex items-center gap-1">
                Editar
              </span>
            </div>
          </button>

        </div>
      </div>
    </div>

    <ManualEditModal 
      :show="showEdit"
      :allocation="itemEditing"
      :todas-salas="allRooms"
      @close="showEdit = false"
      @confirm="confirmEdit"
    />

  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 8px; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.animate-fade { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>