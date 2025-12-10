"""
Configuration management for ATS Pipeline
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Central configuration for the ATS pipeline"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    LLM_MODEL: str = "gpt-4o"
    
    # Neo4j Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "987654321")
    
    # Search Configuration
    VECTOR_TOP_K: int = 50  # Number of candidates from vector search
    FINAL_TOP_K: int = 10   # Number of final results to return
    
    # Ranking Weights
    VECTOR_SCORE_WEIGHT: float = 0.4
    SKILL_MATCH_WEIGHT: float = 0.3
    EXPERIENCE_WEIGHT: float = 0.2
    EDUCATION_WEIGHT: float = 0.1
    
    # Performance
    BATCH_SIZE: int = 10
    ENABLE_CACHE: bool = True
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not cls.NEO4J_URI:
            raise ValueError("NEO4J_URI is required")
        return True

# Validate on import
Config.validate()
