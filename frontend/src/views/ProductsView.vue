<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Products</h1>
      <div style="display:flex;gap:.5rem;">
        <button v-if="auth.canEditProduct" class="btn btn-secondary" @click="showCatModal = true">+ Category</button>
        <button v-if="auth.canEditProduct" class="btn btn-primary" @click="openCreate">+ Add Product</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card filter-bar">
      <input v-model="search" class="form-input" placeholder="Search name or SKU..." style="flex:1;max-width:300px;" @input="onSearch" />
      <select v-model="categoryFilter" class="form-input" style="max-width:200px;" @change="load">
        <option value="">All Categories</option>
        <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <label style="display:flex;align-items:center;gap:.5rem;font-size:.875rem;cursor:pointer;">
        <input type="checkbox" v-model="lowStockFilter" @change="load" />
        Low Stock Only
      </label>
    </div>

    <div class="card">
      <DataTable :columns="columns" :rows="store.products" :total="store.total" :skip="skip" :limit="limit" :loading="store.loading" @page-change="onPageChange">
        <template #price="{ row }">${{ Number(row.price).toFixed(2) }}</template>
        <template #stock_quantity="{ row }">
          <span :style="{ color: row.stock_quantity <= row.low_stock_threshold ? 'var(--danger)' : 'inherit', fontWeight: row.stock_quantity <= row.low_stock_threshold ? '600' : '400' }">
            {{ row.stock_quantity }}
            <span v-if="row.stock_quantity <= row.low_stock_threshold" style="font-size:.7rem;"> ⚠️</span>
          </span>
        </template>
        <template #category="{ row }">{{ row.category?.name || '—' }}</template>
        <template #actions="{ row }">
          <div style="display:flex;gap:.5rem;">
            <button v-if="auth.canEditProduct" class="btn btn-secondary btn-sm" @click="openEdit(row)">Edit</button>
            <button v-if="auth.canDelete" class="btn btn-danger btn-sm" @click="confirmDelete(row)">Delete</button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Product Form Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
        <div class="modal" style="max-width:600px;">
          <div class="modal-header">
            <h3 class="modal-title">{{ editing ? 'Edit Product' : 'New Product' }}</h3>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <form @submit.prevent="submitForm">
            <div class="alert alert-error" v-if="formError">{{ formError }}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 1rem;">
              <div class="form-group">
                <label class="form-label">Name *</label>
                <input v-model="form.name" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">SKU *</label>
                <input v-model="form.sku" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Price *</label>
                <input v-model="form.price" type="number" step="0.01" min="0" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Stock Quantity</label>
                <input v-model="form.stock_quantity" type="number" min="0" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Low Stock Threshold</label>
                <input v-model="form.low_stock_threshold" type="number" min="0" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Category</label>
                <select v-model="form.category_id" class="form-input">
                  <option value="">No category</option>
                  <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-input" rows="2"></textarea>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showForm = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner" style="width:14px;height:14px;border-width:2px;"></span>
                {{ editing ? 'Save' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Category Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showCatModal" @click.self="showCatModal = false">
        <div class="modal" style="max-width:360px;">
          <div class="modal-header">
            <h3 class="modal-title">New Category</h3>
            <button class="modal-close" @click="showCatModal = false">✕</button>
          </div>
          <form @submit.prevent="submitCategory">
            <div class="form-group">
              <label class="form-label">Name *</label>
              <input v-model="catForm.name" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <input v-model="catForm.description" class="form-input" />
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCatModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingCat">Save</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <ConfirmModal v-model="showConfirm" message="This will deactivate the product." :loading="deleting" @confirm="doDelete" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/ui/DataTable.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const store = useProductsStore()
const auth  = useAuthStore()
const search = ref('')
const categoryFilter = ref('')
const lowStockFilter = ref(false)
const skip = ref(0)
const limit = 20

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'sku', label: 'SKU' },
  { key: 'price', label: 'Price' },
  { key: 'stock_quantity', label: 'Stock' },
  { key: 'category', label: 'Category' },
  { key: 'actions', label: '' },
]

const showForm = ref(false)
const editing = ref(null)
const form = ref({})
const saving = ref(false)
const formError = ref('')

const showCatModal = ref(false)
const catForm = ref({ name: '', description: '' })
const savingCat = ref(false)

const showConfirm = ref(false)
const deleting = ref(false)
const toDelete = ref(null)

function load() {
  store.fetchProducts({
    search: search.value,
    category_id: categoryFilter.value || undefined,
    low_stock: lowStockFilter.value || undefined,
    skip: skip.value,
    limit,
  })
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { skip.value = 0; load() }, 350)
}

function onPageChange(s) { skip.value = s; load() }

function openCreate() {
  editing.value = null
  form.value = { name: '', sku: '', price: '', stock_quantity: 0, low_stock_threshold: 10, category_id: '', description: '' }
  formError.value = ''
  showForm.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { name: row.name, sku: row.sku, price: row.price, stock_quantity: row.stock_quantity, low_stock_threshold: row.low_stock_threshold, category_id: row.category?.id || '', description: row.description || '' }
  formError.value = ''
  showForm.value = true
}

async function submitForm() {
  saving.value = true
  formError.value = ''
  try {
    const payload = { ...form.value, category_id: form.value.category_id || null }
    if (editing.value) {
      await store.updateProduct(editing.value.id, payload)
    } else {
      await store.createProduct(payload)
    }
    showForm.value = false
    load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    saving.value = false
  }
}

async function submitCategory() {
  savingCat.value = true
  try {
    await store.createCategory(catForm.value)
    showCatModal.value = false
    catForm.value = { name: '', description: '' }
  } finally {
    savingCat.value = false
  }
}

function confirmDelete(row) { toDelete.value = row; showConfirm.value = true }
async function doDelete() {
  deleting.value = true
  try {
    await store.deleteProduct(toDelete.value.id)
    showConfirm.value = false
    load()
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  store.fetchCategories()
  load()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: .75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  padding: .75rem 1rem;
}
</style>
