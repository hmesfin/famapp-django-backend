<template>
  <TransitionRoot as="template" :show="show">
    <Dialog as="div" class="relative z-50" :static="true">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 dark:bg-gray-900 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl">
              <!-- Header -->
              <div class="bg-white dark:bg-gray-800 px-6 pt-6 pb-4">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center space-x-3 mb-2">
                      <TaskPriorityBadge :priority="task.priority" />
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="statusBadgeClass">
                        {{ statusText }}
                      </span>
                    </div>
                    <DialogTitle as="h3" class="text-xl font-semibold leading-6 text-gray-900 dark:text-gray-100">
                      {{ task.title }}
                    </DialogTitle>
                  </div>
                  
                  <!-- Actions -->
                  <div class="flex items-center space-x-2">
                    <button
                      @click="$emit('edit', task)"
                      class="inline-flex items-center p-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      <PencilIcon class="h-4 w-4" />
                    </button>
                    <button
                      @click="$emit('close')"
                      class="inline-flex items-center p-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none"
                    >
                      <XMarkIcon class="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>

              <!-- Content -->
              <div class="px-6 pb-6">
                <!-- Description -->
                <div class="mb-6">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Description</h4>
                  <div class="prose prose-sm max-w-none text-gray-600 dark:text-gray-400">
                    <p v-if="task.description">{{ task.description }}</p>
                    <p v-else class="italic text-gray-400 dark:text-gray-500">No description provided</p>
                  </div>
                </div>

                <!-- Task Details Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                  <!-- Project -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Project</h4>
                    <div v-if="typeof task.project === 'object' && task.project" class="text-sm text-gray-600 dark:text-gray-400">
                      {{ task.project.name }}
                    </div>
                    <p v-else class="text-sm text-gray-400 dark:text-gray-500 italic">No project</p>
                  </div>

                  <!-- Sprint -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Sprint</h4>
                    <div v-if="typeof task.sprint === 'object' && task.sprint" class="text-sm text-gray-600 dark:text-gray-400">
                      <div class="flex items-center space-x-2">
                        <span>{{ task.sprint.name }}</span>
                        <span v-if="task.sprint.is_active" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200">
                          Active
                        </span>
                      </div>
                      <p v-if="task.sprint.goal" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ task.sprint.goal }}</p>
                    </div>
                    <p v-else class="text-sm text-gray-400 dark:text-gray-500 italic">Not in a sprint</p>
                  </div>
                  <!-- Assignee -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Assignee</h4>
                    <div v-if="task.assignee" class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div class="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                            {{ getUserInitials(task.assignee) }}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {{ getUserDisplayName(task.assignee) }}
                        </p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ task.assignee?.email || 'No email' }}</p>
                      </div>
                    </div>
                    <p v-else class="text-sm text-gray-400 dark:text-gray-500 italic">Unassigned</p>
                  </div>

                  <!-- Story Points -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Story Points</h4>
                    <div class="flex items-center">
                      <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200">
                        {{ task.story_points || 0 }} points
                      </span>
                    </div>
                  </div>

                  <!-- Due Date -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Due Date</h4>
                    <div v-if="task.due_date" class="flex items-center space-x-2">
                      <CalendarDaysIcon class="h-4 w-4 text-gray-400 dark:text-gray-500" />
                      <span 
                        class="text-sm"
                        :class="{
                          'text-red-600 dark:text-red-400': isOverdue,
                          'text-yellow-600 dark:text-yellow-400': isDueSoon,
                          'text-gray-600 dark:text-gray-400': !isOverdue && !isDueSoon
                        }"
                      >
                        {{ formatDate(task.due_date) }}
                      </span>
                    </div>
                    <p v-else class="text-sm text-gray-400 dark:text-gray-500 italic">No due date set</p>
                  </div>

                  <!-- Created -->
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Created</h4>
                    <div class="flex items-center space-x-2">
                      <ClockIcon class="h-4 w-4 text-gray-400 dark:text-gray-500" />
                      <span class="text-sm text-gray-600 dark:text-gray-400">
                        {{ formatDate(task.created_at) }}
                      </span>
                      <span v-if="task.created_by" class="text-sm text-gray-500 dark:text-gray-400">
                        by {{ getUserDisplayName(task.created_by) }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Comments Section -->
                <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <div class="flex items-center justify-between mb-4">
                    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Comments ({{ task.comments?.length || 0 }})
                    </h4>
                  </div>
                  
                  <!-- Add Comment Form -->
                  <div class="mb-6">
                    <div class="flex space-x-3">
                      <div class="flex-shrink-0">
                        <div class="h-8 w-8 bg-indigo-600 rounded-full flex items-center justify-center">
                          <span class="text-xs font-medium text-white">
                            {{ currentUserInitials }}
                          </span>
                        </div>
                      </div>
                      <div class="flex-1">
                        <textarea
                          v-model="newComment"
                          @keydown.enter.ctrl="handleAddComment"
                          @keydown.enter.meta="handleAddComment"
                          rows="2"
                          placeholder="Add a comment... (Ctrl+Enter to submit)"
                          class="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                          :disabled="isAddingComment"
                        />
                        <div class="mt-2 flex justify-end space-x-2">
                          <button
                            v-if="newComment.trim()"
                            @click="newComment = ''"
                            type="button"
                            class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                            :disabled="isAddingComment"
                          >
                            Cancel
                          </button>
                          <button
                            @click="handleAddComment"
                            type="button"
                            :disabled="!newComment.trim() || isAddingComment"
                            class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span v-if="isAddingComment" class="flex items-center">
                              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Adding...
                            </span>
                            <span v-else>Add Comment</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Comments List -->
                  <div v-if="task.comments && task.comments.length > 0" class="space-y-4 max-h-96 overflow-y-auto">
                    <div
                      v-for="comment in task.comments"
                      :key="comment.public_id"
                      class="flex space-x-3 group"
                    >
                      <div class="flex-shrink-0">
                        <div class="h-6 w-6 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                          <span class="text-xs font-medium text-gray-700 dark:text-gray-300">
                            {{ getUserInitials(comment.author) }}
                          </span>
                        </div>
                      </div>
                      <div class="flex-1">
                        <div class="flex items-start justify-between">
                          <div class="flex-1">
                            <div class="flex items-center space-x-2">
                              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                {{ getUserDisplayName(comment.author) }}
                              </span>
                              <span class="text-xs text-gray-500 dark:text-gray-400">
                                {{ formatRelativeTime(comment.created_at) }}
                              </span>
                              <span v-if="comment.edited" class="text-xs text-gray-400 dark:text-gray-500 italic">
                                (edited)
                              </span>
                            </div>
                            
                            <!-- Edit Mode -->
                            <div v-if="editingCommentId === comment.public_id" class="mt-1">
                              <textarea
                                v-model="editingCommentContent"
                                @keydown.escape="cancelEditComment"
                                @keydown.enter.ctrl="saveEditComment"
                                @keydown.enter.meta="saveEditComment"
                                rows="2"
                                class="block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-gray-100 px-3 py-2"
                                :disabled="isSavingComment"
                              />
                              <div class="mt-2 flex space-x-2">
                                <button
                                  @click="cancelEditComment"
                                  type="button"
                                  class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                                  :disabled="isSavingComment"
                                >
                                  Cancel
                                </button>
                                <button
                                  @click="saveEditComment"
                                  type="button"
                                  :disabled="!editingCommentContent.trim() || isSavingComment"
                                  class="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 disabled:opacity-50"
                                >
                                  {{ isSavingComment ? 'Saving...' : 'Save' }}
                                </button>
                              </div>
                            </div>
                            
                            <!-- View Mode -->
                            <p v-else class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {{ comment.content }}
                            </p>
                          </div>
                          
                          <!-- Comment Actions (only for comment author) -->
                          <div 
                            v-if="canEditComment(comment) && editingCommentId !== comment.public_id"
                            class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1 ml-2"
                          >
                            <button
                              @click="startEditComment(comment)"
                              type="button"
                              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                              title="Edit comment"
                            >
                              <PencilIcon class="h-3 w-3" />
                            </button>
                            <button
                              @click="handleDeleteComment(comment)"
                              type="button"
                              class="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                              title="Delete comment"
                            >
                              <TrashIcon class="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-4 text-sm text-gray-500 dark:text-gray-400">
                    No comments yet. Be the first to comment!
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="bg-gray-50 dark:bg-gray-700 px-6 py-3 flex justify-between items-center">
                <div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
                  <span>Last updated {{ formatDate(task.updated_at) }}</span>
                  <span v-if="task.updated_by" class="ml-1">by {{ getUserDisplayName(task.updated_by) }}</span>
                </div>
                
                <div class="flex items-center space-x-3">
                  <button
                    @click="$emit('close')"
                    class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  >
                    Close
                  </button>
                  <button
                    @click="$emit('edit', task)"
                    class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Edit Task
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import {
  XMarkIcon,
  PencilIcon,
  CalendarDaysIcon,
  ClockIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import TaskPriorityBadge from './TaskPriorityBadge.vue'
import type { Task, Comment } from '../types/project.types'
import { getUserDisplayName, getUserInitials } from '@/utils/userHelpers'
import { formatDate, formatRelativeTime } from '@/utils/dateHelpers'
import { useAuthStore } from '@/stores/auth'
import { useCommentStore } from '../stores/commentStore'
import { useToastStore } from '@/shared/stores/toastStore'

interface Props {
  show: boolean
  task: Task
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  edit: [task: Task]
  commentAdded: [comment: Comment]
  commentUpdated: [comment: Comment]
  commentDeleted: [commentId: string]
}>()

// Stores
const authStore = useAuthStore()
const commentStore = useCommentStore()
const toastStore = useToastStore()

// Comment state
const newComment = ref('')
const isAddingComment = ref(false)
const editingCommentId = ref<string | null>(null)
const editingCommentContent = ref('')
const isSavingComment = ref(false)

// Computed properties
const currentUserInitials = computed(() => {
  const user = authStore.user
  if (!user) return '?'
  const firstInitial = user.first_name?.[0] || ''
  const lastInitial = user.last_name?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || user.email?.[0]?.toUpperCase() || '?'
})
const statusText = computed(() => {
  const statusMap = {
    todo: 'To Do',
    in_progress: 'In Progress', 
    review: 'In Review',
    done: 'Done',
    blocked: 'Blocked'
  }
  return statusMap[props.task.status] || props.task.status
})

const statusBadgeClass = computed(() => {
  const classMap = {
    todo: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200',
    in_progress: 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200',
    review: 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200',
    done: 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200',
    blocked: 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200'
  }
  return classMap[props.task.status] || classMap.todo
})

const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  return new Date(props.task.due_date) < new Date()
})

