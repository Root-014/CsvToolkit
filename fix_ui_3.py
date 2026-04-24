import os

file_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\frontend\src\App.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Search for the area
for i, line in enumerate(lines):
    if 'key={`res-`}' in line or 'key={`res-' in line:
        # Check if map is above it
        if 'blockResults.map' not in lines[i-1] and 'blockResults.map' not in lines[i-2]:
            lines.insert(i, '                                           {blockResults.map((msg) => msg && (\n')
            break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fix 3 applied successfully")
