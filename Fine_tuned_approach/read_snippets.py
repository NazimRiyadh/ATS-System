
try:
    with open('snippet_results.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    try:
        with open('snippet_results.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        with open('snippet_results.txt', 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')

print("=== SNIPPETS START ===")
lines = content.split('\n')
for line in lines:
    if "Snippet:" in line or "Candidate File:" in line:
        print(line)
print("=== SNIPPETS END ===")
