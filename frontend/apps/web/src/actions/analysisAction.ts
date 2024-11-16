"use server";

import { getApiClient } from "@/lib/api";
import { authOptions } from "@/lib/auth";
import {
  ApiError,
  type PaginatedWeeklyAnalysisList,
} from "@frontend/types/api";
import { getServerSession } from "next-auth";

export type AnalysisAction = () => Promise<PaginatedWeeklyAnalysisList | null>;

const analysisAction: AnalysisAction = async () => {
  const session = await getServerSession(authOptions);

  try {
    const apiClient = await getApiClient(session);
    const analyses = await apiClient.analysis.analysisList();
    return analyses;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error("API Error:", error);
    }
    return null;
  }
};

export { analysisAction };
