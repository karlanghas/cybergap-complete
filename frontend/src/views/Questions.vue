<template>
  <div class="min-h-screen bg-slate-950 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">Banco de Preguntas</h1>
          <p class="text-slate-400 mt-1">Gestiona las preguntas para tus auditorías</p>
        </div>
        <div class="flex gap-3">
          <button 
            @click="showCategoryModal = true"
            class="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2.5 rounded-lg transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
            </svg>
            Categorías
          </button>
          <button 
            @click="openQuestionModal()" 
            class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg transition-all font-medium shadow-lg shadow-emerald-500/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Nueva Pregunta
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ questions.length }}</div>
            <div class="text-sm text-slate-400">Total Preguntas</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ categories.length }}</div>
            <div class="text-sm text-slate-400">Categorías</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ questions.filter(q => q.question_type === 'single_choice').length }}</div>
            <div class="text-sm text-slate-400">Selección Única</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ totalMaxScore }}</div>
            <div class="text-sm text-slate-400">Puntaje Máximo</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4 mb-6">
      <select 
        v-model="filterCategory"
        class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
      >
        <option :value="null">Todas las categorías</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>

      <select 
        v-model="filterType"
        class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
      >
        <option :value="null">Todos los tipos</option>
        <option value="single_choice">Selección Única</option>
        <option value="multiple_choice">Selección Múltiple</option>
        <option value="text">Texto Libre</option>
        <option value="scale">Escala</option>
        <option value="yes_no">Sí/No</option>
      </select>

      <input 
        v-model="searchQuery"
        type="text"
        placeholder="Buscar preguntas..."
        class="flex-1 min-w-[300px] bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
      />
    </div>

    <!-- Questions List -->
    <div class="space-y-4">
      <div 
        v-for="question in filteredQuestions" 
        :key="question.id"
        class="bg-slate-900/50 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span 
                v-if="question.category"
                :style="{ backgroundColor: question.category.color + '20', color: question.category.color }"
                class="px-2.5 py-1 rounded-full text-xs font-medium"
              >
                {{ question.category.name }}
              </span>
              <span :class="getTypeClass(question.question_type)" class="px-2.5 py-1 rounded-full text-xs font-medium">
                {{ getTypeName(question.question_type) }}
              </span>
              <span class="text-xs text-slate-500">
                Puntaje máx: {{ question.max_score }}
              </span>
            </div>
            
            <h3 class="text-white font-medium mb-2">{{ question.text }}</h3>
            
            <p v-if="question.description" class="text-sm text-slate-400 mb-3">
              {{ question.description }}
            </p>

            <!-- Options Preview -->
            <div v-if="question.options && question.options.length > 0" class="flex flex-wrap gap-2">
              <span 
                v-for="(opt, idx) in question.options.slice(0, 4)" 
                :key="idx"
                class="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300"
              >
                {{ opt.text }} ({{ opt.score }} pts)
              </span>
              <span v-if="question.options.length > 4" class="px-2 py-1 text-xs text-slate-500">
                +{{ question.options.length - 4 }} más
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button 
              @click="duplicateQuestion(question)"
              class="p-2 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition-colors"
              title="Duplicar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
              </svg>
            </button>
            <button 
              @click="openQuestionModal(question)"
              class="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-800 rounded-lg transition-colors"
              title="Editar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button 
              @click="confirmDelete(question)"
              class="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
              title="Eliminar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredQuestions.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 mx-auto text-slate-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <h3 class="text-xl text-slate-400">No hay preguntas</h3>
        <p class="text-slate-500 mt-2">Comienza creando tu primera pregunta</p>
      </div>
    </div>

    <!-- Question Modal -->
    <div v-if="showQuestionModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl shadow-2xl my-8">
        <div class="p-6 border-b border-slate-700">
          <h2 class="text-xl font-bold text-white">
            {{ editingQuestion ? 'Editar Pregunta' : 'Nueva Pregunta' }}
          </h2>
        </div>
        
        <form @submit.prevent="saveQuestion" class="p-6 space-y-5 max-h-[70vh] overflow-y-auto">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Categoría</label>
              <select 
                v-model="questionForm.category_id"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              >
                <option :value="null">Sin categoría</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Tipo de Pregunta *</label>
              <select 
                v-model="questionForm.question_type"
                required
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              >
                <option value="single_choice">Selección Única</option>
                <option value="multiple_choice">Selección Múltiple</option>
                <option value="text">Texto Libre</option>
                <option value="scale">Escala (1-5)</option>
                <option value="yes_no">Sí/No</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Texto de la Pregunta *</label>
            <textarea 
              v-model="questionForm.text"
              required
              rows="3"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              placeholder="¿La organización cuenta con..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Descripción / Ayuda</label>
            <textarea 
              v-model="questionForm.description"
              rows="2"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              placeholder="Información adicional para el usuario..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Puntaje Máximo</label>
              <input 
                v-model.number="questionForm.max_score"
                type="number"
                min="0"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div class="flex items-end gap-4">
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="questionForm.required" class="w-4 h-4 text-emerald-500 bg-slate-800 border-slate-700 rounded">
                <span class="text-sm text-slate-300">Obligatoria</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="questionForm.is_active" class="w-4 h-4 text-emerald-500 bg-slate-800 border-slate-700 rounded">
                <span class="text-sm text-slate-300">Activa</span>
              </label>
            </div>
          </div>

          <!-- Options for choice questions -->
          <div v-if="['single_choice', 'multiple_choice'].includes(questionForm.question_type)">
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm font-medium text-slate-300">Opciones de Respuesta</label>
              <button 
                type="button"
                @click="addOption"
                class="text-sm text-emerald-400 hover:text-emerald-300"
              >
                + Agregar opción
              </button>
            </div>
            
            <div class="space-y-3">
              <div 
                v-for="(opt, idx) in questionForm.options" 
                :key="idx"
                class="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3"
              >
                <input 
                  v-model="opt.value"
                  type="text"
                  placeholder="Valor"
                  class="w-24 bg-slate-700 border border-slate-600 text-white rounded px-3 py-1.5 text-sm"
                />
                <input 
                  v-model="opt.text"
                  type="text"
                  placeholder="Texto de la opción"
                  class="flex-1 bg-slate-700 border border-slate-600 text-white rounded px-3 py-1.5 text-sm"
                />
                <input 
                  v-model.number="opt.score"
                  type="number"
                  placeholder="Pts"
                  class="w-20 bg-slate-700 border border-slate-600 text-white rounded px-3 py-1.5 text-sm"
                />
                <button 
                  type="button"
                  @click="removeOption(idx)"
                  class="text-red-400 hover:text-red-300 p-1"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button" 
              @click="showQuestionModal = false"
              class="flex-1 px-4 py-2.5 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 font-medium"
            >
              {{ saving ? 'Guardando...' : (editingQuestion ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Category Modal -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl">
        <div class="p-6 border-b border-slate-700 flex items-center justify-between">
          <h2 class="text-xl font-bold text-white">Categorías</h2>
          <button @click="showCategoryModal = false" class="text-slate-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div class="p-6">
          <!-- New Category Form -->
          <div class="flex gap-3 mb-6">
            <input 
              v-model="newCategory.name"
              type="text"
              placeholder="Nombre de categoría"
              class="flex-1 bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
            />
            <input 
              v-model="newCategory.color"
              type="color"
              class="w-12 h-10 rounded-lg cursor-pointer bg-slate-800 border border-slate-700"
            />
            <button 
              @click="addCategory"
              class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600"
            >
              Agregar
            </button>
          </div>

          <!-- Categories List -->
          <div class="space-y-3 max-h-[400px] overflow-y-auto">
            <div 
              v-for="cat in categories" 
              :key="cat.id"
              class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <div 
                  class="w-4 h-4 rounded-full"
                  :style="{ backgroundColor: cat.color }"
                ></div>
                <span class="text-white">{{ cat.name }}</span>
                <span class="text-xs text-slate-500">({{ cat.questions_count || 0 }} preguntas)</span>
              </div>
              <button 
                @click="deleteCategory(cat)"
                class="text-slate-400 hover:text-red-400"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/stores/api'

const questions = ref([])
const categories = ref([])
const filterCategory = ref(null)
const filterType = ref(null)
const searchQuery = ref('')

const showQuestionModal = ref(false)
const showCategoryModal = ref(false)
const editingQuestion = ref(null)
const saving = ref(false)

const questionForm = ref({
  text: '',
  description: '',
  question_type: 'single_choice',
  category_id: null,
  options: [],
  max_score: 10,
  required: true,
  is_active: true
})

const newCategory = ref({
  name: '',
  color: '#10b981'
})

const totalMaxScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + (q.max_score || 0), 0)
})

