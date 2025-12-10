
try:
    with open('proof.log', 'r', encoding='utf-8') as f:
        content = f.read()
    print(content)
except Exception as e:
    print(e)
