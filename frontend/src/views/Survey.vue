<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900">
    <!-- Loading State -->
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-400">Cargando cuestionario...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="min-h-screen flex items-center justify-center p-4">
      <div class="bg-slate-900/80 border border-red-500/30 rounded-2xl p-8 max-w-md text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <h2 class="text-xl font-bold text-white mb-2">{{ error.title || 'Error' }}</h2>
        <p class="text-slate-400">{{ error.message }}</p>
      </div>
    </div>

    <!-- Completed State -->
    <div v-else-if="completed" class="min-h-screen flex items-center justify-center p-4">
      <div class="bg-slate-900/80 border border-emerald-500/30 rounded-2xl p-8 max-w-md text-center">
        <div class="w-20 h-20 mx-auto mb-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">¡Gracias!</h2>
        <p class="text-slate-400 mb-6">Tus respuestas han sido registradas correctamente.</p>
        <p class="text-sm text-slate-500">Puedes cerrar esta ventana.</p>
      </div>
    </div>

    <!-- Survey Form -->
    <div v-else class="max-w-3xl mx-auto p-4 py-8">
      <!-- Header -->
      <div class="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl p-6 mb-6">
        <div class="flex items-center gap-4 mb-4">
          <img 
            v-if="survey?.info?.company_logo" 
            :src="survey.info.company_logo" 
            class="h-12 w-auto"
            alt="Logo"
          />
          <div v-else class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-white">{{ survey?.info?.questionnaire_name }}</h1>
            <p class="text-slate-400">{{ survey?.info?.company_name }}</p>
          </div>
        </div>
        
        <div class="flex items-center justify-between text-sm">
          <span class="text-slate-400">
            Hola, <span class="text-white font-medium">{{ survey?.info?.user_name }}</span>
          </span>
          <span class="text-slate-400">
            {{ currentIndex + 1 }} de {{ survey?.questions?.length || 0 }} preguntas
          </span>
        </div>
        
        <!-- Progress Bar -->
        <div class="mt-4 w-full bg-slate-700 rounded-full h-2">
          <div 
            class="bg-emerald-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Question Card -->
      <div v-if="currentQuestion" class="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl p-6 mb-6">
        <div class="mb-6">
          <span class="text-xs text-emerald-400 uppercase tracking-wider font-medium">
            Pregunta {{ currentIndex + 1 }}
          </span>
          <h2 class="text-xl font-semibold text-white mt-2">{{ currentQuestion.text }}</h2>
          <p v-if="currentQuestion.description" class="text-slate-400 mt-2">
            {{ currentQuestion.description }}
          </p>
        </div>

        <!-- Answer Input based on type -->
        <div class="space-y-4">
          <!-- Single Choice -->
          <div v-if="currentQuestion.question_type === 'single_choice'" class="space-y-3">
            <label 
              v-for="opt in currentQuestion.options" 
              :key="opt.value"
              class="flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl cursor-pointer transition-all"
              :class="{ 'border-emerald-500 bg-emerald-500/10': answers[currentQuestion.assignment_id] === opt.value }"
            >
              <input 
                type="radio" 
                :name="`q_${currentQuestion.assignment_id}`"
                :value="opt.value"
                v-model="answers[currentQuestion.assignment_id]"
                class="w-5 h-5 text-emerald-500 bg-slate-700 border-slate-600 focus:ring-emerald-500"
              />
              <span class="text-white">{{ opt.text }}</span>
            </label>
          </div>

          <!-- Multiple Choice -->
          <div v-else-if="currentQuestion.question_type === 'multiple_choice'" class="space-y-3">
            <label 
              v-for="opt in currentQuestion.options" 
              :key="opt.value"
              class="flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl cursor-pointer transition-all"
              :class="{ 'border-emerald-500 bg-emerald-500/10': (answers[currentQuestion.assignment_id] || []).includes(opt.value) }"
            >
              <input 
                type="checkbox" 
                :value="opt.value"
                v-model="answers[currentQuestion.assignment_id]"
                class="w-5 h-5 text-emerald-500 bg-slate-700 border-slate-600 rounded focus:ring-emerald-500"
              />
              <span class="text-white">{{ opt.text }}</span>
            </label>
          </div>

          <!-- Yes/No -->
          <div v-else-if="currentQuestion.question_type === 'yes_no'" class="flex gap-4">
            <button 
              @click="answers[currentQuestion.assignment_id] = 'yes'"
              class="flex-1 p-4 rounded-xl border-2 transition-all"
              :class="answers[currentQuestion.assignment_id] === 'yes' 
                ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400' 
                : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800'"
            >
              <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Sí
            </button>
            <button 
              @click="answers[currentQuestion.assignment_id] = 'no'"
              class="flex-1 p-4 rounded-xl border-2 transition-all"
              :class="answers[currentQuestion.assignment_id] === 'no' 
                ? 'border-red-500 bg-red-500/20 text-red-400' 
                : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800'"
            >
              <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
              No
            </button>
          </div>

          <!-- Scale -->
          <div v-else-if="currentQuestion.question_type === 'scale'" class="space-y-4">
            <div class="flex justify-between gap-2">
              <button 
                v-for="n in 5" 
                :key="n"
                @click="answers[currentQuestion.assignment_id] = n"
                class="flex-1 py-4 rounded-xl border-2 text-xl font-bold transition-all"
                :class="answers[currentQuestion.assignment_id] === n 
                  ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400' 
                  : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800'"
              >
                {{ n }}
              </button>
            </div>
            <div class="flex justify-between text-sm text-slate-500">
              <span>Totalmente en desacuerdo</span>
              <span>Totalmente de acuerdo</span>
            </div>
          </div>

          <!-- Text -->
          <div v-else-if="currentQuestion.question_type === 'text'">
            <textarea 
              v-model="answers[currentQuestion.assignment_id]"
              rows="5"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
              placeholder="Escribe tu respuesta aquí..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex items-center justify-between gap-4">
        <button 
          @click="previousQuestion"
          :disabled="currentIndex === 0"
          class="px-6 py-3 bg-slate-800 text-white rounded-xl hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Anterior
          </span>
        </button>

        <button 
          v-if="currentIndex < (survey?.questions?.length || 0) - 1"
          @click="nextQuestion"
          :disabled="!hasAnswer"
          class="px-6 py-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          <span class="flex items-center gap-2">
            Siguiente
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </span>
        </button>

        <button 
          v-else
          @click="submitSurvey"
          :disabled="!hasAnswer || submitting"
          class="px-8 py-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          <span v-if="submitting" class="flex items-center gap-2">
            <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Enviando...
          </span>
          <span v-else class="flex items-center gap-2">
            Enviar Respuestas
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const token = route.params.token

