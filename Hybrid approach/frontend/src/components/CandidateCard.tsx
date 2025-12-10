import React from "react";
import { CandidateMatch } from "@/lib/types";
import { ThumbsUp, ThumbsDown, MessageSquare } from "lucide-react";

interface CandidateCardProps {
    candidate: CandidateMatch;
    onFeedback: (action: "like" | "dislike") => void;
    onChat: () => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
    candidate,
    onFeedback,
    onChat,
}) => {
    return (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-xl font-bold text-gray-900">{candidate.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                        {candidate.total_experience} years experience
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                        Score: {(candidate.final_score || 0).toFixed(2)}
                    </span>
                </div>
            </div>

            <p className="mt-3 text-gray-600 text-sm line-clamp-3">
                {candidate.summary}
            </p>

            {candidate.match_reason && (
                <div className="mt-3 bg-green-50 p-3 rounded-md border border-green-100">
                    <p className="text-xs text-green-800 font-medium">AI Analysis:</p>
                    <p className="text-xs text-green-700 mt-1">{candidate.match_reason}</p>
                </div>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
                {candidate.matched_skills.slice(0, 5).map((skill) => (
                    <span
                        key={skill}
                        className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                    >
                        {skill}
                    </span>
                ))}
            </div>

            <div className="mt-6 flex justify-between items-center border-t pt-4">
                <button
                    onClick={onChat}
                    className="flex items-center text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Chat with Profile
                </button>

                <div className="flex space-x-3">
                    <button
                        onClick={() => onFeedback("like")}
                        className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-full transition-colors"
                    >
                        <ThumbsUp className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => onFeedback("dislike")}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                    >
                        <ThumbsDown className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
};
