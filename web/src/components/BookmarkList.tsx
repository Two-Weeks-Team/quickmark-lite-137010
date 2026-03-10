"use client";

import { useEffect, useState } from 'react';
import { getBookmarks, Bookmark } from '@/lib/api';

export default function BookmarkList() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getBookmarks();
        setBookmarks(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load bookmarks');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filtered = bookmarks.filter(b => {
    const term = filter.toLowerCase();
    return (
      (b.title?.toLowerCase().includes(term) ?? false) ||
      b.url.toLowerCase().includes(term) ||
      b.tags.some(t => t.toLowerCase().includes(term))
    );
  });

  return (
    <section className="border p-4 rounded bg-white shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Your Bookmarks</h2>
      <input
        type="text"
        placeholder="Search by title, URL or tags"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="w-full p-2 mb-4 border rounded"
      />
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && filtered.length === 0 && <p>No bookmarks found.</p>}
      <ul className="space-y-2">
        {filtered.map(b => (
          <li key={b.id} className="p-2 border rounded hover:bg-gray-100">
            <a href={b.url} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-600">
              {b.title || b.url}
            </a>
            {b.tags.length > 0 && (
              <div className="mt-1 text-sm text-gray-600">
                Tags: {b.tags.join(', ')}
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
