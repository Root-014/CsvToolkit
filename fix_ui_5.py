import os

file_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\frontend\src\App.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix reasoning-content map
for i in range(1005, 1020):
    if '{restOfHistory.map' in lines[i]:
        # Replace the whole block until the next ))
        for j in range(i, i+20):
            if '))} ' in lines[j] or '))}' in lines[j]:
                new_hist = [
                    '                                                   {restOfHistory.map((msg) => msg && (\n',
                    '                                                     <div key={`hist-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || "").toLowerCase() === "user" ? "user" : ""}`} style={{ opacity: 0.8, transform: "scale(0.98)", transformOrigin: "left", marginBottom: "32px" }}>\n',
                    '                                                       <div className="avatar" style={{ width: "28px", height: "28px" }}>{getAvatarIcon(msg.sender)}</div>\n',
                    '                                                       <div className={`chat-bubble ${(msg.type || "").toLowerCase() === "agent" ? "agent" : (msg.type || "").toLowerCase() === "user" ? "user-msg" : "system"}`}>\n',
                    '                                                         {msg.type === "agent" && getAgentHeaderStyle(msg.sender)}\n',
                    '                                                         <div className="markdown-content">\n',
                    '                                                           <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>\n',
                    '                                                             {msg.content || ""}\n',
                    '                                                           </ReactMarkdown>\n',
                    '                                                         </div>\n',
                    '                                                       </div>\n',
                    '                                                     </div>\n',
                    '                                                   ))}\n'
                ]
                lines[i:j+1] = new_hist
                break
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fix 5 applied successfully")
