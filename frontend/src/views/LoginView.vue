<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <span style="font-size:2rem;">🛍️</span>
        <h1>RetailERP</h1>
        <p>Sign in to your account</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="alert alert-error" v-if="error">{{ error }}</div>

        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="ramzan06@gmail.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center;" :disabled="loading">
          <span v-if="loading" class="spinner" style="width:14px;height:14px;border-width:2px;"></span>
          Sign In
        </button>
      </form>

      <!-- Demo accounts -->
      <div class="demo-accounts">
        <div class="demo-title">Demo accounts — click to fill</div>
        <div class="demo-grid">
          <button
            v-for="acc in demoAccounts"
            :key="acc.role"
            class="demo-btn"
            type="button"
            @click="fillCredentials(acc)"
          >
            <span class="demo-role-badge" :class="`role-${acc.role}`">{{ acc.role }}</span>
            <span class="demo-email">{{ acc.email }}</span>
            <span class="demo-pass">{{ acc.password }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth    = useAuthStore()
const router  = useRouter()
const loading = ref(false)
const error   = ref('')
const form    = ref({ email: '', password: '' })

const demoAccounts = [
  { role: 'admin',   email: 'ramzan06@gmail.com',  password: 'ramzan123'  },
  { role: 'manager', email: 'manager@example.com', password: 'manager123' },
  { role: 'kassir',  email: 'kassir@example.com',  password: 'kassir123'  },
  { role: 'ombochi', email: 'ombochi@example.com', password: 'ombochi123' },
]

function fillCredentials(acc) {
  form.value.email    = acc.email
  form.value.password = acc.password
}

async function handleLogin() {
  error.value   = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #f0f9ff 100%);
  padding: 1rem;
}

.login-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0,0,0,.1);
  padding: 2.5rem;
  width: 100%;
  max-width: 440px;
}

.login-brand {
  text-align: center;
  margin-bottom: 2rem;
}
.login-brand h1 { font-size: 1.75rem; font-weight: 700; color: var(--gray-900); margin: 0.5rem 0 0.25rem; }
.login-brand p  { color: var(--gray-500); font-size: 0.9rem; }

/* ── Demo accounts ── */
.demo-accounts {
  margin-top: 1.75rem;
  border-top: 1px solid var(--gray-100);
  padding-top: 1.25rem;
}

.demo-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--gray-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
  text-align: center;
}

.demo-grid {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.demo-btn {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, border-color 0.15s;
  font-family: inherit;
}
.demo-btn:hover {
  background: var(--primary-light);
  border-color: var(--primary);
}

.demo-role-badge {
  display: inline-block;
  padding: 0.15em 0.55em;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: capitalize;
  min-width: 58px;
  text-align: center;
  flex-shrink: 0;
}
.role-admin   { background: #fce7f3; color: #9d174d; }
.role-manager { background: #dbeafe; color: #1d4ed8; }
.role-kassir  { background: #dcfce7; color: #15803d; }
.role-ombochi { background: #fef9c3; color: #854d0e; }

.demo-email {
  font-size: 0.8rem;
  color: var(--gray-700);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.demo-pass {
  font-size: 0.75rem;
  color: var(--gray-400);
  font-family: monospace;
  flex-shrink: 0;
}
</style>
