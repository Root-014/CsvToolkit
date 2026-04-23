import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix duplicate styles and escaped slashes
code = code.replace(r"style={{ marginBottom: \'48px\' }} style={{ marginBottom: '48px' }}", "style={{ marginBottom: '48px' }}")
code = code.replace(r"style={{ marginBottom: \'48px\' }} style={{ opacity: 0.8, transform: 'scale(0.98)', transformOrigin: 'left', marginBottom: '32px' }}", "style={{ opacity: 0.8, transform: 'scale(0.98)', transformOrigin: 'left', marginBottom: '32px' }}")
code = code.replace(r"style={{ marginBottom: \'48px\' }}", "style={{ marginBottom: '48px' }}")

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('App.jsx cleaned.')
