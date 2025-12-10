
import os
import requests
import csv
import io
import random
import uuid

# URL for a mirror of the Snehaan Bhawal / Kaggle Resume Dataset
DATASET_URL = "https://raw.githubusercontent.com/SayamAlt/Resume-Classification-using-fine-tuned-BERT/master/UpdatedResumeDataSet.csv"
OUTPUT_DIR = "./resumes"

# 100 Diverse, Distinct Names (US, UK, Asia, Europe, LatAm)
DIVERSE_NAMES = [
    "Liam O'Connor", "Olivia Smith", "Noah Johnson", "Emma Williams",
    "Wei Zhang", "Li Yan", "Hiroshi Tanaka", "Yuki Sato",
    "Priya Sharma", "Rahul Verma", "Ananya Gupta", "Arjun Singh",
    "Carlos Rodriguez", "Sofia Martinez", "Miguel Hernandez", "Isabella Lopez",
    "Jean-Luc Dubois", "Marie Laurent", "Lukas Mueller", "Anna Schmidt",
    "Ivan Petrov", "Elena Sokolov", "Lars Jensen", "Freja Hansen",
    "Ahmed Hassan", "Fatima Ali", "Omar Khalid", "Aisha Khan",
    "Samuel Okafor", "Chioma Eze", "Kwame Mensah", "Amara Diallo",
    "James Bond", "Sarah Connor", "Tony Stark", "Natasha Romanoff",
    "Bruce Wayne", "Clark Kent", "Peter Parker", "Diana Prince",
    "Walter White", "Jesse Pinkman", "Saul Goodman", "Gustavo Fring",
    "Michael Scott", "Jim Halpert", "Pam Beesly", "Dwight Schrute",
    "Sheldon Cooper", "Leonard Hofstadter", "Penny Teller", "Howard Wolowitz",
    "Harry Potter", "Hermione Granger", "Ron Weasley", "Draco Malfoy",
    "Luke Skywalker", "Leia Organa", "Han Solo", "Kylo Ren",
    "Frodo Baggins", "Samwise Gamgee", "Aragorn Elessar", "Legolas Greenleaf",
    "Jon Snow", "Daenerys Targaryen", "Tyrion Lannister", "Arya Stark",
    "Sherlock Holmes", "John Watson", "Hercule Poirot", "Miss Marple",
    "Jack Sparrow", "Will Turner", "Elizabeth Swann", "Hector Barbossa",
    "Marty McFly", "Doc Brown", "Ellen Ripley", "Sarah Connor",
    "Neo Anderson", "Trinity Moss", "Morpheus Lawrence", "Agent Smith",
    "Forrest Gump", "Jenny Curran", "Bubba Blue", "Lt. Dan Taylor",
    "Rocky Balboa", "Apollo Creed", "Ivan Drago", "Adonis Creed",
    "Maverick Mitchell", "Iceman Kazansky", "Goose Bradshaw", "Viper Metcalf"
]

def fetch_and_process():
    print(f"Downloading Kaggle Resume Dataset from {DATASET_URL}...")
    response = requests.get(DATASET_URL)
    response.raise_for_status()

    # Clean Output Directory
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning {OUTPUT_DIR}...")
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        os.makedirs(OUTPUT_DIR)

    # Parse CSV
    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    
    random.shuffle(DIVERSE_NAMES)
    name_idx = 0
    count = 0
    target_count = 50 # Limit to 50 for reasonable ingestion time per user request context
    
    processed_rows = list(reader)
    # Shuffle rows to get a mix of categories (otherwise first 50 might be all Data Science)
    random.shuffle(processed_rows)

    for row in processed_rows:
        if count >= target_count:
            break
            
        resume_text = row.get('Resume', '').strip()
        category = row.get('Category', 'Candidate').strip().replace(" ", "_")
        
        if len(resume_text) < 200:
            continue
            
        # Assign Name
        name = DIVERSE_NAMES[name_idx % len(DIVERSE_NAMES)]
        name_idx += 1
        
        # Inject Name at top
        final_text = f"Name: {name}\n\n{resume_text}"
        
        # Create Filename
        safe_name = name.replace(" ", "_").replace("'", "")
        unique_id = uuid.uuid4().hex[:6]
        filename = f"{category}_{safe_name}_{unique_id}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(final_text)
            
        print(f"Saved: {filename}")
        count += 1
        
    print(f"Successfully populated {count} resumes from Kaggle Dataset.")

if __name__ == "__main__":
    fetch_and_process()
