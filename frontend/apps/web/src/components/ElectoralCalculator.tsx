import { useMemo, useState } from "react";
import USAMap from "react-usa-map";
import { ELECTION_PRESETS } from "../data/presets";
import { STATE_DATA } from "../data/stateData";
import { IssueAnalysisPanel } from "./IssueAnalysisPanel";

interface StateProjection {
  democratic: number;
  republican: number;
  winProbability: number; // Probability of Democratic win (0-1)
  margin: number;
}

interface ElectionPreset {
  demographicSupport: Record<string, number>;
  issueStances: Record<string, { position: number; importance: number }>;
  nationalPopularVote?: {
    democratic: number;
    republican: number;
  };
}

export function ElectoralCalculator() {
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [demographicSupport, setDemographicSupport] = useState(
    ELECTION_PRESETS["2020"].demographicSupport
  );
  const [issueStances, setIssueStances] = useState(
    ELECTION_PRESETS["2020"].issueStances
  );
  const [currentPreset, setCurrentPreset] = useState<"2020" | "2016">("2020");

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const year = e.target.value as "2020" | "2016";
    setCurrentPreset(year);
    const preset = ELECTION_PRESETS[year];
    setDemographicSupport(preset.demographicSupport);
    setIssueStances({ ...preset.issueStances });
  };

  const calculateStateProjection = (stateAbbr: string): StateProjection => {
    const state = STATE_DATA[stateAbbr];
    if (!state)
      return { democratic: 0, republican: 0, winProbability: 0, margin: 0 };

    const totalVoters = Object.values(state.demographics).reduce(
      (sum, data) => sum + data.voters,
      0
    );

    const baselineResult = state.historicalResults[currentPreset];
    let democraticShare = baselineResult.democraticShare;

    Object.entries(state.demographics).forEach(([demographic, data]) => {
      const currentSupport =
        demographicSupport[demographic as keyof typeof demographicSupport] ??
        50;
      const baselineSupport =
        ELECTION_PRESETS[currentPreset].demographicSupport[
          demographic as keyof typeof demographicSupport
        ] ?? 50;

      const shift = currentSupport - baselineSupport;
      const weightedShift = shift * (data.voters / totalVoters);
      democraticShare += weightedShift * 0.5;
    });

    Object.entries(issueStances).forEach(([issue, stance]) => {
      const correlation = state.issueCorrelations[issue] ?? 0;
      const baselineStance =
        ELECTION_PRESETS[currentPreset].issueStances[issue]?.position ?? 50;

      const positionShift = stance.position - baselineStance;
      const adjustment =
        positionShift * (stance.importance / 100) * correlation * 0.1;
      democraticShare += adjustment;
    });

    democraticShare = Math.max(35, Math.min(65, democraticShare));
    const republicanShare = 100 - democraticShare;
    const margin = democraticShare - republicanShare;

    return {
      democratic: democraticShare,
      republican: republicanShare,
      winProbability: 1 - normalCDF(0, margin, 2),
      margin: Math.abs(margin),
    };
  };

  const normalCDF = (x: number, mean: number, sigma: number) => {
    const z = (x - mean) / (Math.SQRT2 * sigma);
    return 0.5 * (1 + erf(z));
  };

  const erf = (x: number) => {
    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;
    const t = 1 / (1 + p * x);
    const y =
      1 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
    return sign * y;
  };

  const getMapColors = () => {
    const colors: Record<string, { fill: string }> = {};

    Object.keys(STATE_DATA).forEach((stateAbbr) => {
      const projection = calculateStateProjection(stateAbbr);
      const { winProbability, margin } = projection;

      const intensity = Math.min(255, Math.round((margin * 255) / 20));
      const alpha = 0.2 + (intensity / 255) * 0.8;

      let color: string;
      if (winProbability > 0.9) {
        color = `rgba(0, 0, 255, ${alpha})`; // Solid Dem
      } else if (winProbability > 0.75) {
        color = `rgba(0, 0, 200, ${alpha})`; // Likely Dem
      } else if (winProbability > 0.6) {
        color = `rgba(100, 100, 255, ${alpha})`; // Lean Dem
      } else if (winProbability > 0.4) {
        color = `rgba(128, 0, 128, ${alpha})`; // Tossup
      } else if (winProbability > 0.25) {
        color = `rgba(255, 100, 100, ${alpha})`; // Lean Rep
      } else if (winProbability > 0.1) {
        color = `rgba(200, 0, 0, ${alpha})`; // Likely Rep
      } else {
        color = `rgba(255, 0, 0, ${alpha})`; // Solid Rep
      }

      colors[stateAbbr] = { fill: color };
    });

    return colors;
  };

  const electoralTotals = useMemo(() => {
    let democratic = 0;
    let republican = 0;
    let swing = 0;

    Object.entries(STATE_DATA).forEach(([stateAbbr, state]) => {
      const projection = calculateStateProjection(stateAbbr);
      const margin = Math.abs(projection.democratic - projection.republican);

      if (margin < 5) {
        swing += state.electoralVotes;
      } else if (projection.democratic > projection.republican) {
        democratic += state.electoralVotes;
      } else {
        republican += state.electoralVotes;
      }
    });

    return { democratic, republican, swing };
  }, [demographicSupport, issueStances]);

  return (
    <div className="p-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <div className="mb-4 flex justify-between items-center">
            <div className="flex gap-4 items-center">
              <div className="text-xl font-bold">Electoral Projection</div>
              <select
                className="border rounded p-1"
                onChange={handlePresetChange}
                value={currentPreset}
              >
                <option value="2020">2020 Election</option>
                <option value="2016">2016 Election</option>
              </select>
            </div>
            <div className="flex gap-4">
              <div className="text-blue-600">
                Dem: {electoralTotals.democratic}
              </div>
              <div className="text-purple-600">
                Swing: {electoralTotals.swing}
              </div>
              <div className="text-red-600">
                Rep: {electoralTotals.republican}
              </div>
            </div>
          </div>

          {selectedState && STATE_DATA[selectedState] && (
            <div className="mb-4 bg-white rounded shadow p-4">
              <h3 className="font-bold mb-2">
                {STATE_DATA[selectedState].name}
              </h3>
              <div className="flex gap-4">
                <div>
                  Electoral Votes: {STATE_DATA[selectedState].electoralVotes}
                </div>
                <div>
                  Current Projection:{" "}
                  {(() => {
                    const proj = calculateStateProjection(selectedState);
                    return (
                      <span className="font-bold">
                        D: {proj.democratic.toFixed(1)}% | R:{" "}
                        {proj.republican.toFixed(1)}%
                      </span>
                    );
                  })()}
                </div>
                <div className="text-sm">
                  {currentPreset} Result: D:{" "}
                  {
                    STATE_DATA[selectedState].historicalResults[currentPreset]
                      .democraticShare
                  }
                  % | R:{" "}
                  {
                    STATE_DATA[selectedState].historicalResults[currentPreset]
                      .republicanShare
                  }
                  %
                </div>
              </div>
            </div>
          )}

          <USAMap
            customize={getMapColors()}
            onClick={(event: any) =>
              setSelectedState(event.target.dataset.name)
            }
          />
          <div className="mt-2 text-sm text-gray-600 flex justify-center gap-4">
            <div>■ Strong Dem</div>
            <div>■ Lean Dem</div>
            <div>■ Swing State</div>
            <div>■ Lean Rep</div>
            <div>■ Strong Rep</div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded shadow p-4">
            <h3 className="font-bold mb-4">Demographic Support Levels</h3>
            {Object.entries(demographicSupport).map(([demographic, value]) => (
              <div key={demographic} className="mb-4">
                <label className="block mb-2 capitalize">
                  {demographic.replace(/([A-Z])/g, " $1").trim()}: {value}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value}
                  onChange={(e) =>
                    setDemographicSupport((prev) => ({
                      ...prev,
                      [demographic]: parseInt(e.target.value),
                    }))
                  }
                  className="w-full"
                />
              </div>
            ))}
          </div>

          <IssueAnalysisPanel
            issues={issueStances}
            onIssueChange={setIssueStances}
          />
        </div>
      </div>
    </div>
  );
}
