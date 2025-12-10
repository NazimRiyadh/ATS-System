import os
import json
import uuid
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from neo4j import GraphDatabase
from pydantic import BaseModel

# --- CONFIGURATION ---
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "987654321"

# Initialize Clients
client = OpenAI(api_key=OPENAI_API_KEY)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# --- DATA MODELS ---
class WorkExperience(BaseModel):
    company: str
    role: str
    years_duration: float
    description: str

class Skill(BaseModel):
    name: str
    proficiency: str

class CandidateProfile(BaseModel):
    name: str
    summary: str
    skills: List[Skill]
    experience: List[WorkExperience]
    education_level: str

# --- GRAPH MANAGER (SIMPLIFIED - NO VECTOR SEARCH) ---
class GraphManager:
    def __init__(self, driver):
        self.driver = driver
        self.ensure_constraints()

    def ensure_constraints(self):
        """Creates Constraints for performance."""
        query_constraint = "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE"
        
        with self.driver.session() as session:
            session.run(query_constraint)
            print("✅ Database Constraints Verified.")

    def add_candidate_to_graph(self, profile: CandidateProfile):
        """Add candidate to graph database."""
        candidate_id = str(uuid.uuid4())
        
        cypher_query = """
        MERGE (c:Candidate {name: $name})
        SET c.id = $id, 
            c.summary = $summary, 
            c.education = $education

        WITH c
        UNWIND $skills AS skill
        MERGE (s:Skill {name: toLower(skill.name)})
        MERGE (c)-[:HAS_SKILL {proficiency: skill.proficiency}]->(s)

        WITH c
        UNWIND $experiences AS exp
        MERGE (comp:Company {name: exp.company})
        MERGE (c)-[:WORKED_AT {role: exp.role, years: exp.years_duration}]->(comp)
        """
        
        with self.driver.session() as session:
            session.run(cypher_query, 
                        name=profile.name,
                        id=candidate_id,
                        summary=profile.summary,
                        education=profile.education_level,
                        skills=[s.model_dump() for s in profile.skills],
                        experiences=[e.model_dump() for e in profile.experience]
            )
        print(f"✅ Candidate {profile.name} added to Graph.")

    def search_candidates(self, required_skill: str = None, min_years: int = 0):
        """
        Graph-based search with filtering.
        """
        if required_skill:
            cypher_query = """
            MATCH (candidate:Candidate)-[:HAS_SKILL]->(s:Skill)
            WHERE toLower(s.name) CONTAINS toLower($req_skill)
            
            OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
            WITH candidate, coalesce(sum(r.years), 0) as total_experience
            WHERE total_experience >= $min_years
            
            RETURN candidate.name as name, 
                   candidate.summary as summary, 
                   total_experience
            ORDER BY total_experience DESC
            """
        else:
            cypher_query = """
            MATCH (candidate:Candidate)
            
            OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
            WITH candidate, coalesce(sum(r.years), 0) as total_experience
            WHERE total_experience >= $min_years
            
            RETURN candidate.name as name, 
                   candidate.summary as summary, 
                   total_experience
            ORDER BY total_experience DESC
            """
        
        with self.driver.session() as session:
            result = session.run(cypher_query, 
                                 min_years=min_years, 
                                 req_skill=required_skill)
            return [record.data() for record in result]

# --- HELPER FUNCTIONS ---
def parse_resume_to_json(resume_text: str) -> CandidateProfile:
    """Uses GPT-4o to extract structured graph data from raw text."""
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extract candidate details. Calculate years duration for jobs accurately."},
            {"role": "user", "content": resume_text},
        ],
        response_format=CandidateProfile,
    )
    return completion.choices[0].message.parsed

def llm_rerank(candidates, job_description):
    """Final step: Ask LLM to explain why the filtered candidates match."""
    if not candidates:
        return "No candidates met the filters."
        
    prompt = f"""
    You are a recruiter. Rank these candidates for the following Job Description:
    "{job_description}"
    
    Candidates (Pre-filtered by DB):
    {json.dumps(candidates, indent=2)}
    
    Output: A prioritized list with a 1-sentence reason for each.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- EXECUTION PIPELINE ---
def main():
    # Initialize Manager
    graph_mgr = GraphManager(driver)

    # --- SCENARIO: INGESTION ---
    print("\n--- 1. INGESTING CANDIDATE ---")
    raw_resume = """
    Jane Doe. Python Developer.
    I love building AI systems and backend APIs.
    Experience:
    - TechCorp (2020-2023): Senior Backend Engineer. Built scalable APIs.
    - StartUpX (2018-2020): Junior Dev. Worked on React and Node.js.
    Skills: Python, Neo4j, FastAPI, Docker.
    Education: Bachelors in CS.
    """
    
    # 1. LLM Extracts Graph Data
    structured_profile = parse_resume_to_json(raw_resume)
    # 2. Store in Neo4j
    graph_mgr.add_candidate_to_graph(structured_profile)

    # --- SCENARIO: RETRIEVAL ---
    print("\n--- 2. RECRUITER SEARCH ---")
    job_description = "Looking for a Python expert with at least 4 years of experience for an AI role."
    
    # Graph Search with filters
    matches = graph_mgr.search_candidates(
        required_skill="Python", 
        min_years=4
    )
    
    print(f"Found {len(matches)} candidates passing Graph filters.")
    
    # 3. Final LLM Scoring
    if matches:
        print("\n--- 3. AI RECRUITER ANALYSIS ---")
        final_verdict = llm_rerank(matches, job_description)
        print(final_verdict)
    else:
        print("\n❌ No candidates found matching the criteria.")

    # Cleanup
    driver.close()
    print("\n✅ Process completed successfully!")

if __name__ == "__main__":
    main()
