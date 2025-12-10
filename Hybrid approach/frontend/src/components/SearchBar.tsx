import React, { useState } from "react";
import { Search } from "lucide-react";
import { SearchFilters } from "@/lib/types";

interface SearchBarProps {
    onSearch: (query: string, filters: SearchFilters) => void;
    isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
    const [query, setQuery] = useState("");
    const [location, setLocation] = useState("");
    const [minExp, setMinExp] = useState("");
    const [skills, setSkills] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const filters: SearchFilters = {
            location: location || undefined,
            min_years_experience: minExp ? parseInt(minExp) : undefined,
            required_skills: skills ? skills.split(",").map((s) => s.trim()) : undefined,
        };
        onSearch(query, filters);
    };

    return (
        <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search candidates (e.g. 'Senior Python Developer')"
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                    />
                </div>
                <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300 font-medium"
                >
                    {isLoading ? "Searching..." : "Search"}
                </button>
            </div>

            <div className="mt-4 flex gap-4 text-sm">
                <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="Location (e.g. New York)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 outline-none"
                />
                <input
                    type="number"
                    value={minExp}
                    onChange={(e) => setMinExp(e.target.value)}
                    placeholder="Min Years Exp"
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 outline-none"
                />
                <input
                    type="text"
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    placeholder="Skills (comma separated)"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 outline-none"
                />
            </div>
        </form>
    );
};
