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
}

export const apiClient = new ApiClient()

// Auth-specific API calls
export const authApi = {
  getCurrentUser: () => apiClient.get('/auth/me'),
  verifyToken: () => apiClient.post('/auth/verify-token'),
  healthCheck: () => apiClient.get('/auth/health'),
}