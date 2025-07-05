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
      <div className="max-w-7xl mx-auto flex justify-between items-center gap-2">
        <div className="flex items-center gap-3">
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
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-gray-900 dark:text-white truncate">WITB Database</h1>
        </div>
        <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
          <input
            type="text"
            value={query}
            onChange={handleChange}
            placeholder="Search players/clubs..."
            className="w-32 sm:w-48 md:w-64 border border-gray-300 dark:border-gray-600 rounded px-2 md:px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <div className="flex-shrink-0">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
}
