"use client";

import { useState } from "react";
import { ThemeToggle } from "@/components/theme-toggle";

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
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">WITB Database</h1>
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={query}
            onChange={handleChange}
            placeholder="Search players/clubs..."
            className="w-64 border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
