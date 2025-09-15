"use client";

interface AnimatedHamburgerProps {
  isOpen: boolean;
  onClick: () => void;
  className?: string;
  "aria-label"?: string;
}

export function AnimatedHamburger({
  isOpen,
  onClick,
  className = "",
  "aria-label": ariaLabel = "Toggle menu",
}: AnimatedHamburgerProps) {
  return (
    <button
      onClick={onClick}
      className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors ${className}`}
      aria-label={ariaLabel}
      aria-expanded={isOpen}
    >
      <div className="relative w-5 h-5 flex flex-col justify-center items-center">
        {/* Top line */}
        <span
          className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 ease-in-out transform origin-center ${
            isOpen ? "rotate-45 translate-y-[2px]" : "rotate-0 translate-y-0"
          }`}
        />

        {/* Middle line */}
        <span
          className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 ease-in-out my-1 ${
            isOpen ? "opacity-0 scale-0" : "opacity-100 scale-100"
          }`}
        />

        {/* Bottom line */}
        <span
          className={`block w-5 h-0.5 bg-gray-600 dark:bg-gray-300 transition-all duration-300 ease-in-out transform origin-center ${
            isOpen ? "-rotate-45 -translate-y-[2px]" : "rotate-0 translate-y-0"
          }`}
        />
      </div>
    </button>
  );
}
