import { analysisAction } from "@/actions/analysisAction";
import AnalysisCard from "@/components/analyses/AnalysisCard";
import { auth } from "@/lib/auth";

const AnalysesPage = async () => {
  const session = await auth();

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-2">Weekly Voter Sentiment Analyses</h1>
        <p className="text-gray-500">Please <a href="/login" className="text-blue-600 underline">log in</a> to view analyses.</p>
      </div>
    );
  }

  const analyses = await analysisAction();

  if (!analyses) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-2">Weekly Voter Sentiment Analyses</h1>
        <p className="text-red-500">Failed to load analyses. The API may be unavailable.</p>
      </div>
    );
  }

  if (analyses.results.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-3xl font-bold mb-4">Weekly Voter Sentiment Analyses</h1>
        <p className="text-gray-500">No analyses yet. Run a scraping job first.</p>
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
