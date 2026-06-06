import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchOrders(params = {}) {
    loading.value = true
    try {
      const res = await api.get('/orders', { params })
      orders.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function getOrder(id) {
    const res = await api.get(`/orders/${id}`)
    return res.data
  }

  async function createOrder(data) {
    const res = await api.post('/orders', data)
    return res.data
  }

  async function updateStatus(id, status) {
    const res = await api.patch(`/orders/${id}/status`, { status })
    return res.data
  }

  return { orders, total, loading, fetchOrders, getOrder, createOrder, updateStatus }
})
