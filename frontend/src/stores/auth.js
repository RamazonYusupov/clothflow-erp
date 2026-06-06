import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user  = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // ── Role helpers ──────────────────────────────────────────────────────────
  const isAdmin   = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => user.value?.role === 'manager')
  const isKassir  = computed(() => user.value?.role === 'kassir')
  const isOmbochi = computed(() => user.value?.role === 'ombochi')

  const canDelete       = computed(() => user.value?.role === 'admin')
  const canViewReports  = computed(() => ['admin', 'manager'].includes(user.value?.role))
  const canManageUsers  = computed(() => user.value?.role === 'admin')
  const canEditProduct  = computed(() => ['admin', 'ombochi'].includes(user.value?.role))
  const canCreateOrder  = computed(() => ['admin', 'manager', 'kassir'].includes(user.value?.role))
  const canEditOrder    = computed(() => ['admin', 'manager'].includes(user.value?.role))
  const canEditCustomer = computed(() => ['admin', 'manager'].includes(user.value?.role))
  const canViewCustomers= computed(() => ['admin', 'manager', 'kassir'].includes(user.value?.role))
  const canViewOrders   = computed(() => ['admin', 'manager', 'kassir'].includes(user.value?.role))

  function hasRole(...roles) {
    return roles.includes(user.value?.role)
  }

  // ── Actions ───────────────────────────────────────────────────────────────
  async function login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    localStorage.setItem('access_token', token.value)
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('access_token')
  }

  if (token.value && !user.value) {
    fetchMe()
  }

  return {
    token, user, isAuthenticated,
    isAdmin, isManager, isKassir, isOmbochi,
    canDelete, canViewReports, canManageUsers,
    canEditProduct, canCreateOrder, canEditOrder,
    canEditCustomer, canViewCustomers, canViewOrders,
    hasRole, login, logout, fetchMe,
  }
})
