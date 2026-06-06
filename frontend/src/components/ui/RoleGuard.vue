<template>
  <slot v-if="hasAccess" />
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  roles: {
    type: Array,
    required: true,
  },
})

const auth = useAuthStore()
const hasAccess = computed(() => props.roles.includes(auth.user?.role))
</script>
