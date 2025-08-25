import Image from "next/image";
import { getClubHeadImagePath } from "@/lib/image-utils";

interface ClubImageProps {
  brandName: string;
  modelName: string;
  category?: string;
  className?: string;
  width?: number;
  height?: number;
  style?: React.CSSProperties;
}

export function ClubImage({ 
  brandName, 
  modelName,
  category,
  className = "", 
  width = 48, 
  height = 48,
  style
}: ClubImageProps) {
  const imagePath = getClubHeadImagePath(brandName, modelName);
  
  if (!imagePath) {
    // No club head image available - return null to not render anything
    return null;
  }
  
  return (
    <Image
      src={imagePath}
      alt={`${brandName} ${modelName} ${category || 'club'}`}
      width={width}
      height={height}
      className={`object-contain ${className}`}
      style={style}
      priority={false}
    />
  );
}