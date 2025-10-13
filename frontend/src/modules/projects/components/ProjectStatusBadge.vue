<template>
  <BaseBadge
    :variant="variant"
    :content="displayStatus"
    :leading-icon="StatusIcon"
    size="sm"
    :style="'soft'"
    shape="pill"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  ClockIcon, 
  PlayIcon, 
  PauseIcon, 
  CheckCircleIcon, 
  ArchiveBoxIcon 
} from '@heroicons/vue/24/outline'
import BaseBadge from '@/shared/components/BaseBadge.vue'
import type { ProjectStatus } from '../types/project.types'

interface Props {
  status: ProjectStatus
}

const props = defineProps<Props>()

const statusConfig = {
  planning: {
    label: 'Planning',
    variant: 'secondary' as const,
    icon: ClockIcon
  },
  active: {
    label: 'Active',
    variant: 'success' as const,
    icon: PlayIcon
  },
  on_hold: {
    label: 'On Hold',
    variant: 'warning' as const,
    icon: PauseIcon
  },
  completed: {
    label: 'Completed',
    variant: 'info' as const,
    icon: CheckCircleIcon
  },
  archived: {
    label: 'Archived',
    variant: 'secondary' as const,
    icon: ArchiveBoxIcon
  }
}

const config = computed(() => statusConfig[props.status] || statusConfig.planning)
const variant = computed(() => config.value.variant)
const StatusIcon = computed(() => config.value.icon)
const displayStatus = computed(() => config.value.label)
</script>