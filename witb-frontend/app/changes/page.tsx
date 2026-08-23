"use client";

import Header from "@/components/ui/Header";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { BagChangeFeed } from "@/components/witb/BagChangeFeed";
import { useState } from "react";

export default function ChangesPage() {
  const [, setQuery] = useState("");

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-page">
        <Header onSearch={setQuery} />

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="py-8">
            <h1 className="text-3xl font-bold tracking-tight text-ink">
              What Changed
            </h1>
            <p className="mt-2 text-ink-secondary">
              Recent equipment changes across the pros, newest first
            </p>
          </div>

          {/* Change Feed */}
          <div className="pb-12">
            <ErrorBoundary>
              <BagChangeFeed limit={50} />
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
}
