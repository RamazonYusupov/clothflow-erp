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
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({ email: '', password: '' })

async function handleLogin() {
  error.value = ''
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
  max-width: 400px;
}
.login-brand {
  text-align: center;
  margin-bottom: 2rem;
}
.login-brand h1 { font-size: 1.75rem; font-weight: 700; color: var(--gray-900); margin: 0.5rem 0 0.25rem; }
.login-brand p { color: var(--gray-500); font-size: 0.9rem; }
</style>
