import { analysisAction } from "@/actions/analysisAction";
import AnalysisCard from "@/components/analyses/AnalysisCard";

const AnalysesPage = async () => {
  const analyses = await analysisAction();

  if (!analyses) {
    return (
      <div className="container mx-auto px-4">
        <h1 className="text-2xl text-red-600 text-center py-8">
          Failed to load analyses
        </h1>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">
        Weekly Voter Sentiment Analyses
      </h1>

      <div className="space-y-6">
        {analyses.results.map((analysis) => (
          <AnalysisCard key={analysis.id} analysis={analysis} />
        ))}
      </div>
    </div>
  );
};

export default AnalysesPage;
