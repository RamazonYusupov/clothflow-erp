import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useProductsStore = defineStore('products', () => {
  const products = ref([])
  const categories = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const res = await api.get('/products', { params })
      products.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    const res = await api.get('/categories')
    categories.value = res.data
  }

  async function createProduct(data) {
    const res = await api.post('/products', data)
    return res.data
  }

  async function updateProduct(id, data) {
    const res = await api.put(`/products/${id}`, data)
    return res.data
  }

  async function deleteProduct(id) {
    await api.delete(`/products/${id}`)
  }

  async function createCategory(data) {
    const res = await api.post('/categories', data)
    categories.value.push(res.data)
    return res.data
  }

  return { products, categories, total, loading, fetchProducts, fetchCategories, createProduct, updateProduct, deleteProduct, createCategory }
})
