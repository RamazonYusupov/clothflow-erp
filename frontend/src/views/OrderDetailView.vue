<template>
  <div>
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:.75rem;">
        <button class="btn btn-secondary btn-sm" @click="$router.back()">← Back</button>
        <h1 class="page-title">{{ order?.order_number || 'Order' }}</h1>
        <StatusBadge v-if="order" :status="order.status" />
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><span class="spinner"></span></div>

    <template v-else-if="order">
      <div class="order-grid">
        <!-- Info -->
        <div class="card">
          <h3 class="section-title">Order Info</h3>
          <dl class="info-list">
            <div class="info-row"><dt>Customer</dt><dd>{{ order.customer?.full_name || '—' }}</dd></div>
            <div class="info-row"><dt>Email</dt><dd>{{ order.customer?.email || '—' }}</dd></div>
            <div class="info-row"><dt>Status</dt><dd><StatusBadge :status="order.status" /></dd></div>
            <div class="info-row"><dt>Total</dt><dd>${{ Number(order.total_amount).toFixed(2) }}</dd></div>
            <div class="info-row"><dt>Notes</dt><dd>{{ order.notes || '—' }}</dd></div>
            <div class="info-row"><dt>Created</dt><dd>{{ fmtDate(order.created_at) }}</dd></div>
          </dl>

          <!-- Status transition — admin & manager only -->
          <div class="status-actions" v-if="nextStatuses.length && auth.canEditOrder">
            <h4 style="font-size:.8rem;color:var(--gray-500);margin-bottom:.5rem;">UPDATE STATUS</h4>
            <div style="display:flex;gap:.5rem;flex-wrap:wrap;">
              <button
                v-for="s in nextStatuses" :key="s"
                class="btn btn-sm"
                :class="s === 'cancelled' ? 'btn-danger' : 'btn-primary'"
                @click="changeStatus(s)"
                :disabled="updatingStatus"
              >
                → {{ s }}
              </button>
            </div>
          </div>
        </div>

        <!-- Items -->
        <div class="card">
          <h3 class="section-title">Items</h3>
          <table class="table">
            <thead><tr><th>Product</th><th>SKU</th><th>Qty</th><th>Unit Price</th><th>Subtotal</th></tr></thead>
            <tbody>
              <tr v-for="item in order.items" :key="item.id">
                <td>{{ item.product?.name || '—' }}</td>
                <td>{{ item.product?.sku || '—' }}</td>
                <td>{{ item.quantity }}</td>
                <td>${{ Number(item.unit_price).toFixed(2) }}</td>
                <td>${{ Number(item.subtotal).toFixed(2) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="4" style="text-align:right;font-weight:600;">Total</td>
                <td style="font-weight:700;">${{ Number(order.total_amount).toFixed(2) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const route = useRoute()
const auth  = useAuthStore()
const order = ref(null)
const loading = ref(true)
const updatingStatus = ref(false)

const transitions = {
  new: ['confirmed', 'cancelled'],
  confirmed: ['shipped', 'cancelled'],
  shipped: ['delivered'],
  delivered: [],
  cancelled: [],
}

const nextStatuses = computed(() => transitions[order.value?.status] || [])

function fmtDate(d) { return d ? new Date(d).toLocaleString() : '—' }

async function load() {
  try {
    const res = await api.get(`/orders/${route.params.id}`)
    order.value = res.data
  } finally {
    loading.value = false
  }
}

async function changeStatus(status) {
  updatingStatus.value = true
  try {
    const res = await api.patch(`/orders/${order.value.id}/status`, { status })
    order.value = res.data
  } finally {
    updatingStatus.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.order-grid { display: grid; grid-template-columns: 320px 1fr; gap: 1rem; }
.section-title { font-size: .9rem; font-weight: 600; color: var(--gray-700); margin-bottom: 1rem; }
.info-list { display: flex; flex-direction: column; gap: .625rem; }
.info-row { display: flex; gap: .5rem; font-size: .875rem; }
.info-row dt { color: var(--gray-500); min-width: 80px; }
.info-row dd { color: var(--gray-800); }
.status-actions { margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--gray-100); }

@media (max-width: 800px) {
  .order-grid { grid-template-columns: 1fr; }
}
</style>
