<template>
  <div>
    <div class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns.length" class="loading-overlay">
              <span class="spinner"></span>
            </td>
          </tr>
          <tr v-else-if="!rows.length">
            <td :colspan="columns.length" style="text-align:center; color: var(--gray-400); padding: 2rem;">
              No records found
            </td>
          </tr>
          <tr v-else v-for="row in rows" :key="row.id" @click="$emit('row-click', row)" :class="{ clickable: rowClickable }">
            <td v-for="col in columns" :key="col.key">
              <slot :name="col.key" :row="row">{{ row[col.key] }}</slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="total > limit">
      <span>{{ skip + 1 }}–{{ Math.min(skip + limit, total) }} of {{ total }}</span>
      <button :disabled="skip === 0" @click="$emit('page-change', skip - limit)">‹ Prev</button>
      <button :disabled="skip + limit >= total" @click="$emit('page-change', skip + limit)">Next ›</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: Array,
  rows: Array,
  total: Number,
  skip: { type: Number, default: 0 },
  limit: { type: Number, default: 20 },
  loading: Boolean,
  rowClickable: Boolean,
})
defineEmits(['row-click', 'page-change'])
</script>

<style scoped>
.table-wrapper { overflow-x: auto; }
.clickable { cursor: pointer; }
</style>
