
try:
    with open('results.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    try:
        with open('results.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        with open('results.txt', 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')

print("=== CONTENT START ===")
lines = content.split('\n')
for line in lines:
    if "Step 1" in line or "Step 2" in line or "LLM Response" in line or "Candidate" in line or "Name:" in line or "found" in line:
        print(line)
    # Also print the reasoning body
    if len(line) > 50 and "INFO" not in line:
        print(line)
print("=== CONTENT END ===")
