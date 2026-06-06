<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="modelValue" @click.self="$emit('update:modelValue', false)">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h3 class="modal-title">{{ title }}</h3>
          <button class="modal-close" @click="$emit('update:modelValue', false)">✕</button>
        </div>
        <p style="color: var(--gray-600); font-size: 0.9rem;">{{ message }}</p>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('update:modelValue', false)">Cancel</button>
          <button class="btn btn-danger" @click="$emit('confirm')" :disabled="loading">
            <span v-if="loading" class="spinner" style="width:14px;height:14px;border-width:2px;"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure?' },
  confirmText: { type: String, default: 'Delete' },
  loading: Boolean,
})
defineEmits(['update:modelValue', 'confirm'])
</script>
