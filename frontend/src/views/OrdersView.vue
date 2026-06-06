<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Orders</h1>
      <button class="btn btn-primary" @click="openNewOrder">+ New Order</button>
    </div>

    <!-- Filters -->
    <div class="card filter-bar">
      <select v-model="statusFilter" class="form-input" style="max-width:180px;" @change="load">
        <option value="">All Statuses</option>
        <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="card">
      <DataTable :columns="columns" :rows="store.orders" :total="store.total" :skip="skip" :limit="limit" :loading="store.loading" row-clickable @row-click="goToDetail" @page-change="onPageChange">
        <template #status="{ row }"><StatusBadge :status="row.status" /></template>
        <template #total_amount="{ row }">${{ Number(row.total_amount).toFixed(2) }}</template>
        <template #created_at="{ row }">{{ fmtDate(row.created_at) }}</template>
      </DataTable>
    </div>

    <!-- New Order Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
        <div class="modal" style="max-width:640px;">
          <div class="modal-header">
            <h3 class="modal-title">New Order</h3>
            <button class="modal-close" @click="showCreate = false">✕</button>
          </div>
          <form @submit.prevent="submitOrder">
            <div class="alert alert-error" v-if="orderError">{{ orderError }}</div>

            <div class="form-group">
              <label class="form-label">Customer *</label>
              <div v-if="loadingDropdowns" style="font-size:.875rem;color:var(--gray-400);padding:.5rem 0;">Loading customers…</div>
              <select v-else v-model="orderForm.customer_id" class="form-input" required>
                <option value="">Select customer...</option>
                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.full_name }} — {{ c.email }}</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Notes</label>
              <textarea v-model="orderForm.notes" class="form-input" rows="2"></textarea>
            </div>

            <div class="items-section">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem;">
                <span class="form-label" style="margin:0;">Items</span>
                <button type="button" class="btn btn-secondary btn-sm" @click="addItem">+ Add Item</button>
              </div>
              <div v-for="(item, idx) in orderForm.items" :key="idx" class="item-row">
                <div v-if="loadingDropdowns" style="flex:2;font-size:.875rem;color:var(--gray-400);">Loading products…</div>
                <select v-else v-model="item.product_id" class="form-input" style="flex:2;" required>
                  <option value="">Select product...</option>
                  <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} (Stock: {{ p.stock_quantity }}) — ${{ Number(p.price).toFixed(2) }}</option>
                </select>
                <input v-model.number="item.quantity" type="number" min="1" class="form-input" style="flex:.5;min-width:70px;" required />
                <button type="button" class="btn btn-danger btn-sm" @click="removeItem(idx)" :disabled="orderForm.items.length === 1">✕</button>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCreate = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner" style="width:14px;height:14px;border-width:2px;"></span>
                Create Order
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useOrdersStore } from '@/stores/orders'
import DataTable from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const store = useOrdersStore()
const router = useRouter()

const statusFilter = ref('')
const skip = ref(0)
const limit = 20
const statuses = ['new', 'confirmed', 'shipped', 'delivered', 'cancelled']

const columns = [
  { key: 'order_number', label: 'Order #' },
  { key: 'status', label: 'Status' },
  { key: 'total_amount', label: 'Total' },
  { key: 'created_at', label: 'Date' },
]

const showCreate = ref(false)
const submitting = ref(false)
const orderError = ref('')
const customers = ref([])
const products = ref([])
const loadingDropdowns = ref(false)
const orderForm = ref({ customer_id: '', notes: '', items: [{ product_id: '', quantity: 1 }] })

async function openNewOrder() {
  orderError.value = ''
  orderForm.value = { customer_id: '', notes: '', items: [{ product_id: '', quantity: 1 }] }
  showCreate.value = true
  loadingDropdowns.value = true
  try {
    const [cr, pr] = await Promise.all([
      api.get('/customers', { params: { limit: 500 } }),
      api.get('/products', { params: { limit: 500 } }),
    ])
    customers.value = cr.data.items
    products.value = pr.data.items
  } finally {
    loadingDropdowns.value = false
  }
}

function fmtDate(d) { return d ? new Date(d).toLocaleDateString() : '—' }
function load() { store.fetchOrders({ status: statusFilter.value || undefined, skip: skip.value, limit }) }
function onPageChange(s) { skip.value = s; load() }
function goToDetail(row) { router.push(`/orders/${row.id}`) }
function addItem() { orderForm.value.items.push({ product_id: '', quantity: 1 }) }
function removeItem(idx) { orderForm.value.items.splice(idx, 1) }

async function submitOrder() {
  submitting.value = true
  orderError.value = ''
  try {
    const res = await api.post('/orders', orderForm.value)
    showCreate.value = false
    orderForm.value = { customer_id: '', notes: '', items: [{ product_id: '', quantity: 1 }] }
    router.push(`/orders/${res.data.id}`)
  } catch (e) {
    orderError.value = e.response?.data?.detail || 'Failed to create order'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.filter-bar { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; margin-bottom:1rem; padding:.75rem 1rem; }
.items-section { background: var(--gray-50); border-radius: 6px; padding: .75rem; margin-bottom: .5rem; }
.item-row { display: flex; align-items: center; gap: .5rem; margin-bottom: .5rem; }
</style>
