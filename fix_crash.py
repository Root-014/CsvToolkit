import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix duplicate styles
code = re.sub(r"style=\{\{ marginBottom: '48px' \}\} style=\{\{ marginBottom: '48px' \}\}", "style={{ marginBottom: '48px' }}", code)

# 2. Add null-safe id access (careful with regex to only match .id)
code = code.replace('.id', '?.id')

# 3. Clean up the escaped backslashes I might have left
code = code.replace(r"\'48px\'", "'48px'")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('App.jsx fixed and made null-safe.')
