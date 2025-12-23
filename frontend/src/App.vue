<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'

const route = useRoute()

// Rutas públicas que no necesitan sidebar
const isPublicRoute = computed(() => {
  return route.path.startsWith('/survey') || route.path === '/login'
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Layout para rutas públicas (survey) -->
    <template v-if="isPublicRoute">
      <router-view />
    </template>
    
    <!-- Layout para admin -->
    <template v-else>
      <Sidebar />
      <div class="lg:pl-64">
        <Navbar />
        <main class="p-6">
          <router-view />
        </main>
      </div>
    </template>
  </div>
</template>
