
with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the old filter group by a unique anchor that won't clash
OLD_ANCHOR = "value={sheetFilters.val}"
if OLD_ANCHOR not in content:
    print("ERROR: anchor not found")
    exit(1)

# Identify full block to replace — from the start of <div className="toolbar-group"> before the anchor
# We'll locate it by splitting on the plain-text-input lines
lines = content.split('\n')
start_i = end_i = None
for i, line in enumerate(lines):
    if 'sheetFilters.val}' in line and 'sheetFilters.vals' not in line:
        # Walk backwards to the opening <div className="toolbar-group">
        j = i
        while j >= 0:
            if 'toolbar-group' in lines[j] and 'toolbar-label' not in lines[j]:
                start_i = j
                break
            j -= 1
        # Walk forwards to closing </div>
        k = i
        depth = 0
        found_close = False
        # Count after the <input ... />  to find the </div>
        for k in range(i, len(lines)):
            if '</div>' in lines[k]:
                end_i = k
                break
        break

if start_i is None or end_i is None:
    print(f"ERROR: could not find block. start={start_i} end={end_i}")
    exit(1)

print(f"Replacing lines {start_i+1} to {end_i+1}")
print("OLD block:")
for l in lines[start_i:end_i+1]:
    print(repr(l))

# Detect indentation from the opening div line
indent = len(lines[start_i]) - len(lines[start_i].lstrip())
ind = ' ' * indent
ind1 = ' ' * (indent + 3)   # one extra level
ind2 = ' ' * (indent + 5)   # two extra levels

new_block = [
    ind  + '<div className="toolbar-group">',
    ind1 + '<span className="toolbar-label"><Filter size={14}/> Filter:</span>',
    ind1 + '<select',
    ind2 + 'className="sheets-select"',
    ind2 + 'value={sheetFilters.col}',
    ind2 + 'onChange={(e) => {',
    ind2 + '  const newCol = e.target.value;',
    ind2 + '  setSheetFilters({ col: newCol, vals: [] });',
    ind2 + '  fetchColumnValues(newCol);',
    ind2 + '}}',
    ind1 + '>',
    ind2 + '<option value="">Select Column</option>',
    ind2 + '{sheetData?.columns.map(c => <option key={c} value={c}>{c}</option>)}',
    ind1 + '</select>',
    ind1 + '<MultiSelectDropdown',
    ind2 + 'options={colValues}',
    ind2 + 'selected={sheetFilters.vals || []}',
    ind2 + 'onChange={(vals) => setSheetFilters(f => ({ ...f, vals }))}',
    ind2 + 'disabled={!sheetFilters.col || colValuesLoading}',
    ind2 + "placeholder={colValuesLoading ? 'Loading...' : 'Select values...'}",
    ind1 + '/>',
    ind  + '</div>',
]

lines[start_i:end_i+1] = new_block

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("DONE - filter group replaced successfully")
