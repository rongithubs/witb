import { supabase } from './supabase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiResponse<T> {
  data?: T
  error?: string
}

class ApiClient {
  private async getAuthHeaders(): Promise<Record<string, string>> {
    const { data: { session } } = await supabase.auth.getSession()
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`
    }

    return headers
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json()
        return { error: errorData.detail || 'Request failed' }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      return { error: 'Network error' }
    }
  }

  async post<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: body ? JSON.stringify(body) : undefined,
      })

      if (!response.ok) {
        const errorData = await response.json()
        return { error: errorData.detail || 'Request failed' }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      return { error: 'Network error' }
    }
  }

  async put<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers,
        body: body ? JSON.stringify(body) : undefined,
      })

      if (!response.ok) {
        const errorData = await response.json()
        return { error: errorData.detail || 'Request failed' }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      return { error: 'Network error' }
    }
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json()
        return { error: errorData.detail || 'Request failed' }
      }

      const data = await response.json()
      return { data }
    } catch (error) {
      return { error: 'Network error' }
    }
  }
}

export const apiClient = new ApiClient()

// SWR fetcher function
export const fetcher = async (url: string) => {
  const response = await apiClient.get(url)
  if (response.error) {
    throw new Error(response.error)
  }
  return response.data
}

// Simplified API for direct calls
export const api = {
  get: (url: string) => apiClient.get(url),
  post: (url: string, data?: any) => apiClient.post(url, data),
  put: (url: string, data?: any) => apiClient.put(url, data),
  delete: (url: string) => apiClient.delete(url),
}

// Auth-specific API calls
export const authApi = {
  getCurrentUser: () => apiClient.get('/auth/me'),
  verifyToken: () => apiClient.post('/auth/verify-token'),
  healthCheck: () => apiClient.get('/auth/health'),
  getFavorites: () => apiClient.get('/auth/me/favorites'),
  addFavorite: (playerId: string) => apiClient.post('/auth/me/favorites', { player_id: playerId }),
  removeFavorite: (playerId: string) => apiClient.delete(`/auth/me/favorites/${playerId}`),
}