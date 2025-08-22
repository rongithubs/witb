"use client";

import { useState } from "react";
import { Search, X } from "lucide-react";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { LoginButton } from "@/components/auth/LoginButton";

type HeaderProps = {
  onSearch: (query: string) => void;
};

export default function Header({ onSearch }: HeaderProps) {
  const [query, setQuery] = useState("");
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onSearch(e.target.value);
  };

  const clearSearch = () => {
    setQuery("");
    onSearch("");
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="mx-auto px-4 sm:px-6">
        {/* Mobile-first layout */}
        <div className="flex items-center justify-between h-16">
          {/* Logo - always visible */}
          <div className="flex items-center flex-shrink-0">
            <Link href="/" className="hover:opacity-80 transition-opacity">
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                WITB
              </h1>
            </Link>
          </div>

          {/* Desktop: Search + Actions */}
          <div className="hidden md:flex items-center gap-4 flex-1 justify-center max-w-2xl mx-8">
            <div className="relative flex-1 max-w-lg">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                value={query}
                onChange={handleChange}
                placeholder="Search players or equipment..."
                className="block w-full pl-10 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:focus:ring-emerald-400 focus:border-transparent shadow-sm text-sm"
              />
              {query && (
                <button
                  onClick={clearSearch}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  <X className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                </button>
              )}
            </div>
          </div>

          {/* Actions - always visible on desktop */}
          <div className="hidden md:flex items-center gap-3 flex-shrink-0">
            <LoginButton />
            <ThemeToggle />
          </div>

          {/* Mobile: Actions only */}
          <div className="flex md:hidden items-center gap-2 flex-shrink-0">
            <LoginButton />
            <ThemeToggle />
          </div>
        </div>

        {/* Mobile: Full-width search bar */}
        <div className="md:hidden pb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={query}
              onChange={handleChange}
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setIsSearchFocused(false)}
              placeholder="Search players or equipment..."
              className={`block w-full pl-12 pr-12 py-4 border-2 rounded-2xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none text-base transition-all duration-200 ${
                isSearchFocused
                  ? 'border-emerald-500 dark:border-emerald-400 bg-white dark:bg-gray-900 shadow-lg'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            />
            {query && (
              <button
                onClick={clearSearch}
                className="absolute inset-y-0 right-0 pr-4 flex items-center"
              >
                <X className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
