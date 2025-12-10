import os
import json
import uuid
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

# --- CONFIGURATION ---
# Load environment variables (Create a .env file or set these manually)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")  # FIXED: Updated to match Neo4j Desktop
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "987654321")

# Initialize Clients
client = OpenAI(api_key=OPENAI_API_KEY)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# --- PART 1: DATA MODELS (STRUCTURED EXTRACTION) ---
# We use Pydantic to ensure the LLM returns data in the exact format our Graph needs.

class WorkExperience(BaseModel):
    company: str
    role: str
    years_duration: float
    description: str

class Skill(BaseModel):
    name: str
    proficiency: str  # e.g., Junior, Senior, Expert

class CandidateProfile(BaseModel):
    name: str
    summary: str # Professional Bio
    skills: List[Skill]
    experience: List[WorkExperience]
    education_level: str

# --- PART 2: THE GRAPH DATABASE MANAGER ---

class GraphManager:
    def __init__(self, driver):
        self.driver = driver
        self.ensure_indexes()

    def ensure_indexes(self):
        """Creates Vector Index and Constraints for performance."""
        query_vector = """
        CREATE VECTOR INDEX candidate_bio_index IF NOT EXISTS
        FOR (c:Candidate) ON (c.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 1536,
         `vector.similarity_function`: 'cosine'
        }}
        """
        query_constraint = "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE"
        
        with self.driver.session() as session:
            session.run(query_vector)
            session.run(query_constraint)
            print("✅ Database Indexes & Constraints Verified.")

    def add_candidate_to_graph(self, profile: CandidateProfile, embedding: List[float]):
        """
        Push structured data to Graph AND Vector to DB.
        This represents the 'Dual Path' ingestion.
        """
        candidate_id = str(uuid.uuid4())
        
        cypher_query = """
        // 1. Create the Candidate Node with Vector Embedding
        MERGE (c:Candidate {name: $name})
        SET c.id = $id, 
            c.summary = $summary, 
            c.education = $education,
            c.embedding = $embedding

        // 2. Create and Link Skills
        WITH c
        UNWIND $skills AS skill
        MERGE (s:Skill {name: toLower(skill.name)})
        MERGE (c)-[:HAS_SKILL {proficiency: skill.proficiency}]->(s)

        // 3. Create and Link Experience (Companies)
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
                        embedding=embedding,
                        skills=[s.model_dump() for s in profile.skills],
                        experiences=[e.model_dump() for e in profile.experience]
            )
        print(f"✅ Candidate {profile.name} added to Graph & Vector Store.")

    def hybrid_search(self, query_vector: List[float], required_skill: str = None, min_years: int = 0):
        """
        THE CORE LOGIC: Vector Search + Graph Filtering.
        1. Search Vectors for semantic similarity.
        2. Filter results using Graph relationships (years of exp, specific skills).
        """
        # Build conditional query based on whether skill is required
        if required_skill:
            cypher_query = """
            // Step 1: Vector Search (Find top 10 semantically similar candidates)
            CALL db.index.vector.queryNodes('candidate_bio_index', 10, $embedding)
            YIELD node AS candidate, score

            // Step 2: Calculate total experience
            OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
            WITH candidate, score, coalesce(sum(r.years), 0) as total_experience
            
            // Step 3: Check for required skill
            MATCH (candidate)-[:HAS_SKILL]->(s:Skill)
            WHERE toLower(s.name) CONTAINS toLower($req_skill)

            // Step 4: Apply experience filter
            WHERE total_experience >= $min_years

            // Return Data for LLM Reranking
            RETURN candidate.name as name, 
                   candidate.summary as summary, 
                   total_experience, 
                   score as vector_score
            ORDER BY vector_score DESC
            """
        else:
            cypher_query = """
            // Step 1: Vector Search (Find top 10 semantically similar candidates)
            CALL db.index.vector.queryNodes('candidate_bio_index', 10, $embedding)
            YIELD node AS candidate, score

            // Step 2: Calculate total experience and filter
            OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
            WITH candidate, score, coalesce(sum(r.years), 0) as total_experience
            WHERE total_experience >= $min_years

            // Return Data for LLM Reranking
            RETURN candidate.name as name, 
                   candidate.summary as summary, 
                   total_experience, 
                   score as vector_score
            ORDER BY vector_score DESC
            """
        
        with self.driver.session() as session:
            result = session.run(cypher_query, 
                                 embedding=query_vector, 
                                 min_years=min_years, 
                                 req_skill=required_skill)
            return [record.data() for record in result]

# --- PART 3: HELPER FUNCTIONS (LLM & EMBEDDINGS) ---

def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

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
        return "No candidates met the hard filters."
        
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

# --- PART 4: EXECUTION PIPELINE ---

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
    # 2. Embedding Model creates Vector
    vector_embedding = get_embedding(structured_profile.summary)
    # 3. Store in Neo4j
    graph_mgr.add_candidate_to_graph(structured_profile, vector_embedding)


    # --- SCENARIO: RETRIEVAL ---
    print("\n--- 2. RECRUITER SEARCH ---")
    job_description = "Looking for a Python expert with at least 4 years of experience for an AI role."
    
    # 1. Turn JD into Vector
    jd_vector = get_embedding(job_description)
    
    # 2. Hybrid Search (Vector Match + Graph Constraint of 4+ years)
    # Note: Jane has 3 years (2020-2023) + 2 years (2018-2020) = 5 years total.
    # If we asked for 6 years, she would disappear from results efficiently.
    matches = graph_mgr.hybrid_search(
        query_vector=jd_vector, 
        required_skill="Python", 
        min_years=4
    )
    
    print(f"Found {len(matches)} candidates passing Graph filters.")
    
    # 3. Final LLM Scoring
    if matches:
        print("\n--- 3. AI RECRUITER ANALYSIS ---")
        final_verdict = llm_rerank(matches, job_description)
        print(final_verdict)

    # Cleanup
    driver.close()

if __name__ == "__main__":
    main()
