
try:
    with open('proof.log', 'rb') as f:
        content = f.read().decode('utf-16', errors='ignore') # Check if utf-16
except:
    with open('proof.log', 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

print("=== DECODED LOG ===")
lines = content.split('\n')
capturing = False
for line in lines:
    if "PROMPT SENT TO LLM" in line:
        capturing = True
        print(line)
    elif capturing:
        print(line)
        if "="*100 in line:
            capturing = False
            
    # Also print retrieval results
    if "Retrieved" in line or "Name:" in line or "Asking LLM" in line:
        print(line)

print("=== END ===")
