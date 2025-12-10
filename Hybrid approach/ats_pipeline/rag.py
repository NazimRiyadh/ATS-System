"""
RAG Chatbot for Candidate Interaction
"""
from typing import Optional
from openai import OpenAI
from .config import Config
from .graph_db import get_graph_db
import logging

logger = logging.getLogger(__name__)

class RAGChatbot:
    """Chat with a candidate's profile using RAG"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.graph_db = get_graph_db()
        self.model = Config.LLM_MODEL
        
    def chat(self, candidate_id: str, user_message: str) -> str:
        """
        Generate a response based on candidate profile
        
        Args:
            candidate_id: ID of the candidate
            user_message: User's question
            
        Returns:
            AI response
        """
        # 1. Retrieve Candidate Context
        context = self._get_candidate_context(candidate_id)
        if not context:
            return "I couldn't find that candidate's profile."
            
        # 2. Construct Prompt
        system_prompt = f"""You are an AI assistant helping a recruiter. 
        You have access to the following candidate profile:
        
        Name: {context.get('name')}
        Summary: {context.get('summary')}
        Total Experience: {context.get('total_experience')} years
        Skills: {', '.join(context.get('skills', []))}
        
        Answer the user's question based ONLY on this information. 
        If the information is not in the profile, say "I don't see that in their profile."
        Be concise and professional.
        """
        
        # 3. Generate Response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"RAG chat failed: {e}")
            return "I encountered an error while analyzing the profile."
            
    def _get_candidate_context(self, candidate_id: str) -> dict:
        """Fetch candidate details from Graph DB"""
        query = """
        MATCH (c:Candidate {id: $id})
        OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill)
        RETURN c.name as name, 
               c.summary as summary, 
               c.total_experience as total_experience,
               collect(s.name) as skills
        """
        
        try:
            with self.graph_db.driver.session() as session:
                result = session.run(query, id=candidate_id)
                record = result.single()
                if record:
                    return dict(record)
        except Exception as e:
            logger.error(f"Failed to fetch candidate context: {e}")
            
        return {}

# Global instance
_rag_chatbot: Optional[RAGChatbot] = None

def get_rag_chatbot() -> RAGChatbot:
    global _rag_chatbot
    if _rag_chatbot is None:
        _rag_chatbot = RAGChatbot()
    return _rag_chatbot
