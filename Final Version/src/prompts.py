"""
Custom prompts for ATS domain entity extraction.
"""

# Entity extraction prompt for resume documents
ATS_ENTITY_EXTRACTION_PROMPT = """
-Goal-
Extract entities and relationships from the resume text. 
Return the output as a simple list of tuples using the "|" delimiter.

-Entity Types-
1. PERSON (Name)
2. SKILL (e.g., Python, SQL)
3. ROLE (e.g., Data Analyst)
4. COMPANY (e.g., Microsoft)
5. CERTIFICATION
6. LOCATION

-Output Format-
("entity"|name|type|description)
("relationship"|source|relationship_type|target|description)

-Examples-
("entity"|John Doe|PERSON|Candidate name)
("entity"|Python|SKILL|Programming language)
("relationship"|John Doe|HAS_SKILL|Python|Expert proficiency)

-Constraints-
1. Do NOT add quotes " around values unless they are part of the name.
2. Do NOT add markdown code blocks.
3. Output specific tuples only.

-Text-
{input_text}

-Output-
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
