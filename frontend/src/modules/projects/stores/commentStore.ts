/**
 * Comment Store - Pinia State Management
 * Ham Dog & TC's focused comment management store!
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import projectService from '../services/projectService'
import { useToastStore } from '@/stores/toast'
import type {
  Comment
} from '../types/project.types'

export const useCommentStore = defineStore('comment', () => {
  const toastStore = useToastStore()

  // State
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function addComment(taskId: string, content: string) {
    loading.value = true
    error.value = null

    try {
      const newComment = await projectService.addComment(taskId, { content })
      
      toastStore.success('Comment added successfully!')
      return newComment
    } catch (err: any) {
      error.value = err.message || 'Failed to add comment'
      toastStore.error('Failed to add comment')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateComment(commentId: string, content: string) {
    loading.value = true
    error.value = null

    try {
      const updatedComment = await projectService.updateComment(commentId, content)
      
      toastStore.success('Comment updated successfully!')
      return updatedComment
    } catch (err: any) {
      error.value = err.message || 'Failed to update comment'
      toastStore.error('Failed to update comment')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteComment(commentId: string) {
    loading.value = true
    error.value = null

    try {
      await projectService.deleteComment(commentId)
      
      toastStore.success('Comment deleted successfully!')
    } catch (err: any) {
      error.value = err.message || 'Failed to delete comment'
      toastStore.error('Failed to delete comment')
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset store
  function resetCommentStore() {
    loading.value = false
    error.value = null
  }

  return {
    // State
    loading,
    error,

    // Actions
    addComment,
    updateComment,
    deleteComment,

    // Utils
    resetCommentStore
  }
})