"""
Neo4j Graph Database Manager with Vector Index Support
"""
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import uuid
from .config import Config
from .models import CandidateProfile, SearchFilters, CandidateMatch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphDatabaseManager:
    """Manages Neo4j graph database operations with vector support"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        self.ensure_schema()
    
    def close(self):
        """Close database connection"""
        self.driver.close()
    
    def ensure_schema(self):
        """Create indexes and constraints"""
        queries = [
            # Unique constraints
            "CREATE CONSTRAINT candidate_id_unique IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (comp:Company) REQUIRE comp.name IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX candidate_name_idx IF NOT EXISTS FOR (c:Candidate) ON (c.name)",
            "CREATE INDEX skill_name_idx IF NOT EXISTS FOR (s:Skill) ON (s.name)",
        ]
        
        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    logger.warning(f"Schema query warning: {e}")
        
        logger.info("✅ Database schema verified")
    
    def create_vector_index(self):
        """
        Create vector index for candidate embeddings
        Note: This uses Neo4j 5.x+ syntax
        """
        query = """
        CREATE VECTOR INDEX candidate_embedding_idx IF NOT EXISTS
        FOR (c:Candidate) ON (c.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: $dimensions,
            `vector.similarity_function`: 'cosine'
          }
        }
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, dimensions=Config.EMBEDDING_DIMENSIONS)
                
                # Verify index exists
                result = session.run("SHOW INDEXES")
                for record in result:
                    if record['name'] == 'candidate_embedding_idx':
                        logger.info("✅ Vector index created/verified")
                        return True
                        
            logger.warning("⚠️ Vector index creation command succeeded but index not found. Vector search will be disabled.")
            return False
        except Exception as e:
            logger.error(f"❌ Vector index creation failed: {e}")
            logger.info("Continuing without vector index - will use graph-only search")
            return False
    
    def add_candidate(self, profile: CandidateProfile, embedding: List[float]) -> str:
        """
        Add candidate to graph database with embedding
        
        Args:
            profile: Candidate profile
            embedding: Vector embedding
            
        Returns:
            Candidate ID
        """
        candidate_id = str(uuid.uuid4())
        
        # 1. Create Candidate Node
        query_candidate = """
        CREATE (c:Candidate {
            id: $id,
            name: $name,
            email: $email,
            phone: $phone,
            location: $location,
            summary: $summary,
            total_experience: $total_experience,
            embedding: $embedding,
            created_at: datetime()
        })
        """
        
        # 2. Add Skills
        query_skills = """
        MATCH (c:Candidate {id: $id})
        UNWIND $skills AS skill
        MERGE (s:Skill {name: toLower(skill.name)})
        ON CREATE SET s.normalized_name = toLower(skill.name)
        MERGE (c)-[r:HAS_SKILL]->(s)
        SET r.proficiency = skill.proficiency,
            r.years_experience = skill.years_experience
        """
        
        # 3. Add Experience
        query_experience = """
        MATCH (c:Candidate {id: $id})
        UNWIND $experiences AS exp
        MERGE (comp:Company {name: exp.company})
        CREATE (c)-[r:WORKED_AT]->(comp)
        SET r.role = exp.role,
            r.years = exp.years_duration,
            r.start_date = exp.start_date,
            r.end_date = exp.end_date,
            r.description = exp.description,
            r.technologies = exp.technologies
        """
        
        # 4. Add Education
        query_education = """
        MATCH (c:Candidate {id: $id})
        UNWIND $education AS edu
        MERGE (inst:Institution {name: edu.institution})
        CREATE (c)-[r:STUDIED_AT]->(inst)
        SET r.degree = edu.degree,
            r.field = edu.field,
            r.graduation_year = edu.graduation_year,
            r.gpa = edu.gpa
        """
        
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                # Create candidate
                tx.run(
                    query_candidate,
                    id=candidate_id,
                    name=profile.name,
                    email=profile.email,
                    phone=profile.phone,
                    location=profile.location,
                    summary=profile.summary,
                    total_experience=profile.calculate_total_experience(),
                    embedding=embedding
                )
                
                # Add skills if present
                if profile.skills:
                    tx.run(
                        query_skills,
                        id=candidate_id,
                        skills=[{
                            'name': s.name,
                            'proficiency': s.proficiency,
                            'years_experience': s.years_experience
                        } for s in profile.skills]
                    )
                
                # Add experience if present
                if profile.experience:
                    tx.run(
                        query_experience,
                        id=candidate_id,
                        experiences=[{
                            'company': e.company,
                            'role': e.role,
                            'years_duration': e.years_duration,
                            'start_date': e.start_date,
                            'end_date': e.end_date,
                            'description': e.description,
                            'technologies': e.technologies
                        } for e in profile.experience]
                    )
                
                # Add education if present
                if profile.education:
                    tx.run(
                        query_education,
                        id=candidate_id,
                        education=[{
                            'degree': e.degree,
                            'field': e.field,
                            'institution': e.institution,
                            'graduation_year': e.graduation_year,
                            'gpa': e.gpa
                        } for e in profile.education]
                    )
                
                tx.commit()
            
        logger.info(f"✅ Added candidate: {profile.name} (ID: {candidate_id})")
        return candidate_id
    
    def vector_search(self, query_embedding: List[float], top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            
        Returns:
            List of candidate matches with scores
        """
        query = """
        CALL db.index.vector.queryNodes('candidate_embedding_idx', $top_k, $embedding)
        YIELD node AS candidate, score
        
        RETURN candidate.id as id,
               candidate.name as name,
               candidate.summary as summary,
               candidate.total_experience as total_experience,
               candidate.location as location,
               score as vector_score
        ORDER BY score DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, embedding=query_embedding, top_k=top_k)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def graph_search(self, filters: SearchFilters, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Perform graph-based search with filters
        
        Args:
            filters: Search filters
            limit: Maximum results
            
        Returns:
            List of matching candidates
        """
        # Build dynamic query based on filters
        where_clauses = []
        params = {'limit': limit}
        
        # Base query
        query_parts = ["MATCH (c:Candidate)"]
        
        # Required skills filter
        if filters.required_skills:
            query_parts.append("""
            MATCH (c)-[:HAS_SKILL]->(s:Skill)
            WHERE toLower(s.name) IN $required_skills
            WITH c, count(DISTINCT s) as skill_matches
            """)
            where_clauses.append("skill_matches >= $min_skill_matches")
            params['required_skills'] = [s.lower() for s in filters.required_skills]
            # Relaxed matching: Require only 50% of skills to match
            params['min_skill_matches'] = max(1, int(len(filters.required_skills) * 0.5))
        
        # Experience filter
        if filters.min_years_experience > 0:
            where_clauses.append("c.total_experience >= $min_years")
            params['min_years'] = filters.min_years_experience
        
        if filters.max_years_experience:
            where_clauses.append("c.total_experience <= $max_years")
            params['max_years'] = filters.max_years_experience
        
        # Location filter
        if filters.location:
            where_clauses.append("toLower(c.location) CONTAINS toLower($location)")
            params['location'] = filters.location
        
        # Add WHERE clause if needed
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Return statement
        query_parts.append("""
        RETURN c.id as id,
               c.name as name,
               c.summary as summary,
               c.total_experience as total_experience,
               c.location as location
        LIMIT $limit
        """)
        
        query = "\n".join(query_parts)
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    def get_candidate_skills(self, candidate_id: str) -> List[str]:
        """Get all skills for a candidate"""
        query = """
        MATCH (c:Candidate {id: $candidate_id})-[:HAS_SKILL]->(s:Skill)
        RETURN s.name as skill
        """
        
        with self.driver.session() as session:
            result = session.run(query, candidate_id=candidate_id)
            return [record['skill'] for record in result]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        queries = {
            'total_candidates': "MATCH (c:Candidate) RETURN count(c) as count",
            'total_skills': "MATCH (s:Skill) RETURN count(s) as count",
            'total_companies': "MATCH (comp:Company) RETURN count(comp) as count",
        }
        
        stats = {}
        with self.driver.session() as session:
            for key, query in queries.items():
                result = session.run(query)
                stats[key] = result.single()['count']
        
        return stats

# Global instance
_graph_db: Optional[GraphDatabaseManager] = None

def get_graph_db() -> GraphDatabaseManager:
    """Get or create the global graph database instance"""
    global _graph_db
    if _graph_db is None:
        _graph_db = GraphDatabaseManager()
    return _graph_db
