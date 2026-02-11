<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'success'])

const activeTab = ref<'csv' | 'manual' | 'salas'>('csv')

// --- CSV ---
const isDragging = ref(false)
const file = ref<File | null>(null)
const uploadStatus = ref('')
const isLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// --- Manual ---
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

// --- Salas ---
const salas = ref<any[]>([])
const filtroTexto = ref('')
const loadingSalas = ref(false)
const showAddRoomModal = ref(false) // New state for add room modal

// Estado para Ação em Lote
const loteBloco = ref('')
const loteAndar = ref('')

// Estado para Adicionar Sala
const addSala = ref({
  bloco: '',
  andar: '',
  especialidade: ''
})

const carregarSalas = async () => {
  loadingSalas.value = true
  try {
    const res = await fetch('http://localhost:8000/api/salas')
    if (res.ok) {
      salas.value = await res.json()
    }
  } finally {
    loadingSalas.value = false
  }
}

// Extrai Blocos Únicos
const blocosDisponiveis = computed(() => {
  const blocos = new Set(salas.value.map(s => s.bloco))
  return Array.from(blocos).sort()
})

// Extrai Andares
const andaresDisponiveis = computed(() => {
  if (!loteBloco.value) return []
  
  // Filtra salas do bloco selecionado
  const salasDoBloco = salas.value.filter(s => s.bloco === loteBloco.value)
  const andares = new Set(salasDoBloco.map(s => s.andar))
  
  // Ordena numéricamente se possível
  return Array.from(andares).sort((a, b) => {
      if (a === '0') return -1
      if (b === '0') return 1
      return String(a).localeCompare(String(b), undefined, { numeric: true })
  })
})

const formatAndar = (andar: string) => {
    if (andar === '0') return 'Térreo'
    return `${andar}º Andar`
}

// Limpa o andar se o bloco mudar
watch(loteBloco, () => {
  loteAndar.value = ''
})

const aplicarLote = async (statusManutencao: boolean) => {
  if (!loteBloco.value || !loteAndar.value) {
    alert("Selecione um Bloco e um Andar.")
    return
  }
  
  const acao = statusManutencao ? "BLOQUEAR" : "LIBERAR"
  const setor = `Bloco ${loteBloco.value} - ${formatAndar(loteAndar.value)}`
  
  if(!confirm(`Tem certeza que deseja ${acao} todas as salas do ${setor}?`)) return

  isLoading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/salas/lote/update', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bloco: loteBloco.value,
        andar: loteAndar.value,
        is_maintenance: statusManutencao
      })
    })
    
    if (res.ok) {
      const data = await res.json()
      alert(`Sucesso! ${data.afetados} salas foram atualizadas.`)
      carregarSalas() 
    } else {
      alert("Erro ao atualizar lote.")
    }
  } catch (e) {
    alert("Erro de conexão.")
  } finally {
    isLoading.value = false
  }
}

const criarSalaManual = async () => {
    if (!addSala.value.bloco || !addSala.value.andar) {
        alert("Preencha Bloco e Andar.")
        return
    }
    
    isLoading.value = true
    try {
        const res = await fetch('http://localhost:8000/api/salas', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                bloco: addSala.value.bloco,
                andar: addSala.value.andar,
                especialidade_preferencial: addSala.value.especialidade
            })
        })
        
        if (res.ok) {
            const data = await res.json()
            alert(`Sala ${data.sala} criada com sucesso!`)
            carregarSalas()
            addSala.value.especialidade = '' // Reset parcial
            showAddRoomModal.value = false // Close modal on success
        } else {
            alert("Erro ao criar sala. Verifique se o setor existe.")
        }
    } catch(e) {
        alert("Erro de conexão.")
    } finally {
        isLoading.value = false
    }
}

