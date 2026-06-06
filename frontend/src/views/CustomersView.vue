<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Customers</h1>
      <button v-if="auth.canEditCustomer" class="btn btn-primary" @click="openCreate">+ Add Customer</button>
    </div>

    <!-- Search -->
    <div class="card" style="margin-bottom:1rem; padding:.75rem 1rem;">
      <input v-model="search" class="form-input" placeholder="Search by name, email or phone..." style="max-width:360px;" @input="onSearch" />
    </div>

    <div class="card">
      <DataTable
        :columns="columns"
        :rows="store.customers"
        :total="store.total"
        :skip="skip"
        :limit="limit"
        :loading="store.loading"
        row-clickable
        @row-click="goToDetail"
        @page-change="onPageChange"
      >
        <template #created_at="{ row }">{{ fmtDate(row.created_at) }}</template>
        <template #actions="{ row }">
          <div style="display:flex;gap:.5rem;" @click.stop>
            <button v-if="auth.canEditCustomer" class="btn btn-secondary btn-sm" @click="openEdit(row)">Edit</button>
            <button v-if="auth.canDelete" class="btn btn-danger btn-sm" @click="confirmDelete(row)">Delete</button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editing ? 'Edit Customer' : 'New Customer' }}</h3>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <form @submit.prevent="submitForm">
            <div class="alert alert-error" v-if="formError">{{ formError }}</div>
            <div class="form-group">
              <label class="form-label">Full Name *</label>
              <input v-model="form.full_name" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input v-model="form.email" type="email" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Phone</label>
              <input v-model="form.phone" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Address</label>
              <textarea v-model="form.address" class="form-input" rows="2"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Notes</label>
              <textarea v-model="form.notes" class="form-input" rows="2"></textarea>
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

    <ConfirmModal v-model="showConfirm" message="This will permanently delete the customer." :loading="deleting" @confirm="doDelete" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCustomersStore } from '@/stores/customers'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/ui/DataTable.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const store = useCustomersStore()
const auth  = useAuthStore()
const router = useRouter()

const search = ref('')
const skip = ref(0)
const limit = 20

const columns = [
  { key: 'full_name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'created_at', label: 'Created' },
  { key: 'actions', label: '' },
]

const showForm = ref(false)
const editing = ref(null)
const form = ref({})
const saving = ref(false)
const formError = ref('')

const showConfirm = ref(false)
const deleting = ref(false)
const toDelete = ref(null)

function fmtDate(d) { return d ? new Date(d).toLocaleDateString() : '—' }

function load() {
  store.fetchCustomers({ search: search.value, skip: skip.value, limit })
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { skip.value = 0; load() }, 350)
}

function onPageChange(newSkip) { skip.value = newSkip; load() }

function goToDetail(row) { router.push(`/customers/${row.id}`) }

function openCreate() {
  editing.value = null
  form.value = { full_name: '', email: '', phone: '', address: '', notes: '' }
  formError.value = ''
  showForm.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { full_name: row.full_name, email: row.email || '', phone: row.phone || '', address: row.address || '', notes: row.notes || '' }
  formError.value = ''
  showForm.value = true
}

async function submitForm() {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await store.updateCustomer(editing.value.id, form.value)
    } else {
      await store.createCustomer(form.value)
    }
    showForm.value = false
    load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) { toDelete.value = row; showConfirm.value = true }

async function doDelete() {
  deleting.value = true
  try {
    await store.deleteCustomer(toDelete.value.id)
    showConfirm.value = false
    load()
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>
