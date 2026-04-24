import os

file_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\frontend\src\App.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix reasoning logs (approx line 1012)
for i in range(1000, 1020):
    if '<ReactMarkdown' in lines[i] and 'reasoning-content' in ''.join(lines[i-10:i]):
        lines[i] = '                                                           <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>\n'
        lines[i+1] = '                                                             {msg.content || \'\'}\n'
        lines[i+2] = '                                                           </ReactMarkdown>\n'
        lines[i+3] = '                                                         </div>\n'

# Fix blockResults (approx line 1028)
for i in range(1020, 1040):
    if '<ReactMarkdown' in lines[i] and 'blockResults' in ''.join(lines[i-10:i]):
        lines[i-5] = '                                             <div key={`res-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || "").toLowerCase() === "user" ? "user" : ""}`} style={{ marginBottom: "64px" }}>\n'
        lines[i] = '                                                 <div className="markdown-content">\n'
        lines[i+1] = '                                                   <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>\n'
        lines[i+2] = '                                                     {msg.content || ""}\n'
        lines[i+3] = '                                                   </ReactMarkdown>\n'
        lines[i+4] = '                                                 </div>\n'
        lines[i+5] = '                                               </div>\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fix applied successfully")
