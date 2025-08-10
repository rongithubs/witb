"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { memo, useState } from "react";
import { WITBItem } from "@/types/schemas";
import {
  Trophy,
  Calendar,
  Target,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Info,
} from "lucide-react";

type TournamentWinner = {
  winner: string;
  tournament: string;
  date: string;
  score: string;
  witb_items?: WITBItem[];
};

interface TournamentWinnerProps {
  isCollapsed?: boolean;
}

const TournamentWinnerWithBag = memo(function TournamentWinnerWithBag({ isCollapsed = false }: TournamentWinnerProps) {
  const [showEquipment, setShowEquipment] = useState(false);
  const {
    data: winnerData,
    error,
    isLoading,
  } = useSWR<TournamentWinner>("/tournament-winner", fetcher);

  const sortEquipmentByClubLength = (items: WITBItem[]) => {
    const clubOrder = {
      'driver': 1,
      '1-wood': 2,
      '2-wood': 3,
      '3-wood': 4,
      '4-wood': 5,
      '5-wood': 6,
      '6-wood': 7,
      '7-wood': 8,
      '9-wood': 9,
      'hybrid': 10,
      '1-hybrid': 10,
      '2-hybrid': 11,
      '3-hybrid': 12,
      '4-hybrid': 13,
      '5-hybrid': 14,
      '6-hybrid': 15,
      'iron': 16,
      '1-iron': 16,
      '2-iron': 17,
      '3-iron': 18,
      '4-iron': 19,
      '5-iron': 20,
      '6-iron': 21,
      '7-iron': 22,
      '8-iron': 23,
      '9-iron': 24,
      'pitching wedge': 25,
      'pw': 25,
      'gap wedge': 26,
      'gw': 26,
      'approach wedge': 27,
      'aw': 27,
      'sand wedge': 28,
      'sw': 28,
      'lob wedge': 29,
      'lw': 29,
      'wedge': 30,
      'putter': 31,
      'ball': 32,
    };

    return [...items].sort((a, b) => {
      const getClubOrder = (category: string) => {
        const normalizedCategory = category.toLowerCase();
        
        // Direct match
        if (clubOrder[normalizedCategory as keyof typeof clubOrder]) {
          return clubOrder[normalizedCategory as keyof typeof clubOrder];
        }
        
        // Check for partial matches
        for (const [key, value] of Object.entries(clubOrder)) {
          if (normalizedCategory.includes(key)) {
            return value;
          }
        }
        
        // Default to end if not found
        return 999;
      };

      return getClubOrder(a.category) - getClubOrder(b.category);
    });
  };

  const witbItems = sortEquipmentByClubLength(winnerData?.witb_items || []);
  
  console.log("Component rendering - showEquipment:", showEquipment, "witbItems length:", witbItems.length);
  console.log("API data:", { winnerData, error, isLoading });
  console.log("Sorted equipment order:", witbItems.map(item => item.category));

  const handleToggleEquipment = () => {
    console.log("handleToggleEquipment called! Current showEquipment:", showEquipment);
    const newState = !showEquipment;
    console.log("Setting showEquipment to:", newState);
    setShowEquipment(newState);

    if (newState) {
      setTimeout(() => {
        const equipmentSection = document.getElementById("equipment-section");
        console.log("Looking for equipment section:", equipmentSection);
        if (equipmentSection) {
          equipmentSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
            inline: "nearest",
          });
        }
      }, 300);
    }
  };

  if (isLoading) {
    return (
      <div className="mb-8">
        <div className="bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6 animate-pulse">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
              <div>
                <div className="h-4 w-24 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
                <div className="h-6 w-32 bg-gray-300 dark:bg-gray-600 rounded mb-1"></div>
                <div className="h-4 w-40 bg-gray-300 dark:bg-gray-600 rounded"></div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="h-4 w-20 bg-gray-300 dark:bg-gray-600 rounded"></div>
              <div className="h-8 w-32 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !winnerData) {
    return null;
  }

  return (
    <div className={`transition-all duration-500 ease-in-out ${isCollapsed ? "mb-4" : "mb-12"}`}>
      {/* Single morphing banner */}
      <div 
        className={`relative w-full overflow-hidden shadow-2xl transition-all duration-1000 cubic-bezier(0.4, 0.0, 0.2, 1) ${
          isCollapsed 
            ? 'h-40 sm:h-32 md:h-24 rounded-xl bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20 border border-emerald-200 dark:border-emerald-700' 
            : 'h-64 sm:h-80 md:h-96 lg:h-[28rem] rounded-xl sm:rounded-3xl bg-gradient-to-br from-emerald-600 via-green-700 to-teal-800'
        }`}
        style={{
          transition: 'height 1000ms cubic-bezier(0.4, 0.0, 0.2, 1), background 800ms cubic-bezier(0.4, 0.0, 0.2, 1) 200ms, border-radius 800ms cubic-bezier(0.4, 0.0, 0.2, 1) 100ms'
        }}
      >
        {/* Background overlay for collapsed state */}
        <div 
          className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"
          style={{
            opacity: isCollapsed ? 0 : 1,
            transition: 'opacity 600ms cubic-bezier(0.4, 0.0, 0.2, 1) 400ms'
          }}
        />

        {/* Decorative elements - fade out when collapsed */}
        <div 
          className="absolute top-8 right-8"
          style={{
            opacity: isCollapsed ? 0 : 0.1,
            transform: isCollapsed ? 'scale(0.7)' : 'scale(1)',
            transition: 'opacity 500ms cubic-bezier(0.4, 0.0, 0.2, 1) 300ms, transform 600ms cubic-bezier(0.4, 0.0, 0.2, 1) 200ms'
          }}
        >
          <Trophy size={120} className="text-white" />
        </div>
        <div 
          className="absolute bottom-8 left-8"
          style={{
            opacity: isCollapsed ? 0 : 0.05,
            transform: isCollapsed ? 'scale(0.7)' : 'scale(1)',
            transition: 'opacity 500ms cubic-bezier(0.4, 0.0, 0.2, 1) 350ms, transform 600ms cubic-bezier(0.4, 0.0, 0.2, 1) 250ms'
          }}
        >
          <div className="w-32 h-32 rounded-full border-4 border-white"></div>
        </div>

        {/* Content container */}
        <div 
          className={`absolute inset-0 flex items-center z-10 ${
            isCollapsed ? 'px-4 py-2 sm:px-10 sm:py-0' : 'px-4 sm:px-6'
          }`}
          style={{
            justifyContent: isCollapsed ? 'flex-start' : 'center',
            transition: 'justify-content 800ms cubic-bezier(0.4, 0.0, 0.2, 1) 100ms, padding 800ms cubic-bezier(0.4, 0.0, 0.2, 1) 100ms'
          }}
        >
          <div 
            className={`w-full transition-all duration-700 ease-in-out ${
              isCollapsed 
                ? 'flex flex-col items-center justify-center gap-2 text-center sm:flex-row sm:justify-between sm:items-center sm:text-left' 
                : 'flex flex-col items-center justify-center gap-0 text-center text-white'
            }`}
          >
            {/* Winner Info Section */}
            <div className={`flex items-center transition-all duration-700 ease-in-out ${isCollapsed ? 'gap-3 sm:gap-5' : 'gap-3 flex-col'}`}>
              {/* Trophy Icon */}
              <div 
                className={`flex-shrink-0 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full flex items-center justify-center transition-all duration-700 ease-in-out ${
                  isCollapsed ? 'w-10 h-10' : 'w-16 h-16 mb-6'
                }`}
              >
                <Trophy size={isCollapsed ? 16 : 20} className="text-white" />
              </div>

              {/* Text Content */}
              <div className={`transition-all duration-700 ease-in-out ${isCollapsed ? 'text-left' : 'text-center'}`}>
                {/* Badge */}
                <div className={`inline-flex items-center gap-2 rounded-full transition-all duration-700 ease-in-out ${
                  isCollapsed 
                    ? 'px-3 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-900/30 mb-1' 
                    : 'px-4 py-2 bg-white/20 backdrop-blur-sm border border-white/30 text-sm font-medium text-white mb-6'
                }`}>
                  {!isCollapsed && <Trophy size={16} className="text-yellow-300" />}
                  <span>
                    {isCollapsed ? 'LATEST WINNER' : 'Latest Tournament Winner'}
                  </span>
                </div>

                {/* Player Name */}
                <h1 
                  className={`font-bold tracking-tight transition-all duration-700 ease-in-out ${
                    isCollapsed 
                      ? 'text-lg text-gray-900 dark:text-white mb-1.5' 
                      : 'text-4xl md:text-5xl lg:text-6xl text-white mb-4'
                  }`}
                >
                  {winnerData.winner}
                </h1>

                {/* Tournament Name */}
                <h2 
                  className={`font-medium transition-all duration-700 ease-in-out ${
                    isCollapsed 
                      ? 'text-xs text-gray-600 dark:text-gray-300' 
                      : 'text-xl md:text-2xl lg:text-3xl text-white/90 mb-6'
                  }`}
                >
                  {winnerData.tournament}
                </h2>
              </div>
            </div>

            {/* Stats and Button Section */}
            <div 
              className={`flex items-center gap-2 transition-all duration-700 ease-in-out ${
                isCollapsed ? 'flex-col justify-center w-full sm:w-auto sm:flex-row' : 'flex-col sm:flex-row justify-center mt-6'
              }`}
            >
              {/* Stats */}
              <div 
                className={`flex items-center gap-4 transition-all duration-700 ease-in-out ${
                  isCollapsed ? 'text-xs text-gray-600 dark:text-gray-400' : 'text-white/80'
                }`}
              >
                {winnerData.date && (
                  <div className="flex items-center gap-1">
                    <Calendar size={isCollapsed ? 12 : 18} />
                    <span className={isCollapsed ? 'text-xs' : 'text-base md:text-lg font-medium'}>
                      {winnerData.date}
                    </span>
                  </div>
                )}
                {winnerData.score && (
                  <div className="flex items-center gap-1">
                    <Target size={isCollapsed ? 12 : 18} />
                    <span className={isCollapsed ? 'text-xs' : 'text-base md:text-lg font-medium'}>
                      {winnerData.score}
                    </span>
                  </div>
                )}
              </div>

              {/* Equipment Toggle Button */}
              {witbItems.length > 0 && (
                <button
                  type="button"
                  onClick={handleToggleEquipment}
                  className={`inline-flex items-center gap-2 font-medium rounded-lg transition-all duration-300 flex-shrink-0 ${
                    isCollapsed
                      ? 'px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs'
                      : 'px-8 py-4 bg-white/20 backdrop-blur-sm border border-white/30 hover:bg-white/30 text-white text-base rounded-full hover:scale-105 focus:ring-2 focus:ring-white/50 shadow-lg mt-2'
                  }`}
                >
                  <span>{showEquipment ? "Hide Equipment" : "View Equipment"}</span>
                  {showEquipment ? (
                    <ChevronUp size={isCollapsed ? 14 : 20} />
                  ) : (
                    <ChevronDown size={isCollapsed ? 14 : 20} />
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Glass reflection effects - fade out when collapsed */}
        <div className={`absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent pointer-events-none transition-opacity duration-700 ${isCollapsed ? 'opacity-0' : 'opacity-100'}`}></div>
        <div className={`absolute top-0 left-0 w-full h-1/3 bg-gradient-to-b from-white/5 to-transparent pointer-events-none transition-opacity duration-700 ${isCollapsed ? 'opacity-0' : 'opacity-100'}`}></div>
      </div>

      {/* Equipment Section */}
      <div
        id="equipment-section"
        className={`transition-all duration-700 ease-in-out overflow-hidden ${
          showEquipment ? "max-h-[5000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div
          className={`transition-all duration-500 delay-200 ${
            showEquipment ? "translate-y-0" : "translate-y-8"
          }`}
        >
          {/* Section Header */}
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-2">
              What&apos;s In The Bag
            </h2>
            <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Discover the exact equipment {winnerData.winner} used to win the{" "}
              {winnerData.tournament}
            </p>
          </div>

          {/* Equipment Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {witbItems.map((item, index) => (
              <div
                key={index}
                className="group relative bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden"
                style={{
                  animationDelay: `${index * 100}ms`,
                  animation: showEquipment
                    ? "fadeInUp 0.6s ease-out forwards"
                    : "none",
                }}
              >
                {/* Category Badge */}
                <div className="absolute top-4 left-4 z-10">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700">
                    {item.category}
                  </span>
                </div>

                {/* Product URL Button */}
                {item.product_url && (
                  <div className="absolute top-4 right-4 z-10">
                    <a
                      href={item.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center w-8 h-8 bg-white/90 dark:bg-slate-700/90 backdrop-blur-sm rounded-full shadow-sm hover:shadow-md transition-all duration-200 hover:scale-110 group/link"
                    >
                      <ExternalLink
                        size={14}
                        className="text-slate-600 dark:text-slate-400 group-hover/link:text-emerald-600 dark:group-hover/link:text-emerald-400"
                      />
                    </a>
                  </div>
                )}

                {/* Card Content */}
                <div className="p-6 pt-12">
                  {/* Brand Name */}
                  <div className="text-lg font-bold text-slate-900 dark:text-white mb-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors duration-200">
                    {item.brand}
                  </div>

                  {/* Model Name */}
                  <div className="text-base font-semibold text-slate-700 dark:text-slate-300 mb-4 line-clamp-2">
                    {item.model}
                  </div>

                  {/* Specifications */}
                  {(item.loft || item.shaft) && (
                    <div className="space-y-2 mb-4">
                      {item.loft && (
                        <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                          <Info
                            size={14}
                            className="text-slate-400 dark:text-slate-500"
                          />
                          <span className="font-medium">Loft:</span>
                          <span>{item.loft}</span>
                        </div>
                      )}
                      {item.shaft && (
                        <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                          <Info
                            size={14}
                            className="text-slate-400 dark:text-slate-500"
                          />
                          <span className="font-medium">Shaft:</span>
                          <span className="line-clamp-1">{item.shaft}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* View Product Button */}
                  {item.product_url && (
                    <a
                      href={item.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-all duration-200 hover:shadow-md justify-center group/btn"
                    >
                      <span>View Product</span>
                      <ExternalLink
                        size={14}
                        className="group-hover/btn:translate-x-0.5 transition-transform duration-200"
                      />
                    </a>
                  )}
                </div>

                {/* Hover overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-emerald-50/50 to-transparent dark:from-emerald-900/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
              </div>
            ))}
          </div>

          {/* Additional Info */}
          <div className="mt-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Equipment specifications as used during the tournament
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
});

export default TournamentWinnerWithBag;
