"""
Feedback Loop and Learning System
"""
from typing import Optional
from .graph_db import get_graph_db
import logging

logger = logging.getLogger(__name__)

class FeedbackSystem:
    """Handles user feedback and ranking adjustments"""
    
    def __init__(self):
        self.graph_db = get_graph_db()
    
    def record_feedback(self, candidate_id: str, query: str, action: str):
        """
        Record user feedback for a candidate
        
        Args:
            candidate_id: ID of the candidate
            query: Search query used
            action: User action ("click", "like", "dislike")
        """
        # Normalize action
        action = action.lower()
        weight = 0
        if action == "click":
            weight = 1
        elif action == "like":
            weight = 3
        elif action == "dislike":
            weight = -3
            
        query_cypher = """
        MATCH (c:Candidate {id: $candidate_id})
        MERGE (q:SearchQuery {text: toLower($query)})
        MERGE (c)-[r:RELEVANT_TO]->(q)
        ON CREATE SET r.score = $weight, r.count = 1
        ON MATCH SET r.score = r.score + $weight, r.count = r.count + 1
        """
        
        try:
            with self.graph_db.driver.session() as session:
                session.run(query_cypher, candidate_id=candidate_id, query=query, weight=weight)
            logger.info(f"✅ Recorded feedback: {action} for candidate {candidate_id} on query '{query}'")
        except Exception as e:
            logger.error(f"❌ Failed to record feedback: {e}")

    def get_feedback_score(self, candidate_id: str, query: str) -> float:
        """
        Get feedback score boost for a candidate on a query
        """
        query_cypher = """
        MATCH (c:Candidate {id: $candidate_id})-[r:RELEVANT_TO]->(q:SearchQuery)
        WHERE q.text CONTAINS toLower($query) OR toLower($query) CONTAINS q.text
        RETURN sum(r.score) as total_score
        """
        
        try:
            with self.graph_db.driver.session() as session:
                result = session.run(query_cypher, candidate_id=candidate_id, query=query)
                record = result.single()
                if record and record["total_score"]:
                    # Normalize score to a reasonable boost factor (e.g., 0.0 to 0.2)
                    raw_score = record["total_score"]
                    return min(max(raw_score * 0.01, -0.2), 0.2)
        except Exception as e:
            logger.error(f"Failed to get feedback score: {e}")
            
        return 0.0

# Global instance
_feedback_system: Optional[FeedbackSystem] = None

def get_feedback_system() -> FeedbackSystem:
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system
