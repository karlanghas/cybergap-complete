<template>
  <div class="min-h-screen bg-slate-950 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">Usuarios</h1>
          <p class="text-slate-400 mt-1">Gestión de usuarios por área organizacional</p>
        </div>
        <div class="flex gap-3">
          <button 
            @click="showBulkModal = true"
            class="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2.5 rounded-lg transition-all duration-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            Importar
          </button>
          <button 
            @click="openModal()" 
            class="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-lg transition-all duration-200 font-medium shadow-lg shadow-emerald-500/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Nuevo Usuario
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <select 
          v-model="filters.company_id" 
          @change="onCompanyChange"
          class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
        >
          <option :value="null">Todas las empresas</option>
          <option v-for="company in companies" :key="company.id" :value="company.id">
            {{ company.name }}
          </option>
        </select>

        <select 
          v-model="filters.area_id"
          class="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
          :disabled="!filters.company_id"
        >
          <option :value="null">Todas las áreas</option>
          <option v-for="area in areas" :key="area.id" :value="area.id">
            {{ area.name }}
          </option>
        </select>

        <div class="flex-1">
          <input 
            v-model="filters.search"
            type="text"
            placeholder="Buscar por nombre o email..."
            class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <button 
          @click="loadUsers"
          class="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-800/50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Usuario</th>
            <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Empresa</th>
            <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Área</th>
            <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Cargo</th>
            <th class="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Estado</th>
            <th class="px-6 py-4 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800">
          <tr v-for="user in users" :key="user.id" class="hover:bg-slate-800/30 transition-colors">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-white font-bold">
                  {{ getInitials(user.full_name) }}
                </div>
                <div>
                  <div class="text-white font-medium">{{ user.full_name }}</div>
                  <div class="text-sm text-slate-400">{{ user.email }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-slate-300">{{ user.company_name || '—' }}</td>
            <td class="px-6 py-4 text-slate-300">{{ user.area_name || '—' }}</td>
            <td class="px-6 py-4 text-slate-300">{{ user.position || '—' }}</td>
            <td class="px-6 py-4">
              <span 
                :class="user.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'"
                class="px-2.5 py-1 rounded-full text-xs font-medium"
              >
                {{ user.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center justify-end gap-2">
                <button 
                  @click="openModal(user)"
                  class="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700 rounded-lg transition-colors"
                  title="Editar"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button 
                  @click="confirmDelete(user)"
                  class="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded-lg transition-colors"
                  title="Eliminar"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="px-6 py-12 text-center text-slate-500">
              <svg class="w-12 h-12 mx-auto mb-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              No hay usuarios para mostrar
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- User Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl">
        <div class="p-6 border-b border-slate-700">
          <h2 class="text-xl font-bold text-white">
            {{ editingUser ? 'Editar Usuario' : 'Nuevo Usuario' }}
          </h2>
        </div>
        
        <form @submit.prevent="saveUser" class="p-6 space-y-5">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-300 mb-2">Nombre Completo *</label>
              <input 
                v-model="form.full_name" 
                type="text" 
                required
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
                placeholder="Juan Pérez"
              />
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-300 mb-2">Email *</label>
              <input 
                v-model="form.email" 
                type="email" 
                required
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
                placeholder="juan@empresa.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Empresa *</label>
              <select 
                v-model="form.company_id"
                @change="loadAreasForForm"
                required
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
              >
                <option :value="null" disabled>Seleccionar...</option>
                <option v-for="company in companies" :key="company.id" :value="company.id">
                  {{ company.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Área *</label>
              <select 
                v-model="form.area_id"
                required
                :disabled="!form.company_id"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
              >
                <option :value="null" disabled>Seleccionar...</option>
                <option v-for="area in formAreas" :key="area.id" :value="area.id">
                  {{ area.name }}
                </option>
              </select>
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-300 mb-2">Cargo</label>
              <input 
                v-model="form.position" 
                type="text"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
                placeholder="Gerente de TI"
              />
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-slate-300 mb-2">Teléfono</label>
              <input 
                v-model="form.phone" 
                type="tel"
                class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
                placeholder="+56 9 1234 5678"
              />
            </div>
          </div>

          <div class="flex items-center gap-3">
            <input 
              type="checkbox" 
              v-model="form.is_active" 
              id="user_active"
              class="w-4 h-4 text-emerald-500 bg-slate-800 border-slate-700 rounded focus:ring-emerald-500"
            />
            <label for="user_active" class="text-sm text-slate-300">Usuario activo</label>
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
              class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 font-medium"
            >
              {{ saving ? 'Guardando...' : (editingUser ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Bulk Import Modal -->
    <div v-if="showBulkModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl shadow-2xl">
        <div class="p-6 border-b border-slate-700">
          <h2 class="text-xl font-bold text-white">Importar Usuarios</h2>
          <p class="text-slate-400 text-sm mt-1">Importa múltiples usuarios desde un archivo CSV o manualmente</p>
        </div>
        
        <div class="p-6">
          <div class="mb-6">
            <label class="block text-sm font-medium text-slate-300 mb-2">Empresa destino *</label>
            <select 
              v-model="bulkForm.company_id"
              @change="loadAreasForBulk"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500"
            >
              <option :value="null" disabled>Seleccionar empresa...</option>
              <option v-for="company in companies" :key="company.id" :value="company.id">
                {{ company.name }}
              </option>
            </select>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Datos de usuarios (JSON)
            </label>
            <textarea 
              v-model="bulkForm.data"
              rows="10"
              class="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-emerald-500 font-mono text-sm"
              placeholder='[
  {"full_name": "Juan Pérez", "email": "juan@empresa.com", "area_id": 1, "position": "Gerente"},
  {"full_name": "María García", "email": "maria@empresa.com", "area_id": 2, "position": "Analista"}
]'
            ></textarea>
          </div>

          <div class="bg-slate-800/50 rounded-lg p-4 mb-6">
            <div class="text-sm text-slate-400">
              <strong class="text-slate-300">Áreas disponibles:</strong>
              <div class="mt-2 flex flex-wrap gap-2">
                <span v-for="area in bulkAreas" :key="area.id" class="px-2 py-1 bg-slate-700 rounded text-xs">
                  ID {{ area.id }}: {{ area.name }}
                </span>
                <span v-if="bulkAreas.length === 0" class="text-slate-500">Selecciona una empresa primero</span>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button 
              type="button" 
              @click="showBulkModal = false"
              class="flex-1 px-4 py-2.5 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button 
              @click="importUsers"
              :disabled="!bulkForm.company_id || !bulkForm.data"
              class="flex-1 px-4 py-2.5 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50 font-medium"
            >
              Importar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/stores/api'

const users = ref([])
const companies = ref([])
const areas = ref([])
const formAreas = ref([])
const bulkAreas = ref([])

const showModal = ref(false)
const showBulkModal = ref(false)
const editingUser = ref(null)
const saving = ref(false)

const filters = ref({
  company_id: null,
  area_id: null,
  search: ''
})

const form = ref({
  full_name: '',
  email: '',
  company_id: null,
  area_id: null,
  position: '',
  phone: '',
  is_active: true
})

const bulkForm = ref({
  company_id: null,
  data: ''
})

onMounted(async () => {
  await loadCompanies()
  await loadUsers()
})

async function loadCompanies() {
  try {
    const response = await api.get('/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Error loading companies:', error)
  }
}

async function loadUsers() {
  try {
    let url = '/users?'
    if (filters.value.company_id) url += `company_id=${filters.value.company_id}&`
    if (filters.value.area_id) url += `area_id=${filters.value.area_id}&`
    if (filters.value.search) url += `search=${filters.value.search}&`
    
    const response = await api.get(url)
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
  }
}

async function onCompanyChange() {
  filters.value.area_id = null
  if (filters.value.company_id) {
    const response = await api.get(`/areas?company_id=${filters.value.company_id}`)
    areas.value = response.data
  } else {
    areas.value = []
  }
  await loadUsers()
}

async function loadAreasForForm() {
  if (form.value.company_id) {
    const response = await api.get(`/areas?company_id=${form.value.company_id}`)
    formAreas.value = response.data
  } else {
    formAreas.value = []
  }
  form.value.area_id = null
}

async function loadAreasForBulk() {
  if (bulkForm.value.company_id) {
    const response = await api.get(`/areas?company_id=${bulkForm.value.company_id}`)
    bulkAreas.value = response.data
  } else {
    bulkAreas.value = []
  }
}

function openModal(user = null) {
  editingUser.value = user
  if (user) {
    form.value = {
      full_name: user.full_name,
      email: user.email,
      company_id: user.company_id,
      area_id: user.area_id,
      position: user.position || '',
      phone: user.phone || '',
      is_active: user.is_active
    }
    loadAreasForForm()
  } else {
    form.value = {
      full_name: '',
      email: '',
      company_id: filters.value.company_id,
      area_id: filters.value.area_id,
      position: '',
      phone: '',
      is_active: true
    }
    if (form.value.company_id) {
      loadAreasForForm()
    }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingUser.value = null
}

async function saveUser() {
  saving.value = true
  try {
    if (editingUser.value) {
      await api.put(`/users/${editingUser.value.id}`, form.value)
    } else {
      await api.post('/users', form.value)
    }
    await loadUsers()
    closeModal()
  } catch (error) {
    console.error('Error saving user:', error)
    alert(error.response?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(user) {
  if (!confirm(`¿Eliminar a "${user.full_name}"?`)) return
  
  try {
    await api.delete(`/users/${user.id}`)
    await loadUsers()
  } catch (error) {
    console.error('Error deleting user:', error)
    alert(error.response?.data?.detail || 'Error al eliminar')
  }
}

async function importUsers() {
  try {
    const data = JSON.parse(bulkForm.value.data)
    await api.post('/users/bulk', {
      company_id: bulkForm.value.company_id,
      users: data
    })
    showBulkModal.value = false
    bulkForm.value = { company_id: null, data: '' }
    await loadUsers()
    alert('Usuarios importados correctamente')
  } catch (error) {
    console.error('Error importing users:', error)
    alert(error.response?.data?.detail || 'Error al importar. Verifica el formato JSON.')
  }
}

function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
}
</script>
