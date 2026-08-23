"use client";

import Header from "@/components/ui/Header";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { UserProfile } from "@/components/auth/UserProfile";
import { useState } from "react";

export default function ProfilePage() {
  const [, setQuery] = useState("");

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-page">
        <Header onSearch={setQuery} />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="py-8">
            <h1 className="text-3xl font-bold tracking-tight text-ink">
              My Profile
            </h1>
            <p className="mt-2 text-ink-secondary">
              Manage your account and favorite players
            </p>
          </div>
          
          {/* User Profile Content */}
          <div className="pb-12">
            <ErrorBoundary>
              <UserProfile />
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
}