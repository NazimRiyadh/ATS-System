export interface CandidateMatch {
    candidate_id: string;
    name: string;
    summary: string;
    total_experience: number;
    matched_skills: string[];
    vector_score?: number;
    skill_match_score?: number;
    final_score?: number;
    match_reason?: string;
}

export interface SearchFilters {
    required_skills?: string[];
    min_years_experience?: number;
    location?: string;
}
