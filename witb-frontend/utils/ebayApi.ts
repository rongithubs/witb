import { EBaySearchResponse, EBaySearchParams, EBayProduct } from '@/types/schemas';
import { generateMockEBayResponse } from './mockEBayData';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-api.com' 
  : 'http://localhost:8000';

class EBayApiService {
  private async fetchWithTimeout(url: string, options: RequestInit, timeout = 5000): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async searchProducts(params: EBaySearchParams): Promise<EBaySearchResponse> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params.brand) searchParams.append('brand', params.brand);
      if (params.model) searchParams.append('model', params.model);
      if (params.category) searchParams.append('category', params.category);
      if (params.condition) searchParams.append('condition', params.condition);
      if (params.max_price) searchParams.append('max_price', params.max_price.toString());
      if (params.min_price) searchParams.append('min_price', params.min_price.toString());
      if (params.limit) searchParams.append('limit', params.limit.toString());

      const url = `${API_BASE_URL}/ebay/search?${searchParams.toString()}`;
      
      const response = await this.fetchWithTimeout(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`eBay API error: ${response.status}`);
      }

      const data: EBaySearchResponse = await response.json();

      // If API returns empty results or sandbox data, fall back to mock data
      if (data.products.length === 0 || data.total_found === 0) {
        console.log('eBay API returned no results, using mock data for development');
        return generateMockEBayResponse(
          params.brand,
          params.model,
          params.category,
          params.limit
        );
      }

      return data;
    } catch (error) {
      console.warn('eBay API call failed, falling back to mock data:', error);
      
      // Fall back to mock data on any error
      return generateMockEBayResponse(
        params.brand,
        params.model,
        params.category,
        params.limit
      );
    }
  }

  async getProductDetails(productId: string): Promise<EBayProduct> {
    try {
      const url = `${API_BASE_URL}/ebay/product/${productId}`;
      
      const response = await this.fetchWithTimeout(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`eBay API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('eBay product details API call failed:', error);
      throw error;
    }
  }

  // Helper method to search for specific WITB equipment
  async searchForWITBItem(brand: string, model: string, category?: string): Promise<EBaySearchResponse> {
    // Clean up the model name for better search results
    const cleanModel = model
      .replace(/\s*\(.*?\)\s*/g, '') // Remove parenthetical info
      .replace(/\s*-\s*/g, ' ')       // Replace dashes with spaces
      .trim();

    return this.searchProducts({
      brand: brand,
      model: cleanModel,
      category: category,
      // Remove condition filter to show all conditions
      limit: 20,
    });
  }

  // Get price summary for quick display
  async getPriceSummary(brand: string, model: string, category?: string): Promise<{
    minPrice: number;
    maxPrice: number;
    averagePrice: number;
    listingCount: number;
  }> {
    try {
      const response = await this.searchForWITBItem(brand, model, category);
      
      if (response.products.length === 0) {
        return {
          minPrice: 0,
          maxPrice: 0,
          averagePrice: 0,
          listingCount: 0,
        };
      }

      const prices = response.products.map(p => p.price_info.current_price);
      
      return {
        minPrice: Math.min(...prices),
        maxPrice: Math.max(...prices),
        averagePrice: Math.round(prices.reduce((sum, price) => sum + price, 0) / prices.length),
        listingCount: response.products.length,
      };
    } catch (error) {
      console.warn('Error getting price summary:', error);
      return {
        minPrice: 0,
        maxPrice: 0,
        averagePrice: 0,
        listingCount: 0,
      };
    }
  }

}

// Export singleton instance
export const ebayApi = new EBayApiService();

// Export the class for potential custom instances
export default EBayApiService;