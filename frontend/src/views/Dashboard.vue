<script setup>
import { ref, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import api from '@/stores/api'
import {
  BuildingOfficeIcon,
  UsersIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

const loading = ref(true)
const stats = ref({
  companies: 0,
  users: 0,
  questionnaires: 0,
  divergences: 0,
  completion_rate: 0,
  responses_today: 0
})

const complianceData = ref({
  labels: [],
  datasets: []
})

const statusData = ref({
  labels: ['Completado', 'En Progreso', 'Pendiente'],
  datasets: [{
    data: [0, 0, 0],
    backgroundColor: ['#10b981', '#f59e0b', '#6b7280']
  }]
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: { callback: (value) => value + '%' }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  }
}

const fetchDashboard = async () => {
  try {
    const response = await api.get('/reports/dashboard')
    const data = response.data
    
    stats.value = {
      companies: data.total_companies || 0,
      users: data.total_users || 0,
      questionnaires: data.total_questionnaires || 0,
      divergences: data.total_divergences || 0,
      completion_rate: data.avg_completion_rate || 0,
      responses_today: data.responses_today || 0
    }
    
    // Compliance by company
    if (data.compliance_by_company) {
      complianceData.value = {
        labels: data.compliance_by_company.map(c => c.name),
        datasets: [{
          label: 'Cumplimiento',
          data: data.compliance_by_company.map(c => c.compliance),
          backgroundColor: '#3b82f6'
        }]
      }
    }
    
    // Status distribution
    if (data.status_distribution) {
      statusData.value.datasets[0].data = [
        data.status_distribution.completed || 0,
        data.status_distribution.in_progress || 0,
        data.status_distribution.pending || 0
      ]
    }
  } catch (error) {
    console.error('Error fetching dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Companies -->
      <div class="stat-card flex items-center">
        <div class="p-3 bg-blue-100 rounded-lg">
          <BuildingOfficeIcon class="w-6 h-6 text-blue-600" />
        </div>
        <div class="ml-4">
          <p class="stat-value">{{ stats.companies }}</p>
          <p class="stat-label">Empresas</p>
        </div>
      </div>
      
      <!-- Users -->
      <div class="stat-card flex items-center">
        <div class="p-3 bg-green-100 rounded-lg">
          <UsersIcon class="w-6 h-6 text-green-600" />
        </div>
        <div class="ml-4">
          <p class="stat-value">{{ stats.users }}</p>
          <p class="stat-label">Usuarios</p>
        </div>
      </div>
      
      <!-- Questionnaires -->
      <div class="stat-card flex items-center">
        <div class="p-3 bg-purple-100 rounded-lg">
          <ClipboardDocumentListIcon class="w-6 h-6 text-purple-600" />
        </div>
        <div class="ml-4">
          <p class="stat-value">{{ stats.questionnaires }}</p>
          <p class="stat-label">Cuestionarios</p>
        </div>
      </div>
      
      <!-- Divergences -->
      <div class="stat-card flex items-center">
        <div class="p-3 bg-red-100 rounded-lg">
          <ExclamationTriangleIcon class="w-6 h-6 text-red-600" />
        </div>
        <div class="ml-4">
          <p class="stat-value">{{ stats.divergences }}</p>
          <p class="stat-label">Divergencias</p>
        </div>
      </div>
    </div>
    
    <!-- Completion Rate Banner -->
    <div class="card p-6 bg-gradient-to-r from-primary-600 to-cyan-500 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium opacity-90">Tasa de Completación Global</h3>
          <p class="text-3xl font-bold mt-1">{{ stats.completion_rate.toFixed(1) }}%</p>
        </div>
        <div class="p-4 bg-white/20 rounded-full">
          <CheckCircleIcon class="w-10 h-10" />
        </div>
      </div>
      <div class="mt-4">
        <div class="progress-bar bg-white/30">
          <div 
            class="progress-bar-fill bg-white"
            :style="{ width: `${stats.completion_rate}%` }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Compliance by Company -->
      <div class="card lg:col-span-2">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Cumplimiento por Empresa</h3>
        </div>
        <div class="card-body">
          <div class="h-64">
            <Bar 
              v-if="complianceData.labels.length > 0"
              :data="complianceData" 
              :options="barOptions" 
            />
            <div v-else class="flex items-center justify-center h-full text-gray-400">
              No hay datos disponibles
            </div>
          </div>
        </div>
      </div>
      
      <!-- Status Distribution -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-900">Estado de Cuestionarios</h3>
        </div>
        <div class="card-body">
          <div class="h-64">
            <Doughnut :data="statusData" :options="doughnutOptions" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="card">
      <div class="card-header">
        <h3 class="text-lg font-medium text-gray-900">Acciones Rápidas</h3>
      </div>
      <div class="card-body">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <router-link 
            to="/companies"
            class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <BuildingOfficeIcon class="w-8 h-8 text-blue-600" />
            <div class="ml-3">
              <p class="font-medium text-gray-900">Nueva Empresa</p>
              <p class="text-sm text-gray-500">Crear cliente</p>
            </div>
          </router-link>
          
          <router-link 
            to="/questions"
            class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ClipboardDocumentListIcon class="w-8 h-8 text-purple-600" />
            <div class="ml-3">
              <p class="font-medium text-gray-900">Banco de Preguntas</p>
              <p class="text-sm text-gray-500">Gestionar preguntas</p>
            </div>
          </router-link>
          
          <router-link 
            to="/questionnaires"
            class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowTrendingUpIcon class="w-8 h-8 text-green-600" />
            <div class="ml-3">
              <p class="font-medium text-gray-900">Nuevo Cuestionario</p>
              <p class="text-sm text-gray-500">Iniciar campaña</p>
            </div>
          </router-link>
          
          <router-link 
            to="/questionnaires"
            class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ExclamationTriangleIcon class="w-8 h-8 text-red-600" />
            <div class="ml-3">
              <p class="font-medium text-gray-900">Ver Divergencias</p>
              <p class="text-sm text-gray-500">Alertas activas</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
