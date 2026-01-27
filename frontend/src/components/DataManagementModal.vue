<script setup lang="ts">
import { ref } from 'vue'

// defineProps and defineEmits are compiler macros and should not be imported
// Only isOpen is required here. If 'data' was present, it was a mistake.
const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'success'])

const activeTab = ref<'csv' | 'manual'>('csv')

const isDragging = ref(false)
const file = ref<File | null>(null)
const uploadStatus = ref('')
const isLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const novaDemanda = ref({
  medico_nome: '',
  especialidade: '',
  dia_semana: 'SEG',
  turno: 'MANHA',
  tipo_recurso: 'EXTRA'
})

const especialidades = [
  "CARDIOLOGIA", "PEDIATRIA", "ORTOPEDIA", "GINECOLOGIA", 
  "DERMATOLOGIA", "NEUROLOGIA", "GASTROENTEROLOGIA", 
  "CIRURGIA GERAL", "ONCOLOGIA", "NEFROLOGIA", "UROLOGIA"
]

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const selectedFile = target.files[0]
    if (selectedFile) {
      validarArquivo(selectedFile)
    }
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validarArquivo(droppedFile)
    }
  }
}

const validarArquivo = (arquivo: File) => {
  if (arquivo.name.endsWith('.csv') || arquivo.type.includes('csv')) {
    file.value = arquivo
    uploadStatus.value = 'Arquivo pronto.'
  } else {
    uploadStatus.value = 'Apenas arquivos .csv são permitidos.'
  }
}

const baixarModelo = () => {
  const csvContent = "data:text/csv;charset=utf-8," 
    + "nome,nome_especialidade,dia_semana,turno,vinculo_descricao\n"
    + "Dr. Teste,CARDIOLOGIA,2,MANHA,DOCENTE";
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "modelo_grades.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

const enviarArquivo = async () => {
  if (!file.value) return
  isLoading.value = true
  const formData = new FormData()
  formData.append('file', file.value)
  
  try {
    const res = await fetch('http://localhost:8000/api/upload/grades', { method: 'POST', body: formData })
    if (res.ok) {
      const data = await res.json()
      alert(`Importação concluída! ${data.detalhes?.grades_importadas} registros.`)
      file.value = null
      uploadStatus.value = ''
      emit('success')
      emit('close')
    } else {
      uploadStatus.value = 'Erro no processamento.'
    }
  } catch (e) {
    uploadStatus.value = 'Erro de conexão.'
  } finally {
    isLoading.value = false
  }
}

const salvarManual = async () => {
  if(!novaDemanda.value.medico_nome || !novaDemanda.value.especialidade) return
  
  try {
    const res = await fetch('http://localhost:8000/api/grade/adicionar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novaDemanda.value)
    })
    if (res.ok) {
      alert('Adicionado com sucesso!')
      emit('success')
      emit('close')
    }
  } catch (e) {
    alert('Erro ao salvar.')
  }
}

const sincronizarSalas = async () => {
  isLoading.value = true
  try {
    await fetch('http://localhost:8000/api/setup/importar-salas', { method: 'POST' })
    alert('Estrutura de salas sincronizada com o padrão do sistema.')
    emit('success')
  } catch (e) {
    alert('Erro ao sincronizar salas.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in" @click.self="$emit('close')">
    <div class="bg-white rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <div class="bg-blue-800 p-4 flex justify-between items-center text-white">
        <h2 class="font-bold text-lg flex items-center gap-2">
          ⚙️ Gerenciamento de Dados
        </h2>
        <button @click="$emit('close')" class="hover:bg-blue-700 p-1 rounded transition">&times;</button>
      </div>

      <div class="flex border-b border-gray-200">
        <button 
          @click="activeTab = 'csv'" 
          class="flex-1 py-3 text-sm font-medium transition-colors"
          :class="activeTab === 'csv' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700'"
        >
          📂 Importar Grades (CSV)
        </button>
        <button 
          @click="activeTab = 'manual'" 
          class="flex-1 py-3 text-sm font-medium transition-colors"
          :class="activeTab === 'manual' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700'"
        >
          ✍️ Inserção Manual
        </button>
      </div>

      <div class="p-6 overflow-y-auto">
        
        <div v-if="activeTab === 'csv'" class="space-y-4">
          <div 
            class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
            :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input type="file" ref="fileInput" class="hidden" accept=".csv" @change="handleFileSelect">
            <div v-if="!file" class="text-gray-500">
              <p class="text-2xl mb-2">📄</p>
              Clique ou arraste o arquivo <strong>grades.csv</strong>
            </div>
            <div v-else class="text-green-600 font-bold">
              ✅ {{ file.name }}
            </div>
          </div>

          <div class="flex justify-between items-center text-sm">
            <button @click="baixarModelo" class="text-blue-600 underline">Baixar Modelo</button>
            <span class="text-gray-400">{{ uploadStatus }}</span>
          </div>

          <div class="mt-4 pt-4 border-t flex justify-end">
            <button @click="enviarArquivo" :disabled="!file || isLoading" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
              {{ isLoading ? 'Processando...' : 'Importar Grades' }}
            </button>
          </div>

          <div class="mt-6 bg-gray-50 p-3 rounded border border-gray-200 flex justify-between items-center">
            <div>
              <p class="text-sm font-bold text-gray-700">Estrutura de Salas</p>
              <p class="text-xs text-gray-500">Sincroniza com o cadastro padrão do sistema.</p>
            </div>
            <button @click="sincronizarSalas" :disabled="isLoading" class="text-xs border border-gray-300 px-3 py-1 rounded hover:bg-gray-100 text-gray-600">
              🔄 Ressincronizar Salas
            </button>
          </div>
        </div>

        <div v-if="activeTab === 'manual'" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Profissional</label>
            <input v-model="novaDemanda.medico_nome" class="w-full border p-2 rounded focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Nome do médico">
          </div>
          
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Especialidade</label>
            <select v-model="novaDemanda.especialidade" class="w-full border p-2 rounded bg-white">
              <option v-for="esp in especialidades" :key="esp" :value="esp">{{ esp }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Dia</label>
              <select v-model="novaDemanda.dia_semana" class="w-full border p-2 rounded bg-white">
                <option value="SEG">Segunda</option>
                <option value="TER">Terça</option>
                <option value="QUA">Quarta</option>
                <option value="QUI">Quinta</option>
                <option value="SEX">Sexta</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Turno</label>
              <select v-model="novaDemanda.turno" class="w-full border p-2 rounded bg-white">
                <option value="MANHA">Manhã</option>
                <option value="TARDE">Tarde</option>
                <option value="NOITE">Noite</option>
              </select>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t flex justify-end gap-2">
            <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancelar</button>
            <button @click="salvarManual" class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 shadow transition">Salvar Demanda</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>