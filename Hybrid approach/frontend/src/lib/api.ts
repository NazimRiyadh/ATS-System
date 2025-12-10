import { CandidateMatch, SearchFilters } from "./types";

const API_BASE_URL = "http://localhost:8001/api/v1";

export async function searchCandidates(
    query: string,
    filters?: SearchFilters
): Promise<CandidateMatch[]> {
    const response = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, filters }),
    });
    if (!response.ok) throw new Error("Search failed");
    return response.json();
}

export async function submitFeedback(
    candidateId: string,
    query: string,
    action: "click" | "like" | "dislike"
) {
    await fetch(`${API_BASE_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: candidateId, query, action }),
    });
}

export async function chatWithCandidate(
    candidateId: string,
    message: string
): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: candidateId, message }),
    });
    if (!response.ok) throw new Error("Chat failed");
    const data = await response.json();
    return data.response;
}
