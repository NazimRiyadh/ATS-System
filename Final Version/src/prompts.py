"""
Custom prompts for ATS domain entity extraction.
"""

# Entity extraction prompt for resume documents
ATS_ENTITY_EXTRACTION_PROMPT = """
You are an expert resume parser. Extract entities and relationships from the resume text below.

## ENTITIES to extract:
- **PERSON**: Candidate's full name
- **SKILL**: Programming languages, frameworks, tools, soft skills
- **TECHNOLOGY**: Specific technologies, platforms, databases, cloud services
- **COMPANY**: Organizations, companies worked at
- **ROLE**: Job titles, positions held
- **PROJECT**: Named projects or significant work
- **CERTIFICATION**: Degrees, certifications, licenses
- **EDUCATION**: Universities, schools, educational institutions
- **LOCATION**: Cities, countries, regions

## RELATIONSHIPS to extract:
- PERSON **HAS_SKILL** SKILL (with proficiency: expert/advanced/intermediate/beginner)
- PERSON **WORKED_AT** COMPANY (with duration if mentioned)
- PERSON **HELD_ROLE** ROLE (with dates if mentioned)
- PERSON **WORKED_ON** PROJECT
- PERSON **HAS_CERTIFICATION** CERTIFICATION
- PERSON **STUDIED_AT** EDUCATION
- PERSON **USES** TECHNOLOGY
- SKILL **RELATED_TO** TECHNOLOGY
- ROLE **REQUIRES** SKILL

## Output Format:
For each entity, output:
ENTITY: {{name}}~{{type}}~{{description}}

For each relationship, output:
RELATION: {{source_entity}}~{{relationship_type}}~{{target_entity}}~{{description}}

## Resume Text:
{input_text}

## Extracted Entities and Relationships:
"""

# Query enhancement prompt for better retrieval
QUERY_ENHANCEMENT_PROMPT = """
You are an ATS query optimizer. Given a job description or search query, extract the key requirements.

## Input Query:
{query}

## Extract:
1. Required skills (must-have)
2. Preferred skills (nice-to-have)
3. Experience level (years, seniority)
4. Industry/domain keywords
5. Role-specific terms

## Output (JSON format):
{{
  "required_skills": [],
  "preferred_skills": [],
  "experience_level": "",
  "industry_keywords": [],
  "role_terms": []
}}
"""

# Candidate summary prompt
CANDIDATE_SUMMARY_PROMPT = """
Based on the following candidate information, provide a concise professional summary.

## Candidate Information:
{candidate_info}

## Job Context:
{job_context}

## Generate:
A 2-3 sentence summary highlighting the candidate's fit for the role, including:
1. Relevant experience
2. Key matching skills
3. Notable achievements

## Summary:
"""

# Chat response prompt with source attribution
CHAT_RESPONSE_PROMPT = """
You are an intelligent ATS assistant helping recruiters find and evaluate candidates.

## Available Information:
{context}

## User Question:
{query}

## Instructions:
1. Answer the question based ONLY on the provided information
2. If information is not available, clearly state that
3. Cite specific candidates, skills, or data points when relevant
4. Be concise but thorough
5. Format lists and comparisons clearly

## Response:
"""

# Ranking explanation prompt
RANKING_EXPLANATION_PROMPT = """
Explain why the following candidates are ranked in this order for the given job.

## Job Requirements:
{job_requirements}

## Ranked Candidates:
{ranked_candidates}

## For each candidate, explain:
1. Key matching qualifications
2. Relevant experience highlights
3. Any gaps or considerations
4. Overall fit score justification

## Ranking Explanation:
"""
