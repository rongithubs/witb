import Image from "next/image";
import { getBrandLogoPath } from "@/lib/image-utils";

interface BrandLogoProps {
  brandName: string;
  className?: string;
  width?: number;
  height?: number;
  fallbackClassName?: string;
}

export function BrandLogo({ 
  brandName, 
  className = "", 
  width = 80, 
  height = 32,
  fallbackClassName = ""
}: BrandLogoProps) {
  const logoPath = getBrandLogoPath(brandName);
  
  if (!logoPath) {
    // Fallback to brand name text
    return (
      <span className={`font-bold text-gray-900 dark:text-white ${fallbackClassName}`}>
        {brandName}
      </span>
    );
  }
  
  // Brand-specific styling for color inversion
  const getBrandSpecificClasses = (brand: string) => {
    const brandLower = brand.toLowerCase();
    if (brandLower === 'taylormade') {
      // TaylorMade: black in light mode, white in dark mode
      return 'brightness-0 dark:brightness-0 dark:invert';
    }
    if (brandLower === 'titleist') {
      // Titleist: normal in light mode, white in dark mode
      return 'dark:brightness-0 dark:invert';
    }
    if (brandLower === 'ping') {
      // PING: normal in light mode, white in dark mode
      return 'dark:brightness-0 dark:invert';
    }
    return '';
  };
  
  return (
    <Image
      src={logoPath}
      alt={`${brandName} logo`}
      width={width}
      height={height}
      className={`object-contain ${getBrandSpecificClasses(brandName)} ${className}`}
      priority={false}
    />
  );
}