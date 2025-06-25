"use client";

import { useState } from "react";

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
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 p-4 shadow-sm">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">WITB Database</h1>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder="Search players/clubs..."
          className="w-64 border rounded px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
    </header>
  );
}
