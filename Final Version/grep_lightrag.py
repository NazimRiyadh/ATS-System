
import os

search_path = "venv312/Lib/site-packages/lightrag"
query = "community"
output_file = "grep_output.txt"

print(f"Searching for '{query}' in {search_path}...")

with open(output_file, "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f):
                            if query in line.lower():
                                out.write(f"{path}:{i+1}: {line.strip()}\n")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

print(f"Done. Saved to {output_file}")
