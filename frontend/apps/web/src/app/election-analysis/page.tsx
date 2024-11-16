"use client";

import { ElectoralCalculator } from "@/components/ElectoralCalculator";

export default function ElectionAnalysisPage() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Election Analysis Tool</h1>
        <p className="text-gray-600">
          Analyze electoral impacts based on demographic support and issue
          positions
        </p>
      </div>

      <ElectoralCalculator />
    </main>
  );
}
