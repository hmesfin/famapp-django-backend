<template>
  <BaseBadge
    :variant="variant"
    :content="displayPriority"
    :leading-icon="PriorityIcon"
    size="xs"
    :style="'soft'"
    shape="rounded"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  ArrowUpIcon, 
  ArrowRightIcon,
  ExclamationTriangleIcon,
  FireIcon 
} from '@heroicons/vue/24/outline'
import BaseBadge from '@/shared/components/BaseBadge.vue'
import type { TaskPriority } from '../types/project.types'

interface Props {
  priority: TaskPriority
}

const props = defineProps<Props>()

const priorityConfig = {
  low: {
    label: 'Low',
    variant: 'secondary' as const,
    icon: ArrowRightIcon
  },
  medium: {
    label: 'Medium',
    variant: 'info' as const,
    icon: ArrowUpIcon
  },
  high: {
    label: 'High',
    variant: 'warning' as const,
    icon: ExclamationTriangleIcon
  },
  critical: {
    label: 'Critical',
    variant: 'danger' as const,
    icon: FireIcon
  }
}

const config = computed(() => priorityConfig[props.priority] || priorityConfig.medium)
const variant = computed(() => config.value.variant)
const PriorityIcon = computed(() => config.value.icon)
const displayPriority = computed(() => config.value.label)
</script>