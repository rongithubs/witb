"use client";

import { useState } from "react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

type HeaderProps = {
  onSearch: (query: string) => void;
  isMobileMenuOpen?: boolean;
  onToggleMobileMenu?: () => void;
};

export default function Header({ onSearch, isMobileMenuOpen, onToggleMobileMenu }: HeaderProps) {
  const [query, setQuery] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="max-w-7xl mx-auto flex items-center gap-4">
        {/* Left section: Logo and hamburger menu */}
        <div className="flex items-center gap-3 flex-shrink-0">
          {/* Mobile Hamburger Button */}
          {onToggleMobileMenu && (
            <div className="md:hidden">
              <Button
                variant="outline"
                size="sm"
                onClick={onToggleMobileMenu}
                className="hamburger-button flex items-center gap-2"
              >
                {isMobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
              </Button>
            </div>
          )}
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-900 dark:text-white truncate">WITB</h1>
        </div>
        
        {/* Center section: Search bar */}
        <div className="flex-1 flex justify-center">
          <input
            type="text"
            value={query}
            onChange={handleChange}
            placeholder="Search players/clubs..."
            className="w-48 sm:w-64 md:w-80 lg:w-96 max-w-lg border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
        </div>
        
        {/* Right section: Theme toggle */}
        <div className="flex-shrink-0">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