const loading = ref(true)
const error = ref(null)
const completed = ref(false)
const submitting = ref(false)

const survey = ref(null)
const currentIndex = ref(0)
const answers = ref({})

const currentQuestion = computed(() => {
  return survey.value?.questions?.[currentIndex.value]
})

const progress = computed(() => {
  if (!survey.value?.questions?.length) return 0
  const answered = Object.keys(answers.value).filter(k => answers.value[k] !== undefined && answers.value[k] !== '').length
  return Math.round((answered / survey.value.questions.length) * 100)
})

const hasAnswer = computed(() => {
  if (!currentQuestion.value) return false
  const answer = answers.value[currentQuestion.value.assignment_id]
  if (answer === undefined || answer === null || answer === '') return false
  if (Array.isArray(answer) && answer.length === 0) return false
  return true
})

onMounted(async () => {
  await loadSurvey()
})

async function loadSurvey() {
  try {
    const response = await axios.get(`/api/public/survey/${token}`)
    survey.value = response.data
    
    // Initialize answers object
    survey.value.questions.forEach(q => {
      if (q.question_type === 'multiple_choice') {
        answers.value[q.assignment_id] = []
      } else {
        answers.value[q.assignment_id] = null
      }
    })
  } catch (err) {
    console.error('Error loading survey:', err)
    if (err.response?.status === 404) {
      error.value = {
        title: 'Enlace Inválido',
        message: 'Este enlace no es válido o ya no existe.'
      }
    } else if (err.response?.status === 410) {
      error.value = {
        title: 'Enlace Expirado',
        message: err.response.data.detail || 'Este cuestionario ya fue completado o ha expirado.'
      }
    } else {
      error.value = {
        title: 'Error',
        message: 'Ocurrió un error al cargar el cuestionario.'
      }
    }
  } finally {
    loading.value = false
  }
}

function nextQuestion() {
  if (currentIndex.value < survey.value.questions.length - 1) {
    currentIndex.value++
  }
}

function previousQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

async function submitSurvey() {
  submitting.value = true
  
  try {
    const responses = survey.value.questions.map(q => ({
      assignment_id: q.assignment_id,
      answer: answers.value[q.assignment_id],
      time_spent_seconds: 0 // Could track this with timers
    }))
    
    await axios.post(`/api/public/survey/${token}/submit`, { responses })
    completed.value = true
  } catch (err) {
    console.error('Error submitting:', err)
    alert(err.response?.data?.detail || 'Error al enviar las respuestas')
  } finally {
    submitting.value = false
  }
}
</script>
