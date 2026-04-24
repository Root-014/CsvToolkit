import os

file_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\frontend\src\App.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of blockResults
start = -1
for i, line in enumerate(lines):
    if '{blockResults.map' in line:
        start = i
        break

if start != -1:
    # Look for the next </>'
    end = -1
    for j in range(start, len(lines)):
        if '</>' in lines[j]:
            end = j
            break
    
    if end != -1:
        new_block = [
            '                                           {blockResults.map((msg) => msg && (\n',
            '                                             <div key={`res-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || "").toLowerCase() === "user" ? "user" : ""}`} style={{ marginBottom: "64px" }}>\n',
            '                                               <div className="avatar">{getAvatarIcon(msg.sender)}</div>\n',
            '                                               <div className={`chat-bubble ${(msg.type || "").toLowerCase() === "agent" ? "agent" : (msg.type || "").toLowerCase() === "user" ? "user-msg" : "system"} ${msg.sender?.toLowerCase() === "resultinterpreter" ? "final-result" : ""}`}>\n',
            '                                                 {msg.type === "agent" && getAgentHeaderStyle(msg.sender)}\n',
            '                                                 <div className="markdown-content">\n',
            '                                                   <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>\n',
            '                                                     {msg.content || ""}\n',
            '                                                   </ReactMarkdown>\n',
            '                                                 </div>\n',
            '                                               </div>\n',
            '                                             </div>\n',
            '                                           ))}\n'
        ]
        lines[start:end] = new_block

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fix 4 applied successfully")
