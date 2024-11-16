"use client";

import { formatDate } from "@/utils/dateUtils";
import { WeeklyAnalysis } from "@frontend/types/api";
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

interface ReasonsData {
  [key: string]: string; // e.g., "approval_rating_fluctuation": "40%"
}

interface SupportingEvidence {
  [key: string]: string[]; // e.g., "reason1": ["quote1", "quote2"]
}

interface DetailedAnalysis {
  reasons: ReasonsData;
  quotes: Record<string, string[]>;
  summary: string;
}

const CHART_COLORS = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
];

interface AnalysisCardProps {
  analysis: WeeklyAnalysis;
}

const AnalysisCard = ({ analysis }: AnalysisCardProps) => {
  // Parse the JSON strings if they're stored as strings
  const reasons: ReasonsData =
    typeof analysis.reasons === "string"
      ? JSON.parse(analysis.reasons)
      : analysis.reasons;

  const detailedAnalysis: string =
    typeof analysis.detailed_analysis === "string"
      ? analysis.detailed_analysis
      : JSON.stringify(analysis.detailed_analysis);

  const evidence: SupportingEvidence =
    typeof analysis.supporting_evidence === "string"
      ? JSON.parse(analysis.supporting_evidence)
      : analysis.supporting_evidence;

  const chartData = {
    labels: Object.keys(reasons).map((key) =>
      key
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    ),
    datasets: [
      {
        data: Object.values(reasons).map((value) =>
          parseInt(value.replace("%", ""))
        ),
        backgroundColor: CHART_COLORS,
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    plugins: {
      legend: {
        position: "right" as const,
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold mb-2">
            Week of {formatDate(analysis.week_start)} -{" "}
            {formatDate(analysis.week_end)}
          </h2>
          <p className="text-gray-600">
            Source: {analysis.source} | Posts Analyzed:{" "}
            {analysis.total_posts_analyzed}
          </p>
        </div>

        <div className="grid md:grid-cols-12 gap-6">
          <div className="md:col-span-4 h-[300px]">
            <Doughnut data={chartData} options={chartOptions} />
          </div>

          <div className="md:col-span-8">
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">Analysis Summary</h3>
                <p className="text-gray-700">{detailedAnalysis}</p>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">
                  Supporting Evidence
                </h3>
                <div className="space-y-4">
                  {Object.entries(evidence).map(([reason, quotes]) => (
                    <div key={reason}>
                      <h4 className="font-semibold text-gray-900">
                        {reason
                          .split("_")
                          .map(
                            (word) =>
                              word.charAt(0).toUpperCase() + word.slice(1)
                          )
                          .join(" ")}
                        :
                      </h4>
                      <ul className="list-disc pl-5 space-y-2">
                        {quotes.map((quote, index) => (
                          <li key={index} className="text-gray-700 text-sm">
                            {quote}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisCard;
