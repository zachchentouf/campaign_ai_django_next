/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SourceEnum } from './SourceEnum';

export type WeeklyAnalysis = {
    readonly id: number;
    source: SourceEnum;
    week_start: string;
    week_end: string;
    total_posts_analyzed: number;
    reasons: any;
    detailed_analysis: any;
    supporting_evidence: any;
    readonly created_at: string;
    readonly updated_at: string;
};

