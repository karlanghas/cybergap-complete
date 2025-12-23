<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  BuildingOfficeIcon,
  MapIcon,
  UsersIcon,
  QuestionMarkCircleIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  ArrowRightOnRectangleIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { name: 'Dashboard', path: '/', icon: HomeIcon },
  { name: 'Empresas', path: '/companies', icon: BuildingOfficeIcon },
  { name: 'Áreas', path: '/areas', icon: MapIcon },
  { name: 'Usuarios', path: '/users', icon: UsersIcon },
  { name: 'Banco de Preguntas', path: '/questions', icon: QuestionMarkCircleIcon },
  { name: 'Cuestionarios', path: '/questionnaires', icon: ClipboardDocumentListIcon },
  { name: 'Reportes', path: '/reports', icon: ChartBarIcon },
]

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar hidden lg:block">
    <!-- Logo -->
    <div class="flex items-center justify-center h-16 border-b border-gray-700">
      <ShieldCheckIcon class="w-8 h-8 text-cyan-400" />
      <span class="ml-2 text-xl font-bold text-gradient">CyberGAP</span>
    </div>
    
    <!-- Navigation -->
    <nav class="mt-6 px-2">
      <div class="space-y-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="['sidebar-link', { active: isActive(item.path) }]"
        >
          <component :is="item.icon" class="w-5 h-5 mr-3" />
          {{ item.name }}
        </router-link>
      </div>
    </nav>
    
    <!-- User Section -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
      <div class="flex items-center mb-3">
        <div class="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
          <span class="text-white font-medium">
            {{ authStore.user?.full_name?.charAt(0) || 'A' }}
          </span>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-white">{{ authStore.user?.full_name || 'Admin' }}</p>
          <p class="text-xs text-gray-400">{{ authStore.user?.email }}</p>
        </div>
      </div>
      <button
        @click="logout"
        class="w-full flex items-center px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
      >
        <ArrowRightOnRectangleIcon class="w-5 h-5 mr-2" />
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>
