import { useMemo } from 'react';
import type { SystemInfo } from '@/types/schemas';

interface OWGRUpdateInfo {
  last_updated: string;
  added_count: number;
  updated_count: number;
  total_processed: number;
  source?: string;
}

export function useOWGRInfo(systemInfo?: SystemInfo | null) {
  const owgrInfo = useMemo((): OWGRUpdateInfo | null => {
    if (!systemInfo?.owgr_last_updated) return null;
    
    return {
      last_updated: systemInfo.owgr_last_updated,
      added_count: 0, // Not tracked in new system
      updated_count: systemInfo.owgr_updated_count || 0,
      total_processed: systemInfo.owgr_total_processed || 0,
    };
  }, [systemInfo]);

  const formatLastUpdated = (lastUpdated: string) => {
    try {
      return new Date(lastUpdated).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown';
    }
  };

  return {
    owgrInfo,
    isLoading: false, // No longer loading since data comes from parent
    error: null, // No longer making separate API call
    formatLastUpdated: owgrInfo ? formatLastUpdated(owgrInfo.last_updated) : null
  };
}