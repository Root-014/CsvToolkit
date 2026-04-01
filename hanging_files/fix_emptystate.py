
with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_snippet = (
    '                         <div style={{color: \'var(--text-secondary)\', textAlign: \'center\', marginTop: \'40px\'}}>\r\n'
    '                            No metadata available. Please upload a CSV file to generate metadata.\r\n'
    '                         </div>'
)

new_snippet = (
    '                         <div className="empty-state-card">\r\n'
    '                           <div className="empty-state-icon">\r\n'
    '                             <Database size={48} />\r\n'
    '                           </div>\r\n'
    '                           <h3 className="empty-state-title">No Dataset Loaded</h3>\r\n'
    '                           <p className="empty-state-desc">\r\n'
    '                             Upload a CSV file using the panel on the left to generate metadata and analysis.\r\n'
    '                           </p>\r\n'
    '                           <div className="empty-state-hint">\r\n'
    '                             <Upload size={14} /> Drag &amp; drop or click the upload zone to get started\r\n'
    '                           </div>\r\n'
    '                         </div>'
)

if old_snippet in content:
    content = content.replace(old_snippet, new_snippet, 1)
    with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print('REPLACED OK')
else:
    # Try without \r
    old_lf = old_snippet.replace('\r\n', '\n')
    if old_lf in content:
        new_lf = new_snippet.replace('\r\n', '\n')
        content = content.replace(old_lf, new_lf, 1)
        with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
            f.write(content)
        print('REPLACED OK (LF)')
    else:
        # Show what's around "No metadata"
        idx = content.find('No metadata available')
        print('NOT FOUND. Context:')
        print(repr(content[max(0,idx-200):idx+200]))
