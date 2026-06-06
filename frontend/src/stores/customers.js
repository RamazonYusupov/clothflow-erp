import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useCustomersStore = defineStore('customers', () => {
  const customers = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchCustomers(params = {}) {
    loading.value = true
    try {
      const res = await api.get('/customers', { params })
      customers.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function getCustomer(id) {
    const res = await api.get(`/customers/${id}`)
    return res.data
  }

  async function createCustomer(data) {
    const res = await api.post('/customers', data)
    return res.data
  }

  async function updateCustomer(id, data) {
    const res = await api.put(`/customers/${id}`, data)
    return res.data
  }

  async function deleteCustomer(id) {
    await api.delete(`/customers/${id}`)
  }

  return { customers, total, loading, fetchCustomers, getCustomer, createCustomer, updateCustomer, deleteCustomer }
})
