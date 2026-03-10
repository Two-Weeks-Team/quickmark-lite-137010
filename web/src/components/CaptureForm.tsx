"use client";

import { useState } from 'react';
import { createBookmark } from '@/lib/api';
import AIChip from '@/components/AIChip';

export default function CaptureForm() {
  const [url, setUrl] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedTags, setSuggestedTags] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tags = tagsInput
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);
      const bookmark = await createBookmark(url, tags);
      // fetch AI tags for the newly created bookmark
      const aiTags = await fetch(`/api/bookmarks/${bookmark.id}/ai-tags`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: 'openai', max_tags: 3 })
      }).then(r => r.json()).then(d => d.suggested_tags).catch(() => []);
      setSuggestedTags(aiTags);
      setUrl('');
      setTagsInput('');
    } catch (err: any) {
      setError(err.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 border p-4 rounded bg-white shadow-sm">
      <h2 className="text-xl font-semibold">Add a Bookmark</h2>
      <input
        type="url"
        required
        placeholder="https://example.com"
        value={url}
        onChange={e => setUrl(e.target.value)}
        className="p-2 border rounded"
        disabled={loading}
      />
      <input
        type="text"
        placeholder="Optional tags, comma separated"
        value={tagsInput}
        onChange={e => setTagsInput(e.target.value)}
        className="p-2 border rounded"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        {loading ? 'Saving...' : 'Save Bookmark'}
      </button>
      {error && <p className="text-red-600">{error}</p>}
      {suggestedTags.length > 0 && <AIChip tags={suggestedTags} />}
    </form>
  );
}
