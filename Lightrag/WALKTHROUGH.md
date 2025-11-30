# System Walkthrough & Demo

This document demonstrates the capabilities of the LightRAG ATS system, showcasing its ability to understand complex queries and rank candidates effectively using local embeddings and reranking.

## Demo 1: Senior Backend Role
**Query:** `"Senior Python Developer with backend experience"`

The system correctly identifies senior candidates with specific backend skills.

```text
RANKING RESULTS FOR: Senior Python Developer with backend experience
================================================================================

RANK  | SCORE  | NAME                      | SUMMARY
--------------------------------------------------------------------------------
1     | 95   % | Johnathan D. Harper       | Strong experience in backend development and API implementation.
2     | 90   % | Johnathan R. Coder        | Expertise in developing scalable applications and data analytics systems.
3     | 85   % | Johnathan D. Rivers       | Proficient in backend development for high-traffic applications.
--------------------------------------------------------------------------------
```

## Demo 2: Junior Frontend Role
**Query:** `"Junior Frontend Engineer with React and TypeScript"`

The system adapts to find junior profiles with specific framework knowledge.

```text
RANKING RESULTS FOR: Junior Frontend Engineer with React and TypeScript
================================================================================

RANK  | SCORE  | NAME                      | SUMMARY
--------------------------------------------------------------------------------
1     | 90   % | Jordan Rivers             | Strong experience in React and frontend development.
2     | 85   % | John Doe                  | Proficient in web applications with React.
3     | 80   % | Alex Rivers               | Solid frontend skills with React experience.
--------------------------------------------------------------------------------
```

## Demo 3: Specialized Security Role
**Query:** `"Cybersecurity Analyst with network security skills"`

The system finds candidates with niche skills in security.

```text
RANKING RESULTS FOR: Cybersecurity Analyst with network security skills
================================================================================

RANK  | SCORE  | NAME                      | SUMMARY
--------------------------------------------------------------------------------
1     | 90   % | Johnathan A. Cipher       | Strong expertise in network security and extensive cybersecurity experience.
2     | 85   % | Jamie R. Bennett          | Significant experience in network security and incident management.
3     | 80   % | Johnathan "Johnny" Cipher | Detail-oriented analyst with a focus on network security risks.
--------------------------------------------------------------------------------
```

## Conclusion
The system successfully:
1.  **Understands Context**: Distinguishes between "Senior" and "Junior" roles.
2.  **Matches Skills**: Finds candidates with specific tech stacks (Python, React, Network Security).
3.  **Ranks Effectively**: The top results are highly relevant to the query.
