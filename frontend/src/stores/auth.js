import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/stores/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  
  // Actions
  async function login(email, password) {
    try {
      console.log('🔐 Login attempt:', { email, password: '***' })
      const payload = { email, password }
      console.log('📤 Sending payload:', JSON.stringify(payload))
      const response = await api.post('/auth/login', payload)
      console.log('✅ Login success')
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      await fetchUser()
      return { success: true }
    } catch (error) {
      console.error('❌ Login error:', error.response?.data)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de autenticación' 
      }
    }
  }
  
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      logout()
    }
  }
  
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
  }
  
  // Initialize auth header if token exists
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser()
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    fetchUser
  }
})
