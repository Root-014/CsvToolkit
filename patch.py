import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove ErrorBoundary wrapper
code = code.replace('<ErrorBoundary key={`eb-${messages.length}`}>', '')
code = code.replace('</ErrorBoundary>', '')

# 2. Add inline margins
code = code.replace('className="message-row user"', 'className="message-row user" style={{ marginBottom: \'48px\' }}')
code = re.sub(r'(className={`message-row \${.*?}\`})', r'\1 style={{ marginBottom: \'48px\' }}', code)

# 3. Fix the specific one with existing style
code = code.replace(
    "style={{ opacity: 0.8, transform: 'scale(0.98)', transformOrigin: 'left' }}",
    "style={{ opacity: 0.8, transform: 'scale(0.98)', transformOrigin: 'left', marginBottom: '32px' }}"
)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('App.jsx updated.')
