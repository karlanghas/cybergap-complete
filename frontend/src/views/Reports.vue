<template>
  <div class="min-h-screen bg-slate-950 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <button @click="$router.back()" class="flex items-center gap-2 text-slate-400 hover:text-white mb-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Volver
          </button>
          <h1 class="text-3xl font-bold text-white tracking-tight">Reporte de Auditoría</h1>
          <p class="text-slate-400 mt-1">{{ report?.questionnaire?.name || 'Cargando...' }}</p>
        </div>
        <div class="flex gap-3">
          <button 
            @click="calculateDivergences"
            class="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white px-4 py-2.5 rounded-lg transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Recalcular
          </button>
          <button 
            @click="exportExcel"
            class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg transition-all font-medium shadow-lg shadow-emerald-500/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            Exportar Excel
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ report?.compliance_percentage || 0 }}%</div>
            <div class="text-sm text-slate-400">Cumplimiento</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ report?.total_questions || 0 }}</div>
            <div class="text-sm text-slate-400">Preguntas</div>
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
            <div class="text-2xl font-bold text-white">{{ report?.total_responses || 0 }}</div>
            <div class="text-sm text-slate-400">Respuestas</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-white">{{ report?.total_users || 0 }}</div>
            <div class="text-sm text-slate-400">Usuarios</div>
          </div>
        </div>
      </div>

      <div class="bg-slate-900/50 border border-amber-500/30 rounded-xl p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
            <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-amber-400">{{ divergences.length }}</div>
            <div class="text-sm text-slate-400">Divergencias</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Compliance by Area -->
      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Cumplimiento por Área</h3>
        <div class="space-y-4">
          <div v-for="area in report?.by_area || []" :key="area.area_id">
            <div class="flex items-center justify-between text-sm mb-1">
              <span class="text-slate-300">{{ area.area_name }}</span>
              <span class="text-white font-medium">{{ area.compliance }}%</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-3">
              <div 
                class="h-3 rounded-full transition-all"
                :class="getComplianceColor(area.compliance)"
                :style="{ width: `${area.compliance}%` }"
              ></div>
            </div>
          </div>
          <div v-if="!report?.by_area?.length" class="text-center py-8 text-slate-500">
            No hay datos de áreas
          </div>
        </div>
      </div>

      <!-- Compliance by Category -->
      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Cumplimiento por Categoría</h3>
        <div class="space-y-4">
          <div v-for="cat in report?.by_category || []" :key="cat.category_id">
            <div class="flex items-center justify-between text-sm mb-1">
              <span class="text-slate-300">{{ cat.category_name }}</span>
              <span class="text-white font-medium">{{ cat.compliance }}%</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-3">
              <div 
                class="h-3 rounded-full transition-all"
                :class="getComplianceColor(cat.compliance)"
                :style="{ width: `${cat.compliance}%` }"
              ></div>
            </div>
          </div>
          <div v-if="!report?.by_category?.length" class="text-center py-8 text-slate-500">
            No hay datos de categorías
          </div>
        </div>
      </div>
    </div>

    <!-- Divergences Alert Section -->
    <div class="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden mb-8">
      <div class="p-6 border-b border-slate-800">
        <h3 class="text-lg font-semibold text-white flex items-center gap-2">
          <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          Alertas de Divergencia
        </h3>
        <p class="text-sm text-slate-400 mt-1">Respuestas contradictorias detectadas entre usuarios</p>
      </div>

      <div class="divide-y divide-slate-800">
        <div 
          v-for="div in divergences" 
          :key="div.id"
          class="p-5 hover:bg-slate-800/30 transition-colors"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span :class="getSeverityClass(div.severity)" class="px-2.5 py-1 rounded-full text-xs font-bold uppercase">
                  {{ div.severity }}
                </span>
                <span v-if="div.is_resolved" class="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-xs">
                  Resuelto
                </span>
              </div>
              
              <h4 class="text-white font-medium mb-2">{{ div.question_text }}</h4>
              
              <div class="bg-slate-800/50 rounded-lg p-4 space-y-2">
                <div class="text-sm text-slate-400">
                  <strong class="text-slate-300">Respuestas conflictivas:</strong>
                </div>
                <div v-for="(resp, idx) in div.conflicting_responses" :key="idx" class="flex items-center gap-2 text-sm">
                  <span class="w-2 h-2 rounded-full" :class="idx === 0 ? 'bg-blue-400' : 'bg-amber-400'"></span>
                  <span class="text-slate-400">{{ resp.user_name }} ({{ resp.area_name }}):</span>
                  <span class="text-white font-medium">{{ resp.answer }}</span>
                </div>
              </div>
            </div>

            <div class="flex flex-col items-end gap-2">
              <button 
                v-if="!div.is_resolved"
                @click="resolveDivergence(div)"
                class="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 rounded text-sm transition-colors"
              >
                Marcar Resuelto
              </button>
              <div class="text-xs text-slate-500">
                Detectado: {{ formatDate(div.detected_at) }}
              </div>
            </div>
          </div>
        </div>

        <div v-if="divergences.length === 0" class="p-12 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-emerald-500/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <h4 class="text-lg font-medium text-white">Sin divergencias</h4>
          <p class="text-slate-400 mt-1">No se han detectado respuestas contradictorias</p>
        </div>
      </div>
    </div>

    <!-- Detailed Responses -->
    <div class="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
      <div class="p-6 border-b border-slate-800">
        <h3 class="text-lg font-semibold text-white">Respuestas Detalladas</h3>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-800/50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Usuario</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Área</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Pregunta</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Respuesta</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Puntaje</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Fecha</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-for="resp in responses" :key="resp.id" class="hover:bg-slate-800/30">
              <td class="px-6 py-4 text-white">{{ resp.user_name }}</td>
              <td class="px-6 py-4 text-slate-300">{{ resp.area_name }}</td>
              <td class="px-6 py-4 text-slate-300 max-w-xs truncate">{{ resp.question_text }}</td>
              <td class="px-6 py-4 text-white">{{ formatAnswer(resp.answer) }}</td>
              <td class="px-6 py-4">
                <span :class="resp.score > 0 ? 'text-emerald-400' : 'text-slate-400'">
                  {{ resp.score }} / {{ resp.max_score }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-400 text-sm">{{ formatDate(resp.answered_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/stores/api'

const route = useRoute()

const report = ref(null)
const divergences = ref([])
const responses = ref([])

const questionnaireId = route.params.id

onMounted(async () => {
  await loadReport()
  await loadDivergences()
  await loadResponses()
})

async function loadReport() {
  try {
    const response = await api.get(`/reports/questionnaire/${questionnaireId}`)
    report.value = response.data
  } catch (error) {
    console.error('Error loading report:', error)
  }
}

async function loadDivergences() {
  try {
    const response = await api.get(`/questionnaires/${questionnaireId}/divergences`)
    divergences.value = response.data
  } catch (error) {
    console.error('Error loading divergences:', error)
  }
}

async function loadResponses() {
  try {
    const response = await api.get(`/questionnaires/${questionnaireId}/responses`)
    responses.value = response.data
  } catch (error) {
    console.error('Error loading responses:', error)
  }
}

async function calculateDivergences() {
  try {
    await api.post(`/questionnaires/${questionnaireId}/calculate-divergences`)
    await loadDivergences()
    alert('Divergencias recalculadas')
  } catch (error) {
    console.error('Error calculating divergences:', error)
  }
}

async function resolveDivergence(div) {
  const notes = prompt('Notas de resolución (opcional):')
  try {
    await api.put(`/divergences/${div.id}/resolve`, { notes })
    await loadDivergences()
  } catch (error) {
    console.error('Error resolving divergence:', error)
  }
}

async function exportExcel() {
  try {
    const response = await api.get(`/reports/questionnaire/${questionnaireId}/export`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `reporte_${questionnaireId}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Error exporting:', error)
    alert('Error al exportar')
  }
}

function getComplianceColor(value) {
  if (value >= 80) return 'bg-emerald-500'
  if (value >= 60) return 'bg-cyan-500'
  if (value >= 40) return 'bg-amber-500'
  return 'bg-red-500'
}

function getSeverityClass(severity) {
  const classes = {
    LOW: 'bg-slate-500/30 text-slate-300',
    MEDIUM: 'bg-amber-500/30 text-amber-300',
    HIGH: 'bg-orange-500/30 text-orange-300',
    CRITICAL: 'bg-red-500/30 text-red-300'
  }
  return classes[severity] || 'bg-slate-500/30 text-slate-300'
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatAnswer(answer) {
  if (Array.isArray(answer)) return answer.join(', ')
  if (typeof answer === 'object') return JSON.stringify(answer)
  return String(answer)
}
</script>
