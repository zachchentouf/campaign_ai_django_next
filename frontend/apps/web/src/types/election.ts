export interface DemographicData {
  voters: number;
  currentSupport: number;
  volatility: number; // Historical variance in support
}

export interface StateData {
  name: string;
  abbreviation: string;
  electoralVotes: number;
  demographics: {
    [key: string]: DemographicData;
  };
  historicalResults: {
    [year: string]: {
      democraticShare: number;
      republicanShare: number;
      turnout: number;
    };
  };
  issueCorrelations: {
    [issue: string]: number; // correlation coefficient (-1 to 1)
  };
}

export interface IssueStance {
  importance: number; // 0-100
  position: number; // 0-100, where 0 is conservative, 100 is progressive
}
