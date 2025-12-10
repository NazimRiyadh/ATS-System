"""
Resume and Job Description Parser using LLM
"""
from typing import Optional
from openai import OpenAI
from .config import Config
from .models import CandidateProfile, JobRequirement
import logging

logger = logging.getLogger(__name__)

class Parser:
    """Parse resumes and job descriptions using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL
    
    def parse_resume(self, resume_text: str) -> CandidateProfile:
        """
        Parse resume text into structured candidate profile
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            CandidateProfile object
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert resume parser. Extract structured information from resumes.
                        
                        Important guidelines:
                        - Calculate years_duration accurately for each job
                        - Normalize skill names (e.g., "JS" -> "JavaScript")
                        - Extract proficiency levels from context
                        - Identify technologies used in each role
                        - Calculate total years of experience
                        """
                    },
                    {
                        "role": "user",
                        "content": resume_text
                    }
                ],
                response_format=CandidateProfile
            )
            
            profile = completion.choices[0].message.parsed
            logger.info(f"✅ Parsed resume for: {profile.name}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Resume parsing failed: {e}")
            raise
    
    def parse_job_description(self, jd_text: str) -> JobRequirement:
        """
        Parse job description into structured requirements
        
        Args:
            jd_text: Raw job description text
            
        Returns:
            JobRequirement object
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing job descriptions. Extract structured requirements.
                        
                        Important guidelines:
                        - Separate required vs preferred skills
                        - Extract minimum years of experience
                        - Identify education requirements
                        - Normalize skill names
                        """
                    },
                    {
                        "role": "user",
                        "content": jd_text
                    }
                ],
                response_format=JobRequirement
            )
            
            requirements = completion.choices[0].message.parsed
            logger.info(f"✅ Parsed job: {requirements.title}")
            return requirements
            
        except Exception as e:
            logger.error(f"❌ Job description parsing failed: {e}")
            raise

# Global instance
_parser: Optional[Parser] = None

def get_parser() -> Parser:
    """Get or create the global parser instance"""
    global _parser
    if _parser is None:
        _parser = Parser()
    return _parser
