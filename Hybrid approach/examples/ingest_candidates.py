"""
Example: Ingest multiple candidates into the ATS system
"""
import sys
sys.path.append('..')

from ats_pipeline import get_pipeline

# Sample resumes
SAMPLE_RESUMES = [
    """
    John Smith
    Senior Software Engineer
    Email: john.smith@email.com
    Location: San Francisco, CA
    
    SUMMARY:
    Experienced full-stack developer with 8 years of experience building scalable web applications.
    Passionate about clean code, system design, and mentoring junior developers.
    
    EXPERIENCE:
    - Google (2020-Present): Senior Software Engineer
      Led development of microservices architecture serving 10M+ users.
      Technologies: Python, Go, Kubernetes, PostgreSQL
      Duration: 5 years
    
    - Startup Inc (2017-2020): Full Stack Developer
      Built MVP and scaled to 100K users. Implemented CI/CD pipeline.
      Technologies: React, Node.js, MongoDB, AWS
      Duration: 3 years
    
    SKILLS:
    - Python (Expert, 8 years)
    - JavaScript (Advanced, 8 years)
    - React (Advanced, 6 years)
    - PostgreSQL (Advanced, 5 years)
    - Kubernetes (Intermediate, 3 years)
    - System Design (Expert)
    
    EDUCATION:
    - Bachelor of Science in Computer Science
      Stanford University, 2017
      GPA: 3.8
    """,
    
    """
    Sarah Johnson
    Machine Learning Engineer
    Email: sarah.j@email.com
    Location: New York, NY
    
    SUMMARY:
    ML Engineer specializing in NLP and computer vision. Published researcher with
    3 papers in top-tier conferences. Love building AI products that solve real problems.
    
    EXPERIENCE:
    - Meta (2021-Present): ML Engineer
      Developed recommendation systems using deep learning. Improved CTR by 15%.
      Technologies: Python, PyTorch, TensorFlow, Spark
      Duration: 4 years
    
    - IBM Research (2019-2021): Research Scientist
      Conducted research in NLP. Published 2 papers at ACL.
      Technologies: Python, Transformers, BERT
      Duration: 2 years
    
    SKILLS:
    - Python (Expert, 6 years)
    - PyTorch (Expert, 4 years)
    - TensorFlow (Advanced, 5 years)
    - NLP (Expert, 6 years)
    - Computer Vision (Intermediate, 3 years)
    - MLOps (Advanced, 3 years)
    
    EDUCATION:
    - PhD in Computer Science (Machine Learning)
      MIT, 2019
      
    - Master of Science in Computer Science
      MIT, 2017
    """,
    
    """
    Michael Chen
    DevOps Engineer
    Email: m.chen@email.com
    Location: Seattle, WA
    
    SUMMARY:
    DevOps specialist with strong background in cloud infrastructure and automation.
    Experienced in building and maintaining large-scale distributed systems.
    
    EXPERIENCE:
    - Amazon Web Services (2018-Present): Senior DevOps Engineer
      Managed infrastructure for services handling 1B+ requests/day.
      Reduced deployment time by 70% through automation.
      Technologies: AWS, Terraform, Docker, Kubernetes, Python
      Duration: 7 years
    
    - Cisco (2016-2018): DevOps Engineer
      Implemented CI/CD pipelines. Managed on-prem infrastructure.
      Technologies: Jenkins, Ansible, Linux
      Duration: 2 years
    
    SKILLS:
    - AWS (Expert, 7 years)
    - Kubernetes (Expert, 5 years)
    - Docker (Expert, 7 years)
    - Terraform (Advanced, 5 years)
    - Python (Advanced, 6 years)
    - Linux (Expert, 9 years)
    
    EDUCATION:
    - Bachelor of Science in Computer Engineering
      UC Berkeley, 2016
    """
]

def main():
    print("=" * 70)
    print("ATS PIPELINE - CANDIDATE INGESTION DEMO")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = get_pipeline()
    
    # Ingest candidates
    print(f"\nIngesting {len(SAMPLE_RESUMES)} candidates...\n")
    candidate_ids = pipeline.batch_ingest(SAMPLE_RESUMES)
    
    # Show stats
    print("\n" + "=" * 70)
    print("SYSTEM STATISTICS")
    print("=" * 70)
    stats = pipeline.get_stats()
    print(f"Total Candidates: {stats['database']['total_candidates']}")
    print(f"Total Skills: {stats['database']['total_skills']}")
    print(f"Total Companies: {stats['database']['total_companies']}")
    print(f"Embedding Cache Size: {stats['embedding_cache']['cached_embeddings']} embeddings")
    print(f"Vector Index Available: {stats['vector_index_available']}")
    
    print("\n✅ Ingestion complete!")
    print(f"Candidate IDs: {candidate_ids}")
    
    # Close pipeline
    pipeline.close()

if __name__ == "__main__":
    main()
