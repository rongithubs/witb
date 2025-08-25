/**
 * Utilities for handling brand logos and golf equipment images
 */

// Brand name to logo file mapping
const BRAND_LOGO_MAP: Record<string, string> = {
  'TaylorMade': '/images/brands/taylormade-logo.png',
  'Titleist': '/images/brands/titleist-logo.png',
  'PING': '/images/brands/ping-logo.png',
};

// Club head image mapping: brand-model combinations
const CLUB_HEAD_MAP: Record<string, string> = {
  'TaylorMade-Qi10': '/images/clubs/qi10_3wood.png',
  'Titleist-GT2': '/images/clubs/titleist-gt2-driver.avif',
  'Titleist-T100': '/images/clubs/titleist-t100-iron.avif',
};

/**
 * Get the logo image path for a brand name
 * Returns null if no logo is available for the brand
 */
export function getBrandLogoPath(brandName: string): string | null {
  if (!brandName) return null;
  
  // Try exact match first
  if (BRAND_LOGO_MAP[brandName]) {
    return BRAND_LOGO_MAP[brandName];
  }
  
  // Try case-insensitive match
  const brandLower = brandName.toLowerCase();
  for (const [brand, logoPath] of Object.entries(BRAND_LOGO_MAP)) {
    if (brand.toLowerCase() === brandLower) {
      return logoPath;
    }
  }
  
  return null;
}

/**
 * Get the club head image path for a brand-model combination
 * Returns null if no club head image is available
 */
export function getClubHeadImagePath(brandName: string, modelName: string): string | null {
  if (!brandName || !modelName) return null;
  
  // Create brand-model key
  const brandModelKey = `${brandName}-${modelName}`;
  
  // Try exact match first
  if (CLUB_HEAD_MAP[brandModelKey]) {
    return CLUB_HEAD_MAP[brandModelKey];
  }
  
  // Try case-insensitive match
  const brandModelLower = brandModelKey.toLowerCase();
  for (const [key, imagePath] of Object.entries(CLUB_HEAD_MAP)) {
    if (key.toLowerCase() === brandModelLower) {
      return imagePath;
    }
  }
  
  // Try partial matches for model variations (e.g., "Qi10" matches "QI10")
  for (const [key, imagePath] of Object.entries(CLUB_HEAD_MAP)) {
    const [keyBrand, keyModel] = key.split('-');
    if (keyBrand.toLowerCase() === brandName.toLowerCase()) {
      // Check if model is a partial match
      const keyModelLower = keyModel.toLowerCase();
      const modelLower = modelName.toLowerCase();
      if (keyModelLower.includes(modelLower) || modelLower.includes(keyModelLower)) {
        return imagePath;
      }
    }
  }
  
  return null;
}

/**
 * Check if a brand has a logo available
 */
export function hasBrandLogo(brandName: string): boolean {
  return getBrandLogoPath(brandName) !== null;
}

/**
 * Check if a brand-model combination has a club head image available
 */
export function hasClubHeadImage(brandName: string, modelName: string): boolean {
  return getClubHeadImagePath(brandName, modelName) !== null;
}

/**
 * Get all supported brand names that have logos
 */
export function getSupportedBrands(): string[] {
  return Object.keys(BRAND_LOGO_MAP);
}

/**
 * Get all supported club head combinations
 */
export function getSupportedClubHeads(): string[] {
  return Object.keys(CLUB_HEAD_MAP);
}