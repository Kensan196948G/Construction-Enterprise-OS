"use client";

import { Construction } from "lucide-react";

interface Props {
  title: string;
  description?: string;
  section?: string;
}

export default function UnderDevelopment({
  title,
  description,
  section,
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 p-8">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-amber-50 text-amber-500">
        <Construction className="h-10 w-10" />
      </div>
      <div className="text-center max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
        {section && (
          <p className="text-xs font-medium uppercase tracking-wider text-blue-600 mb-3">
            {section}
          </p>
        )}
        <p className="text-gray-500 text-sm leading-relaxed">
          {description ?? "このページは現在開発中です。近日公開予定です。"}
        </p>
      </div>
      <div className="flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-2">
        <span className="text-xs text-amber-700 font-medium">
          🚧 実装予定機能
        </span>
      </div>
    </div>
  );
}
