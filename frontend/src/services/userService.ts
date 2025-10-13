/**
 * User Service
 * Ham Dog & TC's user management API communication
 */
import api from '@/services/api'
import type { User } from '@/stores/auth'

class UserService {
  /**
   * Search for users by email or name
   */
  async searchUsers(query: string): Promise<User[]> {
    const response = await api.get(`/users/search/?q=${encodeURIComponent(query)}`)
    return response || []
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/me/')
    return response
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: string, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/${userId}/`, data)
    return response
  }
}

export default new UserService()