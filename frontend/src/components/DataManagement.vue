<script setup lang="ts">
import { ref } from 'vue'

const isDragging = ref(false)
const file = ref<File | null>(null)
const uploadStatus = ref('')
const isModalOpen = ref(false)
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

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const droppedFile = e.dataTransfer?.files[0]
  validarArquivo(droppedFile)
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    validarArquivo(target.files[0])
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const validarArquivo = (arquivo: File | undefined) => {
  if (arquivo && (arquivo.type.includes('csv') || arquivo.name.endsWith('.csv'))) {
    file.value = arquivo
    uploadStatus.value = 'Arquivo pronto para envio!'
  } else {
    file.value = null
    uploadStatus.value = 'Por favor, envie um arquivo .CSV válido.'
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
  uploadStatus.value = 'Iniciando upload...'
  
  const formData = new FormData()
  formData.append('file', file.value)
  
  try {
    // Tenta conectar no localhost
    const res = await fetch('http://localhost:8000/api/upload/grades', {
       method: 'POST',
       body: formData
    })
    
    if (res.ok) {
      const data = await res.json()
      const qtd = data.detalhes?.grades_importadas || 'N/A'
      uploadStatus.value = `✅ Sucesso! ${qtd} linhas importadas.`
      file.value = null
    } else {
      // Tenta ler o erro do backend
      let errorText = "Erro desconhecido"
      try {
          const errJson = await res.json();
          errorText = errJson.detail || JSON.stringify(errJson);
      } catch (e) {
          errorText = await res.text();
      }
      console.error("Erro do Backend:", errorText)
      uploadStatus.value = `❌ Erro (${res.status}): ${errorText}`
    }
  } catch (error) {
    console.error("Erro de Fetch:", error)
    uploadStatus.value = '❌ Falha na conexão. Backend está offline?'
  } finally {
    isLoading.value = false
  }
}

const salvarManual = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/grade/adicionar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novaDemanda.value)
    })
    if (res.ok) {
      alert("Salvo com sucesso!")
      isModalOpen.value = false
    } else {
      alert("Erro ao salvar.")
    }
  } catch (e) {
    alert("Erro de conexão.")
  }
}
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto animate-fade-in">
    <div class="mb-8 border-b pb-4">
      <h2 class="text-2xl font-bold text-gray-800">Gestão de Grades</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Upload -->
      <div class="bg-white p-6 rounded-xl shadow border">
        <h3 class="font-bold text-lg mb-4 text-blue-800">📂 Importar CSV</h3>
        
        <div 
          class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
          :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input type="file" ref="fileInput" class="hidden" accept=".csv" @change="handleFileSelect">
          <div v-if="!file" class="text-gray-500">Clique ou arraste o CSV aqui</div>
          <div v-else class="text-green-600 font-bold">{{ file.name }}</div>
        </div>

        <div class="mt-4 flex justify-between items-center">
          <button @click="baixarModelo" class="text-xs text-blue-600 underline">Baixar Modelo</button>
          <button @click="enviarArquivo" :disabled="!file || isLoading" class="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
            {{ isLoading ? 'Enviando...' : 'Enviar' }}
          </button>
        </div>
        <p class="mt-2 text-sm text-center font-medium">{{ uploadStatus }}</p>
      </div>

      <!-- Manual -->
      <div class="bg-white p-6 rounded-xl shadow border text-center flex flex-col justify-center">
        <button @click="isModalOpen = true" class="bg-green-600 text-white py-3 rounded-lg font-bold shadow hover:bg-green-700">
          + Nova Demanda Manual
        </button>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg w-full max-w-md">
        <h3 class="font-bold text-lg mb-4">Adicionar Demanda</h3>
        <input v-model="novaDemanda.medico_nome" class="w-full border p-2 rounded mb-2" placeholder="Nome">
        <select v-model="novaDemanda.especialidade" class="w-full border p-2 rounded mb-2">
          <option v-for="esp in especialidades" :key="esp" :value="esp">{{ esp }}</option>
        </select>
        <div class="flex justify-end gap-2 mt-4">
          <button @click="isModalOpen = false" class="px-4 py-2 text-gray-600">Cancelar</button>
          <button @click="salvarManual" class="px-4 py-2 bg-blue-600 text-white rounded">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>