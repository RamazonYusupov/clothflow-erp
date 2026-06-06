<template>
  <div class="forbidden-page">
    <div class="forbidden-card">
      <div class="forbidden-icon">🔒</div>
      <h1>403 — Forbidden</h1>
      <p>Bu sahifaga kirish huquqingiz yo'q.</p>
      <p style="color:var(--gray-400);font-size:.875rem;">You don't have permission to access this page.</p>
      <RouterLink to="/dashboard" class="btn btn-primary" style="margin-top:1.5rem;">
        ← Dashboard ga qaytish
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.forbidden-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-50);
  padding: 1rem;
}
.forbidden-card {
  text-align: center;
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 3rem 2rem;
  max-width: 420px;
  width: 100%;
}
.forbidden-icon { font-size: 4rem; margin-bottom: 1rem; }
h1 { font-size: 1.5rem; font-weight: 700; color: var(--gray-900); margin-bottom: .75rem; }
p { color: var(--gray-600); margin-bottom: .25rem; }
</style>
