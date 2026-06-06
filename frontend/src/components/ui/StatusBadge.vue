<template>
  <span class="badge" :class="`badge-${status}`">{{ status }}</span>
</template>

<script setup>
defineProps({ status: String })
</script>
