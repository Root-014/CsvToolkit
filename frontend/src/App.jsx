import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Editor } from '@monaco-editor/react';
import { Upload, Play, FileText, Terminal, Bot, User, Cpu, Database, ShieldAlert, CheckCircle2, ChevronDown, Code, Save, Minus, Square, X, Folder, Search, Filter, ArrowUp, ArrowDown, ListFilter, RotateCcw } from 'lucide-react';
import './index.css';

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

const FileExplorer = ({ exploreFiles, selectedFilePath, setSelectedFilePath, setExploreFiles }) => {
  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/files`);
      if (res.data.status === 'success') {
        setExploreFiles(res.data.files);
      }
    } catch (err) {
      console.error("Failed to fetch files", err);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const renderTree = (items) => {
    return items.map(item => (
      <div key={item.path} style={{ marginLeft: item.isDir ? '0' : '12px' }}>
        <div 
          className={`tree-item ${item.isDir ? 'folder' : 'file'} ${selectedFilePath === item.path ? 'active' : ''}`}
          onClick={() => !item.isDir && setSelectedFilePath(item.path)}
        >
          {item.isDir ? <Folder size={14} /> : <FileText size={14} />}
          <span>{item.name}</span>
        </div>
        {item.isDir && item.children && item.children.length > 0 && (
          <div style={{ marginLeft: '16px', borderLeft: '1px solid var(--glass-border)' }}>
            {renderTree(item.children)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="file-explorer">
      <div className="explorer-header">
         <Folder size={16} /> PROJECT FILES
      </div>
      <div className="explorer-tree">
         {renderTree(exploreFiles)}
      </div>
    </div>
  );
};

// ---- MultiSelectDropdown ------------------------------------------------
const MultiSelectDropdown = ({ options, selected, onChange, disabled, placeholder }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filtered = options.filter(o => o.toLowerCase().includes(search.toLowerCase()));

  const toggle = (val) => {
    if (selected.includes(val)) onChange(selected.filter(v => v !== val));
    else onChange([...selected, val]);
  };

  const selectAll = () => onChange(filtered);
  const clearAll  = () => onChange([]);

  const label = selected.length === 0
    ? (placeholder || 'Select values...')
    : selected.length === 1
      ? selected[0]
      : `${selected.length} selected`;

  return (
    <div className="ms-dropdown" ref={ref}>
      <button
        className={`ms-trigger ${open ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={() => !disabled && setOpen(o => !o)}
        type="button"
      >
        <span className="ms-label">{label}</span>
        <ChevronDown size={12} className={`ms-chevron ${open ? 'rotated' : ''}`} />
      </button>

      {open && (
        <div className="ms-panel">
          {/* Search */}
          <div className="ms-search-wrap">
            <Search size={13} className="ms-search-icon" />
            <input
              className="ms-search"
              placeholder="Search..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              autoFocus
            />
          </div>

          {/* Bulk actions */}
          <div className="ms-bulk">
            <button className="ms-bulk-btn" onClick={selectAll}>All</button>
            <button className="ms-bulk-btn" onClick={clearAll}>None</button>
            <span className="ms-count">{selected.length}/{options.length}</span>
          </div>

          {/* Options list */}
          <div className="ms-options">
            {filtered.length === 0
              ? <div className="ms-empty">No matches</div>
              : filtered.map(opt => (
                <label key={opt} className="ms-option">
                  <input
                    type="checkbox"
                    checked={selected.includes(opt)}
                    onChange={() => toggle(opt)}
                  />
                  <span>{opt}</span>
                </label>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
};
// -------------------------------------------------------------------------

// Sub-component for File Viewer (Table part)
const FileViewer = ({ 
  selectedFilePath, 
  setSelectedFilePath, 
  sheetData, 
  setSheetData, 
  sheetLoading, 
  setSheetLoading,
  sheetFilters,
  setSheetFilters,
  sheetSort,
  setSheetSort,
  sheetLimit,
  setSheetLimit
}) => {
  const [colValues, setColValues] = useState([]);        // unique values for filter col
  const [colValuesLoading, setColValuesLoading] = useState(false);

  
  const loadCsvData = async (path, options = {}) => {
    setSheetLoading(true);
    try {
      const currentVals = options.filter_vals !== undefined ? options.filter_vals : sheetFilters.vals;
      const res = await axios.post(`${API_BASE}/api/view_csv`, {
        file_path: path,
        filter_col: options.filter_col !== undefined ? options.filter_col : sheetFilters.col,
        filter_vals: currentVals,
        sort_col: options.sort_col !== undefined ? options.sort_col : sheetSort.col,
        sort_ascending: options.sort_ascending !== undefined ? options.sort_ascending : sheetSort.asc,
        limit_type: options.limit_type !== undefined ? options.limit_type : sheetLimit.type,
        limit_n: options.limit_n !== undefined ? options.limit_n : sheetLimit.n
      });
      if (res.data.status === 'success') {
        setSheetData(res.data);
      }
    } catch (err) {
      console.error("Failed to load CSV", err);
    } finally {
      setSheetLoading(false);
    }
  };

  // Fetch unique values for the selected filter column
  const fetchColumnValues = async (col) => {
    if (!col || !selectedFilePath) { setColValues([]); return; }
    setColValuesLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/column_values`, {
        file_path: selectedFilePath,
        column: col
      });
      if (res.data.status === 'success') setColValues(res.data.values);
      else setColValues([]);
    } catch { setColValues([]); }
    finally { setColValuesLoading(false); }
  };

  useEffect(() => {
    if (selectedFilePath && selectedFilePath.endsWith('.csv')) {
      loadCsvData(selectedFilePath);
    } else {
      setSheetData(null);
    }
  }, [selectedFilePath]);

  const handleApplyOps = () => {
    loadCsvData(selectedFilePath);
  };

  const handleHeaderSort = (col) => {
    const newAsc = sheetSort.col === col ? !sheetSort.asc : true;
    setSheetSort({ col, asc: newAsc });
    loadCsvData(selectedFilePath, { 
      sort_col: col, 
      sort_ascending: newAsc 
    });
  };

  const resetOps = () => {
    const defaultFilters = { col: "", vals: [] };
    const defaultSort = { col: "", asc: true };
    const defaultLimit = { type: "top", n: 50 };
    setSheetFilters(defaultFilters);
    setSheetSort(defaultSort);
    setSheetLimit(defaultLimit);
    setColValues([]);
    loadCsvData(selectedFilePath, {
      filter_col: "",
      filter_vals: [],
      sort_col: "",
      sort_ascending: true,
      limit_type: "top",
      limit_n: 50
    });
  };

  return (
    <div className="file-viewer-container">
      <div className="sheets-view">
        {selectedFilePath ? (
          selectedFilePath.endsWith('.csv') ? (
            <>
              <div className="sheets-toolbar">
                <div className="toolbar-group">
                   <span className="toolbar-label"><Filter size={14}/> Filter:</span>
                   <select
                     className="sheets-select"
                     value={sheetFilters.col}
                     onChange={(e) => {
                       const newCol = e.target.value;
                       setSheetFilters({ col: newCol, vals: [] });
                       fetchColumnValues(newCol);
                     }}
                   >
                     <option value="">Select Column</option>
                     {sheetData?.columns.map(c => <option key={c} value={c}>{c}</option>)}
                   </select>
                   <MultiSelectDropdown
                     options={colValues}
                     selected={sheetFilters.vals || []}
                     onChange={(vals) => setSheetFilters(f => ({ ...f, vals }))}
                     disabled={!sheetFilters.col || colValuesLoading}
                     placeholder={colValuesLoading ? 'Loading...' : 'Select values...'}
                   />
                </div>

                <div className="toolbar-group">
                   <span className="toolbar-label"><ArrowUp size={14}/> Sort:</span>
                   <select 
                     className="sheets-select"
                     value={sheetSort.col}
                     onChange={(e) => setSheetSort({...sheetSort, col: e.target.value})}
                   >
                     <option value="">Select Column</option>
                     {sheetData?.columns.map(c => <option key={c} value={c}>{c}</option>)}
                   </select>
                   <button 
                     className="terminal-btn"
                     onClick={() => setSheetSort({...sheetSort, asc: !sheetSort.asc})}
                   >
                     {sheetSort.asc ? <ArrowUp size={14}/> : <ArrowDown size={14}/>}
                   </button>
                </div>

                <div className="toolbar-group">
                   <select 
                     className="sheets-select"
                     value={sheetLimit.type}
                     onChange={(e) => setSheetLimit({...sheetLimit, type: e.target.value})}
                   >
                     <option value="top">Top</option>
                     <option value="bottom">Bottom</option>
                   </select>
                   <input 
                     type="number"
                     className="sheets-input"
                     style={{ width: '60px' }}
                     value={sheetLimit.n}
                     onChange={(e) => setSheetLimit({...sheetLimit, n: parseInt(e.target.value) || 10})}
                   />
                </div>

                <div className="toolbar-group" style={{marginLeft: 'auto'}}>
                   <button className="btn-primary" style={{padding: '6px 12px', fontSize: '0.85rem'}} onClick={handleApplyOps}>
                      Apply
                   </button>
                   <button className="terminal-btn" title="Reset" onClick={resetOps}>
                      <RotateCcw size={14} />
                   </button>
                </div>
              </div>

              <div className="sheets-table-container">
                {sheetLoading ? (
                  <div className="sheets-empty">
                    <div className="spinner"></div>
                    <span>Processing with Pandas...</span>
                  </div>
                ) : sheetData ? (
                  <table className="sheets-table">
                    <thead>
                      <tr>
                        {sheetData.columns.map(col => (
                          <th key={col} onClick={() => handleHeaderSort(col)} className="sortable-header">
                            <div className="header-content">
                              {col}
                              {sheetSort.col === col && (
                                <span className="sort-icon">
                                  {sheetSort.asc ? <ArrowUp size={12}/> : <ArrowDown size={12}/>}
                                </span>
                              )}
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sheetData.data.map((row, i) => (
                        <tr key={i}>
                          {sheetData.columns.map(col => (
                            <td key={col}>{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : null}
              </div>

              <div className="sheets-status">
                 {sheetData && (
                   <>
                     <span>Showing {sheetData.display_rows} of {sheetData.total_rows} rows</span>
                     <span>{selectedFilePath}</span>
                   </>
                 )}
              </div>
            </>
          ) : selectedFilePath.toLowerCase().endsWith('.html') ? (
            <div className="sheets-html-viewer" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                 <button 
                   className="btn-primary" 
                   onClick={() => window.open(`${API_BASE}/api/file_content?path=${encodeURIComponent(selectedFilePath)}`, '_blank')}
                 >
                   Open in New Tab
                 </button>
              </div>
              <iframe 
                src={`${API_BASE}/api/file_content?path=${encodeURIComponent(selectedFilePath)}`} 
                style={{ flex: 1, border: 'none', backgroundColor: 'white', borderRadius: '0 0 8px 8px' }} 
                title="HTML Viewer"
              />
            </div>
          ) : (
            <div className="sheets-empty">
               <FileText size={48} style={{ opacity: 0.2 }} />
               <span>Click a CSV or HTML file on the left to view data.</span>
            </div>
          )
        ) : (
          <div className="sheets-empty">
             <Search size={48} style={{ opacity: 0.2 }} />
             <span>Select a file to begin explorer.</span>
          </div>
        )}
      </div>
    </div>
  );
};


function App() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadLogs, setUploadLogs] = useState([]);
  const [markdownContent, setMarkdownContent] = useState("");
  const [query, setQuery] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'markdown'
  const [showFullLog, setShowFullLog] = useState(false);
  const [expandedTimelineSteps, setExpandedTimelineSteps] = useState(new Set());

  // Editor state
  const [editorCode, setEditorCode] = useState("");
  const [originalCode, setOriginalCode] = useState("");
  const [editorOutput, setEditorOutput] = useState("");
  const [isCodeRunning, setIsCodeRunning] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(240);
  const [isTerminalMinimized, setIsTerminalMinimized] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  
  // File Viewer state
  const [exploreFiles, setExploreFiles] = useState([]);
  const [selectedFilePath, setSelectedFilePath] = useState("");
  const [sheetData, setSheetData] = useState(null);
  const [sheetLoading, setSheetLoading] = useState(false);
  const [sheetFilters, setSheetFilters] = useState({ col: "", vals: [] });
  const [sheetSort, setSheetSort] = useState({ col: "", asc: true });
  const [sheetLimit, setSheetLimit] = useState({ type: "top", n: 50 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      // Calculate height from bottom
      const newHeight = window.innerHeight - e.clientY - 48; // Adjustment for margin/padding
      if (newHeight > 40 && newHeight < window.innerHeight * 0.7) {
        setTerminalHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  useEffect(() => {
     if (activeTab === 'code') {
       axios.get(`${API_BASE}/api/code`).then(res => {
         if (res.data.status === 'success') {
           setEditorCode(res.data.code);
           setOriginalCode(res.data.code);
         }
       }).catch(err => console.error(err));
     }
  }, [activeTab]);

  const saveCode = async () => {
     try {
         await axios.post(`${API_BASE}/api/code`, { code: editorCode });
         setOriginalCode(editorCode);
     } catch (err) {
         alert("Failed to save code.");
     }
  };

  const runEditorCode = async () => {
     setIsCodeRunning(true);
     setEditorOutput("Executing...\n");
     try {
         const res = await axios.post(`${API_BASE}/api/run_code`);
         if(res.data.status === 'success' || res.data.status === 'error'){
            setEditorOutput(res.data.output);
         }
     } catch (err) {
         setEditorOutput("Failed to execute code: " + err.message);
     } finally {
         setIsCodeRunning(false);
     }
  };

  const toggleTimelineStep = (id) => {
    const newSet = new Set(expandedTimelineSteps);
    if (newSet.has(id)) { newSet.delete(id); } else { newSet.add(id); }
    setExpandedTimelineSteps(newSet);
  };

  
  const chatEndRef = useRef(null);
  const wsRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle Drag & Drop
  const onDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('dragging');
  };

  const onDragLeave = (e) => {
    e.currentTarget.classList.remove('dragging');
  };

  const onDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragging');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const onFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (selectedFile) => {
    if (!selectedFile.name.endsWith('.csv')) {
      alert('Please upload a valid CSV file.');
      return;
    }
    
    setFile(selectedFile);
    setIsUploading(true);
    setUploadLogs([]);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    const pollInterval = setInterval(async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/upload_progress?filename=${encodeURIComponent(selectedFile.name)}`);
            if (res.data.status === 'success') {
                setUploadLogs(res.data.progress);
            }
        } catch (e) {
            console.error(e);
        }
    }, 200);

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData);
      clearInterval(pollInterval);
      if (res.data.status === 'success') {
        setMarkdownContent(res.data.markdown);
        setActiveTab('markdown');
      } else {
        alert("Error analyzing file: " + res.data.message);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to upload file.");
    } finally {
      setIsUploading(false);
      clearInterval(pollInterval);
    }
  };

  const runAnalysis = () => {
    if (!query.trim()) {
      alert("Please enter a request.");
      return;
    }
    if (!file && !markdownContent) {
      alert("Please upload a CSV file first.");
      return;
    }

    // Reset Chat
    let initialMessages = [{
      id: Date.now(),
      sender: "You",
      content: `**Request configuration:**\n${query}`,
      type: "user"
    }];
    setMessages(initialMessages);
    setIsRunning(true);
    setActiveTab('chat');

    wsRef.current = new WebSocket(`${WS_BASE}/ws/run`);
    
    let currentMessage = null;
    let localMessages = [...initialMessages];

    wsRef.current.onopen = () => {
      wsRef.current.send(query);
    };

    wsRef.current.onmessage = (event) => {
      const line = event.data;
      
      // Check for Agent Header
      const agentMatch = line.match(/^(\w+)\s+\(to\s+(\w+)\):/);
      
      if (agentMatch) {
         // Push current message if exists
         if (currentMessage) {
           localMessages.push({...currentMessage});
         }
         currentMessage = {
            id: Date.now() + Math.random(),
            sender: agentMatch[1],
            receiver: agentMatch[2],
            content: "",
            type: "agent"
         };
         
         setMessages([...localMessages, currentMessage]);
      } else if (line.includes("--------------------------------------------------------------------------------")) {
         // Separator line, ignore
      } else if (line.startsWith("[SYSTEM") || line.startsWith("[INFO") || line.startsWith("[OK") || line.startsWith("[ERROR")) {
         // System message
         if (currentMessage) {
           localMessages.push({...currentMessage});
           currentMessage = null;
         }
         localMessages.push({
           id: Date.now() + Math.random(),
           sender: "System",
           content: line,
           type: "system"
         });
         setMessages([...localMessages]);
         
         if (line.includes("Agent run completed.")) {
             setIsRunning(false);
         }
      } else {
         // Append to current message content
         if (currentMessage) {
            currentMessage.content += line + "\n";
            // Update state without redefining localMessages array fully, for reactivity
            setMessages([...localMessages, currentMessage]);
         } else {
            // Orphan line (startup logs etc)
            localMessages.push({
               id: Date.now() + Math.random(),
               sender: "System",
               content: line,
               type: "system"
            });
            setMessages([...localMessages]);
         }
      }
    };

    wsRef.current.onclose = () => {
      setIsRunning(false);
    };
    
    wsRef.current.onerror = () => {
      setIsRunning(false);
      alert("WebSocket connection error.");
    };
  };

  const getAvatarIcon = (sender) => {
    switch(sender?.toLowerCase()) {
      case 'manager': return <Bot size={20} color="#60a5fa"/>;
      case 'metaagent': return <Database size={20} color="#c084fc"/>;
      case 'coder': return <Terminal size={20} color="#34d399"/>;
      case 'feedbackagent': 
      case 'validator': return <ShieldAlert size={20} color="#f43f5e"/>;
      case 'userproxy':
      case 'you': return <User size={20} color="#a78bfa"/>;
      default: return <Cpu size={20} color="#94a3b8"/>;
    }
  };

  const getAgentHeaderStyle = (sender) => {
    switch(sender?.toLowerCase()) {
      case 'manager': return <div className="chat-header manager-color">Root</div>;
      case 'metaagent': return <div className="chat-header meta-color">MetaAgent</div>;
      case 'coder': return <div className="chat-header coder-color">Coder</div>;
      case 'feedbackagent': 
      case 'validator': return <div className="chat-header validator-color">Validator</div>;
      case 'userproxy': return <div className="chat-header user-color">UserProxy</div>;
      case 'you': return <div className="chat-header user-color">{sender}</div>;
      default: return <div className="chat-header">{sender}</div>;
    }
  };

  // Derived state to identify current active agent and final result
  const finalMessage = messages.find(m => m.content && m.content.includes("RESPONSE :"));
  let finalResultContent = null;
  if (finalMessage) {
    const match = finalMessage.content.match(/RESPONSE\s*:*\s*([\s\S]*)/i);
    if (match) {
        finalResultContent = match[1].trim();
    } else {
        finalResultContent = finalMessage.content.replace("RESPONSE :", "").trim();
    }
  } else if (!isRunning && messages.length > 2) {
    const lastMsg = [...messages].reverse().find(m => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy');
    if (lastMsg) finalResultContent = lastMsg.content;
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>AutoGen CSV Analyst</h1>
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)'}}>
           <span style={{ fontSize: '0.9rem'}}>Powered by AutoGen & Minimax</span>
           <Bot size={20} color="#c084fc"/>
        </div>
      </header>

      <main className="main-content">

        {/* Left Control Panel */}
        <aside className="left-panel">

          <div className="glass-panel" style={{ minHeight: '300px', display: 'flex', flexDirection: 'column' }}>
            {activeTab === 'fileviewer' ? (
              <FileExplorer sidebarMode={true} 
                exploreFiles={exploreFiles} 
                selectedFilePath={selectedFilePath} 
                setSelectedFilePath={setSelectedFilePath}
                setExploreFiles={setExploreFiles}
              />
            ) : (
              <>
                <h2 className="panel-title"><Database size={18}/> Dataset Upload</h2>
                
                <input 
                  type="file" 
                  id="file-upload" 
                  accept=".csv" 
                  style={{ display: 'none' }} 
                  onChange={onFileChange}
                />
                
                <label htmlFor="file-upload" style={{ flex: 1, display: 'flex' }}>
                  <div 
                    className={`upload-zone ${isUploading ? 'uploading' : ''}`}
                    style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
                    onDragOver={onDragOver}
                    onDragLeave={onDragLeave}
                    onDrop={onDrop}
                  >
                    {isUploading ? (
                      <div className="upload-progress-timeline">
                        {uploadLogs.length === 0 ? (
                           <div className="timeline-item active">
                              <div className="timeline-indicator"><div className="pulse"></div></div>
                              <div className="timeline-content">Initializing... Please wait.</div>
                           </div>
                        ) : (
                           uploadLogs.map((log, idx) => (
                             <div key={idx} className={`timeline-item ${idx === uploadLogs.length - 1 ? 'active' : 'completed'}`}>
                                <div className="timeline-indicator">
                                   {idx === uploadLogs.length - 1 ? <div className="pulse"></div> : <CheckCircle2 size={12} color="var(--success)" />}
                                </div>
                                <div className="timeline-content">{log.replace(/\[\d+\/\d+\] /, '')}</div>
                             </div>
                           ))
                        )}
                      </div>
                    ) : (
                      <>
                        <Upload size={32} className="upload-icon" />
                        <div className="upload-text">Drag & drop your CSV here or click to browse</div>
                      </>
                    )}
                  </div>
                </label>

                {file && (
                  <div className="file-info">
                    <CheckCircle2 size={16} />
                    <span>{file.name} successfully analyzed!</span>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="glass-panel" style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
            <h2 className="panel-title"><Terminal size={18}/> Request Configuration</h2>
            <div className="input-group" style={{flex: 1}}>
              <textarea 
                className="chat-input"
                placeholder="E.g., Which channel has the maximum actuals?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button 
                className="btn-primary" 
                onClick={runAnalysis}
                disabled={!file || !markdownContent || isUploading || isRunning}
              >
                {isRunning ? (
                   <>Running Analysis <div className="spinner"></div></>
                ) : (
                   <><Play size={18}/> Trigger Function</>
                )}
              </button>
            </div>
          </div>
        </aside>

        {/* Right Dashboard Area */}
        <section className="glass-panel right-panel">
            <div className="tabs">
              <button 
                 className={`tab-btn ${activeTab === 'markdown' ? 'active' : ''}`}
                 onClick={() => setActiveTab('markdown')}
              >
                <FileText size={16} style={{display:'inline', verticalAlign:'middle', marginRight:'6px'}}/>
                Dataset Metadata
              </button>
              <button 
                 className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
                 onClick={() => setActiveTab('chat')}
              >
                <Bot size={16} style={{display:'inline', verticalAlign:'middle', marginRight:'6px'}}/>
                Agent Conversation
              </button>
              <button 
                 className={`tab-btn ${activeTab === 'code' ? 'active' : ''}`}
                 onClick={() => setActiveTab('code')}
              >
                <Code size={16} style={{display:'inline', verticalAlign:'middle', marginRight:'6px'}}/>
                Editor {editorCode !== originalCode ? <span style={{color: 'var(--danger)', marginLeft: '4px'}}>•</span> : ''}
              </button>
              <button 
                 className={`tab-btn ${activeTab === 'fileviewer' ? 'active' : ''}`}
                 onClick={() => setActiveTab('fileviewer')}
              >
                <Folder size={16} style={{display:'inline', verticalAlign:'middle', marginRight:'6px'}}/>
                File Viewer
              </button>
           </div>
           
           <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column'}}>
               {activeTab === 'markdown' ? (
                   <div className="md-content">
                     {markdownContent ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownContent}</ReactMarkdown>
                     ) : (
                        <div className="sheets-empty" style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '40px'}}>
                           <Database size={56} style={{ opacity: 0.15 }} />
                           <h3 style={{margin: 0, color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.15rem'}}>No Dataset Loaded</h3>
                           <p style={{margin: 0, color: 'var(--text-secondary)', fontSize: '0.95rem', textAlign: 'center', maxWidth: '360px', lineHeight: 1.6}}>
                             Upload a CSV file using the panel on the left to automatically generate dataset metadata — column types, statistics, and a full summary.
                           </p>
                           <div style={{marginTop: '8px', padding: '10px 20px', borderRadius: '10px', background: 'rgba(192, 132, 252, 0.08)', border: '1px solid rgba(192, 132, 252, 0.2)', color: '#c084fc', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px'}}>
                             <Upload size={14} /> Drag & drop a .csv file to get started
                           </div>
                        </div>
                     )}
                   </div>
               ) : activeTab === 'code' ? (
                   <div style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
                      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '16px'}}>
                          <div style={{display: 'flex', gap: '8px', color: 'var(--text-secondary)', alignItems: 'center'}}>
                             <Terminal size={16}/> <span>generated_code/main.py</span>
                             {editorCode !== originalCode && <span style={{color: 'var(--danger)', fontSize: '0.85em', fontWeight: 'bold'}}>(Unsaved changes)</span>}
                          </div>
                          <div style={{display: 'flex', gap: '12px'}}>
                              <button className="btn-secondary" style={{padding: '6px 12px', fontSize: '0.9rem', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: 'white', borderRadius: '8px', cursor: editorCode === originalCode ? 'not-allowed' : 'pointer'}} onClick={saveCode} disabled={editorCode === originalCode}>
                                 <Save size={14} style={{display: 'inline', marginRight: '4px'}}/> Save
                              </button>
                              <button className="btn-primary" style={{padding: '6px 12px', fontSize: '0.9rem'}} onClick={runEditorCode} disabled={isCodeRunning}>
                                 <Play size={14} style={{display: 'inline', marginRight: '4px'}}/> {isCodeRunning ? 'Running...' : 'Run Code'}
                              </button>
                          </div>
                      </div>
                      <div style={{flex: 1, border: '1px solid var(--glass-border)', borderRadius: '8px', overflow: 'hidden'}}>
                         <Editor
                           height="100%"
                           defaultLanguage="python"
                           theme="vs-dark"
                           value={editorCode}
                           onChange={(value) => setEditorCode(value)}
                           options={{ minimap: { enabled: false }, fontSize: 14 }}
                         />
                      </div>
                      {editorOutput && (
                         <div 
                           className={`execution-terminal ${isTerminalMinimized ? 'minimized' : ''}`}
                           style={{ height: isTerminalMinimized ? '40px' : `${terminalHeight}px` }}
                         >
                            <div className="terminal-resize-handle" onMouseDown={() => setIsResizing(true)} />
                            
                            <div className="terminal-header">
                               <div className="terminal-title">
                                  <Terminal size={14} />
                                  <span>Execution Output</span>
                               </div>
                               <div className="terminal-controls">
                                  <button 
                                    className="terminal-btn" 
                                    onClick={() => setIsTerminalMinimized(!isTerminalMinimized)}
                                    title={isTerminalMinimized ? "Maximize" : "Minimize"}
                                  >
                                     {isTerminalMinimized ? <Square size={12} /> : <Minus size={12} />}
                                  </button>
                                  <button 
                                    className="terminal-btn close" 
                                    onClick={() => setEditorOutput("")}
                                    title="Close"
                                  >
                                     <X size={12} />
                                  </button>
                               </div>
                            </div>

                            <div className="terminal-body">
                               {editorOutput}
                            </div>
                         </div>
                      )}
                   </div>
               ) : activeTab === 'chat' ? (
                   <div className="chat-container">
                        {isRunning && (
                            <div className="agent-typing">
                                <div className="spinner-border" style={{width: '16px', height: '16px', borderWidth: '0.15em'}}></div>
                                <span>Agent ecosystem is processing...</span>
                            </div>
                        )}
                        {/* Always display the initial user prompt if available */}
                        {messages.filter(m => m.type === 'user').map(msg => (
                             <div key={msg.id} className="message-row user" style={{marginBottom: '20px'}}>
                                 <div className="avatar">{getAvatarIcon(msg.sender)}</div>
                                 <div className="chat-bubble user-msg" style={{fontSize: '0.95rem', color: '#e2e8f0'}}>
                                     <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                                 </div>
                             </div>
                        ))}

                        
                        {/* Expandable Step-by-Step Agent Timeline */}
                        {!finalResultContent && messages.filter(m => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy').length > 0 && (
                            <div className="agent-timeline">
                                {messages.filter(m => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy').map((msg, idx) => {
                            const isExpanded = expandedTimelineSteps.has(msg.id);
                            const isLast = idx === messages.filter(m => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy').length - 1;
                            const displayName = msg.sender?.toLowerCase() === 'manager' ? 'Root' : msg.sender;
                            
                            return (
                                <div key={msg.id} className="timeline-step">
                                    <div className="timeline-header" onClick={() => toggleTimelineStep(msg.id)}>
                                        <div className="timeline-header-left">
                                            {getAvatarIcon(msg.sender)}
                                            <span style={{color: 'var(--text-primary)'}}>{displayName}</span>
                                            {msg.receiver && (
                                                <span style={{color: 'var(--text-secondary)', fontSize: '0.85em'}}>
                                                    → {msg.receiver?.toLowerCase() === 'manager' ? 'Root' : msg.receiver}
                                                </span>
                                            )}
                                        </div>
                                        <ChevronDown size={20} className={`chevron ${isExpanded ? 'open' : ''}`} />
                                    </div>
                                    
                                    {isExpanded && (
                                        <div className="timeline-body md-content">
                                            <ReactMarkdown 
                                                remarkPlugins={[remarkGfm]}
                                                components={{
                                                code({inline, className, children, ...props}) {
                                                        const match = /language-(\w+)/.exec(className || '')
                                                        return !inline && match ? (
                                                            <SyntaxHighlighter
                                                                children={String(children).replace(/\n$/, '')}
                                                                style={vscDarkPlus}
                                                                language={match[1]}
                                                                PreTag="div"
                                                                {...props}
                                                            />
                                                        ) : (
                                                            <code className={className} {...props}>
                                                                {children}
                                                            </code>
                                                        )
                                                    }
                                                }}
                                            >
                                                {msg.content.replace(/Code output:[\s\n]*\|/g, "Code output:\n\n|")}
                                            </ReactMarkdown>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                        </div>
                        )}
                        
                        {finalResultContent && (
                            (() => {
                                let reqStr = "";
                                let resStr = finalResultContent;
                                const reqMatch = finalResultContent.match(/REQUEST\s*:\s*(.*?)(?=\s*RESPONSE\s*:|$)/s);
                                const resMatch = finalResultContent.match(/RESPONSE\s*:\s*(.*)/s);
                                if (reqMatch) reqStr = reqMatch[1];
                                if (resMatch) resStr = resMatch[1];
                                
                                return (
                                    <div className="final-result-card" style={{border: '1px solid var(--primary-dark)', background: 'rgba(30, 41, 59, 0.5)'}}>
                                        <div style={{display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '20px'}}>
                                            <div className="avatar user" style={{width: '48px', height: '48px', fontSize: '1.4rem', flexShrink: 0, background: 'var(--primary)'}}>
                                                {getAvatarIcon("Manager")}
                                            </div>
                                            <div>
                                                <h3 style={{margin: 0, fontSize: '1.4rem'}}><CheckCircle2 size={24} style={{color: 'var(--success)', verticalAlign: 'middle', marginRight: '8px', marginTop: '-3px'}} /> Expert Analysis Complete</h3>
                                                <div style={{color: 'var(--text-secondary)', fontSize: '0.95rem', marginTop: '6px'}}>Synthesized by Root Manager</div>
                                            </div>
                                        </div>

                                        {reqStr && (
                                            <div style={{background: 'rgba(0,0,0,0.2)', padding: '20px', borderRadius: '8px', marginBottom: '24px', borderLeft: '4px solid var(--primary)'}}>
                                                <strong style={{color: 'var(--text-secondary)', display: 'block', marginBottom: '12px', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px'}}>Target Objective</strong>
                                                <div style={{fontSize: '1.05rem', fontStyle: 'italic', fontWeight: 500, color: 'var(--text-primary)'}}>{reqStr.trim()}</div>
                                            </div>
                                        )}
                                        
                                        <div className="md-content final-markdown" style={{fontSize: '1.1rem', lineHeight: '1.7', color: 'var(--text-primary)'}}>
                                            <ReactMarkdown 
                                                remarkPlugins={[remarkGfm]}
                                                components={{
                                                    code({inline, className, children, ...props}) {
                                                        const match = /language-(\w+)/.exec(className || '')
                                                        return !inline && match ? (
                                                            <SyntaxHighlighter
                                                                children={String(children).replace(/\n$/, '')}
                                                                style={vscDarkPlus}
                                                                language={match[1]}
                                                                PreTag="div"
                                                                {...props}
                                                            />
                                                        ) : (
                                                            <code className={className} {...props}>
                                                                {children}
                                                            </code>
                                                        )
                                                    }
                                                }}
                                            >
                                                {resStr.trim()}
                                            </ReactMarkdown>
                                        </div>
                                        <button className="btn-primary" style={{marginTop: '32px', gap: '8px', padding: '12px 24px', height: 'auto', background: 'transparent', color: 'var(--primary)', border: '2px solid var(--primary-dark)', transition: 'all 0.2s'}} 
                                                onMouseOver={(e) => { e.currentTarget.style.background = 'var(--primary-dark)'; e.currentTarget.style.color = '#fff'; }}
                                                onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--primary)'; }}
                                                onClick={() => setShowFullLog(true)}>
                                            <Cpu size={18} /> Explore Core Reasoning
                                        </button>
                                    </div>
                                );
                            })()
                        )}

                        {!isRunning && !finalResultContent && messages.length === 0 && (
                            <div style={{color: 'var(--text-secondary)', textAlign: 'center', marginTop: '40px'}}>
                               Agent terminal is awaiting execution...
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>
               ) : activeTab === 'fileviewer' ? (
                   <FileViewer 
                                                      selectedFilePath={selectedFilePath}
                      setSelectedFilePath={setSelectedFilePath}
                      sheetData={sheetData}
                      setSheetData={setSheetData}
                      sheetLoading={sheetLoading}
                      setSheetLoading={setSheetLoading}
                      sheetFilters={sheetFilters}
                      setSheetFilters={setSheetFilters}
                      sheetSort={sheetSort}
                      setSheetSort={setSheetSort}
                      sheetLimit={sheetLimit}
                      setSheetLimit={setSheetLimit}
                   />
               ) : null}
           </div>

            {/* Right Side Drawer for Full Trace */}
            {showFullLog && (
                <div className="drawer-overlay" onClick={() => setShowFullLog(false)}>
                    <div className="drawer-panel" onClick={e => e.stopPropagation()}>
                        <div className="drawer-header">
                            <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                <Cpu size={20} className="primary-color" /> Raw Agent Trace
                            </div>
                            <button className="close-btn" onClick={() => setShowFullLog(false)} aria-label="Close">✕</button>
                        </div>
                        <div className="drawer-body">
                            <div className="drawer-body-inner">
                            {messages.map((msg) => {
                               if (msg.sender?.toLowerCase() === 'userproxy') return null;
                               
                               if (msg.type === 'system') {
                                   return (
                                       <div key={msg.id} className="chat-bubble system">
                                           <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                                       </div>
                                   );
                               }
                               const isUser = msg.type === 'user';
                               return (
                                   <div key={msg.id} className={`message-row ${isUser ? 'user' : ''}`}>
                                       <div className="avatar">
                                           {getAvatarIcon(msg.sender)}
                                       </div>
                                       <div className={`chat-bubble ${isUser ? 'user-msg' : 'agent'}`}>
                                           {getAgentHeaderStyle(msg.sender)}
                                           {msg.type === 'agent' && msg.receiver && (
                                               <span style={{fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px', display: 'block'}}>
                                                  to {msg.receiver}
                                               </span>
                                           )}
                                           <ReactMarkdown 
                                              remarkPlugins={[remarkGfm]}
                                              components={{
                                                code({inline, className, children, ...props}) {
                                                  const match = /language-(\w+)/.exec(className || '')
                                                  return !inline && match ? (
                                                    <SyntaxHighlighter
                                                      children={String(children).replace(/\n$/, '')}
                                                      style={vscDarkPlus}
                                                      language={match[1]}
                                                      PreTag="div"
                                                      {...props}
                                                    />
                                                  ) : (
                                                    <code className={className} {...props}>
                                                      {children}
                                                    </code>
                                                  )
                                                }
                                              }}
                                           >
                                               {msg.content.replace(/Code output:[\s\n]*\|/g, "Code output:\n\n|")}
                                           </ReactMarkdown>
                                       </div>
                                   </div>
                               );
                           })}
                           </div>
                        </div>
                    </div>
                </div>
            )}

        </section>
      </main>
    </div>
  );
}

export default App;
