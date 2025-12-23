<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/stores/api'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  BuildingOfficeIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const companies = ref([])
const loading = ref(true)
const searchQuery = ref('')
const showModal = ref(false)
const editingCompany = ref(null)

const form = ref({
  name: '',
  rut: '',
  industry: '',
  contact_name: '',
  contact_email: '',
  contact_phone: ''
})

const fetchCompanies = async () => {
  try {
    const response = await api.get('/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Error fetching companies:', error)
  } finally {
    loading.value = false
  }
}

const openModal = (company = null) => {
  editingCompany.value = company
  if (company) {
    form.value = { ...company }
  } else {
    form.value = {
      name: '',
      rut: '',
      industry: '',
      contact_name: '',
      contact_email: '',
      contact_phone: ''
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCompany.value = null
}

const saveCompany = async () => {
  try {
    if (editingCompany.value) {
      await api.put(`/companies/${editingCompany.value.id}`, form.value)
    } else {
      await api.post('/companies', form.value)
    }
    closeModal()
    fetchCompanies()
  } catch (error) {
    console.error('Error saving company:', error)
    alert(error.response?.data?.detail || 'Error al guardar')
  }
}

const deleteCompany = async (company) => {
  if (!confirm(`¿Eliminar empresa "${company.name}"?`)) return
  try {
    await api.delete(`/companies/${company.id}`)
    fetchCompanies()
  } catch (error) {
    console.error('Error deleting company:', error)
  }
}

const filteredCompanies = () => {
  if (!searchQuery.value) return companies.value
  const query = searchQuery.value.toLowerCase()
  return companies.value.filter(c => 
    c.name.toLowerCase().includes(query) ||
    c.rut?.toLowerCase().includes(query)
  )
}

onMounted(fetchCompanies)
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="relative flex-1 max-w-md">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar empresas..."
          class="form-input pl-10"
        />
      </div>
      <button @click="openModal()" class="btn-primary flex items-center">
        <PlusIcon class="w-5 h-5 mr-2" />
        Nueva Empresa
      </button>
    </div>
    
    <!-- Companies Grid -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>
    
    <div v-else-if="filteredCompanies().length === 0" class="text-center py-12">
      <BuildingOfficeIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900">No hay empresas</h3>
      <p class="text-gray-500 mt-1">Crea tu primera empresa para comenzar</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="company in filteredCompanies()"
        :key="company.id"
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="router.push(`/companies/${company.id}`)"
      >
        <div class="card-body">
          <div class="flex items-start justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <BuildingOfficeIcon class="w-6 h-6 text-primary-600" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">{{ company.name }}</h3>
                <p class="text-sm text-gray-500">{{ company.rut || 'Sin RUT' }}</p>
              </div>
            </div>
            <div class="flex space-x-2" @click.stop>
              <button 
                @click="openModal(company)"
                class="p-2 text-gray-400 hover:text-primary-600 hover:bg-gray-100 rounded-lg"
              >
                <PencilIcon class="w-5 h-5" />
              </button>
              <button 
                @click="deleteCompany(company)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-gray-100 rounded-lg"
              >
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div class="mt-4 pt-4 border-t border-gray-100">
            <div class="grid grid-cols-3 gap-4 text-center">
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ company.areas_count || 0 }}</p>
                <p class="text-xs text-gray-500">Áreas</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ company.users_count || 0 }}</p>
                <p class="text-xs text-gray-500">Usuarios</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ company.questionnaires_count || 0 }}</p>
                <p class="text-xs text-gray-500">Encuestas</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-black/50" @click="closeModal"></div>
        <div class="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingCompany ? 'Editar Empresa' : 'Nueva Empresa' }}
          </h3>
          
          <form @submit.prevent="saveCompany" class="space-y-4">
            <div>
              <label class="form-label">Nombre *</label>
              <input v-model="form.name" type="text" required class="form-input" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">RUT</label>
                <input v-model="form.rut" type="text" class="form-input" placeholder="12.345.678-9" />
              </div>
              <div>
                <label class="form-label">Industria</label>
                <input v-model="form.industry" type="text" class="form-input" />
              </div>
            </div>
            <div>
              <label class="form-label">Contacto</label>
              <input v-model="form.contact_name" type="text" class="form-input" placeholder="Nombre del contacto" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">Email</label>
                <input v-model="form.contact_email" type="email" class="form-input" />
              </div>
              <div>
                <label class="form-label">Teléfono</label>
                <input v-model="form.contact_phone" type="text" class="form-input" />
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeModal" class="btn-secondary">Cancelar</button>
              <button type="submit" class="btn-primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