const isDueSoon = computed(() => {
  if (!props.task.due_date || isOverdue.value) return false
  const dueDate = new Date(props.task.due_date)
  const threeDaysFromNow = new Date()
  threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3)
  return dueDate <= threeDaysFromNow
})

// Utility functions
// Comment methods
function canEditComment(comment: Comment): boolean {
  return authStore.user?.public_id === comment.author?.public_id
}

async function handleAddComment() {
  if (!newComment.value.trim() || isAddingComment.value) return
  
  isAddingComment.value = true
  try {
    const comment = await commentStore.addComment(props.task.public_id, newComment.value.trim())
    
    // Add the comment to the task's comment list locally (only once!)
    if (!props.task.comments) {
      props.task.comments = []
    }
    props.task.comments.push(comment)
    
    emit('commentAdded', comment)
    newComment.value = ''
    // Don't show toast here - commentStore already shows it
  } catch (error) {
    console.error('Failed to add comment:', error)
    // Don't show error toast here - commentStore already shows it
  } finally {
    isAddingComment.value = false
  }
}

function startEditComment(comment: Comment) {
  editingCommentId.value = comment.public_id
  editingCommentContent.value = comment.content
}

function cancelEditComment() {
  editingCommentId.value = null
  editingCommentContent.value = ''
}

