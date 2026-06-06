<template>
  <div class="chart-wrapper">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{ date, revenue }]
  label: { type: String, default: 'Revenue' },
})

const chartData = computed(() => ({
  labels: props.data.map(d => d.date),
  datasets: [
    {
      label: props.label,
      data: props.data.map(d => Number(d.revenue)),
      borderColor: '#4f46e5',
      backgroundColor: 'rgba(79,70,229,0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 3,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { mode: 'index', intersect: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (v) => '$' + v.toLocaleString() },
    },
  },
}
</script>

<style scoped>
.chart-wrapper { height: 260px; }
</style>
