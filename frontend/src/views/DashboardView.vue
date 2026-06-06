<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
    </div>

    <div v-if="loading" class="loading-overlay"><span class="spinner"></span></div>

    <template v-else>
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <StatCard icon="💰" label="Total Sales" :value="'$' + fmt(data.kpi?.total_sales)" iconBg="#dcfce7" />
        <StatCard icon="🛒" label="Total Orders" :value="data.kpi?.orders_count" iconBg="#dbeafe" />
        <StatCard icon="⚠️" label="Low Stock Items" :value="data.kpi?.low_stock_count" iconBg="#fef9c3" />
        <StatCard icon="👥" label="New Customers (30d)" :value="data.kpi?.new_customers" iconBg="#fce7f3" />
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3 class="card-title">Daily Revenue (Last 30 Days)</h3>
          <RevenueChart :data="data.daily_revenue || []" />
        </div>

        <div class="card top-products-card">
          <h3 class="card-title">Top Products</h3>
          <div v-if="!data.top_products?.length" style="color:var(--gray-400);font-size:.875rem;">No data yet</div>
          <ol class="top-list" v-else>
            <li v-for="p in data.top_products" :key="p.product_id" class="top-item">
              <span class="top-name">{{ p.product_name }}</span>
              <span class="top-rev">${{ fmt(p.total_revenue) }}</span>
            </li>
          </ol>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import StatCard from '@/components/ui/StatCard.vue'
import RevenueChart from '@/components/charts/RevenueChart.vue'

const loading = ref(true)
const data = ref({})

function fmt(val) {
  const n = Number(val || 0)
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(async () => {
  try {
    const res = await api.get('/analytics/dashboard')
    data.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.charts-row { display: grid; grid-template-columns: 1fr 340px; gap: 1rem; }
.chart-card, .top-products-card { padding: 1.25rem; }
.card-title { font-size: 0.9rem; font-weight: 600; color: var(--gray-700); margin-bottom: 1rem; }
.top-list { padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; }
.top-item { display: flex; justify-content: space-between; font-size: 0.875rem; }
.top-name { color: var(--gray-700); }
.top-rev { font-weight: 600; color: var(--primary); }

@media (max-width: 900px) {
  .charts-row { grid-template-columns: 1fr; }
}
</style>