async function saveEditComment() {
  if (!editingCommentContent.value.trim() || !editingCommentId.value || isSavingComment.value) return
  
  isSavingComment.value = true
  try {
    const updatedComment = await commentStore.updateComment(
      editingCommentId.value,
      editingCommentContent.value.trim()
    )
    
    // Update local comment
    const index = props.task.comments?.findIndex(c => c.public_id === editingCommentId.value)
    if (index !== undefined && index >= 0 && props.task.comments) {
      props.task.comments[index] = updatedComment
    }
    
    emit('commentUpdated', updatedComment)
    cancelEditComment()
    // Don't show toast here - commentStore already shows it
  } catch (error) {
    console.error('Failed to update comment:', error)
    // Don't show error toast here - commentStore already shows it
  } finally {
    isSavingComment.value = false
  }
}

async function handleDeleteComment(comment: Comment) {
  if (!confirm('Are you sure you want to delete this comment?')) return
  
  try {
    await commentStore.deleteComment(comment.public_id)
    
    // Remove the comment from the task's comment list locally (only once!)
    if (props.task.comments) {
      props.task.comments = props.task.comments.filter(c => c.public_id !== comment.public_id)
    }
    
    emit('commentDeleted', comment.public_id)
    // Don't show toast here - commentStore already shows it
  } catch (error) {
    console.error('Failed to delete comment:', error)
    // Don't show error toast here - commentStore already shows it
  }
}
</script>