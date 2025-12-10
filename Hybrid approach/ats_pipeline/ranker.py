"""
Candidate Ranking and Scoring System
"""
from typing import List
from openai import OpenAI
import json
from .config import Config
from .models import CandidateMatch, JobRequirement
import logging

logger = logging.getLogger(__name__)

class CandidateRanker:
    """Ranks and scores candidates with LLM-based explanations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def calculate_final_scores(
        self,
        matches: List[CandidateMatch],
        job_requirement: JobRequirement
    ) -> List[CandidateMatch]:
        """
        Calculate final scores for all candidates
        
        Args:
            matches: List of candidate matches
            job_requirement: Job requirements
            
        Returns:
            Ranked list of candidates with final scores
        """
        for match in matches:
            # Calculate individual component scores
            match.experience_score = self._calculate_experience_score(
                match.total_experience,
                job_requirement.min_years_experience
            )
            
            match.education_score = 0.5  # Placeholder - would need education data
            
            # Calculate weighted final score
            match.final_score = (
                Config.VECTOR_SCORE_WEIGHT * match.vector_score +
                Config.SKILL_MATCH_WEIGHT * match.skill_match_score +
                Config.EXPERIENCE_WEIGHT * match.experience_score +
                Config.EDUCATION_WEIGHT * match.education_score
            )
        
        # Sort by final score
        matches.sort(key=lambda x: x.final_score, reverse=True)
        
        logger.info(f"✅ Calculated scores for {len(matches)} candidates")
        return matches
    
    def add_llm_explanations(
        self,
        matches: List[CandidateMatch],
        job_description: str,
        top_n: int = 5
    ) -> List[CandidateMatch]:
        """
        Add LLM-generated explanations for top candidates
        
        Args:
            matches: Ranked candidates
            job_description: Job description text
            top_n: Number of candidates to explain
            
        Returns:
            Candidates with explanations
        """
        if not matches:
            return matches
        
        # Only explain top N candidates
        candidates_to_explain = matches[:top_n]
        
        # Prepare candidate data for LLM
        candidates_data = []
        for i, match in enumerate(candidates_to_explain, 1):
            candidates_data.append({
                "rank": i,
                "name": match.name,
                "summary": match.summary,
                "experience_years": match.total_experience,
                "skills": match.matched_skills,
                "scores": {
                    "vector_similarity": round(match.vector_score, 3),
                    "skill_match": round(match.skill_match_score, 3),
                    "final_score": round(match.final_score, 3)
                }
            })
        
        prompt = f"""You are an expert recruiter. Analyze these candidates for the following job:

JOB DESCRIPTION:
{job_description}

CANDIDATES (Pre-ranked by AI):
{json.dumps(candidates_data, indent=2)}

For each candidate, provide a concise 1-2 sentence explanation of:
1. Why they are a good match
2. Their key strengths for this role

Format your response as a JSON array with objects containing "name" and "explanation" fields.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert recruiter providing candidate match explanations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            explanations = json.loads(response.choices[0].message.content)
            
            # Add explanations to matches
            if "candidates" in explanations:
                for i, explanation_data in enumerate(explanations["candidates"]):
                    if i < len(candidates_to_explain):
                        candidates_to_explain[i].match_reason = explanation_data.get("explanation", "")
            
            logger.info(f"✅ Added LLM explanations for top {len(candidates_to_explain)} candidates")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate LLM explanations: {e}")
        
        return matches
    
    def _calculate_experience_score(
        self,
        candidate_years: float,
        required_years: int
    ) -> float:
        """
        Calculate experience score
        
        Returns score between 0 and 1:
        - 1.0 if candidate has exactly required years or more
        - Proportional if less than required
        """
        if required_years == 0:
            return 1.0
        
        if candidate_years >= required_years:
            # Bonus for extra experience, but capped
            bonus = min((candidate_years - required_years) / required_years * 0.2, 0.2)
            return min(1.0 + bonus, 1.0)
        else:
            # Proportional score if less than required
            return candidate_years / required_years

# Global instance
_ranker: Optional[CandidateRanker] = None

def get_ranker() -> CandidateRanker:
    """Get or create the global ranker instance"""
    global _ranker
    if _ranker is None:
        _ranker = CandidateRanker()
    return _ranker
