import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/403',   name: '403',   component: () => import('@/views/ForbiddenView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        // All roles can see dashboard
      },
      {
        path: 'customers',
        name: 'customers',
        component: () => import('@/views/CustomersView.vue'),
        meta: { roles: ['admin', 'manager', 'kassir'] },
      },
      {
        path: 'customers/:id',
        name: 'customer-detail',
        component: () => import('@/views/CustomerDetailView.vue'),
        meta: { roles: ['admin', 'manager', 'kassir'] },
      },
      {
        path: 'products',
        name: 'products',
        component: () => import('@/views/ProductsView.vue'),
        // All roles can view products
      },
      {
        path: 'orders',
        name: 'orders',
        component: () => import('@/views/OrdersView.vue'),
        meta: { roles: ['admin', 'manager', 'kassir'] },
      },
      {
        path: 'orders/:id',
        name: 'order-detail',
        component: () => import('@/views/OrderDetailView.vue'),
        meta: { roles: ['admin', 'manager', 'kassir'] },
      },
      {
        path: 'reports',
        name: 'reports',
        component: () => import('@/views/ReportsView.vue'),
        meta: { roles: ['admin', 'manager'] },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/UsersView.vue'),
        meta: { roles: ['admin'] },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Redirect to login if not authenticated
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  // Already logged in — skip login page
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  // Wait for user to load (page refresh case)
  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchMe()
  }

  // Role guard
  if (to.meta.roles && auth.user && !to.meta.roles.includes(auth.user.role)) {
    return { name: '403' }
  }
})

export default router
