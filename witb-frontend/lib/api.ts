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

      // Handle 204 No Content responses (common for DELETE operations)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return { data: undefined as T }
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
  console.log('Fetcher called for URL:', url)
  const response = await apiClient.get(url)
  console.log('Fetcher response:', response)
  if (response.error) {
    console.error('Fetcher error:', response.error)
    throw new Error(response.error)
  }
  return response.data
}

// Simplified API for direct calls
export const api = {
  get: async (url: string) => {
    const response = await apiClient.get(url)
    if (response.error) {
      throw new Error(response.error)
    }
    return response.data
  },
  post: async (url: string, data?: any) => {
    const response = await apiClient.post(url, data)
    if (response.error) {
      throw new Error(response.error)
    }
    return response.data
  },
  put: async (url: string, data?: any) => {
    const response = await apiClient.put(url, data)
    if (response.error) {
      throw new Error(response.error)
    }
    return response.data
  },
  delete: async (url: string) => {
    const response = await apiClient.delete(url)
    if (response.error) {
      throw new Error(response.error)
    }
    return response.data
  },
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