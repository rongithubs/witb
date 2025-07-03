import { useState, useCallback } from 'react';

export function usePagination(initialPage: number = 1) {
  const [page, setPage] = useState(initialPage);

  const nextPage = useCallback(() => {
    setPage(prev => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setPage(prev => Math.max(1, prev - 1));
  }, []);

  const goToPage = useCallback((pageNumber: number) => {
    setPage(Math.max(1, pageNumber));
  }, []);

  const resetPage = useCallback(() => {
    setPage(1);
  }, []);

  return {
    page,
    nextPage,
    prevPage,
    goToPage,
    resetPage,
    setPage
  };
}