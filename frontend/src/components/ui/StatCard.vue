<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ background: iconBg }">{{ icon }}</div>
    <div class="stat-body">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">{{ value }}</div>
      <div class="stat-sub" v-if="sub">{{ sub }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: String,
  label: String,
  value: [String, Number],
  sub: String,
  iconBg: { type: String, default: '#e0e7ff' },
})
</script>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.stat-icon {
  width: 52px; height: 52px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}
.stat-label { font-size: 0.8rem; color: var(--gray-500); font-weight: 500; margin-bottom: 0.25rem; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: var(--gray-900); }
.stat-sub { font-size: 0.75rem; color: var(--gray-400); margin-top: 0.125rem; }
</style>
