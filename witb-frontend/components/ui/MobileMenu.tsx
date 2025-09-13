"use client";

import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { useAuth } from "@/providers/auth-provider";
import { X, User, LogOut, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

const handleScrollToLeaderboard = () => {
  // Find the club leaderboard element and scroll to it
  const leaderboardElement =
    document.querySelector('[data-testid="club-leaderboard"]') ||
    document.querySelector(".club-leaderboard") ||
    document.querySelector('[id*="leaderboard"]');

  if (leaderboardElement) {
    leaderboardElement.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } else {
    // Fallback: scroll to a general position where leaderboard likely is
    window.scrollTo({
      top: window.innerHeight * 0.8, // Scroll down about 80% of viewport
      behavior: "smooth",
    });
  }
};

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  const { user, signOut } = useAuth();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
      onClose();
    } catch (error) {
      console.error("Sign out error:", error);
    } finally {
      setIsSigningOut(false);
    }
  };

  const handleLinkClick = () => {
    onClose();
  };

  const handleLeaderboardClick = () => {
    onClose();

    // Check if we're currently on the main page
    const currentPath = window.location.pathname;

    if (currentPath === '/') {
      // Already on main page, just scroll to leaderboard
      setTimeout(() => {
        handleScrollToLeaderboard();
      }, 100);
    } else {
      // Navigate to main page first, then scroll
      router.push('/');
      // Wait longer for navigation to complete before scrolling
      setTimeout(() => {
        handleScrollToLeaderboard();
      }, 500);
    }
  };

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const menuContent = (
    <>
      {/* Backdrop - only show when open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] md:hidden"
          onClick={onClose}
        />
      )}

      {/* Menu Drawer - always render for animation */}
      <div
        ref={menuRef}
        className={`fixed top-0 left-0 h-full w-80 bg-white dark:bg-gray-900 shadow-2xl z-[70] transform transition-all duration-[400ms] md:hidden flex flex-col ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{
          transitionTimingFunction: "ease-out",
        }}
      >
        {/* Content - only show when user exists */}
        {user && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.user_metadata?.full_name?.split(" ")[0] ||
                      user.user_metadata?.name?.split(" ")[0] ||
                      user.email?.split("@")[0] ||
                      "User"}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user.email}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Menu Content - takes full remaining space */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Navigation Items */}
              <div className="flex-1 overflow-y-auto">
                <div className="p-4 space-y-2">
                  <Link
                    href="/profile"
                    onClick={handleLinkClick}
                    className="flex items-center gap-3 p-3 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <User className="h-5 w-5" />
                    <span className="text-sm font-medium">My Profile</span>
                  </Link>

                  <button
                    onClick={handleLeaderboardClick}
                    className="w-full flex items-center gap-3 p-3 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <TrendingUp className="h-5 w-5" />
                    <span className="text-sm font-medium">Club Leaderboard</span>
                  </button>
                </div>
              </div>

              {/* Footer - pushed to absolute bottom with no bottom padding */}
              <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 pt-4 px-4">
                <button
                  onClick={handleSignOut}
                  disabled={isSigningOut}
                  className="w-full flex items-center gap-3 p-3 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50 mb-0"
                >
                  <LogOut className="h-5 w-5" />
                  <span className="text-sm font-medium">
                    {isSigningOut ? "Signing out..." : "Sign Out"}
                  </span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );

  // Render via Portal to document.body for proper layering
  return typeof document !== "undefined"
    ? createPortal(menuContent, document.body)
    : null;
}
