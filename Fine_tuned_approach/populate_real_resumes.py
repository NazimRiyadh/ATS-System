
import os
import requests
import csv
import io
import shutil

RESUME_URL = "https://raw.githubusercontent.com/wmurphyrd/resume/master/resume-data.csv"
OUTPUT_DIR = "./resumes"

def populate_real_resumes():
    print("Downloading Real Resume Dataset...")
    response = requests.get(RESUME_URL)
    response.raise_for_status()
    
    # Check if we need to clean dir
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning {OUTPUT_DIR}...")
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        os.makedirs(OUTPUT_DIR)

    # Parse CSV
    print("Parsing CSV...")
    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    
    count = 0
    target = 50
    
    for row in reader:
        if count >= target:
            break
            
        text = row.get('text', '').strip()
        job_title = row.get('title', 'Candidate').replace("/", "_").replace(" ", "_")
        
        if len(text) < 200: # Skip empty/short ones
            continue
            
        # Create filename
        filename = f"{job_title}_{count+1:02d}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(text)
            
        print(f"Saved: {filename}")
        count += 1
        
    print(f"Successfully populated {count} real resumes.")

if __name__ == "__main__":
    populate_real_resumes()
