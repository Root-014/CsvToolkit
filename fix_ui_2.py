import os

file_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\frontend\src\App.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove duplicate div at 1023
if 'res-' in lines[1022] and 'res-' in lines[1023]:
    del lines[1023]

# Fix closing braces
# The previous script might have left some lines orphaned.
# I'll just restore the map correctly.

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '{blockResults.map((msg) => msg && (' in line:
        start_idx = i
    if '</>' in line and i > start_idx and start_idx != -1:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_map = [
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
    lines[start_idx:end_idx] = new_map

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fix 2 applied successfully")