const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    if (filterCategory.value && q.category_id !== filterCategory.value) return false
    if (filterType.value && q.question_type !== filterType.value) return false
    if (searchQuery.value && !q.text.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    return true
  })
})

onMounted(async () => {
  await loadQuestions()
  await loadCategories()
})

async function loadQuestions() {
  try {
    const response = await api.get('/questions')
    questions.value = response.data
  } catch (error) {
    console.error('Error loading questions:', error)
  }
}

async function loadCategories() {
  try {
    const response = await api.get('/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

function openQuestionModal(question = null) {
  editingQuestion.value = question
  if (question) {
    questionForm.value = {
      text: question.text,
      description: question.description || '',
      question_type: question.question_type,
      category_id: question.category_id,
      options: question.options ? [...question.options] : [],
      max_score: question.max_score,
      required: question.required,
      is_active: question.is_active
    }
  } else {
    questionForm.value = {
      text: '',
      description: '',
      question_type: 'single_choice',
      category_id: null,
      options: [
        { value: 'a', text: '', score: 0 },
        { value: 'b', text: '', score: 0 }
      ],
      max_score: 10,
      required: true,
      is_active: true
    }
  }
  showQuestionModal.value = true
}

function addOption() {
  const nextValue = String.fromCharCode(97 + questionForm.value.options.length) // a, b, c, d...
  questionForm.value.options.push({ value: nextValue, text: '', score: 0 })
}

function removeOption(idx) {
  questionForm.value.options.splice(idx, 1)
}

async function saveQuestion() {
  saving.value = true
  try {
    const data = { ...questionForm.value }
    if (!['single_choice', 'multiple_choice'].includes(data.question_type)) {
      data.options = null
    }
    
    if (editingQuestion.value) {
      await api.put(`/questions/${editingQuestion.value.id}`, data)
    } else {
      await api.post('/questions', data)
    }
    
    await loadQuestions()
    showQuestionModal.value = false
  } catch (error) {
    console.error('Error saving question:', error)
    alert(error.response?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

async function duplicateQuestion(question) {
  try {
    const data = {
      ...question,
      text: question.text + ' (copia)',
      id: undefined
    }
    await api.post('/questions', data)
    await loadQuestions()
  } catch (error) {
    console.error('Error duplicating question:', error)
  }
}

async function confirmDelete(question) {
  if (!confirm(`¿Eliminar la pregunta "${question.text.substring(0, 50)}..."?`)) return
  try {
    await api.delete(`/questions/${question.id}`)
    await loadQuestions()
  } catch (error) {
    console.error('Error deleting question:', error)
    alert(error.response?.data?.detail || 'Error al eliminar')
  }
}

async function addCategory() {
  if (!newCategory.value.name) return
  try {
    await api.post('/categories', newCategory.value)
    await loadCategories()
    newCategory.value = { name: '', color: '#10b981' }
  } catch (error) {
    console.error('Error adding category:', error)
  }
}

async function deleteCategory(cat) {
  if (!confirm(`¿Eliminar la categoría "${cat.name}"?`)) return
  try {
    await api.delete(`/categories/${cat.id}`)
    await loadCategories()
  } catch (error) {
    console.error('Error deleting category:', error)
  }
}

function getTypeName(type) {
  const types = {
    single_choice: 'Selección Única',
    multiple_choice: 'Selección Múltiple',
    text: 'Texto Libre',
    scale: 'Escala',
    yes_no: 'Sí/No'
  }
  return types[type] || type
}

function getTypeClass(type) {
  const classes = {
    single_choice: 'bg-blue-500/20 text-blue-400',
    multiple_choice: 'bg-purple-500/20 text-purple-400',
    text: 'bg-amber-500/20 text-amber-400',
    scale: 'bg-cyan-500/20 text-cyan-400',
    yes_no: 'bg-emerald-500/20 text-emerald-400'
  }
  return classes[type] || 'bg-slate-500/20 text-slate-400'
}
</script>
