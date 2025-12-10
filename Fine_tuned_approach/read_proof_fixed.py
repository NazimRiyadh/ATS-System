
try:
    with open('proof_fixed.log', 'rb') as f:
        content = f.read().decode('utf-16', errors='ignore')
except:
    with open('proof_fixed.log', 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

print("=== DECODED FIXED LOG ===")
lines = content.split('\n')
for line in lines:
    if "PROMPT SENT TO LLM" in line or "PROFILE:" in line or "Name:" in line or "[LLM Final Answer]" in line:
        print(line[:200]) # Truncate lines for sanity
print("=== END ===")
