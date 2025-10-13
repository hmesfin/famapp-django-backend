<template>
  <BaseCard variant="default" size="sm">
    <div class="flex items-center">
      <!-- Icon -->
      <div class="flex-shrink-0">
        <component
          :is="icon"
          :class="iconClasses"
          class="h-6 w-6"
        />
      </div>
      
      <!-- Content -->
      <div class="ml-5 w-0 flex-1">
        <dl>
          <dt :class="titleClasses">
            {{ title }}
          </dt>
          <dd :class="valueClasses">
            {{ formattedValue }}
          </dd>
        </dl>
      </div>
      
      <!-- Optional trend indicator -->
      <div v-if="trend" class="flex-shrink-0">
        <component
          :is="trend.direction === 'up' ? ArrowUpIcon : ArrowDownIcon"
          :class="trendClasses"
          class="h-4 w-4"
        />
        <span :class="trendTextClasses" class="text-xs font-medium ml-1">
          {{ trend.value }}%
        </span>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/24/outline'
import type { Component } from 'vue'
import BaseCard from './BaseCard.vue'

type StatVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'

interface TrendData {
  direction: 'up' | 'down'
  value: number
}

interface Props {
  title: string
  value: number | string
  icon?: Component
  variant?: StatVariant
  trend?: TrendData
  format?: 'number' | 'currency' | 'percentage'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'secondary',
  format: 'number'
})

// Variant icon colors
const iconVariantClasses = {
  primary: 'text-primary-600 dark:text-primary-500',
  secondary: 'text-secondary-400 dark:text-secondary-500',
  success: 'text-success-600 dark:text-success-500',
  warning: 'text-warning-500 dark:text-warning-400',
  danger: 'text-danger-600 dark:text-danger-500',
  info: 'text-info-600 dark:text-info-500'
}

const iconClasses = computed(() => [
  iconVariantClasses[props.variant]
])

const titleClasses = [
  'text-sm',
  'font-medium',
  'text-secondary-500',
  'dark:text-secondary-400',
  'truncate'
]

const valueClasses = [
  'text-lg',
  'font-semibold',
  'text-secondary-900',
  'dark:text-secondary-100'
]

const trendClasses = computed(() => [
  props.trend?.direction === 'up' ? 'text-success-500' : 'text-danger-500'
])

const trendTextClasses = computed(() => [
  props.trend?.direction === 'up' ? 'text-success-600' : 'text-danger-600',
  'dark:text-opacity-90'
])

const formattedValue = computed(() => {
  const val = props.value

  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(Number(val))
    
    case 'percentage':
      return `${val}%`
    
    case 'number':
    default:
      return new Intl.NumberFormat('en-US').format(Number(val))
  }
})
</script>