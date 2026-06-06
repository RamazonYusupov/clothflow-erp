<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Users</h1>
      <button class="btn btn-primary" @click="openCreate">+ Add User</button>
    </div>

    <div class="card">
      <DataTable
        :columns="columns"
        :rows="users"
        :total="total"
        :skip="skip"
        :limit="limit"
        :loading="loading"
        @page-change="onPageChange"
      >
        <template #role="{ row }">
          <span class="role-badge" :class="`role-${row.role}`">{{ row.role }}</span>
        </template>
        <template #is_active="{ row }">
          <span :style="{ color: row.is_active ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }">
            {{ row.is_active ? 'Active' : 'Inactive' }}
          </span>
        </template>
        <template #created_at="{ row }">{{ fmtDate(row.created_at) }}</template>
        <template #actions="{ row }">
          <div style="display:flex;gap:.5rem;">
            <button class="btn btn-secondary btn-sm" @click="openEdit(row)">Edit</button>
            <button class="btn btn-secondary btn-sm" @click="openChangeRole(row)">Role</button>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(row)" :disabled="row.id === auth.user?.id">Delete</button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editing ? 'Edit User' : 'New User' }}</h3>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <form @submit.prevent="submitForm">
            <div class="alert alert-error" v-if="formError">{{ formError }}</div>
            <div class="form-group">
              <label class="form-label">Full Name *</label>
              <input v-model="form.full_name" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Email *</label>
              <input v-model="form.email" type="email" class="form-input" required />
            </div>
            <div class="form-group" v-if="!editing">
              <label class="form-label">Password *</label>
              <input v-model="form.password" type="password" class="form-input" required minlength="6" />
            </div>
            <div class="form-group">
              <label class="form-label">Role *</label>
              <select v-model="form.role" class="form-input" required>
                <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </div>
            <div class="form-group" v-if="editing">
              <label class="form-label">Status</label>
              <select v-model="form.is_active" class="form-input">
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
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

    <!-- Change Role Modal -->
    <Teleport to="body">
      <div class="modal-overlay" v-if="showRoleModal" @click.self="showRoleModal = false">
        <div class="modal" style="max-width:360px;">
          <div class="modal-header">
            <h3 class="modal-title">Change Role — {{ roleTarget?.full_name }}</h3>
            <button class="modal-close" @click="showRoleModal = false">✕</button>
          </div>
          <div class="form-group">
            <label class="form-label">New Role</label>
            <select v-model="newRole" class="form-input">
              <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showRoleModal = false">Cancel</button>
            <button class="btn btn-primary" @click="submitRoleChange" :disabled="saving">Save</button>
          </div>
        </div>
      </div>
    </Teleport>

    <ConfirmModal v-model="showConfirm" title="Delete User" message="This will permanently delete the user account." :loading="deleting" @confirm="doDelete" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/ui/DataTable.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const auth = useAuthStore()

const users   = ref([])
const total   = ref(0)
const loading = ref(false)
const skip    = ref(0)
const limit   = 20

const roles = [
  { value: 'admin',   label: 'Admin — Full access' },
  { value: 'manager', label: 'Manager — Sales & customers' },
  { value: 'kassir',  label: 'Kassir — Orders & view only' },
  { value: 'ombochi', label: 'Ombochi — Products & inventory' },
]

const columns = [
  { key: 'full_name',  label: 'Name' },
  { key: 'email',      label: 'Email' },
  { key: 'role',       label: 'Role' },
  { key: 'is_active',  label: 'Status' },
  { key: 'created_at', label: 'Created' },
  { key: 'actions',    label: '' },
]

const showForm  = ref(false)
const editing   = ref(null)
const form      = ref({})
const saving    = ref(false)
const formError = ref('')

const showRoleModal = ref(false)
const roleTarget    = ref(null)
const newRole       = ref('kassir')

const showConfirm = ref(false)
const deleting    = ref(false)
const toDelete    = ref(null)

function fmtDate(d) { return d ? new Date(d).toLocaleDateString() : '—' }

async function load() {
  loading.value = true
  try {
    const res = await api.get('/users', { params: { skip: skip.value, limit } })
    users.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onPageChange(s) { skip.value = s; load() }

function openCreate() {
  editing.value = null
  form.value = { full_name: '', email: '', password: '', role: 'kassir', is_active: true }
  formError.value = ''
  showForm.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { full_name: row.full_name, email: row.email, role: row.role, is_active: row.is_active }
  formError.value = ''
  showForm.value = true
}

async function submitForm() {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await api.put(`/users/${editing.value.id}`, form.value)
    } else {
      await api.post('/users', form.value)
    }
    showForm.value = false
    load()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'An error occurred'
  } finally {
    saving.value = false
  }
}

function openChangeRole(row) {
  roleTarget.value = row
  newRole.value = row.role
  showRoleModal.value = true
}

async function submitRoleChange() {
  saving.value = true
  try {
    await api.patch(`/users/${roleTarget.value.id}/role`, { role: newRole.value })
    showRoleModal.value = false
    load()
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) { toDelete.value = row; showConfirm.value = true }

async function doDelete() {
  deleting.value = true
  try {
    await api.delete(`/users/${toDelete.value.id}`)
    showConfirm.value = false
    load()
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.role-badge {
  display: inline-block;
  padding: .2em .65em;
  border-radius: 999px;
  font-size: .75rem;
  font-weight: 600;
  text-transform: capitalize;
}
.role-admin   { background: #fce7f3; color: #9d174d; }
.role-manager { background: #dbeafe; color: #1d4ed8; }
.role-kassir  { background: #dcfce7; color: #15803d; }
.role-ombochi { background: #fef9c3; color: #854d0e; }
</style>
