<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="brand-icon">🛍️</span>
      <span class="brand-text">Retake-ERP</span>
    </div>

    <nav class="sidebar-nav">
      <RouterLink to="/dashboard" class="nav-item">
        <span class="nav-icon">📊</span><span>Dashboard</span>
      </RouterLink>

      <RouterLink v-if="auth.canViewCustomers" to="/customers" class="nav-item">
        <span class="nav-icon">👥</span><span>Customers</span>
      </RouterLink>

      <RouterLink to="/products" class="nav-item">
        <span class="nav-icon">📦</span><span>Products</span>
      </RouterLink>

      <RouterLink v-if="auth.canViewOrders" to="/orders" class="nav-item">
        <span class="nav-icon">🛒</span><span>Orders</span>
      </RouterLink>

      <RouterLink v-if="auth.canViewReports" to="/reports" class="nav-item">
        <span class="nav-icon">📈</span><span>Reports</span>
      </RouterLink>

      <RouterLink v-if="auth.canManageUsers" to="/users" class="nav-item">
        <span class="nav-icon">👤</span><span>Users</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info" v-if="auth.user">
        <div class="user-avatar">{{ initials }}</div>
        <div class="user-meta">
          <div class="user-name">{{ auth.user.full_name }}</div>
          <span class="role-pill" :class="`role-${auth.user.role}`">{{ auth.user.role }}</span>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout">⬅ Logout</button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()

const initials = computed(() => {
  if (!auth.user) return '?'
  return auth.user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: var(--sidebar-width);
  background: var(--gray-900);
  display: flex;
  flex-direction: column;
  z-index: 100;
}
.sidebar-brand {
  display: flex; align-items: center; gap: .75rem;
  padding: 1.25rem; border-bottom: 1px solid var(--gray-700);
}
.brand-icon { font-size: 1.5rem; }
.brand-text { font-size: 1.1rem; font-weight: 700; color: #fff; }

.sidebar-nav {
  flex: 1; padding: 1rem .75rem;
  display: flex; flex-direction: column; gap: .25rem;
}
.nav-item {
  display: flex; align-items: center; gap: .75rem;
  padding: .625rem .75rem; border-radius: 6px;
  color: var(--gray-400); font-size: .875rem; font-weight: 500;
  transition: background .15s, color .15s;
}
.nav-item:hover { background: var(--gray-800); color: #fff; }
.nav-item.router-link-active { background: var(--primary); color: #fff; }
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }

.sidebar-footer {
  padding: 1rem; border-top: 1px solid var(--gray-700);
  display: flex; flex-direction: column; gap: .75rem;
}
.user-info { display: flex; align-items: center; gap: .625rem; }
.user-avatar {
  width: 36px; height: 36px; background: var(--primary);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: .8rem; font-weight: 700; flex-shrink: 0;
}
.user-name { font-size: .875rem; font-weight: 600; color: #fff; margin-bottom: .2rem; }

.role-pill {
  display: inline-block; padding: .15em .5em;
  border-radius: 999px; font-size: .7rem; font-weight: 600;
  text-transform: capitalize;
}
.role-admin   { background: #9d174d; color: #fff; }
.role-manager { background: #1d4ed8; color: #fff; }
.role-kassir  { background: #15803d; color: #fff; }
.role-ombochi { background: #854d0e; color: #fff; }

.logout-btn {
  background: none; color: var(--gray-400);
  font-size: .8rem; padding: .3rem 0; text-align: left;
  transition: color .15s;
}
.logout-btn:hover { color: #fff; }
</style>
