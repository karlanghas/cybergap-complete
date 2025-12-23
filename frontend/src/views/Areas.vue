<template>
  <div class="min-h-screen bg-slate-950 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">Áreas</h1>
          <p class="text-slate-400 mt-1">Gestión de áreas organizacionales por empresa</p>
        </div>
        <button 
          @click="openModal()" 
          class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg transition-all duration-200 font-medium shadow-lg shadow-emerald-500/25"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nueva Área
        </button>
      </div>
    </div>

    <!-- Company Filter -->
    <div class="mb-6">
      <select 
        v-model="selectedCompany" 
        @change="loadAreas"
        class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-w-[300px]"
      >
        <option :value="null">Seleccionar empresa...</option>
        <option v-for="company in companies" :key="company.id" :value="company.id">
          {{ company.name }}
        </option>
      </select>
    </div>

    <!-- Areas Tree -->
    <div v-if="selectedCompany" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Tree View -->
      <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
          Estructura Organizacional
        </h3>
        
        <div v-if="areasTree.length === 0" class="text-center py-8">
          <div class="text-slate-500">No hay áreas creadas</div>
          <button @click="openModal()" class="mt-4 text-emerald-400 hover:text-emerald-300">
            Crear primera área
          </button>
        </div>
        
        <div v-else class="space-y-2">
          <AreaTreeItem 
            v-for="area in areasTree" 
            :key="area.id" 
            :area="area" 
            :level="0"
            @edit="openModal"
            @delete="confirmDelete"
            @add-child="openModal(null, $event)"
          />
        </div>
      </div>

      <!-- Stats Panel -->
      <div class="space-y-6">
        <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">Resumen</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-slate-800/50 rounded-lg p-4">
              <div class="text-3xl font-bold text-emerald-400">{{ flatAreas.length }}</div>
              <div class="text-sm text-slate-400">Total Áreas</div>
            </div>
            <div class="bg-slate-800/50 rounded-lg p-4">
              <div class="text-3xl font-bold text-blue-400">{{ totalUsers }}</div>
              <div class="text-sm text-slate-400">Total Usuarios</div>
            </div>
          </div>
        </div>

        <!-- Recent Areas -->
        <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h3 class="text-lg font-semibold text-white mb-4">Áreas Recientes</h3>
          <div class="space-y-3">
            <div 
              v-for="area in flatAreas.slice(0, 5)" 
              :key="area.id"
              class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
            >
              <div>
                <div class="text-white font-medium">{{ area.name }}</div>
                <div class="text-sm text-slate-400">{{ area.users_count || 0 }} usuarios</div>
              </div>
              <span 
                :class="area.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'"
                class="px-2 py-1 rounded text-xs font-medium"
              >
                {{ area.is_active ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <svg class="w-16 h-16 text-slate-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
      </svg>
      <h3 class="text-xl font-medium text-slate-400">Selecciona una empresa</h3>
      <p class="text-slate-500 mt-2">Elige una empresa para ver y gestionar sus áreas</p>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md shadow-2xl">
        <div class="p-6 border-b border-slate-700">
          <h2 class="text-xl font-bold text-white">
            {{ editingArea ? 'Editar Área' : 'Nueva Área' }}
          </h2>
        </div>
        
        <form @submit.prevent="saveArea" class="p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Nombre del Área *</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="Ej: Gerencia de TI"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Descripción</label>
            <textarea 
              v-model="form.description" 
              rows="3"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
              placeholder="Descripción del área..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Área Padre</label>
            <select 
              v-model="form.parent_id"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option :value="null">Sin área padre (Nivel raíz)</option>
              <option 
                v-for="area in availableParents" 
                :key="area.id" 
                :value="area.id"
              >
                {{ '—'.repeat(area.level || 0) }} {{ area.name }}
              </option>
            </select>
          </div>

          <div class="flex items-center gap-3">
            <input 
              type="checkbox" 
              v-model="form.is_active" 
              id="is_active"
              class="w-4 h-4 text-emerald-500 bg-slate-800 border-slate-700 rounded focus:ring-emerald-500"
            />
            <label for="is_active" class="text-sm text-slate-300">Área activa</label>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button" 
              @click="closeModal"
              class="flex-1 px-4 py-2.5 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ saving ? 'Guardando...' : (editingArea ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '../stores/api'
import AreaTreeItem from '../components/AreaTreeItem.vue'

const api = useApi()

const companies = ref([])
const selectedCompany = ref(null)
const areasTree = ref([])
const flatAreas = ref([])
const showModal = ref(false)
const editingArea = ref(null)
const saving = ref(false)

const form = ref({
  name: '',
  description: '',
  parent_id: null,
  is_active: true
})

const totalUsers = computed(() => {
  return flatAreas.value.reduce((sum, area) => sum + (area.users_count || 0), 0)
})

const availableParents = computed(() => {
  if (!editingArea.value) return flatAreas.value
  // Exclude self and children when editing
  const excludeIds = new Set([editingArea.value.id])
  const addChildren = (areas) => {
    areas.forEach(a => {
      if (a.parent_id === editingArea.value.id) {
        excludeIds.add(a.id)
      }
    })
  }
  addChildren(flatAreas.value)
  return flatAreas.value.filter(a => !excludeIds.has(a.id))
})

onMounted(async () => {
  await loadCompanies()
})

async function loadCompanies() {
  try {
    const response = await api.get('/companies')
    companies.value = response.data
    if (companies.value.length === 1) {
      selectedCompany.value = companies.value[0].id
      await loadAreas()
    }
  } catch (error) {
    console.error('Error loading companies:', error)
  }
}

async function loadAreas() {
  if (!selectedCompany.value) {
    areasTree.value = []
    flatAreas.value = []
    return
  }
  
  try {
    // Load tree structure
    const treeResponse = await api.get(`/areas/tree/${selectedCompany.value}`)
    areasTree.value = treeResponse.data
    
    // Load flat list for stats
    const flatResponse = await api.get(`/areas?company_id=${selectedCompany.value}`)
    flatAreas.value = flatResponse.data
  } catch (error) {
    console.error('Error loading areas:', error)
  }
}

function openModal(area = null, parentId = null) {
  editingArea.value = area
  if (area) {
    form.value = {
      name: area.name,
      description: area.description || '',
      parent_id: area.parent_id,
      is_active: area.is_active
    }
  } else {
    form.value = {
      name: '',
      description: '',
      parent_id: parentId,
      is_active: true
    }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingArea.value = null
  form.value = { name: '', description: '', parent_id: null, is_active: true }
}

async function saveArea() {
  saving.value = true
  try {
    const data = {
      ...form.value,
      company_id: selectedCompany.value
    }
    
    if (editingArea.value) {
      await api.put(`/areas/${editingArea.value.id}`, data)
    } else {
      await api.post('/areas', data)
    }
    
    await loadAreas()
    closeModal()
  } catch (error) {
    console.error('Error saving area:', error)
    alert(error.response?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(area) {
  if (!confirm(`¿Eliminar el área "${area.name}"? Esta acción no se puede deshacer.`)) {
    return
  }
  
  try {
    await api.delete(`/areas/${area.id}`)
    await loadAreas()
  } catch (error) {
    console.error('Error deleting area:', error)
    alert(error.response?.data?.detail || 'Error al eliminar')
  }
}
</script>
