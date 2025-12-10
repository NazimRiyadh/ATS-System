"use client";

import React, { useState } from "react";
import { SearchBar } from "@/components/SearchBar";
import { CandidateCard } from "@/components/CandidateCard";
import { ChatBox } from "@/components/ChatBox";
import { searchCandidates, submitFeedback } from "@/lib/api";
import { CandidateMatch, SearchFilters } from "@/lib/types";
import { LayoutDashboard, Users } from "lucide-react";

export default function Home() {
  const [candidates, setCandidates] = useState<CandidateMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");
  const [activeChatCandidate, setActiveChatCandidate] = useState<{
    id: string;
    name: string;
  } | null>(null);

  const handleSearch = async (query: string, filters: SearchFilters) => {
    setIsLoading(true);
    setCurrentQuery(query);
    try {
      const results = await searchCandidates(query, filters);
      setCandidates(results);
    } catch (error) {
      console.error("Search failed:", error);
      alert("Search failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (
    candidateId: string,
    action: "like" | "dislike"
  ) => {
    try {
      await submitFeedback(candidateId, currentQuery, action);
      // Optional: Show toast or visual feedback
      console.log(`Feedback ${action} recorded for ${candidateId}`);
    } catch (error) {
      console.error("Feedback failed:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <LayoutDashboard className="w-6 h-6 text-blue-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">ATS Hybrid</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-gray-500 text-sm">
                <Users className="w-4 h-4 mr-1" />
                <span>Recruiter View</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Find the perfect candidate
          </h1>
          <p className="text-gray-600">
            Search using natural language or specific filters.
          </p>
        </div>

        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Results */}
        <div className="space-y-6">
          {candidates.length > 0 ? (
            <div className="grid grid-cols-1 gap-6">
              {candidates.map((candidate) => (
                <CandidateCard
                  key={candidate.candidate_id}
                  candidate={candidate}
                  onFeedback={(action) =>
                    handleFeedback(candidate.candidate_id, action)
                  }
                  onChat={() =>
                    setActiveChatCandidate({
                      id: candidate.candidate_id,
                      name: candidate.name,
                    })
                  }
                />
              ))}
            </div>
          ) : (
            !isLoading && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-2">No candidates found</div>
                <p className="text-sm text-gray-500">
                  Try adjusting your search query or filters
                </p>
              </div>
            )
          )}
        </div>
      </main>

      {/* Chat Overlay */}
      {activeChatCandidate && (
        <ChatBox
          candidateId={activeChatCandidate.id}
          candidateName={activeChatCandidate.name}
          onClose={() => setActiveChatCandidate(null)}
        />
      )}
    </div>
  );
}
