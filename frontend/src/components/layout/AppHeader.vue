<template>
  <header class="app-header">
    <div class="header-title">{{ routeTitle }}</div>
    <div class="header-right">
      <span class="header-user" v-if="auth.user">{{ auth.user.full_name }}</span>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

const titles = {
  dashboard: 'Dashboard',
  customers: 'Customers',
  'customer-detail': 'Customer Detail',
  products: 'Products',
  orders: 'Orders',
  'order-detail': 'Order Detail',
  reports: 'Reports',
}

const routeTitle = computed(() => titles[route.name] || 'Retail ERP')
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background: #fff;
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-title { font-size: 1rem; font-weight: 600; color: var(--gray-800); }
.header-user { font-size: 0.875rem; color: var(--gray-600); }
</style>
