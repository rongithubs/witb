// Utility function to convert country names to flag emojis
export const getCountryFlag = (country: string | null | undefined): string => {
  if (!country) return '🏳️';
  
  const countryToFlag: Record<string, string> = {
    // Major golf nations
    'United States': '🇺🇸',
    'USA': '🇺🇸',
    'Northern Ireland': '🇬🇧', // Part of UK
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'Ireland': '🇮🇪',
    'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'Canada': '🇨🇦',
    'Australia': '🇦🇺',
    'New Zealand': '🇳🇿',
    'South Africa': '🇿🇦',
    
    // European countries
    'Spain': '🇪🇸',
    'Germany': '🇩🇪',
    'France': '🇫🇷',
    'Italy': '🇮🇹',
    'Sweden': '🇸🇪',
    'Denmark': '🇩🇰',
    'Norway': '🇳🇴',
    'Netherlands': '🇳🇱',
    'Belgium': '🇧🇪',
    'Austria': '🇦🇹',
    'Switzerland': '🇨🇭',
    'Finland': '🇫🇮',
    
    // Asian countries
    'Japan': '🇯🇵',
    'South Korea': '🇰🇷',
    'Korea': '🇰🇷',
    'China': '🇨🇳',
    'Thailand': '🇹🇭',
    'Philippines': '🇵🇭',
    'Singapore': '🇸🇬',
    'Malaysia': '🇲🇾',
    'India': '🇮🇳',
    
    // Other countries
    'Argentina': '🇦🇷',
    'Brazil': '🇧🇷',
    'Mexico': '🇲🇽',
    'Chile': '🇨🇱',
    'Colombia': '🇨🇴',
    'Zimbabwe': '🇿🇼',
    'Fiji': '🇫🇯',
    'Venezuela': '🇻🇪',
    'Paraguay': '🇵🇾',
    'Taiwan': '🇹🇼',
    'Czech Republic': '🇨🇿',
    'Poland': '🇵🇱',
    'Portugal': '🇵🇹',
    'Russia': '🇷🇺',
    'Ukraine': '🇺🇦',
  };
  
  // Try exact match first
  if (countryToFlag[country]) {
    return countryToFlag[country];
  }
  
  // Try case-insensitive match
  const normalizedCountry = country.toLowerCase();
  for (const [key, flag] of Object.entries(countryToFlag)) {
    if (key.toLowerCase() === normalizedCountry) {
      return flag;
    }
  }
  
  // Default flag for unknown countries
  return '🏳️';
};

// Helper function to format age display
export const formatAge = (age: number | null | undefined): string => {
  if (!age) return '';
  return `${age} years old`;
};

// Helper function to format age display for compact view
export const formatAgeCompact = (age: number | null | undefined): string => {
  if (!age) return '';
  return `${age}y`;
};