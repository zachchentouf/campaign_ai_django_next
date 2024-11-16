interface IssueStance {
  position: number;
  importance: number;
}

interface IssueAnalysisPanelProps {
  issues: Record<string, IssueStance>;
  onIssueChange: (issues: Record<string, IssueStance>) => void;
}

export function IssueAnalysisPanel({
  issues,
  onIssueChange,
}: IssueAnalysisPanelProps) {
  const handlePositionChange = (issue: string, position: number) => {
    onIssueChange({
      ...issues,
      [issue]: { ...issues[issue], position },
    });
  };

  const handleImportanceChange = (issue: string, importance: number) => {
    onIssueChange({
      ...issues,
      [issue]: { ...issues[issue], importance },
    });
  };

  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="font-bold mb-4">Issue Positions</h3>
      {Object.entries(issues).map(([issue, stance]) => (
        <div key={issue} className="mb-6">
          <div className="mb-4">
            <label className="block mb-2 capitalize">
              {issue.replace(/([A-Z])/g, " $1").trim()}
            </label>
            <div className="text-sm text-gray-600 flex justify-between mb-1">
              <span>Conservative ({100 - stance.position}%)</span>
              <span>({stance.position}%) Liberal</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={stance.position}
              onChange={(e) =>
                handlePositionChange(issue, parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          <div>
            <label className="block mb-2 text-sm">
              Issue Importance: {stance.importance}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={stance.importance}
              onChange={(e) =>
                handleImportanceChange(issue, parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
