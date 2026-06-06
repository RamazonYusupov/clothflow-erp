<template>
  <div>
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:.75rem;">
        <button class="btn btn-secondary btn-sm" @click="$router.back()">← Back</button>
        <h1 class="page-title">{{ customer?.full_name || 'Customer' }}</h1>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><span class="spinner"></span></div>

    <template v-else-if="customer">
      <div class="detail-grid">
        <div class="card">
          <h3 class="section-title">Contact Info</h3>
          <dl class="info-list">
            <div class="info-row"><dt>Email</dt><dd>{{ customer.email || '—' }}</dd></div>
            <div class="info-row"><dt>Phone</dt><dd>{{ customer.phone || '—' }}</dd></div>
            <div class="info-row"><dt>Address</dt><dd>{{ customer.address || '—' }}</dd></div>
            <div class="info-row"><dt>Notes</dt><dd>{{ customer.notes || '—' }}</dd></div>
            <div class="info-row"><dt>Member since</dt><dd>{{ fmtDate(customer.created_at) }}</dd></div>
          </dl>
        </div>

        <div class="card">
          <h3 class="section-title">Order History ({{ customer.orders?.length || 0 }})</h3>
          <div v-if="!customer.orders?.length" style="color:var(--gray-400);font-size:.875rem;">No orders yet</div>
          <table class="table" v-else>
            <thead><tr><th>Order #</th><th>Status</th><th>Total</th><th>Date</th><th></th></tr></thead>
            <tbody>
              <tr v-for="o in customer.orders" :key="o.id">
                <td>{{ o.order_number }}</td>
                <td><StatusBadge :status="o.status" /></td>
                <td>${{ Number(o.total_amount).toFixed(2) }}</td>
                <td>{{ fmtDate(o.created_at) }}</td>
                <td><RouterLink :to="`/orders/${o.id}`" class="btn btn-secondary btn-sm">View</RouterLink></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCustomersStore } from '@/stores/customers'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const route = useRoute()
const store = useCustomersStore()
const customer = ref(null)
const loading = ref(true)

function fmtDate(d) { return d ? new Date(d).toLocaleDateString() : '—' }

onMounted(async () => {
  try {
    customer.value = await store.getCustomer(route.params.id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-grid { display: grid; grid-template-columns: 340px 1fr; gap: 1rem; }
.section-title { font-size: .9rem; font-weight: 600; color: var(--gray-700); margin-bottom: 1rem; }
.info-list { display: flex; flex-direction: column; gap: .625rem; }
.info-row { display: flex; gap: .5rem; font-size: .875rem; }
.info-row dt { color: var(--gray-500); min-width: 100px; }
.info-row dd { color: var(--gray-800); }

@media (max-width: 800px) {
  .detail-grid { grid-template-columns: 1fr; }
}
</style>
