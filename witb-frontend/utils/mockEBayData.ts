import { EBayProduct, EBaySearchResponse } from '@/types/schemas';

// Mock eBay data for development and demo purposes
export const mockGolfEquipment: Record<string, EBayProduct[]> = {
  // TaylorMade Products
  'taylormade stealth': [
    {
      product_id: 'mock-tm-stealth-1',
      title: 'TaylorMade Stealth Driver 10.5° Right Hand Regular Flex',
      brand: 'TaylorMade',
      model: 'Stealth',
      category: 'Driver',
      price_info: {
        current_price: 399.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-tm-stealth-1',
      image_url: 'https://i.ebayimg.com/images/g/mock123/s-l1600.jpg',
      seller_info: {
        username: 'golf_pro_shop',
        feedback_percentage: 99.5,
        feedback_score: 15420,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-stealth-2',
      title: 'TaylorMade Stealth Driver 9° Right Hand Stiff Flex - Used',
      brand: 'TaylorMade',
      model: 'Stealth',
      category: 'Driver',
      price_info: {
        current_price: 279.99,
        currency: 'USD',
        condition: 'Used - Excellent',
        shipping_cost: 12.99,
      },
      listing_url: 'https://ebay.com/mock-tm-stealth-2',
      seller_info: {
        username: 'golf_deals_depot',
        feedback_percentage: 98.2,
        feedback_score: 8341,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],

  // TaylorMade Qi10
  'taylormade qi10': [
    {
      product_id: 'mock-tm-qi10-1',
      title: 'TaylorMade Qi10 Driver 9° Right Hand Stiff Flex - Brand New',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 549.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-1',
      image_url: 'https://i.ebayimg.com/images/g/qi10-1/s-l1600.jpg',
      seller_info: {
        username: 'pro_golf_warehouse',
        feedback_percentage: 99.7,
        feedback_score: 28450,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-qi10-2',
      title: 'TaylorMade Qi10 Driver 10.5° Regular Flex - Excellent Condition',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 479.99,
        currency: 'USD',
        condition: 'Used - Excellent',
        shipping_cost: 15.99,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-2',
      image_url: 'https://i.ebayimg.com/images/g/qi10-2/s-l1600.jpg',
      seller_info: {
        username: 'golf_gear_exchange',
        feedback_percentage: 98.9,
        feedback_score: 12340,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-qi10-3',
      title: 'TaylorMade Qi10 Driver 8° Stiff Flex - Like New',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 499.99,
        currency: 'USD',
        condition: 'Used - Like New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-3',
      image_url: 'https://i.ebayimg.com/images/g/qi10-3/s-l1600.jpg',
      seller_info: {
        username: 'discount_golf_central',
        feedback_percentage: 97.8,
        feedback_score: 6789,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-qi10-4',
      title: 'TaylorMade Qi10 Driver 12° Senior Flex - Good Condition',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 399.99,
        currency: 'USD',
        condition: 'Good',
        shipping_cost: 12.99,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-4',
      seller_info: {
        username: 'second_swing_golf',
        feedback_percentage: 99.1,
        feedback_score: 19876,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-qi10-5',
      title: 'NEW TaylorMade Qi10 Driver 9.5° X-Stiff Shaft Tour Issue',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 599.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-5',
      image_url: 'https://i.ebayimg.com/images/g/qi10-5/s-l1600.jpg',
      seller_info: {
        username: 'tour_golf_specialists',
        feedback_percentage: 100.0,
        feedback_score: 3421,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-tm-qi10-6',
      title: 'TaylorMade Qi10 Driver 10.5° Regular - Minor Wear',
      brand: 'TaylorMade',
      model: 'Qi10',
      category: 'Driver',
      price_info: {
        current_price: 349.99,
        currency: 'USD',
        condition: 'Good',
        shipping_cost: 9.99,
      },
      listing_url: 'https://ebay.com/mock-tm-qi10-6',
      seller_info: {
        username: 'budget_golf_deals',
        feedback_percentage: 96.5,
        feedback_score: 4567,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],
  'taylormade': [
    {
      product_id: 'mock-tm-sim2-1',
      title: 'TaylorMade SIM2 Max Driver 10.5° Regular Flex',
      brand: 'TaylorMade',
      model: 'SIM2 Max',
      category: 'Driver',
      price_info: {
        current_price: 299.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-tm-sim2-1',
      seller_info: {
        username: 'premium_golf_outlet',
        feedback_percentage: 99.8,
        feedback_score: 22150,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],
  
  // Titleist Products
  'titleist pro v1': [
    {
      product_id: 'mock-titleist-pv1-1',
      title: 'Titleist Pro V1 Golf Balls - Dozen (12 Pack) New 2024',
      brand: 'Titleist',
      model: 'Pro V1',
      category: 'Ball',
      price_info: {
        current_price: 54.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-titleist-pv1-1',
      seller_info: {
        username: 'golf_ball_warehouse',
        feedback_percentage: 99.9,
        feedback_score: 45230,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
    {
      product_id: 'mock-titleist-pv1-2',
      title: 'Titleist Pro V1 Used Golf Balls - Near Mint Condition (36 Pack)',
      brand: 'Titleist',
      model: 'Pro V1',
      category: 'Ball',
      price_info: {
        current_price: 89.99,
        currency: 'USD',
        condition: 'Used - Like New',
        shipping_cost: 5.99,
      },
      listing_url: 'https://ebay.com/mock-titleist-pv1-2',
      seller_info: {
        username: 'recycled_golf_balls',
        feedback_percentage: 97.8,
        feedback_score: 12890,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],

  // Scotty Cameron Putters
  'scotty cameron': [
    {
      product_id: 'mock-scotty-newport-1',
      title: 'Scotty Cameron Newport 2 Putter 34" Right Hand',
      brand: 'Scotty Cameron',
      model: 'Newport 2',
      category: 'Putter',
      price_info: {
        current_price: 449.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-scotty-newport-1',
      seller_info: {
        username: 'authorized_golf_dealer',
        feedback_percentage: 100.0,
        feedback_score: 8750,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],

  // Callaway Products
  'callaway': [
    {
      product_id: 'mock-callaway-rogue-1',
      title: 'Callaway Rogue ST Max Irons 5-PW Steel Shafts Right Hand',
      brand: 'Callaway',
      model: 'Rogue ST Max',
      category: 'Iron',
      price_info: {
        current_price: 899.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 0,
      },
      listing_url: 'https://ebay.com/mock-callaway-rogue-1',
      seller_info: {
        username: 'golf_equipment_plus',
        feedback_percentage: 99.3,
        feedback_score: 18940,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],

  // Generic golf equipment for fallback
  'golf': [
    {
      product_id: 'mock-generic-driver-1',
      title: 'Premium Golf Driver 10.5° Regular Flex Right Hand',
      brand: 'Generic',
      model: 'Pro Series',
      category: 'Driver',
      price_info: {
        current_price: 199.99,
        currency: 'USD',
        condition: 'New',
        shipping_cost: 15.99,
      },
      listing_url: 'https://ebay.com/mock-generic-1',
      seller_info: {
        username: 'discount_golf_store',
        feedback_percentage: 96.5,
        feedback_score: 5430,
      },
      location: 'US',
      listing_type: 'FixedPrice',
    },
  ],
};

export function generateMockEBayResponse(
  brand?: string,
  model?: string,
  category?: string,
  limit = 20
): EBaySearchResponse {
  // Create search key for lookup
  const searchParts = [brand?.toLowerCase(), model?.toLowerCase()].filter(Boolean);
  const searchKey = searchParts.join(' ');
  
  // Debug logging
  console.log('Mock eBay search:', { brand, model, category, searchKey });
  
  // Try to find matching products
  let products: EBayProduct[] = [];
  
  if (mockGolfEquipment[searchKey]) {
    products = mockGolfEquipment[searchKey];
  } else if (brand && mockGolfEquipment[brand.toLowerCase()]) {
    products = mockGolfEquipment[brand.toLowerCase()];
  } else if (category && mockGolfEquipment[category.toLowerCase()]) {
    products = mockGolfEquipment[category.toLowerCase()];
  } else {
    // Fallback to generic golf equipment
    products = mockGolfEquipment['golf'];
  }

  // Filter by category if specified
  if (category) {
    products = products.filter(p => 
      p.category?.toLowerCase().includes(category.toLowerCase())
    );
  }

  // Apply limit
  products = products.slice(0, limit);

  const searchQuery = [brand, model].filter(Boolean).join(' ') || 'golf equipment';

  return {
    products,
    total_found: products.length,
    page: 1,
    per_page: limit,
    search_query: searchQuery,
  };
}

// Helper function to get realistic price range for equipment type
export function getEquipmentPriceRange(category: string): { min: number; max: number } {
  const priceRanges: Record<string, { min: number; max: number }> = {
    driver: { min: 199, max: 599 },
    wood: { min: 179, max: 449 },
    hybrid: { min: 149, max: 299 },
    iron: { min: 499, max: 1299 },
    wedge: { min: 99, max: 199 },
    putter: { min: 149, max: 599 },
    ball: { min: 29, max: 64 },
  };

  return priceRanges[category.toLowerCase()] || { min: 50, max: 200 };
}