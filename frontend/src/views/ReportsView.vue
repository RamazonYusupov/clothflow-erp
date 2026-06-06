<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Reports</h1>
    </div>

    <!-- Date Range -->
    <div class="card filter-bar">
      <div class="form-group" style="margin:0;">
        <label class="form-label">From</label>
        <input v-model="fromDate" type="date" class="form-input" />
      </div>
      <div class="form-group" style="margin:0;">
        <label class="form-label">To</label>
        <input v-model="toDate" type="date" class="form-input" />
      </div>
      <div style="display:flex;gap:.5rem;align-self:flex-end;">
        <button class="btn btn-primary" @click="loadReports" :disabled="loading">
          <span v-if="loading" class="spinner" style="width:12px;height:12px;border-width:2px;"></span>
          Generate
        </button>
        <button class="btn btn-secondary" @click="exportCsv">⬇ Export CSV</button>
      </div>
    </div>

    <div v-if="loaded">
      <!-- Summary cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem;">
        <div class="card" style="text-align:center;">
          <div style="font-size:.8rem;color:var(--gray-500);margin-bottom:.25rem;">Total Revenue</div>
          <div style="font-size:1.75rem;font-weight:700;color:var(--primary)">${{ fmt(revenue.total_revenue) }}</div>
        </div>
        <div class="card" style="text-align:center;">
          <div style="font-size:.8rem;color:var(--gray-500);margin-bottom:.25rem;">Days with Sales</div>
          <div style="font-size:1.75rem;font-weight:700;">{{ revenue.daily_revenue?.length || 0 }}</div>
        </div>
      </div>

      <!-- Chart -->
      <div class="card" style="margin-bottom:1.5rem;">
        <h3 style="font-size:.9rem;font-weight:600;color:var(--gray-700);margin-bottom:1rem;">Revenue Over Period</h3>
        <RevenueChart :data="revenue.daily_revenue || []" label="Revenue" />
      </div>

      <!-- Top Products table -->
      <div class="card">
        <h3 style="font-size:.9rem;font-weight:600;color:var(--gray-700);margin-bottom:1rem;">Top Products</h3>
        <table class="table">
          <thead><tr><th>#</th><th>Product</th><th>SKU</th><th>Qty Sold</th><th>Revenue</th></tr></thead>
          <tbody>
            <tr v-if="!topProducts.length">
              <td colspan="5" style="text-align:center;color:var(--gray-400);padding:2rem;">No data</td>
            </tr>
            <tr v-else v-for="(p, i) in topProducts" :key="p.product_id">
              <td>{{ i + 1 }}</td>
              <td>{{ p.product_name }}</td>
              <td>{{ p.sku }}</td>
              <td>{{ p.total_quantity }}</td>
              <td>${{ Number(p.total_revenue).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="!loading" class="card" style="text-align:center;padding:3rem;color:var(--gray-400);">
      Select a date range and click Generate to view reports
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'
import RevenueChart from '@/components/charts/RevenueChart.vue'

const today = new Date().toISOString().slice(0, 10)
const thirtyAgo = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10)

const fromDate = ref(thirtyAgo)
const toDate = ref(today)
const loading = ref(false)
const loaded = ref(false)
const revenue = ref({})
const topProducts = ref([])

function fmt(v) { return Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 }) }

async function loadReports() {
  loading.value = true
  try {
    const [revRes, topRes] = await Promise.all([
      api.get('/analytics/revenue', { params: { from_date: fromDate.value, to_date: toDate.value } }),
      api.get('/analytics/top-products', { params: { limit: 10 } }),
    ])
    revenue.value = revRes.data
    topProducts.value = topRes.data
    loaded.value = true
  } finally {
    loading.value = false
  }
}

function exportCsv() {
  const token = localStorage.getItem('access_token')
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const url = `${base}/analytics/reports/export?from_date=${fromDate.value}&to_date=${toDate.value}`
  // Fetch with auth then trigger download
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `report_${fromDate.value}_${toDate.value}.csv`
      a.click()
    })
}
</script>

<style scoped>
.filter-bar { display: flex; align-items: flex-end; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; padding: 1rem; }
</style>
