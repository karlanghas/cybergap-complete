<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { Bars3Icon, BellIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const showMobileMenu = ref(false)

const pageTitle = () => {
  const titles = {
    '/': 'Dashboard',
    '/companies': 'Empresas',
    '/questions': 'Banco de Preguntas',
    '/questionnaires': 'Cuestionarios'
  }
  
  if (route.path.startsWith('/companies/')) return 'Detalle de Empresa'
  if (route.path.startsWith('/questionnaires/')) return 'Detalle de Cuestionario'
  if (route.path.startsWith('/divergences/')) return 'Alertas de Divergencia'
  
  return titles[route.path] || 'CyberGAP'
}
</script>

<template>
  <header class="sticky top-0 z-30 bg-white border-b border-gray-200">
    <div class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
      <!-- Mobile menu button -->
      <button
        @click="showMobileMenu = !showMobileMenu"
        class="lg:hidden p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100"
      >
        <Bars3Icon class="w-6 h-6" />
      </button>
      
      <!-- Page Title -->
      <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle() }}</h1>
      
      <!-- Right side -->
      <div class="flex items-center space-x-4">
        <button class="relative p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100 rounded-full">
          <BellIcon class="w-6 h-6" />
          <span class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
      </div>
    </div>
  </header>
</template>