const excluirSala = async (salaId: string) => {
    if(!confirm(`⚠️ Tem certeza que deseja excluir permanentemente a sala ${salaId}?`)) return
    
    try {
        const res = await fetch(`http://localhost:8000/api/salas/${salaId}`, { method: 'DELETE' })
        if (res.ok) {
            carregarSalas()
        } else {
            alert("Erro ao excluir sala.")
        }
    } catch(e) { 
        alert("Erro de conexão.") 
    }
}

const toggleManutencao = async (sala: any) => {
  const novoStatus = !sala.is_maintenance
  sala.is_maintenance = novoStatus
  
  try {
    const res = await fetch(`http://localhost:8000/api/salas/${sala.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_maintenance: novoStatus })
    })
    
    if (!res.ok) {
      sala.is_maintenance = !novoStatus
      alert('Erro ao atualizar status.')
    }
  } catch (e) {
    sala.is_maintenance = !novoStatus
    alert('Erro de conexão.')
  }
}

// Filtro Unificado da Tabela
const salasFiltradas = computed(() => {
  let lista = salas.value

  // Filtra por Bloco
  if (loteBloco.value) {
    lista = lista.filter(s => s.bloco === loteBloco.value)
  }

  // Filtra por Andar
  if (loteAndar.value) {
    lista = lista.filter(s => s.andar === loteAndar.value)
  }

  // Filtra por Texto Livre
  if (filtroTexto.value) {
    const f = filtroTexto.value.toLowerCase()
    lista = lista.filter(s => 
      s.nome_visual.toLowerCase().includes(f) || 
      (s.especialidade_preferencial || '').toLowerCase().includes(f)
    )
  }

  return lista
})

watch(activeTab, (newTab) => {
  if (newTab === 'salas' && salas.value.length === 0) {
    carregarSalas()
  }
})

// Lógica Geral

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.length) {
    const selectedFile = target.files[0]
    if (selectedFile) validarArquivo(selectedFile)
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const droppedFile = e.dataTransfer?.files?.[0]
  if (droppedFile) validarArquivo(droppedFile)
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
    + "nome,nome_especialidade,dia_semana,turno,vinculo_descricao,ativa\n"
    + "Dr. Teste,CARDIOLOGIA,2,MANHA,DOCENTE,TRUE\n"
    + "Dr. Fulano,Pediatria,3,TARDE,DOCENTE,FALSE\n";
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
  if(!confirm("Isso apagará todas as configurações manuais de salas e recarregará do CSV original. Tem certeza?")) return
  
  isLoading.value = true
  try {
    await fetch('http://localhost:8000/api/setup/importar-salas', { method: 'POST' })
    alert('Salas resetadas para o padrão original.')
    carregarSalas()
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
    <div class="bg-white rounded-xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="bg-blue-800 p-4 flex justify-between items-center text-white">
        <h2 class="font-bold text-lg flex items-center gap-2">
          ⚙️ Gerenciamento de Dados
        </h2>
        <button @click="$emit('close')" class="hover:bg-blue-700 p-1 rounded transition cursor-pointer">&times;</button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 bg-gray-50">
        <button 
          @click="activeTab = 'csv'" 
          class="flex-1 py-3 text-sm font-bold transition-colors border-b-2 cursor-pointer"
          :class="activeTab === 'csv' ? 'text-blue-700 border-blue-600 bg-white' : 'text-gray-500 border-transparent hover:text-gray-700'"
        >
          Importar Grades
        </button>
        <button 
          @click="activeTab = 'manual'" 
          class="flex-1 py-3 text-sm font-bold transition-colors border-b-2 cursor-pointer"
          :class="activeTab === 'manual' ? 'text-blue-700 border-blue-600 bg-white' : 'text-gray-500 border-transparent hover:text-gray-700'"
        >
          Inserção Manual
        </button>
        <button 
          @click="activeTab = 'salas'" 
          class="flex-1 py-3 text-sm font-bold transition-colors border-b-2 cursor-pointer"
          :class="activeTab === 'salas' ? 'text-blue-700 border-blue-600 bg-white' : 'text-gray-500 border-transparent hover:text-gray-700'"
        >
          Salas e Setores
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto bg-white flex-1">
        
        <!-- Tab CSV -->
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
            <button @click="baixarModelo" class="text-blue-600 underline cursor-pointer">Baixar Modelo</button>
            <span class="text-gray-400">{{ uploadStatus }}</span>
          </div>

          <div class="mt-4 pt-4 border-t flex justify-end">
            <button @click="enviarArquivo" :disabled="!file || isLoading" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 cursor-pointer cursor disabled:opacity-50 disabled:cursor-not-allowed transition">
              {{ isLoading ? 'Processando...' : 'Importar Grades' }}
            </button>
          </div>
        </div>

        <!-- Tab Manual -->
        <div v-if="activeTab === 'manual'" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Profissional</label>
            <input v-model="novaDemanda.medico_nome" class="w-full border p-2 rounded focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Nome do médico">
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Especialidade</label>
            <select v-model="novaDemanda.especialidade" class="w-full border p-2 rounded bg-white cursor-pointer">
              <option v-for="esp in especialidades" :key="esp" :value="esp">{{ esp }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Dia</label>
              <select v-model="novaDemanda.dia_semana" class="w-full border p-2 rounded bg-white cursor-pointer">
                <option value="SEG">Segunda</option>
                <option value="TER">Terça</option>
                <option value="QUA">Quarta</option>
                <option value="QUI">Quinta</option>
                <option value="SEX">Sexta</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Turno</label>
              <select v-model="novaDemanda.turno" class="w-full border p-2 rounded bg-white cursor-pointer">
                <option value="MANHA">Manhã</option>
                <option value="TARDE">Tarde</option>
                <option value="NOITE">Noite</option>
              </select>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t flex justify-end gap-2">
            <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 cursor-pointer rounded">Cancelar</button>
            <button @click="salvarManual" class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 cursor-pointer shadow transition">Salvar Demanda</button>
          </div>
        </div>

        <!-- Tab SALAS -->
        <div v-if="activeTab === 'salas'" class="flex flex-col h-full">
          
          <!-- Área de Ações em Lote -->
          <div class="bg-blue-50 p-4 rounded-lg border border-blue-100 mb-4">
            <h3 class="text-sm font-bold text-blue-800 mb-2 flex items-center gap-1">
              Filtros por setor
            </h3>
            <div class="flex flex-wrap gap-3 items-end">
              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Bloco</label>
                <select v-model="loteBloco" class="border rounded p-1.5 text-sm w-32 bg-white cursor-pointer hover:border-blue-400 focus:ring-2 focus:ring-blue-200 outline-none">
                  <option value="" selected>Todos</option>
                  <option v-for="b in blocosDisponiveis" :key="b" :value="b">{{ b }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Andar</label>
                <select 
                  v-model="loteAndar" 
                  class="border rounded p-1.5 text-sm w-32 bg-white cursor-pointer hover:border-blue-400 focus:ring-2 focus:ring-blue-200 outline-none"
                  :disabled="!loteBloco"
                >
                  <option value="" selected>Todos</option>
                  <option v-for="a in andaresDisponiveis" :key="a" :value="a">{{ formatAndar(a) }}</option>
                </select>
              </div>
              
              <div class="flex gap-2 ml-auto pl-4 border-l border-blue-200">
                <button 
                  @click="aplicarLote(true)" 
                  class="bg-red-100 text-red-700 text-xs font-bold px-3 py-2 rounded hover:bg-red-200 cursor-pointer border border-red-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  :disabled="!loteBloco || !loteAndar || isLoading"
                  title="Bloqueia todas as salas listadas abaixo"
                >
                  🔒 Bloquear Setor
                </button>
                <button 
                  @click="aplicarLote(false)" 
                  class="bg-green-100 text-green-700 text-xs font-bold px-3 py-2 rounded hover:bg-green-200 cursor-pointer border border-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  :disabled="!loteBloco || !loteAndar || isLoading"
                  title="Libera todas as salas listadas abaixo"
                >
                  ✅ Liberar Setor
                </button>
              </div>
            </div>
          </div>

          <div v-if="loadingSalas" class="text-center py-10 text-gray-400">Carregando...</div>

          <!-- Tabela -->
          <div class="flex flex-col flex-1 min-h-0">
            <div class="flex justify-between items-center mb-2">
                <div class="flex flex-row gap-4">
                  <input v-model="filtroTexto" type="text" placeholder="🔍 Buscar sala..." class="border p-2 rounded w-64 text-sm outline-none focus:ring-1 focus:ring-blue-500">
                  <button @click="showAddRoomModal = true" class="bg-green-100 text-green-700 text-xs font-bold px-3 py-2 rounded hover:bg-green-200 border border-green-200 cursor-pointer">+</button>
                </div>
                <button @click="sincronizarSalas" class="text-xs text-red-600 hover:text-red-800 underline cursor-pointer">Resetar Padrão</button>
            </div>
            
            <div class="flex-1 overflow-y-auto border rounded border-gray-200">
                <table class="w-full text-left text-sm">
                <thead class="bg-gray-100 text-gray-600 uppercase text-xs sticky top-0 z-10">
                    <tr><th class="p-3">Sala</th><th class="p-3">Bloco/Andar</th><th class="p-3">Esp. Pref.</th><th class="p-3 text-center">Status</th><th class="p-3 text-center">Ações</th></tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    <tr v-for="sala in salasFiltradas" :key="sala.id" class="hover:bg-gray-50">
                    <td class="p-3 font-medium text-gray-800">{{ sala.nome_visual }}</td>
                    <td class="p-3 text-gray-500">{{ sala.bloco }} - {{ formatAndar(sala.andar) }}</td>
                    <td class="p-3 text-gray-500 text-xs">{{ sala.especialidade_preferencial || '-' }}</td>
                    <td class="p-3 text-center">
                        <button @click="toggleManutencao(sala)" class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer" :class="sala.is_maintenance ? 'bg-red-500' : 'bg-gray-300'">
                            <span class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform" :class="sala.is_maintenance ? 'translate-x-5' : 'translate-x-1'"/>
                        </button>
                    </td>
                    <td class="p-3 text-center">
                        <button @click="excluirSala(sala.id)" class="text-red-500 hover:text-red-700 cursor-pointer" title="Excluir Sala">🗑️</button>
                    </td>
                    </tr>
                </tbody>
                </table>
            </div>
          </div>
        </div>

      </div>
    </div>
    
    <!-- Add Room Modal (Sub-modal) -->
    <div v-if="showAddRoomModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in" @click.self="showAddRoomModal = false">
      <div class="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl">
        <h3 class="text-lg font-bold mb-4">Adicionar Nova Sala</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Bloco</label>
            <select v-model="addSala.bloco" class="border rounded p-2 text-sm w-full bg-white">
              <option value="" disabled selected>Selecione...</option>
              <option v-for="b in blocosDisponiveis" :key="b" :value="b">{{ b }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Andar</label>
            <select v-model="addSala.andar" class="border rounded p-2 text-sm w-full bg-white" :disabled="!addSala.bloco">
              <option value="" disabled selected>Selecione...</option>
              <option value="0">Térreo</option>
              <option value="1">1º Andar</option>
              <option value="2">2º Andar</option>
              <option value="3">3º Andar</option>
              <option value="4">4º Andar</option>
              <option value="5">5º Andar</option>
              <option value="6">6º Andar</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Especialidade (Opcional)</label>
            <input v-model="addSala.especialidade" type="text" placeholder="Ex: Cardiologia" class="border rounded p-2 text-sm w-full">
          </div>
          <div class="flex justify-end gap-2 mt-4">
            <button @click="showAddRoomModal = false" class="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded cursor-pointer">Cancelar</button>
            <button @click="criarSalaManual" class="bg-green-600 text-white text-sm font-bold px-4 py-2 rounded hover:bg-green-700 cursor-pointer" :disabled="isLoading">Salvar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>