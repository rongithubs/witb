"use client";

import { useState } from "react";
import { ThemeToggle } from "@/components/theme-toggle";
import { LoginButton } from "@/components/auth/LoginButton";

type HeaderProps = {
  onSearch: (query: string) => void;
};

export default function Header({ onSearch }: HeaderProps) {
  const [query, setQuery] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="max-w-7xl mx-auto flex items-center gap-4">
        {/* Left section: Logo */}
        <div className="flex items-center gap-3 flex-shrink-0">
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
        
        {/* Right section: Auth and Theme toggle */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <LoginButton />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
