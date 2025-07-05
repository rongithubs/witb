"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import { useState, memo } from "react";
import { WITBItem } from "@/types/schemas";
import { TournamentWinnerSkeleton } from "@/components/skeletons";

type TournamentWinner = {
  winner: string;
  tournament: string;
  date: string;
  score: string;
  witb_items?: WITBItem[];
};

const TournamentWinner = memo(function TournamentWinner() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { data: winnerData, error, isLoading } = useSWR<TournamentWinner>(
    "/tournament-winner",
    fetcher
  );

  // Use WITB items from the tournament winner API response
  const witbItems = winnerData?.witb_items || [];

  if (isLoading) {
    return <TournamentWinnerSkeleton />;
  }

  if (error || !winnerData) {
    return null; // Don't show anything if there's an error
  }

  return (
    <div className="relative mb-6 p-6 rounded-2xl backdrop-blur-2xl bg-gradient-to-br from-blue-50/80 via-slate-50/60 to-green-50/70 dark:from-white/5 dark:via-white/3 dark:to-white/2 border border-slate-200/60 dark:border-white/5 shadow-2xl shadow-blue-500/10 dark:shadow-green-400/10">
      {/* Glass reflection effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/80 via-blue-50/40 to-transparent opacity-70 dark:from-white/8 dark:via-white/4 dark:to-transparent dark:opacity-20 pointer-events-none"></div>
      
      {/* Glass shine effect for light mode */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-transparent via-white/50 to-blue-100/60 dark:hidden pointer-events-none"></div>
      
      {/* Subtle noise texture for glass realism */}
      <div className="absolute inset-0 rounded-2xl opacity-[0.03] dark:opacity-[0.02] pointer-events-none" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
      }}></div>
      
      <div className="relative flex items-center justify-between">
        <div className="flex items-center">
          <div className="flex-shrink-0 p-2 rounded-full bg-gradient-to-br from-green-400/30 to-green-600/40 dark:from-green-400/20 dark:to-green-600/20 backdrop-blur-sm border border-green-400/50 dark:border-green-400/30 shadow-lg shadow-green-500/20">
            <svg className="h-5 w-5 text-green-400 dark:text-green-300" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-4">
            <h3 className="text-base font-semibold text-slate-800 dark:text-white/90 tracking-tight">
              Latest Tournament Winner
            </h3>
            <div className="mt-1 text-sm text-slate-600 dark:text-white/70">
              <span className="font-semibold">{winnerData.winner}</span> won{" "}
              <span className="font-medium">{winnerData.tournament}</span>
              {winnerData.score && (
                <span className="ml-1">
                  at <span className="font-medium">{winnerData.score}</span>
                </span>
              )}
              {winnerData.date && (
                <span className="ml-2 text-slate-500 dark:text-white/50">• {winnerData.date}</span>
              )}
            </div>
          </div>
        </div>
        
        {witbItems.length > 0 && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-600 dark:text-white/60 font-medium">See what&apos;s in their bag</span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="group w-10 h-10 rounded-full bg-gradient-to-br from-slate-100/80 to-blue-50/60 dark:from-white/8 dark:to-white/4 backdrop-blur-xl border border-slate-200/70 dark:border-white/8 hover:from-slate-200/90 hover:to-blue-100/80 dark:hover:from-white/12 dark:hover:to-white/8 hover:border-slate-300/80 dark:hover:border-white/15 flex items-center justify-center transition-all duration-300 hover:scale-105 active:scale-95 shadow-lg shadow-blue-500/20 dark:shadow-none"
            >
              <svg 
                className={`w-4 h-4 text-slate-700 dark:text-white/80 transition-all duration-300 group-hover:text-slate-900 dark:group-hover:text-white ${isExpanded ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        )}
      </div>
      
      <div className={`overflow-hidden transition-all duration-700 ease-in-out ${isExpanded ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className={`relative mt-6 pt-6 pb-4 border-t border-white/40 dark:border-white/5 transition-all duration-700 ease-in-out ${isExpanded ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
          <h4 className={`text-sm font-semibold text-slate-800 dark:text-white/90 mb-4 tracking-wide transition-all duration-500 delay-200 ease-out ${isExpanded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}>What&apos;s In The Bag</h4>
          <div className="space-y-4 px-1">
            {witbItems.map((club, index) => (
              <div 
                key={index} 
                className="group relative p-4 rounded-xl backdrop-blur-xl bg-gradient-to-br from-slate-50/70 via-blue-50/50 to-white/60 dark:from-white/3 dark:via-white/2 dark:to-white/1 border border-slate-200/50 dark:border-white/5 hover:from-slate-100/80 hover:via-blue-50/70 hover:to-white/80 dark:hover:from-white/6 dark:hover:via-white/4 dark:hover:to-white/3 hover:border-slate-300/60 dark:hover:border-white/10 transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl hover:shadow-blue-500/15 dark:hover:shadow-black/5 animate-fadeInUp"
                style={{
                  animationDelay: `${(index * 120) + 400}ms`,
                  animationFillMode: 'both'
                }}
              >
                {/* Inner glass reflection */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/60 via-blue-50/30 to-transparent opacity-80 dark:from-white/4 dark:via-white/2 dark:to-transparent dark:opacity-30 pointer-events-none"></div>
                
                {/* Light mode glass shine */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-tr from-transparent via-white/40 to-slate-100/50 dark:hidden opacity-60 pointer-events-none"></div>
                
                <div className="relative flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-semibold text-slate-800 dark:text-white/90 text-sm mb-1">{club.category}</div>
                    <div className="text-slate-700 dark:text-white/80 text-sm font-medium mb-2">{club.brand} {club.model}</div>
                    <div className="space-y-1">
                      {club.loft && <div className="text-slate-600 dark:text-white/60 text-xs">Loft: {club.loft}</div>}
                      {club.shaft && <div className="text-slate-600 dark:text-white/60 text-xs">Shaft: {club.shaft}</div>}
                    </div>
                  </div>
                  {club.product_url && (
                    <a
                      href={club.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 px-4 py-2 bg-gradient-to-r from-blue-500/80 to-purple-600/80 hover:from-blue-600/90 hover:to-purple-700/90 text-white text-xs font-medium rounded-lg backdrop-blur-sm border border-white/20 transition-all duration-300 hover:scale-105 active:scale-95 hover:shadow-lg hover:shadow-blue-500/25 flex-shrink-0"
                    >
                      View Product
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});

export default TournamentWinner;