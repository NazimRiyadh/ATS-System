import asyncio
import os
import time
import json
import re
from lightrag import LightRAG, QueryParam
from src.rag_engine import initialize_rag
from src.query_processor import extract_keywords

# Define test cases: Query -> Expected Keywords/Roles in top results
TEST_CASES = [
    {
        "query": "Senior Python Developer with cloud experience",
        "expected_role": "Senior Python Developer",
        "min_hit": 1
    },
    {
        "query": "Junior Frontend Engineer with React skills",
        "expected_role": "Junior Frontend Engineer",
        "min_hit": 1
    },
    {
        "query": "DevOps Engineer with Kubernetes",
        "expected_role": "DevOps Engineer",
        "min_hit": 1
    },
    {
        "query": "Data Scientist with Machine Learning expertise",
        "expected_role": "Data Scientist",
        "min_hit": 1
    },
    {
        "query": "Product Manager for agile teams",
        "expected_role": "Product Manager",
        "min_hit": 1
    }
]

async def evaluate():
    print("Initializing LightRAG for evaluation...")
    rag = await initialize_rag()
    
    total_latency = 0
    total_hits = 0
    total_tests = len(TEST_CASES)
    
    print(f"\nStarting evaluation with {total_tests} test cases...\n")
    
    for i, test in enumerate(TEST_CASES):
        query = test["query"]
        expected = test["expected_role"]
        
        print(f"Test {i+1}: Query='{query}' (Expect: {expected})")
        
        start_time = time.time()
        
        # 1. Pre-process query
        refined_query = await extract_keywords(query)
        
        # 2. Run Query (Structured)
        structured_query = f"""
        {refined_query}
        
        IMPORTANT: Return the result ONLY as a JSON list of objects. 
        Each object must have the following keys:
        - "rank": (integer) 1, 2, 3...
        - "name": (string) Candidate Name
        - "current_role": (string) The candidate's most recent job title (e.g. "Senior Python Developer")
        - "match_score": (integer) 0-100 estimate based on skills and experience match
        - "skills_matched": (list of strings) Key skills found in resume that match query
        - "summary": (string) Brief justification (max 20 words)
        
        Do not include any markdown formatting (like ```json). Just the raw JSON string.
        """
        
        result = await rag.aquery(
            structured_query,
            param=QueryParam(mode="hybrid", top_k=5)
        )
        end_time = time.time()
        latency = end_time - start_time
        total_latency += latency
        
        # 3. Check for hit
        # Clean result to ensure valid JSON
        json_str = result
        if "```json" in json_str:
            json_str = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL).group(1)
        elif "```" in json_str:
            json_str = re.search(r'```\n(.*?)\n```', json_str, re.DOTALL).group(1)
            
        hit = False
        try:
            candidates = json.loads(json_str)
            # Check if any of the top 5 candidates have the expected role in their summary or name
            # Note: Since we generated resumes with role-based filenames/names, this is a reasonable proxy.
            # In a real system, we'd check the 'Role' entity in the graph, but here we check the text output.
            for cand in candidates:
                # Check if expected role is in the extracted 'current_role', 'summary', or 'name'
                role_match = expected.lower() in cand.get('current_role', '').lower()
                summary_match = expected.lower() in cand.get('summary', '').lower()
                name_match = expected.lower() in cand.get('name', '').lower()
                
                if role_match or summary_match or name_match:
                    hit = True
                    break
        except Exception as e:
            print(f"  [ERROR] JSON Parsing failed: {e}")
            print(f"  [DEBUG] Raw Result: {result[:200]}...") # Print first 200 chars
            pass
        
        if hit:
            total_hits += 1
            print(f"  [PASS] Hit found. Latency: {latency:.2f}s")
        else:
            print(f"  [FAIL] Expected '{expected}' not found in top results. Latency: {latency:.2f}s")
            if not hit:
                 print(f"  [DEBUG] Candidates found: {[c.get('name') for c in candidates] if 'candidates' in locals() else 'None'}")
            
    avg_latency = total_latency / total_tests
    accuracy = (total_hits / total_tests) * 100
    
    print("\n=== Evaluation Report ===")
    print(f"Total Tests: {total_tests}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Avg Latency: {avg_latency:.2f}s")
    
    if accuracy >= 80:
        print("\nRESULT: PASSED (Ready for Production)")
    else:
        print("\nRESULT: FAILED (Needs Improvement)")

if __name__ == "__main__":
    asyncio.run(evaluate())
