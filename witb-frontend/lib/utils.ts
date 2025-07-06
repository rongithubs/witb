import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function playerListClasses(isMobileMenuOpen: boolean) {
  return cn(
    "col-span-12 md:col-span-4 lg:col-span-3",
    "fixed top-16 left-0 bottom-0 z-40 w-80",
    "md:relative md:top-auto md:inset-auto md:w-auto",
    "transition-transform duration-300 ease-in-out",
    isMobileMenuOpen
      ? "mobile-menu transform translate-x-0"
      : "transform -translate-x-full md:translate-x-0 md:block",
  );
}
