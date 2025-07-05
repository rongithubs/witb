const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const fetcher = (url: string) => {
  const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
  return fetch(fullUrl).then((res) => {
    if (!res.ok) throw new Error("Failed to fetch");
    return res.json();
  });
};
