import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import rehypeRaw from 'rehype-raw';
import { Editor } from '@monaco-editor/react';
import {
  Upload, Play, FileText, Terminal, Bot, User, Cpu, Database,
  ShieldAlert, CheckCircle2, ChevronDown, Code, Save, Minus,
  Square, X, Folder, MessageSquare, Pencil, Trash2
} from 'lucide-react';
import FileExplorer from './components/FileExplorer';
import FileViewer from './components/FileViewer';
import './index.css';

const API_BASE = "http://localhost:8000";
const WS_BASE  = "ws://localhost:8000";

// ─── Noise patterns to filter from the WebSocket stream ───────────────────────
const NOISY_PATTERNS = [
  /TERMINATING RUN/,
  /No next speaker selected/,
  /Select speaker attempt/,
  /is_termination_msg/,
  /NEXT SPEAKER:/,
  /return None/,
  /^>{4,}/,
  /^<{4,}/,
];

const isNoisyLine = (line) =>
  !line.trim() || NOISY_PATTERNS.some((re) => re.test(line));

// ─── Plan Review Modal ────────────────────────────────────────────────────────
const PlanReviewModal = ({ planContent, setPlanContent, onApprove, onReject }) => {
  const [selection, setSelection] = useState(null);
  const [comment, setComment] = useState("");
  const [isAddingComment, setIsAddingComment] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const containerRef = useRef(null);

  // Auto-fetch plan if content is empty when modal mounts
  useEffect(() => {
    if (planContent) return;
    let cancelled = false;
    const fetchPlan = () => {
      axios.get(`${API_BASE}/api/plan`).then((res) => {
        if (!cancelled && res.data.status === 'success' && res.data.content) {
          setPlanContent(res.data.content);
        }
      }).catch(console.error);
    };
    fetchPlan();
    const interval = setInterval(fetchPlan, 2000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [planContent, setPlanContent]);

  const annotations = useMemo(() => {
    if (!planContent) return [];
    const annRegex = /<!-- ANN:(\{.*?\}) -->/g;
    const matches = [];
    let match;
    while ((match = annRegex.exec(planContent)) !== null) {
      try {
        matches.push(JSON.parse(match[1]));
      } catch (e) {
        console.error("Annotation Parse error", e);
      }
    }
    return matches;
  }, [planContent]);

  const handleMouseUp = () => {
    const sel = window.getSelection();
    const text = sel.toString().trim();
    if (text && text.length > 2) {
      const range = sel.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelection({
        text,
        x: rect.left + rect.width / 2,
        y: rect.top,
      });
    } else {
      if (!isAddingComment) setSelection(null);
    }
  };

  const saveUpdatedPlan = async (newContent) => {
    try {
      await axios.post(`${API_BASE}/api/plan`, { code: newContent });
      setPlanContent(newContent);
    } catch (err) {
      console.error("Failed to save plan:", err);
    }
  };

  const submitComment = () => {
    if (!comment.trim() || !selection) return;
    
    if (editingId) {
      // Logic for editing existing comment
      const ann = annotations.find(a => a.id === editingId);
      if (ann) {
        const oldTag = `<!-- ANN:${JSON.stringify(ann)} -->`;
        const newAnn = { ...ann, text: comment.trim(), comment: comment.trim() };
        const newTag = `<!-- ANN:${JSON.stringify(newAnn)} -->`;
        
        // Replace the previously annotated text with the new comment
        const index = planContent.indexOf(ann.text);
        if (index !== -1) {
          const updated = planContent.slice(0, index) + 
                          comment.trim() + 
                          planContent.slice(index + ann.text.length);
          saveUpdatedPlan(updated.replace(oldTag, newTag));
        } else {
          saveUpdatedPlan(planContent.replace(oldTag, newTag));
        }
      }
    } else {
      // Logic for adding new comment: Replace selection with the comment text
      const newAnn = { id: Date.now().toString(), text: comment.trim(), comment: comment.trim() };
      const commentTag = `<!-- ANN:${JSON.stringify(newAnn)} -->`;
      const index = planContent.indexOf(selection.text);
      if (index !== -1) {
        const updated = planContent.slice(0, index) + 
                        comment.trim() + 
                        " " + commentTag + 
                        planContent.slice(index + selection.text.length);
        saveUpdatedPlan(updated);
      }
    }
    
    setComment("");
    setSelection(null);
    setIsAddingComment(false);
    setEditingId(null);
  };

  const deleteAnnotation = (id) => {
    const ann = annotations.find(a => a.id === id);
    if (ann) {
      const tag = `<!-- ANN:${JSON.stringify(ann)} -->`;
      saveUpdatedPlan(planContent.replace(tag, ""));
    }
  };

  const openEdit = (ann) => {
    setComment(ann.comment);
    setEditingId(ann.id);
    setIsAddingComment(true);
    setSelection({ text: ann.text, x: window.innerWidth / 2, y: window.innerHeight / 2 });
  };

  const highlightedContent = useMemo(() => {
    if (!planContent) return "";
    try {
      let content = planContent;
      // We sort by length descending to avoid nested partial matches
      const sortedAnns = [...annotations].sort((a, b) => b.text.length - a.text.length);
      
      sortedAnns.forEach(ann => {
        if (!ann.text) return;
        // Escape special regex chars
        const escaped = ann.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        // Use a more robust regex to identify the text outside of other tags
        const regex = new RegExp(`(${escaped})(?![^<]*>)`, 'g');
        content = content.replace(regex, `<mark class="plan-highlight" data-id="${ann.id}">$1</mark>`);
      });
      return content;
    } catch (e) {
      console.error("Highlighting engine error:", e);
      return planContent; // Fallback to raw content if highlighting fails
    }
  }, [planContent, annotations]);

  return (
    <div className="modal-backdrop">
      <div className="modal-panel" onMouseUp={handleMouseUp}>
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div className="modal-header-icon">
                <Cpu size={24} color="#fff" />
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>
                  Plan Annotation Studio
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                  <span className="status-badge" style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>Advanced Review</span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {annotations.length} Annotations active • Highlighting enabled
                  </span>
                </div>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="modal-btn modal-btn-reject" onClick={onReject}>
                <X size={18} /> Exit Chat
              </button>
              <button className="modal-btn modal-btn-approve" onClick={onApprove}>
                <CheckCircle2 size={18} /> Approve &amp; Execute
              </button>
            </div>
          </div>
        </div>

        {/* Studio Layout */}
        <div className="modal-body studio-layout">
          {/* Left Sidebar: Comments */}
          <div className="studio-sidebar">
            <div className="sidebar-header">
              <MessageSquare size={14} /> <span>ANNOTATIONS</span>
            </div>
            <div className="sidebar-list">
              {annotations.length === 0 ? (
                <div className="sidebar-empty">
                  No annotations yet. Highlight text in the plan to add your feedback.
                </div>
              ) : (
                annotations.map((ann) => (
                  <div key={ann.id} className="ann-card">
                    <div className="ann-text">"{ann.text}"</div>
                    <div className="ann-comment">{ann.comment}</div>
                    <div className="ann-actions">
                      <button onClick={() => openEdit(ann)} title="Edit"><Pencil size={12} /></button>
                      <button onClick={() => deleteAnnotation(ann.id)} title="Delete" className="delete"><Trash2 size={12} /></button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Main Content: Markdown */}
          <div className="studio-content">
            {!planContent ? (
              <div className="modal-loading">
                <div className="spinner-border" style={{ width: '28px', height: '28px', borderWidth: '0.25em', marginRight: '16px', color: 'var(--primary)' }} />
                <span>Preparing plan...</span>
              </div>
            ) : (
              <div className="annotation-container markdown-body md-content" ref={containerRef}>
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]} 
                  rehypePlugins={[rehypeRaw]}
                  components={MD_COMPONENTS}
                >
                  {highlightedContent}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>

        {/* Floating Tooltip */}
        {selection && !isAddingComment && (
          <button 
            className="floating-comment-trigger"
            style={{ left: selection.x, top: selection.y - 10 }}
            onClick={(e) => { e.stopPropagation(); setIsAddingComment(true); }}
          >
            <MessageSquare size={16} /> Add Comment
          </button>
        )}

        {/* Comment Input Popover */}
        {isAddingComment && (
          <div 
            className="comment-input-popover"
            style={{ left: selection.x, top: selection.y - 10 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '8px', fontStyle: 'italic' }}>
              Annotating: "{selection.text.substring(0, 40)}{selection.text.length > 40 ? '...' : ''}"
            </div>
            <textarea 
              autoFocus
              placeholder="What specifically should change here?"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitComment(); } }}
            />
            <div className="popover-actions">
              <button onClick={() => { setIsAddingComment(false); setEditingId(null); setComment(""); }}>Cancel</button>
              <button className="primary" onClick={submitComment}>Proceed</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ─── Code syntax renderer (reused) ────────────────────────────────────────────
const CodeBlock = ({ inline, className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '');
  return !inline && match ? (
    <SyntaxHighlighter
      children={String(children).replace(/\n$/, '')}
      style={vscDarkPlus}
      language={match[1]}
      PreTag="div"
      {...props}
    />
  ) : (
    <code className={className} {...props}>{children}</code>
  );
};

const MD_COMPONENTS = { code: CodeBlock };

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [file, setFile]               = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadLogs, setUploadLogs]   = useState([]);
  const [markdownContent, setMarkdownContent] = useState('');
  const [query, setQuery]             = useState('');
  const [isRunning, setIsRunning]     = useState(false);

  // Chat
  const [messages, setMessages]     = useState([]);
  const [activeTab, setActiveTab]   = useState('chat');
  const [showFullLog, setShowFullLog] = useState(false);
  const [expandedTimelineSteps, setExpandedTimelineSteps] = useState(new Set());

  // Plan review
  const [planContent, setPlanContent]   = useState('');
  const [showPlanModal, setShowPlanModal] = useState(false);

  // Code editor
  const [editorCode, setEditorCode]       = useState('');
  const [originalCode, setOriginalCode]   = useState('');
  const [editorOutput, setEditorOutput]   = useState('');
  const [isCodeRunning, setIsCodeRunning] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(240);
  const [isTerminalMinimized, setIsTerminalMinimized] = useState(false);
  const [isResizing, setIsResizing] = useState(false);

  // File Viewer
  const [exploreFiles, setExploreFiles]     = useState([]);
  const [selectedFilePath, setSelectedFilePath] = useState('');
  const [sheetData, setSheetData]           = useState(null);
  const [sheetLoading, setSheetLoading]     = useState(false);
  const [sheetFilters, setSheetFilters]     = useState({ col: '', vals: [] });
  const [sheetSort, setSheetSort]           = useState({ col: '', asc: true });
  const [sheetLimit, setSheetLimit]         = useState({ type: 'top', n: 50 });

  const chatEndRef = useRef(null);
  const wsRef      = useRef(null);

  // ── Terminal resize ──────────────────────────────────────────────────────
  useEffect(() => {
    const onMove = (e) => {
      if (!isResizing) return;
      const newH = window.innerHeight - e.clientY - 48;
      if (newH > 40 && newH < window.innerHeight * 0.7) setTerminalHeight(newH);
    };
    const onUp = () => setIsResizing(false);
    if (isResizing) {
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    }
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [isResizing]);

  // ── Load code when editor tab opens ─────────────────────────────────────
  useEffect(() => {
    if (activeTab !== 'code') return;
    axios.get(`${API_BASE}/api/code`).then((res) => {
      if (res.data.status === 'success') {
        setEditorCode(res.data.code);
        setOriginalCode(res.data.code);
      }
    }).catch(console.error);
  }, [activeTab]);

  // ── Auto-scroll on new messages ──────────────────────────────────────────
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ── Helpers ──────────────────────────────────────────────────────────────
  const saveCode = async () => {
    try {
      await axios.post(`${API_BASE}/api/code`, { code: editorCode });
      setOriginalCode(editorCode);
    } catch { alert('Failed to save code.'); }
  };

  const runEditorCode = async () => {
    setIsCodeRunning(true);
    setEditorOutput('Executing…\n');
    try {
      const res = await axios.post(`${API_BASE}/api/run_code`);
      if (res.data.status === 'success' || res.data.status === 'error') {
        setEditorOutput(res.data.output);
      }
    } catch (err) {
      setEditorOutput('Failed to execute: ' + err.message);
    } finally {
      setIsCodeRunning(false);
    }
  };

  const toggleTimelineStep = useCallback((id) => {
    setExpandedTimelineSteps((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  // ── Drag & Drop ──────────────────────────────────────────────────────────
  const onDragOver  = (e) => { e.preventDefault(); e.currentTarget.classList.add('dragging'); };
  const onDragLeave = (e) => { e.currentTarget.classList.remove('dragging'); };
  const onDrop      = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragging');
    if (e.dataTransfer.files?.[0]) handleFileUpload(e.dataTransfer.files[0]);
  };
  const onFileChange = (e) => { if (e.target.files?.[0]) handleFileUpload(e.target.files[0]); };

  const handleFileUpload = async (selectedFile) => {
    if (!selectedFile.name.endsWith('.csv')) { alert('Please upload a valid CSV file.'); return; }
    setFile(selectedFile);
    setIsUploading(true);
    setUploadLogs([]);

    const formData = new FormData();
    formData.append('file', selectedFile);

    const poll = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/upload_progress?filename=${encodeURIComponent(selectedFile.name)}`);
        if (res.data.status === 'success') setUploadLogs(res.data.progress);
      } catch (e) { console.error(e); }
    }, 200);

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData);
      clearInterval(poll);
      if (res.data.status === 'success') {
        setMarkdownContent(res.data.markdown);
        setActiveTab('markdown');
      } else { alert('Error analyzing file: ' + res.data.message); }
    } catch (err) {
      console.error(err);
      alert('Failed to upload file.');
    } finally {
      setIsUploading(false);
      clearInterval(poll);
    }
  };

  // ── WebSocket / run analysis ─────────────────────────────────────────────
  const runAnalysis = () => {
    if (!query.trim())              { alert('Please enter a request.'); return; }
    if (!file && !markdownContent)  { alert('Please upload a CSV file first.'); return; }

    const initial = [{
      id: Date.now(),
      sender: 'You',
      content: `**Request configuration:**\n${query}`,
      type: 'user',
    }];
    setMessages(initial);
    setIsRunning(true);
    setActiveTab('chat');

    wsRef.current = new WebSocket(`${WS_BASE}/ws/run`);
    let currentMessage = null;
    let localMessages  = [...initial];

    wsRef.current.onopen = () => wsRef.current.send(query);

    wsRef.current.onmessage = (event) => {
      const line = event.data;

      // ── Silence noisy AutoGen internal lines ────────────────────────────
      if (isNoisyLine(line)) return;

      // ── Separator ───────────────────────────────────────────────────────
      if (line.includes('---')) return;

      // ── Agent header ────────────────────────────────────────────────────
      const agentMatch = line.match(/^(\w+)\s+\(to\s+(\w+)\):/);
      if (agentMatch) {
        if (currentMessage) localMessages.push({ ...currentMessage });
        currentMessage = {
          id: Date.now() + Math.random(),
          sender: agentMatch[1],
          receiver: agentMatch[2],
          content: '',
          type: 'agent',
        };
        setMessages([...localMessages, currentMessage]);
        return;
      }

      // ── Plan verification trigger ────────────────────────────────────────
      if (line.includes('[ACTION_REQUIRED: VERIFY PLAN]')) {
        if (currentMessage) { localMessages.push({ ...currentMessage }); currentMessage = null; }
        localMessages.push({
          id: Date.now() + Math.random(),
          sender: 'System',
          content: 'Action Required: Verify the implementation plan.',
          type: 'action',
          actionType: 'verify_plan',
          resolved: false,
        });
        setMessages([...localMessages]);
        setShowPlanModal(true);

        // Fetch plan and navigate to plan tab
        axios.get(`${API_BASE}/api/plan`).then((res) => {
          if (res.data.status === 'success') {
            setPlanContent(res.data.content);
            setActiveTab('plan');
          }
        }).catch((err) => console.error('Error fetching plan', err));
        return;
      }

      // ── System / status messages ─────────────────────────────────────────
      if (line.startsWith('[SYSTEM') || line.startsWith('[INFO') ||
          line.startsWith('[OK')     || line.startsWith('[ERROR')) {
        if (currentMessage) { localMessages.push({ ...currentMessage }); currentMessage = null; }
        localMessages.push({ id: Date.now() + Math.random(), sender: 'System', content: line, type: 'system' });
        setMessages([...localMessages]);
        if (line.includes('Agent run completed.')) setIsRunning(false);
        return;
      }

      // ── Regular content lines ────────────────────────────────────────────
      if (currentMessage) {
        currentMessage.content += line + '\n';
        setMessages([...localMessages, currentMessage]);
      } else {
        localMessages.push({ id: Date.now() + Math.random(), sender: 'System', content: line, type: 'system' });
        setMessages([...localMessages]);
      }
    };

    wsRef.current.onclose = () => setIsRunning(false);
    wsRef.current.onerror = () => { setIsRunning(false); alert('WebSocket connection error.'); };
  };

  // ── Plan actions ───────────────────────────────────────────────────
  const resolvePlanAction = (answer) => {
    setShowPlanModal(false);
    setActiveTab('chat');
    wsRef.current?.send(answer);
  };

  const handleApprovePlan = async () => {
    try { await axios.post(`${API_BASE}/api/plan`, { code: planContent }); }
    catch (e) { console.error('Failed to save plan', e); }
    resolvePlanAction('yes');
  };

  const handleRejectPlan = () => {
    setShowPlanModal(false);
    setMessages([]);
    setIsRunning(false);
    setActiveTab('markdown');
    if (wsRef.current) {
      wsRef.current.send('no');
      wsRef.current.close();
    }
  };

  // ── Avatar / style helpers ───────────────────────────────────────────────
  const getAvatarIcon = (sender) => {
    switch (sender?.toLowerCase()) {
      case 'manager':      return <Bot size={20} color="#60a5fa" />;
      case 'metaagent':    return <Database size={20} color="#c084fc" />;
      case 'coder':        return <Terminal size={20} color="#34d399" />;
      case 'feedbackagent':
      case 'validator':    return <ShieldAlert size={20} color="#f43f5e" />;
      case 'userproxy':
      case 'you':          return <User size={20} color="#a78bfa" />;
      default:             return <Cpu size={20} color="#94a3b8" />;
    }
  };

  const getAgentHeaderStyle = (sender) => {
    const map = {
      manager:      ['chat-header manager-color', 'Root'],
      metaagent:    ['chat-header meta-color', 'MetaAgent'],
      coder:        ['chat-header coder-color', 'Coder'],
      feedbackagent:['chat-header validator-color', 'Validator'],
      validator:    ['chat-header validator-color', 'Validator'],
      userproxy:    ['chat-header user-color', 'UserProxy'],
      you:          ['chat-header user-color', sender],
    };
    const [cls, label] = map[sender?.toLowerCase()] ?? ['chat-header', sender];
    return <div className={cls}>{label}</div>;
  };

  // ── Derived: final result ────────────────────────────────────────────────
  const finalMessage = messages.find((m) => m.content?.includes('RESPONSE :'));
  let finalResultContent = null;
  if (finalMessage) {
    const match = finalMessage.content.match(/RESPONSE\s*:*\s*([\s\S]*)/i);
    finalResultContent = match ? match[1].trim() : finalMessage.content.replace('RESPONSE :', '').trim();
  } else if (!isRunning && messages.length > 2) {
    const last = [...messages].reverse().find((m) => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy');
    if (last) finalResultContent = last.content;
  }

  const agentMessages = messages.filter(
    (m) => m.type === 'agent' && m.sender?.toLowerCase() !== 'userproxy' && m.sender !== 'System'
  );

  // ────────────────────────────────────────────────────────────────────────────

  return (
    <div className="app-container">
      <header className="header">
        <h1>AutoGen CSV Analyst</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
          <span style={{ fontSize: '0.9rem' }}>Powered by AutoGen &amp; Minimax</span>
          <Bot size={20} color="#c084fc" />
        </div>
      </header>

      <main className="main-content">

        {/* Left Panel */}
        <aside className="left-panel">
          <div className="glass-panel" style={{ minHeight: '300px', display: 'flex', flexDirection: 'column' }}>
            {activeTab === 'fileviewer' ? (
              <FileExplorer
                exploreFiles={exploreFiles}
                selectedFilePath={selectedFilePath}
                setSelectedFilePath={setSelectedFilePath}
                setExploreFiles={setExploreFiles}
              />
            ) : (
              <>
                <h2 className="panel-title"><Database size={18} /> Dataset Upload</h2>
                <input type="file" id="file-upload" accept=".csv" style={{ display: 'none' }} onChange={onFileChange} />
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
                            <div className="timeline-indicator"><div className="pulse" /></div>
                            <div className="timeline-content">Initializing… Please wait.</div>
                          </div>
                        ) : (
                          uploadLogs.map((log, idx) => (
                            <div key={idx} className={`timeline-item ${idx === uploadLogs.length - 1 ? 'active' : 'completed'}`}>
                              <div className="timeline-indicator">
                                {idx === uploadLogs.length - 1
                                  ? <div className="pulse" />
                                  : <CheckCircle2 size={12} color="var(--success)" />}
                              </div>
                              <div className="timeline-content">{log.replace(/\[\d+\/\d+\] /, '')}</div>
                            </div>
                          ))
                        )}
                      </div>
                    ) : (
                      <>
                        <Upload size={32} className="upload-icon" />
                        <div className="upload-text">Drag &amp; drop your CSV here or click to browse</div>
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

          <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <h2 className="panel-title"><Terminal size={18} /> Request Configuration</h2>
            <div className="input-group" style={{ flex: 1 }}>
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
                {isRunning
                  ? <><span>Running Analysis</span> <div className="spinner" /></>
                  : <><Play size={18} /> Trigger Function</>}
              </button>
            </div>
          </div>
        </aside>

        {/* Right Panel */}
        <section className="glass-panel right-panel">
          {/* Tabs */}
          <div className="tabs">
            {[
              { key: 'markdown',   icon: <FileText size={16} />,  label: 'Dataset Metadata' },
              { key: 'chat',       icon: <Bot size={16} />,       label: 'Agent Conversation' },
              { key: 'code',       icon: <Code size={16} />,      label: `Editor${editorCode !== originalCode ? ' •' : ''}` },
              { key: 'fileviewer', icon: <Folder size={16} />,    label: 'File Viewer' },
            ].map(({ key, icon, label }) => (
              <button
                key={key}
                className={`tab-btn ${activeTab === key ? 'active' : ''}`}
                onClick={() => setActiveTab(key)}
              >
                {icon} {label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>

            {/* ── Dataset Metadata ── */}
            {activeTab === 'markdown' && (
              <div className="md-content">
                {markdownContent ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownContent}</ReactMarkdown>
                ) : (
                  <div className="sheets-empty" style={{ flex: 1, flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '40px' }}>
                    <Database size={56} style={{ opacity: 0.15 }} />
                    <h3 style={{ margin: 0, color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.15rem' }}>No Dataset Loaded</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.95rem', textAlign: 'center', maxWidth: '360px', lineHeight: 1.6 }}>
                      Upload a CSV file using the panel on the left to automatically generate dataset metadata.
                    </p>
                    <div style={{ marginTop: '8px', padding: '10px 20px', borderRadius: '10px', background: 'rgba(192, 132, 252, 0.08)', border: '1px solid rgba(192, 132, 252, 0.2)', color: '#c084fc', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Upload size={14} /> Drag &amp; drop a .csv file to get started
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Code Editor ── */}
            {activeTab === 'code' && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', gap: '8px', color: 'var(--text-secondary)', alignItems: 'center' }}>
                    <Terminal size={16} /> <span>generated_code/main.py</span>
                    {editorCode !== originalCode && (
                      <span style={{ color: 'var(--danger)', fontSize: '0.85em', fontWeight: 'bold' }}>(Unsaved changes)</span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button
                      style={{ padding: '6px 12px', fontSize: '0.9rem', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: 'white', borderRadius: '8px', cursor: editorCode === originalCode ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                      onClick={saveCode}
                      disabled={editorCode === originalCode}
                    >
                      <Save size={14} /> Save
                    </button>
                    <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '0.9rem' }} onClick={runEditorCode} disabled={isCodeRunning}>
                      <Play size={14} /> {isCodeRunning ? 'Running…' : 'Run Code'}
                    </button>
                  </div>
                </div>

                <div style={{ flex: 1, border: '1px solid var(--glass-border)', borderRadius: '8px', overflow: 'hidden' }}>
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
                      <div className="terminal-title"><Terminal size={14} /><span>Execution Output</span></div>
                      <div className="terminal-controls">
                        <button className="terminal-btn" onClick={() => setIsTerminalMinimized(!isTerminalMinimized)} title={isTerminalMinimized ? 'Maximize' : 'Minimize'}>
                          {isTerminalMinimized ? <Square size={12} /> : <Minus size={12} />}
                        </button>
                        <button className="terminal-btn close" onClick={() => setEditorOutput('')} title="Close">
                          <X size={12} />
                        </button>
                      </div>
                    </div>
                    <div className="terminal-body">{editorOutput}</div>
                  </div>
                )}
              </div>
            )}

            {/* ── Agent Conversation ── */}
            {activeTab === 'chat' && (
              <div className="chat-container">
                {isRunning && (
                  <div className="agent-typing">
                    <div className="spinner-border" style={{ width: '16px', height: '16px', borderWidth: '0.15em' }} />
                    <span>Agent ecosystem is processing…</span>
                  </div>
                )}

                {/* User prompt */}
                {messages.filter((m) => m.type === 'user').map((msg) => (
                  <div key={msg.id} className="message-row user" style={{ marginBottom: '20px' }}>
                    <div className="avatar">{getAvatarIcon(msg.sender)}</div>
                    <div className="chat-bubble user-msg" style={{ fontSize: '0.95rem', color: '#e2e8f0' }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}

                {/* Agent timeline (while running, no final result yet) */}
                {!finalResultContent && agentMessages.length > 0 && (
                  <div className="agent-timeline">
                    {agentMessages.map((msg, idx) => {
                      const isExpanded   = expandedTimelineSteps.has(msg.id);
                      const displayName  = msg.sender?.toLowerCase() === 'manager' ? 'Root' : msg.sender;
                      return (
                        <div key={msg.id} className="timeline-step">
                          <div className="timeline-header" onClick={() => toggleTimelineStep(msg.id)}>
                            <div className="timeline-header-left">
                              {getAvatarIcon(msg.sender)}
                              <span style={{ color: 'var(--text-primary)' }}>{displayName}</span>
                              {msg.receiver && (
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>
                                  → {msg.receiver?.toLowerCase() === 'manager' ? 'Root' : msg.receiver}
                                </span>
                              )}
                            </div>
                            <ChevronDown size={20} className={`chevron ${isExpanded ? 'open' : ''}`} />
                          </div>
                          {isExpanded && (
                            <div className="timeline-body md-content">
                              <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                                {msg.content.replace(/Code output:[\s\n]*\|/g, 'Code output:\n\n|')}
                              </ReactMarkdown>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Final result card */}
                {finalResultContent && (() => {
                  const reqMatch = finalResultContent.match(/REQUEST\s*:\s*(.*?)(?=\s*RESPONSE\s*:|$)/s);
                  const resMatch = finalResultContent.match(/RESPONSE\s*:\s*(.*)/s);
                  const reqStr = reqMatch ? reqMatch[1] : '';
                  const resStr = resMatch ? resMatch[1] : finalResultContent;
                  return (
                    <div className="final-result-card" style={{ border: '1px solid var(--primary-dark)', background: 'rgba(30,41,59,0.5)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '20px' }}>
                        <div className="avatar" style={{ width: '48px', height: '48px', flexShrink: 0, background: 'var(--primary)' }}>
                          {getAvatarIcon('Manager')}
                        </div>
                        <div>
                          <h3 style={{ margin: 0, fontSize: '1.4rem' }}>
                            <CheckCircle2 size={24} style={{ color: 'var(--success)', verticalAlign: 'middle', marginRight: '8px', marginTop: '-3px' }} />
                            Expert Analysis Complete
                          </h3>
                          <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginTop: '6px' }}>Synthesized by Root Manager</div>
                        </div>
                      </div>
                      {reqStr && (
                        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '20px', borderRadius: '8px', marginBottom: '24px', borderLeft: '4px solid var(--primary)' }}>
                          <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '12px', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Target Objective</strong>
                          <div style={{ fontSize: '1.05rem', fontStyle: 'italic', fontWeight: 500, color: 'var(--text-primary)' }}>{reqStr.trim()}</div>
                        </div>
                      )}
                      <div className="md-content final-markdown" style={{ fontSize: '1.1rem', lineHeight: '1.7' }}>
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>{resStr.trim()}</ReactMarkdown>
                      </div>
                      <button
                        className="btn-primary"
                        style={{ marginTop: '32px', padding: '12px 24px', height: 'auto', background: 'transparent', color: 'var(--primary)', border: '2px solid var(--primary-dark)' }}
                        onMouseOver={(e) => { e.currentTarget.style.background = 'var(--primary-dark)'; e.currentTarget.style.color = '#fff'; }}
                        onMouseOut={(e)  => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--primary)'; }}
                        onClick={() => setShowFullLog(true)}
                      >
                        <Cpu size={18} /> Explore Core Reasoning
                      </button>
                    </div>
                  );
                })()}

                {!isRunning && !finalResultContent && messages.length === 0 && (
                  <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '40px' }}>
                    Agent terminal is awaiting execution…
                  </div>
                )}



                <div ref={chatEndRef} style={{ height: '32px', flexShrink: 0 }} />
              </div>
            )}

            {/* ── File Viewer ── */}
            {activeTab === 'fileviewer' && (
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
            )}
          </div>

          {/* Raw Agent Trace Drawer */}
          {showFullLog && (
            <div className="drawer-overlay" onClick={() => setShowFullLog(false)}>
              <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
                <div className="drawer-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Cpu size={20} className="primary-color" /> Raw Agent Trace
                  </div>
                  <button className="close-btn" onClick={() => setShowFullLog(false)} aria-label="Close">✕</button>
                </div>
                <div className="drawer-body">
                  <div className="drawer-body-inner">
                    {messages.map((msg) => {
                      if (msg.sender?.toLowerCase() === 'userproxy') return null;
                      if (msg.type === 'system' || msg.sender === 'System') return null;
                      const isUser = msg.type === 'user';
                      return (
                        <div key={msg.id} className={`message-row ${isUser ? 'user' : ''}`}>
                          <div className="avatar">{getAvatarIcon(msg.sender)}</div>
                          <div className={`chat-bubble ${isUser ? 'user-msg' : 'agent'}`}>
                            {getAgentHeaderStyle(msg.sender)}
                            {msg.type === 'agent' && msg.receiver && (
                              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px', display: 'block' }}>
                                to {msg.receiver}
                              </span>
                            )}
                            <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                              {msg.content?.replace(/Code output:[\s\n]*\|/g, 'Code output:\n\n|') ?? ''}
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

      {/* ── Full-screen Plan Review Modal ── */}
      {showPlanModal && (
        <PlanReviewModal
          planContent={planContent}
          setPlanContent={setPlanContent}
          onApprove={handleApprovePlan}
          onReject={handleRejectPlan}
        />
      )}
    </div>
  );
}

export default App;
