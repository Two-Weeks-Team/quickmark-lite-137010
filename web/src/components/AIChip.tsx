"use client";

interface AIChipProps {
  tags: string[];
}

export default function AIChip({ tags }: AIChipProps) {
  return (
    <div className="mt-2 p-2 bg-green-100 border border-green-300 rounded">
      <p className="font-medium text-green-800">AI Suggested Tags:</p>
      <div className="flex flex-wrap gap-2 mt-1">
        {tags.map((tag, idx) => (
          <span key={idx} className="px-2 py-1 bg-green-200 text-green-800 rounded text-sm">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}