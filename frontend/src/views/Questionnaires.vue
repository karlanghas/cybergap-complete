<template>
  <div class="min-h-screen bg-slate-950 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">Cuestionarios</h1>
          <p class="text-slate-400 mt-1">Gestiona campañas de auditoría y asignaciones</p>
        </div>
        <button 
          @click="openModal()" 
          class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg transition-all font-medium shadow-lg shadow-emerald-500/25"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo Cuestionario
        </button>
      </div>
    </div>

    <!-- Filter -->
    <div class="mb-6">
      <select 
        v-model="filterCompany"
        class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
      >
        <option :value="null">Todas las empresas</option>
        <option v-for="company in companies" :key="company.id" :value="company.id">
          {{ company.name }}
        </option>
      </select>
    </div>

    <!-- Questionnaires Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <div 
        v-for="q in filteredQuestionnaires" 
        :key="q.id"
        class="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-all duration-200"
      >
        <!-- Card Header -->
        <div class="p-5 border-b border-slate-800">
          <div class="flex items-start justify-between mb-3">
            <span :class="getStatusClass(q.status)" class="px-2.5 py-1 rounded-full text-xs font-medium">
              {{ getStatusName(q.status) }}
            </span>
            <div class="flex items-center gap-1">
              <button 
                @click="openModal(q)"
                class="p-1.5 text-slate-400 hover:text-blue-400 hover:bg-slate-800 rounded transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button 
                @click="confirmDelete(q)"
                class="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-white mb-1">{{ q.name }}</h3>
          <p class="text-sm text-slate-400">{{ q.company_name }}</p>
        </div>

        <!-- Progress Stats -->
        <div class="p-5 bg-slate-800/30">
          <div class="flex items-center justify-between text-sm mb-2">
            <span class="text-slate-400">Progreso</span>
            <span class="text-white font-medium">{{ q.completed_count || 0 }} / {{ q.total_assignments || 0 }}</span>
          </div>
          <div class="w-full bg-slate-700 rounded-full h-2 mb-4">
            <div 
              class="bg-emerald-500 h-2 rounded-full transition-all"
              :style="{ width: `${getProgress(q)}%` }"
            ></div>
          </div>

          <div class="grid grid-cols-3 gap-4 text-center">
            <div>
              <div class="text-xl font-bold text-white">{{ q.users_count || 0 }}</div>
              <div class="text-xs text-slate-500">Usuarios</div>
            </div>
            <div>
              <div class="text-xl font-bold text-white">{{ q.questions_count || 0 }}</div>
              <div class="text-xs text-slate-500">Preguntas</div>
            </div>
            <div>
              <div class="text-xl font-bold text-amber-400">{{ q.divergences_count || 0 }}</div>
              <div class="text-xs text-slate-500">Divergencias</div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t border-slate-800 flex gap-2">
          <button 
            @click="goToAssignments(q)"
            class="flex-1 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
          >
            Asignaciones
          </button>
          <button 
            @click="sendTokens(q)"
            :disabled="q.status === 'completed'"
            class="flex-1 px-3 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm transition-colors"
          >
            Enviar Tokens
          </button>
          <button 
            @click="goToReport(q)"
            class="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm transition-colors"
            title="Ver Reporte"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredQuestionnaires.length === 0" class="col-span-full text-center py-16">
        <svg class="w-16 h-16 mx-auto text-slate-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <h3 class="text-xl text-slate-400">No hay cuestionarios</h3>
        <p class="text-slate-500 mt-2">Crea tu primer cuestionario para comenzar</p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl">
        <div class="p-6 border-b border-slate-700">
          <h2 class="text-xl font-bold text-white">
            {{ editingItem ? 'Editar Cuestionario' : 'Nuevo Cuestionario' }}
          </h2>
        </div>
        
        <form @submit.prevent="save" class="p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Nombre *</label>
            <input 
              v-model="form.name"
              type="text"
              required
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              placeholder="Auditoría ISO 27001 - Q4 2024"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Empresa *</label>
            <select 
              v-model="form.company_id"
              required
              :disabled="!!editingItem"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
            >
              <option :value="null" disabled>Seleccionar empresa...</option>
              <option v-for="company in companies" :key="company.id" :value="company.id">
                {{ company.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Descripción</label>
            <textarea 
              v-model="form.description"
              rows="3"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              placeholder="Descripción del cuestionario..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Fecha Inicio</label>
              <input 
                v-model="form.start_date"
                type="date"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Fecha Fin</label>
              <input 
                v-model="form.end_date"
                type="date"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Estado</label>
            <select 
              v-model="form.status"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
            >
              <option value="draft">Borrador</option>
              <option value="active">Activo</option>
              <option value="paused">Pausado</option>
              <option value="completed">Completado</option>
            </select>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button"
              @click="showModal = false"
              class="flex-1 px-4 py-2.5 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 font-medium"
            >
              {{ saving ? 'Guardando...' : (editingItem ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assignments Modal -->
    <div v-if="showAssignmentsModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl shadow-2xl max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-700 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Asignaciones</h2>
            <p class="text-sm text-slate-400">{{ selectedQuestionnaire?.name }}</p>
          </div>
          <button @click="showAssignmentsModal = false" class="text-slate-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="p-6 flex-1 overflow-y-auto">
          <!-- Quick Assignment -->
          <div class="bg-slate-800/50 rounded-xl p-5 mb-6">
            <h3 class="text-lg font-medium text-white mb-4">Asignación Rápida</h3>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">Usuarios</label>
                <select 
                  v-model="assignForm.user_ids"
                  multiple
                  class="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 h-32"
                >
                  <option v-for="user in companyUsers" :key="user.id" :value="user.id">
                    {{ user.full_name }} ({{ user.area_name }})
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">Preguntas</label>
                <select 
                  v-model="assignForm.question_ids"
                  multiple
                  class="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 h-32"
                >
                  <option v-for="q in questions" :key="q.id" :value="q.id">
                    {{ q.text.substring(0, 60) }}...
                  </option>
                </select>
              </div>
            </div>

            <button 
              @click="createBulkAssignments"
              :disabled="!assignForm.user_ids.length || !assignForm.question_ids.length"
              class="w-full px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 transition-colors"
            >
              Asignar Seleccionados
            </button>
          </div>

          <!-- Current Assignments -->
          <div>
            <h3 class="text-lg font-medium text-white mb-4">Asignaciones Actuales</h3>
            
            <div class="space-y-3">
              <div 
                v-for="assignment in currentAssignments" 
                :key="assignment.id"
                class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
              >
                <div class="flex-1">
                  <div class="text-white">{{ assignment.user_name }}</div>
                  <div class="text-sm text-slate-400">{{ assignment.question_text?.substring(0, 50) }}...</div>
                </div>
                <div class="flex items-center gap-3">
                  <span :class="assignment.response ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-600/50 text-slate-400'" class="px-2 py-1 rounded text-xs">
                    {{ assignment.response ? 'Respondida' : 'Pendiente' }}
                  </span>
                  <button 
                    @click="deleteAssignment(assignment)"
                    class="text-slate-400 hover:text-red-400"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>

              <div v-if="currentAssignments.length === 0" class="text-center py-8 text-slate-500">
                No hay asignaciones para este cuestionario
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../stores/api'

const router = useRouter()
const api = useApi()

const questionnaires = ref([])
const companies = ref([])
const questions = ref([])
const companyUsers = ref([])
const currentAssignments = ref([])

const filterCompany = ref(null)
const showModal = ref(false)
const showAssignmentsModal = ref(false)
const editingItem = ref(null)
const selectedQuestionnaire = ref(null)
const saving = ref(false)

const form = ref({
  name: '',
  description: '',
  company_id: null,
  start_date: '',
  end_date: '',
  status: 'draft'
})

const assignForm = ref({
  user_ids: [],
  question_ids: []
})

const filteredQuestionnaires = computed(() => {
  if (!filterCompany.value) return questionnaires.value
  return questionnaires.value.filter(q => q.company_id === filterCompany.value)
})

onMounted(async () => {
  await Promise.all([
    loadQuestionnaires(),
    loadCompanies(),
    loadQuestions()
  ])
})

async function loadQuestionnaires() {
  try {
    const response = await api.get('/questionnaires')
    questionnaires.value = response.data
  } catch (error) {
    console.error('Error loading questionnaires:', error)
  }
}

async function loadCompanies() {
  try {
    const response = await api.get('/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Error loading companies:', error)
  }
}

async function loadQuestions() {
  try {
    const response = await api.get('/questions')
    questions.value = response.data
  } catch (error) {
    console.error('Error loading questions:', error)
  }
}

async function loadCompanyUsers(companyId) {
  try {
    const response = await api.get(`/users?company_id=${companyId}`)
    companyUsers.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
  }
}

async function loadAssignments(questionnaireId) {
  try {
    const response = await api.get(`/questionnaires/${questionnaireId}/assignments`)
    currentAssignments.value = response.data
  } catch (error) {
    console.error('Error loading assignments:', error)
  }
}

function openModal(item = null) {
  editingItem.value = item
  if (item) {
    form.value = {
      name: item.name,
      description: item.description || '',
      company_id: item.company_id,
      start_date: item.start_date?.split('T')[0] || '',
      end_date: item.end_date?.split('T')[0] || '',
      status: item.status
    }
  } else {
    form.value = {
      name: '',
      description: '',
      company_id: null,
      start_date: '',
      end_date: '',
      status: 'draft'
    }
  }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/questionnaires/${editingItem.value.id}`, form.value)
    } else {
      await api.post('/questionnaires', form.value)
    }
    await loadQuestionnaires()
    showModal.value = false
  } catch (error) {
    console.error('Error saving:', error)
    alert(error.response?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(q) {
  if (!confirm(`¿Eliminar el cuestionario "${q.name}"?`)) return
  try {
    await api.delete(`/questionnaires/${q.id}`)
    await loadQuestionnaires()
  } catch (error) {
    console.error('Error deleting:', error)
    alert(error.response?.data?.detail || 'Error al eliminar')
  }
}

async function goToAssignments(q) {
  selectedQuestionnaire.value = q
  await loadCompanyUsers(q.company_id)
  await loadAssignments(q.id)
  assignForm.value = { user_ids: [], question_ids: [] }
  showAssignmentsModal.value = true
}

async function createBulkAssignments() {
  try {
    await api.post(`/questionnaires/${selectedQuestionnaire.value.id}/assignments/bulk`, {
      user_ids: assignForm.value.user_ids,
      question_ids: assignForm.value.question_ids
    })
    await loadAssignments(selectedQuestionnaire.value.id)
    await loadQuestionnaires()
    assignForm.value = { user_ids: [], question_ids: [] }
  } catch (error) {
    console.error('Error creating assignments:', error)
    alert(error.response?.data?.detail || 'Error al crear asignaciones')
  }
}

async function deleteAssignment(assignment) {
  try {
    await api.delete(`/questionnaires/assignments/${assignment.id}`)
    await loadAssignments(selectedQuestionnaire.value.id)
  } catch (error) {
    console.error('Error deleting assignment:', error)
  }
}

async function sendTokens(q) {
  if (!confirm(`¿Enviar tokens de acceso a todos los usuarios de "${q.name}"?`)) return
  try {
    const response = await api.post(`/questionnaires/${q.id}/send-tokens`)
    alert(`Tokens enviados: ${response.data.sent_count}`)
    await loadQuestionnaires()
  } catch (error) {
    console.error('Error sending tokens:', error)
    alert(error.response?.data?.detail || 'Error al enviar tokens')
  }
}

function goToReport(q) {
  router.push(`/reports/${q.id}`)
}

function getProgress(q) {
  if (!q.total_assignments) return 0
  return Math.round((q.completed_count / q.total_assignments) * 100)
}

function getStatusClass(status) {
  const classes = {
    draft: 'bg-slate-600/50 text-slate-300',
    active: 'bg-emerald-500/20 text-emerald-400',
    paused: 'bg-amber-500/20 text-amber-400',
    completed: 'bg-blue-500/20 text-blue-400'
  }
  return classes[status] || 'bg-slate-600/50 text-slate-300'
}

function getStatusName(status) {
  const names = {
    draft: 'Borrador',
    active: 'Activo',
    paused: 'Pausado',
    completed: 'Completado'
  }
  return names[status] || status
}
</script>
