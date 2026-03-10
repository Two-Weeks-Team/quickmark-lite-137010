export interface Bookmark {
  id: number;
  url: string;
  title: string;
  tags: string[];
  created_at: string;
}

export async function createBookmark(url: string, tags: string[]): Promise<Bookmark> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bookmarks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url, tags })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || 'Failed to create bookmark');
  }
  return res.json();
}

export async function getBookmarks(): Promise<Bookmark[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bookmarks`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || 'Failed to fetch bookmarks');
  }
  return res.json();
}

export async function getAiTags(id: number, maxTags: number = 3): Promise<string[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bookmarks/${id}/ai-tags`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model: 'openai', max_tags: maxTags })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || 'Failed to get AI tags');
  }
  const data = await res.json();
  return data.suggested_tags;
}