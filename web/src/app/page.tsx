"use client";

import CaptureForm from '@/components/CaptureForm';
import BookmarkList from '@/components/BookmarkList';

export default function HomePage() {
  return (
    <main className="max-w-3xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-6">QuickMark Lite</h1>
      <CaptureForm />
      <div className="mt-8">
        <BookmarkList />
      </div>
    </main>
  );
}
