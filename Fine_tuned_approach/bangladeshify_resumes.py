
import os
import random
import re
import uuid

FIRST_NAMES = [
    "Rahim", "Karim", "Abdul", "Farhana", "Tasnim", "Nusrat", "Shakib", "Tamim", 
    "Mushfiqur", "Mahmudullah", "Liton", "Mehidy", "Taskin", "Mustafizur", "Shoriful", 
    "Ebadot", "Najmul", "Towhid", "Afif", "Nurul", "Rubel", "Taijul", "Soumya", 
    "Mohammad", "Nasum", "Mahedi", "Yasir", "Mosaddek", "Shamim", "Hasan", "Jamal",
    "Kamal", "Rafiq", "Jabbar", "Salam", "Borkot", "Sufia", "Begum", "Rokeya"
]

LAST_NAMES = [
    "Uddin", "Ahmed", "Jabbar", "Khan", "Rahman", "Jahan", "Al Hasan", "Iqbal", 
    "Rahim", "Riyad", "Das", "Hasan", "Islam", "Hossain", "Shanto", "Hridoy", 
    "Sarkar", "Saifuddin", "Ali", "Naim", "Bhuiyan", "Chowdhury", "Talukder", "Mia",
    "Mollah", "Sheikh", "Sikder", "Akter", "Khatun", "Begum"
]

RESUMES_DIR = "./resumes"

def bangladeshify():
    if not os.path.exists(RESUMES_DIR):
        print("Resumes directory not found.")
        return

    files = [f for f in os.listdir(RESUMES_DIR) if f.endswith(".txt")]
    print(f"Found {len(files)} resumes. Converting to EXTREMELY UNIQUE Bangladeshi profile names...")

    for filename in files:
        filepath = os.path.join(RESUMES_DIR, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Generate Unique Name: First + Last + (Optional Middle)
        new_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if random.random() > 0.8: # 20% chance of 3-part name
            new_name += f" {random.choice(LAST_NAMES)}"
            
        # Replace Name in content
        new_content = re.sub(r"Name:.*", f"Name: {new_name}", content)
        if "Name:" not in new_content:
            new_content = f"Name: {new_name}\n{new_content}"
            
        # Save content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        # Formatting Filename: Role_Name_UUID.txt
        # Extract Role from existing filename if possible (usually first part)
        parts = filename.split('_')
        role = parts[0] if len(parts) > 1 else "Candidate"
        
        # Clean name for filename
        safe_name = new_name.replace(" ", "_")
        
        # Add short UUID for guaranteed uniqueness
        unique_id = uuid.uuid4().hex[:8]
        
        new_filename = f"{role}_{safe_name}_{unique_id}.txt"

        new_filepath = os.path.join(RESUMES_DIR, new_filename)
        os.rename(filepath, new_filepath)
        print(f"Renamed: {filename} -> {new_filename}")

    print("Bangladeshification Complete.")


if __name__ == "__main__":
    bangladeshify()
