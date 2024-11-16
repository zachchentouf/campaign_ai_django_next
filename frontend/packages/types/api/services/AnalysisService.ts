/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedWeeklyAnalysisList } from '../models/PaginatedWeeklyAnalysisList';
import type { WeeklyAnalysis } from '../models/WeeklyAnalysis';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AnalysisService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * @param page A page number within the paginated result set.
     * @returns PaginatedWeeklyAnalysisList
     * @throws ApiError
     */
    public analysisList(
        page?: number,
    ): CancelablePromise<PaginatedWeeklyAnalysisList> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/analysis/',
            query: {
                'page': page,
            },
        });
    }

    /**
     * @param id A unique integer value identifying this weekly analysis.
     * @returns WeeklyAnalysis
     * @throws ApiError
     */
    public analysisRetrieve(
        id: number,
    ): CancelablePromise<WeeklyAnalysis> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/analysis/{id}/',
            path: {
                'id': id,
            },
        });
    }

    /**
     * Get trending reasons over time
     * @returns WeeklyAnalysis
     * @throws ApiError
     */
    public analysisTrendsRetrieve(): CancelablePromise<WeeklyAnalysis> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/analysis/trends/',
        });
    }

    /**
     * Manual trigger for analysis
     * @param requestBody
     * @returns WeeklyAnalysis
     * @throws ApiError
     */
    public analysisTriggerAnalysisCreate(
        requestBody: WeeklyAnalysis,
    ): CancelablePromise<WeeklyAnalysis> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/analysis/trigger_analysis/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

    /**
     * Manual trigger for scraping undecided voter posts
     * @param requestBody
     * @returns WeeklyAnalysis
     * @throws ApiError
     */
    public analysisTriggerScrapingCreate(
        requestBody: WeeklyAnalysis,
    ): CancelablePromise<WeeklyAnalysis> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/analysis/trigger_scraping/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }

}
