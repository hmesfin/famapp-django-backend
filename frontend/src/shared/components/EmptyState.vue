<template>
  <div class="text-center py-12">
    <!-- Icon -->
    <component
      :is="icon"
      :class="iconClasses"
      class="mx-auto mb-4"
    />
    
    <!-- Title -->
    <h3 :class="titleClasses">
      {{ title }}
    </h3>
    
    <!-- Description -->
    <p v-if="description" :class="descriptionClasses">
      {{ description }}
    </p>
    
    <!-- Actions -->
    <div v-if="primaryAction || secondaryAction || $slots.actions" class="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
      <!-- Primary Action -->
      <BaseButton
        v-if="primaryAction"
        variant="primary"
        :leading-icon="primaryAction.icon"
        @click="primaryAction.onClick"
      >
        {{ primaryAction.label }}
      </BaseButton>
      
      <!-- Secondary Action -->
      <BaseButton
        v-if="secondaryAction"
        variant="secondary"
        :leading-icon="secondaryAction.icon"
        @click="secondaryAction.onClick"
      >
        {{ secondaryAction.label }}
      </BaseButton>
      
      <!-- Custom actions slot -->
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'
import BaseButton from './BaseButton.vue'

interface ActionConfig {
  label: string
  icon?: Component
  onClick: () => void
}

interface Props {
  // Content
  title: string
  description?: string
  
  // Visual
  icon?: Component
  size?: 'sm' | 'md' | 'lg'
  
  // Actions
  primaryAction?: ActionConfig
  secondaryAction?: ActionConfig
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

// Size configurations
const sizeConfig = {
  sm: {
    icon: 'h-8 w-8',
    title: 'text-base font-medium',
    description: 'text-sm'
  },
  md: {
    icon: 'h-12 w-12',
    title: 'text-lg font-medium',
    description: 'text-sm'
  },
  lg: {
    icon: 'h-16 w-16',
    title: 'text-xl font-semibold',
    description: 'text-base'
  }
}

const iconClasses = computed(() => [
  sizeConfig[props.size].icon,
  'text-secondary-400',
  'dark:text-secondary-500'
])

const titleClasses = computed(() => [
  sizeConfig[props.size].title,
  'text-secondary-900',
  'dark:text-secondary-100'
])

const descriptionClasses = computed(() => [
  sizeConfig[props.size].description,
  'text-secondary-500',
  'dark:text-secondary-400',
  'mt-2'
])
</script>