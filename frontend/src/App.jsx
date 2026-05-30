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
  Square, X, Folder, MessageSquare, Pencil, Trash2, Search, Layout, UserCheck, Maximize2, Layers
} from 'lucide-react';
import FileExplorer from './components/FileExplorer';
import FileViewer from './components/FileViewer';
import './index.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: '#ef4444', background: '#1e293b', borderRadius: '8px', border: '1px solid #ef4444' }}>
          <h3>UI Render Error</h3>
          <p>{this.state.error?.toString()}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

const API_BASE = window.location.origin;
const WS_BASE = window.location.origin.replace(/^http/, 'ws');

// ─── Noise patterns to filter from the WebSocket stream ───────────────────────
const NOISY_PATTERNS = [
  /TERMINATING RUN/,
  /No next speaker selected/,
  /Select speaker attempt/,
  /is_termination_msg/,
  /return None/,
  /^>{4,}/,
  /^<{4,}/,
  /\[INFO\] Initializing Agentic Session/,
  /\[SYSTEM\] Plan Approved/,
  /\[SYSTEM\] Beginning execution phase/,
  /^UserProxy\s+\(to\s+chat_manager\)/,
  /^Next speaker:/,
  /Suggested tool call/,
  /Response from calling tool/
];

const isNoisyLine = (line) =>
  !line.trim() || NOISY_PATTERNS.some((re) => re.test(line));

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

// ─── Plan Review Modal ────────────────────────────────────────────────────────
const PlanReviewModal = ({ planContent, setPlanContent, onApprove, onReject }) => {
  const [annotations, setAnnotations] = useState([]);
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
      }).catch(err => console.error("Plan Fetch Error:", err));
    };
    fetchPlan();
    const interval = setInterval(fetchPlan, 2000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [planContent, setPlanContent]);

  // Load annotations from sidecar API (plan content stays clean)
  useEffect(() => {
    axios.get(`${API_BASE}/api/annotations`)
      .then(res => { if (res.data.status === 'success') setAnnotations(res.data.annotations || []); })
      .catch(console.error);
  }, []);

  const persistAnnotations = async (anns) => {
    setAnnotations(anns);
    try {
      await axios.post(`${API_BASE}/api/annotations`, { annotations: anns });
    } catch (err) {
      console.error("Failed to save annotations:", err);
    }
  };

  const handleMouseUp = () => {
    const sel = window.getSelection();
    const text = sel.toString().trim();
    if (text && text.length > 2) {
      const range = sel.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelection({ text, x: rect.left + rect.width / 2, y: rect.top });
    } else {
      if (!isAddingComment) setSelection(null);
    }
  };

  const submitComment = () => {
    if (!comment.trim() || !selection) return;
    const newAnns = editingId
      ? annotations.map(a => a.id === editingId ? { ...a, comment: comment.trim() } : a)
      : [...annotations, { id: Date.now().toString(), text: selection.text, comment: comment.trim() }];
    persistAnnotations(newAnns);
    setComment(""); setSelection(null); setIsAddingComment(false); setEditingId(null);
  };

  const deleteAnnotation = (id) => persistAnnotations(annotations.filter(a => a.id !== id));

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
      [...annotations].sort((a, b) => b.text.length - a.text.length).forEach(ann => {
        if (!ann.text) return;
        const escaped = ann.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escaped})(?![^<]*>)`, 'g');
        content = content.replace(regex, `<mark class="plan-highlight" data-id="${ann.id}">$1</mark>`);
      });
      return content;
    } catch (e) {
      console.error("Highlighting engine error:", e);
      return planContent;
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
                    <div style={{ fontSize: '0.65rem', color: 'var(--primary)', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px', letterSpacing: '0.05em' }}>
                      Context
                    </div>
                    <div className="ann-text">"{ann.text}"</div>
                    <div style={{ fontSize: '0.65rem', color: '#f472b6', fontWeight: 800, textTransform: 'uppercase', margin: '12px 0 4px 0', letterSpacing: '0.05em' }}>
                      Comment
                    </div>
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
              <div className="annotation-container md-content" ref={containerRef} style={{ padding: '40px', background: '#020617', color: '#f8fafc' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
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

// ─── Timings Bar ──────────────────────────────────────────────────────────────
const TimingsBar = ({ lines }) => {
  const parsed = lines
    .map(line => {
      const m = line.match(/Phase: (.+?) \| Duration: ([\d.]+)s/);
      return m ? { phase: m[1].replace(/^Phase \d+: /, ''), duration: parseFloat(m[2]) } : null;
    })
    .filter(Boolean);
  if (!parsed.length) return null;
  const total = parsed.reduce((s, t) => s + t.duration, 0);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', padding: '8px 20px', background: 'rgba(0,0,0,0.25)', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.72rem', color: 'var(--text-secondary)', flexShrink: 0 }}>
      <span style={{ fontWeight: 600 }}>⏱</span>
      {parsed.map((t, i) => (
        <span key={i} style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
          {t.phase} <span style={{ color: '#60a5fa', fontWeight: 600 }}>{t.duration.toFixed(1)}s</span>
        </span>
      ))}
      <span style={{ color: '#10b981', fontWeight: 600 }}>Total: {total.toFixed(1)}s</span>
    </div>
  );
};


// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  useEffect(() => {
    console.log("🚀 AutoGen Analyst: New UI Layout (v2.0) is active!");
    // Initial metadata and files fetch
    axios.get(`${API_BASE}/api/metadata`).then((res) => {
      if (res.data.status === 'success' && res.data.markdown) {
        setMarkdownContent(res.data.markdown);
      }
    }).catch(console.error);

    axios.get(`${API_BASE}/api/uploaded_files`).then((res) => {
      if (res.data.status === 'success') {
        setUploadedFiles(res.data.files || []);
      }
    }).catch(console.error);
  }, []);

  const [file, setFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadLogs, setUploadLogs] = useState([]);
  const [markdownContent, setMarkdownContent] = useState('');
  const [query, setQuery] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  // Chat
  const [messages, setMessages] = useState(() => {
    try { return JSON.parse(localStorage.getItem('analyst_messages') || '[]'); }
    catch { return []; }
  });
  const [activeTab, setActiveTab] = useState('chat');

  // Plan review
  const [planContent, setPlanContent] = useState('');
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [selectedMetadataFile, setSelectedMetadataFile] = useState(null);

  // Code editor
  const [editorCode, setEditorCode] = useState('');
  const [originalCode, setOriginalCode] = useState('');
  const [editorOutput, setEditorOutput] = useState('');
  const [isCodeRunning, setIsCodeRunning] = useState(false);
  const [expandedBlocks, setExpandedBlocks] = useState(() => new Set());
  const [timings, setTimings] = useState([]);
  const toggleBlockHistory = useCallback((bIdx) => {
    setExpandedBlocks(prev => {
      const next = new Set(prev);
      next.has(bIdx) ? next.delete(bIdx) : next.add(bIdx);
      return next;
    });
  }, []);
  const [terminalHeight, setTerminalHeight] = useState(240);
  const [isTerminalMinimized, setIsTerminalMinimized] = useState(false);
  const [isResizing, setIsResizing] = useState(false);

  // File Viewer
  const [exploreFiles, setExploreFiles] = useState([]);
  const [selectedFilePath, setSelectedFilePath] = useState('');
  const [sheetData, setSheetData] = useState(null);
  const [sheetLoading, setSheetLoading] = useState(false);
  const [sheetFilters, setSheetFilters] = useState({ col: '', vals: [] });
  const [sheetSort, setSheetSort] = useState({ col: '', asc: true });
  const [sheetLimit, setSheetLimit] = useState({ type: 'top', n: 50 });

  const chatEndRef = useRef(null);
  const wsRef = useRef(null);
  const textareaRef = useRef(null);

  // Streaming text reveal
  const [displayedLen, setDisplayedLen] = useState({});
  const messagesRef = useRef(messages);
  const rafRef = useRef(null);
  const sessionMsgIdsRef = useRef(new Set());
  useEffect(() => { messagesRef.current = messages; }, [messages]);

  // RAF loop — drip chars while running
  useEffect(() => {
    if (!isRunning) {
      if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
      setDisplayedLen(prev => {
        const next = { ...prev };
        messagesRef.current.forEach(m => { if (m?.id) next[m.id] = Infinity; });
        return next;
      });
      return;
    }
    const CHARS_PER_SEC = 120; // ~ChatGPT streaming speed
    let lastTs = null;
    let accumulator = 0;
    const tick = (ts) => {
      if (lastTs === null) lastTs = ts;
      const elapsed = (ts - lastTs) / 1000;
      lastTs = ts;
      accumulator += elapsed * CHARS_PER_SEC;
      const charsThisFrame = Math.floor(accumulator);
      if (charsThisFrame > 0) accumulator -= charsThisFrame;
      const msgs = messagesRef.current;
      setDisplayedLen(prev => {
        const next = { ...prev };
        let changed = false;
        // Snap all messages except the last to fully revealed (sequential streaming)
        msgs.forEach((m, i) => {
          if (m?.id && i < msgs.length - 1 && (next[m.id] ?? 0) < Infinity) {
            next[m.id] = Infinity;
            changed = true;
          }
        });
        // Stream only the last (currently active) message
        if (charsThisFrame > 0) {
          const last = msgs[msgs.length - 1];
          if (last?.content) {
            const cur = next[last.id] ?? 0;
            if (cur < last.content.length) {
              next[last.id] = Math.min(cur + charsThisFrame, last.content.length);
              changed = true;
            }
          }
        }
        return changed ? next : prev;
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; } };
  }, [isRunning]);

  const getVisibleContent = (msg) => {
    if (!msg?.content) return '';
    // Old messages (from localStorage) always show fully
    if (!sessionMsgIdsRef.current.has(msg.id)) return msg.content;
    const len = displayedLen[msg.id] ?? 0;
    if (len >= msg.content.length) return msg.content;
    return msg.content.slice(0, len);
  };

  // ── Auto-resize textarea ────────────────────────────────────────────────
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [query]);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e) => {
      // Calculate height from bottom of screen
      const newHeight = window.innerHeight - e.clientY;
      // Limit height: min 80px, max 80% of window
      if (newHeight > 80 && newHeight < window.innerHeight * 0.8) {
        setTerminalHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    document.body.style.cursor = 'ns-resize';
    document.body.style.userSelect = 'none'; // Prevent text selection while dragging

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
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

  // ── Persist messages to localStorage ────────────────────────────────────
  useEffect(() => {
    try { localStorage.setItem('analyst_messages', JSON.stringify(messages)); }
    catch { /* quota exceeded */ }
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
    setEditorOutput('Saving...\n');
    try {
      await axios.post(`${API_BASE}/api/code`, { code: editorCode });
      setOriginalCode(editorCode);
      setEditorOutput('');
    } catch (err) {
      setEditorOutput('Failed to save: ' + err.message);
      setIsCodeRunning(false);
      return;
    }
    const ws = new WebSocket(`${WS_BASE}/ws/run_code`);
    ws.onmessage = (e) => {
      if (e.data === '[DONE]') { setIsCodeRunning(false); ws.close(); return; }
      setEditorOutput(prev => prev + e.data);
    };
    ws.onerror = () => { setEditorOutput(prev => prev + '\n[Connection error]'); setIsCodeRunning(false); };
    ws.onclose = () => setIsCodeRunning(false);
  };


  const newAnalysis = () => {
    setMessages([]);
    localStorage.removeItem('analyst_messages');
    setQuery('');
    setPlanContent('');
    setTimings([]);
    setExpandedBlocks(new Set());
    sessionMsgIdsRef.current = new Set();
    setDisplayedLen({});
    if (wsRef.current) wsRef.current.close();
    setIsRunning(false);
    setActiveTab('chat');
    axios.delete(`${API_BASE}/api/timings`).catch(() => { });
    axios.delete(`${API_BASE}/api/annotations`).catch(() => { });
  };

  // ── Drag & Drop ──────────────────────────────────────────────────────────
  const onDragOver = (e) => { e.preventDefault(); e.currentTarget.classList.add('dragging'); };
  const onDragLeave = (e) => { e.currentTarget.classList.remove('dragging'); };
  const onDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragging');
    if (e.dataTransfer.files?.length) handleFilesUpload(e.dataTransfer.files);
  };
  const onFileChange = (e) => { if (e.target.files?.length) handleFilesUpload(e.target.files); };

  const uploadSingleFile = async (selectedFile) => {
    setFile(selectedFile);
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
        setUploadedFiles(prev => [...new Set([...prev, selectedFile.name])]);
      } else { alert('Error analyzing file: ' + res.data.message); }
    } catch (err) {
      console.error(err);
      alert(`Failed to upload ${selectedFile.name}.`);
    } finally { clearInterval(poll); }
  };

  const handleFilesUpload = async (fileList) => {
    const valid = Array.from(fileList).filter(f =>
      f.name.endsWith('.csv') || f.name.endsWith('.parquet')
    );
    if (valid.length === 0) { alert('Please upload valid CSV or Parquet files.'); return; }
    setIsUploading(true);
    for (let i = 0; i < valid.length; i++) {
      setUploadLogs([`Uploading file ${i + 1} of ${valid.length}: ${valid[i].name}`]);
      await uploadSingleFile(valid[i]);
    }
    setIsUploading(false);
    setActiveTab('chat');
  };

  const handleDeleteFile = async (filename) => {
    if (!window.confirm(`Delete ${filename}?`)) return;
    try {
      const res = await axios.delete(`${API_BASE}/api/uploaded_files/${encodeURIComponent(filename)}`);
      if (res.data.status === 'success') {
        setUploadedFiles(prev => prev.filter(f => f !== filename));
        setMarkdownContent(res.data.markdown || '');
        if (selectedMetadataFile === filename) setSelectedMetadataFile(null);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to delete file.');
    }
  };

  // ── WebSocket / run analysis ─────────────────────────────────────────────
  const runAnalysis = () => {
    if (!query.trim()) { alert('Please enter a request.'); return; }
    if (uploadedFiles.length === 0 && !markdownContent) { alert('Please upload a CSV file first.'); return; }

    const isFollowup = isRunning && wsRef.current && wsRef.current.readyState === WebSocket.OPEN;

    if (isFollowup) {
      // Send follow-up to existing session
      const userMsg = {
        id: Date.now(),
        sender: 'You',
        content: query,
        type: 'user',
      };
      setMessages(prev => [...prev, userMsg]);
      wsRef.current.send(query);
      setQuery('');
      return;
    }

    // Start a new session
    const initial = [{
      id: Date.now(),
      sender: 'You',
      content: query,
      type: 'user',
    }];
    setMessages(prev => [...prev, ...initial]);
    setIsRunning(true);
    setActiveTab('chat');
    setQuery('');

    wsRef.current = new WebSocket(`${WS_BASE}/ws/run`);
    let currentMessage = null;

    wsRef.current.onopen = () => wsRef.current.send(query);

    wsRef.current.onmessage = (event) => {
      const line = event.data;

      // ── Silence noisy AutoGen internal lines ────────────────────────────
      if (isNoisyLine(line)) return;

      // ── Separator ───────────────────────────────────────────────────────
      if (line.startsWith('----------')) return;

      // ── Agent header ────────────────────────────────────────────────────
      const agentMatch = line.match(/^(\w+)\s+\(to\s+(\w+)\):/);
      if (agentMatch) {
        const sender = agentMatch[1];
        const whitelist = ['manager', 'metadata_specialist', 'planner', 'coder', 'feedbackagent', 'userproxy', 'resultinterpreter'];

        if (whitelist.includes(sender.toLowerCase())) {
          const newId = Date.now() + Math.random();
          currentMessage = { id: newId, sender, receiver: agentMatch[2], content: '', type: 'agent' };
          sessionMsgIdsRef.current.add(newId);
          setDisplayedLen(prev => ({ ...prev, [newId]: 0 }));
          setMessages(prev => [...prev, currentMessage]);
        } else {
          currentMessage = null; // Ignore this agent's session
        }
        return;
      }

      // ── Plan verification trigger ────────────────────────────────────────
      if (line.includes('[ACTION_REQUIRED: VERIFY PLAN]')) {
        currentMessage = null;
        setMessages(prev => [...prev, {
          id: Date.now() + Math.random(),
          sender: 'System',
          content: 'Action Required: Verify the implementation plan.',
          type: 'action',
          actionType: 'verify_plan',
          resolved: false,
        }]);
        setShowPlanModal(true);

        axios.get(`${API_BASE}/api/plan`).then((res) => {
          if (res.data.status === 'success') {
            setPlanContent(res.data.content);
          }
        }).catch((err) => console.error('Error fetching plan', err));
        return;
      }

      // ── System / status messages ─────────────────────────────────────────
      if (line.startsWith('[SYSTEM') || line.startsWith('[INFO') ||
        line.startsWith('[OK') || line.startsWith('[ERROR')) {
        currentMessage = null;
        return;
      }

      if (line.startsWith('[WAITING_FOR_INPUT]')) {
        currentMessage = null;
        setIsRunning(false);
        return;
      }

      // ── Regular content lines ────────────────────────────────────────────
      if (currentMessage) {
        try {
          const whitelist = ['manager', 'metadata_specialist', 'planner', 'coder', 'feedbackagent', 'userproxy', 'resultinterpreter'];
          if (whitelist.includes(currentMessage.sender?.toLowerCase())) {
            setMessages(prev => {
              const next = [...prev];
              const lastIdx = next.findLastIndex(m => m?.id === currentMessage?.id);

              // Fallback: if not found by ID (race condition), use last message if sender matches
              const targetIdx = lastIdx !== -1 ? lastIdx : (next.length > 0 && next[next.length - 1]?.sender === currentMessage?.sender ? next.length - 1 : -1);

              if (targetIdx !== -1 && next[targetIdx]) {
                const prevContent = next[targetIdx].content || '';
                let lineToProcess = line;
                const isTableLine = lineToProcess.trim().startsWith('|') && lineToProcess.trim().endsWith('|');
                const isSeparator = isTableLine && lineToProcess.includes('---');
                const trimmedPrev = prevContent.trimEnd();
                let newContent = prevContent + lineToProcess + '\n';

                // 2. Cohesive Stitching & Table Isolation
                if (isTableLine && trimmedPrev.length > 0) {
                  const lines = trimmedPrev.split('\n');
                  const lastNonEmptyLine = lines.filter(l => l.trim()).pop() || '';
                  const wasLastLineTable = lastNonEmptyLine.trim().startsWith('|') && lastNonEmptyLine.trim().endsWith('|');
                  const prevHasSeparator = prevContent.includes('|---') || prevContent.includes('| ---');

                  if (wasLastLineTable) {
                    // If this is a separator line and we already have one, skip it to avoid "unwanted columns/rows"
                    if (isSeparator && prevHasSeparator) {
                      newContent = prevContent; // Skip this line
                    } else {
                      newContent = trimmedPrev + '\n' + lineToProcess + '\n';
                    }
                  } else {
                    // Start new table
                    newContent = trimmedPrev + '\n\n' + lineToProcess + '\n';
                  }
                } else if (!isTableLine && trimmedPrev.length > 0) {
                  const lines = trimmedPrev.split('\n');
                  const lastNonEmptyLine = lines.filter(l => l.trim()).pop() || '';
                  const wasLastLineTable = lastNonEmptyLine.trim().startsWith('|') && lastNonEmptyLine.trim().endsWith('|');
                  if (wasLastLineTable) {
                    newContent = trimmedPrev + '\n\n' + lineToProcess + '\n';
                  }
                }

                next[targetIdx] = { ...next[targetIdx], content: newContent };
              }
              return next;
            });
          }
        } catch (err) {
          console.error('Error processing line:', err);
        }
      }
    };

    wsRef.current.onclose = () => {
      setIsRunning(false);
      axios.get(`${API_BASE}/api/timings`)
        .then(res => { if (res.data.status === 'success') setTimings(res.data.lines || []); })
        .catch(() => { });
    };
    wsRef.current.onerror = () => { setIsRunning(false); alert('WebSocket connection error.'); };
  };

  // ── Plan actions ───────────────────────────────────────────────────
  const resolvePlanAction = (answer) => {
    setShowPlanModal(false);
    wsRef.current?.send(answer);
  };

  const handleApprovePlan = async () => {
    try { await axios.post(`${API_BASE}/api/plan`, { code: planContent }); }
    catch (e) { console.error('Failed to save plan', e); }
    resolvePlanAction('yes');
  };

  const handleRejectPlan = () => {
    setShowPlanModal(false);
    setIsRunning(false);
    if (wsRef.current) {
      wsRef.current.send('no');
      wsRef.current.close();
    }
  };


  // ─── Chat Helpers ─────────────────────────────────────────────────────────
  const getAvatarIcon = (sender) => {
    const s = sender?.toLowerCase();
    if (s === 'manager') return <ShieldAlert size={20} color="#60a5fa" />;
    if (s === 'metadata_specialist') return <Search size={20} color="#c084fc" />;
    if (s === 'planner') return <Layout size={20} color="#f472b6" />;
    if (s === 'coder') return <Terminal size={20} color="#34d399" />;
    if (s === 'executor') return <Play size={20} color="#fbbf24" />;
    if (s === 'feedbackagent') return <UserCheck size={20} color="#f87171" />;
    if (s === 'resultinterpreter') return <Cpu size={20} color="#60a5fa" />;
    if (s === 'you') return <User size={20} color="#fff" />;
    return <Bot size={20} color="#94a3b8" />;
  };

  const getAgentHeaderStyle = (sender) => {
    const map = {
      manager: ['agent-label manager', 'Manager'],
      metadata_specialist: ['agent-label meta', 'Metadata Specialist'],
      planner: ['agent-label planner', 'Planner'],
      coder: ['agent-label coder', 'Coder'],
      executor: ['agent-label executor', 'Executor'],
      feedbackagent: ['agent-label validator', 'Validator'],
      resultinterpreter: ['agent-label manager', 'Root Analyst'],
    };
    const [cls, label] = map[sender?.toLowerCase()] ?? ['agent-label', sender];
    return <div className={cls}>{label}</div>;
  };

  // ── Group messages into per-request session blocks ──────────────────────
  const sessionBlocks = useMemo(() => {
    const blocks = [];
    let current = [];
    messages.forEach((msg, idx) => {
      if (!msg) return;
      if (msg.sender?.toLowerCase() === 'you' && idx !== 0 && current.length > 0) {
        blocks.push(current);
        current = [];
      }
      current.push(msg);
    });
    if (current.length > 0) blocks.push(current);
    return blocks;
  }, [messages]);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <button className="new-chat-btn" onClick={newAnalysis}>
          <MessageSquare size={18} /> New Analysis
        </button>

        <nav className="sidebar-nav">
          <div
            className={`sidebar-item ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <Bot size={18} /> Conversations
          </div>
          <div
            className={`sidebar-item ${activeTab === 'fileviewer' ? 'active' : ''}`}
            onClick={() => setActiveTab('fileviewer')}
          >
            <Folder size={18} /> Filesystem
          </div>
          <div
            className={`sidebar-item ${activeTab === 'code' ? 'active' : ''}`}
            onClick={() => setActiveTab('code')}
          >
            <Code size={18} /> Source Code
          </div>
          <div
            className={`sidebar-item ${activeTab === 'markdown' ? 'active' : ''}`}
            onClick={() => setActiveTab('markdown')}
          >
            <FileText size={18} /> Dataset Metadata
          </div>
        </nav>

        {uploadedFiles.length > 0 && (
          <div className="uploaded-files-section" style={{ marginTop: '32px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, padding: '0 12px', marginBottom: '12px', letterSpacing: '0.05em' }}>UPLOADED FILES</div>
            {uploadedFiles.map(f => (
              <div key={f} className="sidebar-file-item" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '8px', marginBottom: '4px', background: 'rgba(255,255,255,0.02)', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                  {f.endsWith('.parquet') ? <Layers size={14} color="#10b981" /> : <Database size={14} color="#60a5fa" />}
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f}</span>
                </div>
                <button
                  onClick={() => handleDeleteFile(f)}
                  style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }}
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="upload-section">
          <input type="file" id="file-upload" accept=".csv,.parquet" multiple style={{ display: 'none' }} onChange={onFileChange} />
          {!isUploading ? (
            <label htmlFor="file-upload">
              <div
                className="upload-zone"
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
              >
                <div className="upload-icon-wrapper">
                  <Upload size={20} />
                </div>
                <div className="upload-info">
                  <div className="upload-title">Upload Dataset</div>
                  <div className="upload-subtitle">CSV & Parquet, multiple files</div>
                </div>
              </div>
            </label>
          ) : (
            <div className="upload-progress-container">
              <div className="progress-header">
                <div className="spinner-border" />
                <span>Analyzing Dataset...</span>
              </div>
              <div className="progress-logs">
                {uploadLogs.slice(-3).map((log, i) => (
                  <div key={i} className="progress-log-entry">
                    <div className="log-dot" />
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}
          {file && !isUploading && (
            <div className="file-info-badge">
              <CheckCircle2 size={12} />
              <span>{file.name}</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Stage */}
      <main className="main-stage">
        <header className="header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h1 style={{ margin: 0, fontSize: '1.2rem', background: 'linear-gradient(90deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: 600 }}>
              Agentic Analysis
            </h1>
            <span className="status-badge" style={{ fontSize: '0.7rem', background: isRunning ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255,255,255,0.05)', color: isRunning ? '#10b981' : '#94a3b8', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>
              {isRunning ? 'Agent Active' : 'Idle'}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {activeTab === 'code' && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="sidebar-item" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: '#fff', borderRadius: '8px' }} onClick={saveCode} disabled={editorCode === originalCode}>
                  <Save size={14} /> Save
                </button>
                <button className="sidebar-item" style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'var(--primary-color)', color: '#fff', borderRadius: '8px' }} onClick={runEditorCode} disabled={isCodeRunning}>
                  <Play size={14} /> Run
                </button>
              </div>
            )}
            <Database size={18} color="var(--text-secondary)" />
          </div>
        </header>

        <div style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>

          {/* 1. Chat View */}
          {activeTab === 'chat' && (
            <>
              <div className="chat-container">
                {messages.length === 0 ? (
                  <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', opacity: 0.5, marginTop: '100px' }}>
                    <Bot size={64} />
                    <div style={{ textAlign: 'center' }}>
                      <h2 style={{ marginBottom: '8px' }}>How can I help you today?</h2>
                      <p>Upload a dataset and start analyzing with agentic intelligence.</p>
                    </div>
                  </div>
                ) : (
                  <>
                    {sessionBlocks.map((block, bIdx) => {
                      if (!block || block.length === 0) return null;

                      const resultIdx = block.findIndex(m => m && m.sender?.toLowerCase() === 'resultinterpreter');
                      const isLastBlock = bIdx === sessionBlocks.length - 1;
                      const canCollapse = resultIdx !== -1 && (!isLastBlock || !isRunning);
                      const blockHistory = resultIdx !== -1 ? block.slice(0, resultIdx) : block;
                      const blockResults = resultIdx !== -1 ? block.slice(resultIdx) : [];
                      const userMsg = block.find(m => m && m.sender?.toLowerCase() === 'you');
                      const restOfHistory = blockHistory.filter(m => m !== userMsg);

                      return (
                        <div key={`block-${bIdx}`} className="session-block" style={{ marginBottom: isLastBlock ? 0 : '40px', borderBottom: isLastBlock ? 'none' : '1px solid rgba(255,255,255,0.05)', paddingBottom: isLastBlock ? 0 : '40px' }}>
                          {userMsg && (
                            <div key={`user-${userMsg?.id}`} className="message-row user" style={{ marginBottom: '48px' }}>
                              <div className="avatar">{getAvatarIcon(userMsg.sender)}</div>
                              <div className="chat-bubble user-msg">
                                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                                  {userMsg.content || ''}
                                </ReactMarkdown>
                              </div>
                            </div>
                          )}

                          {!canCollapse ? (
                            block.filter(m => m !== userMsg).map((msg) => msg && (
                              <div key={`flat-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || '').toLowerCase() === 'user' ? 'user' : ''}`} style={{ marginBottom: '48px' }}>
                                <div className="avatar">{getAvatarIcon(msg.sender)}</div>
                                <div className={`chat-bubble ${(msg.type || '').toLowerCase() === 'agent' ? 'agent' : (msg.type || '').toLowerCase() === 'user' ? 'user-msg' : 'system'}`}>
                                  {msg.type === 'agent' && getAgentHeaderStyle(msg.sender)}
                                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                                    {getVisibleContent(msg)}
                                  </ReactMarkdown>
                                </div>
                              </div>
                            ))
                          ) : (
                            <>
                              {restOfHistory.length > 0 && (
                                <div className="reasoning-container" style={{ marginLeft: '60px' }}>
                                  <button
                                    className="reasoning-toggle"
                                    style={{ marginLeft: 0 }}
                                    onClick={() => toggleBlockHistory(bIdx)}
                                  >
                                    <ChevronDown size={14} style={{ transform: !expandedBlocks.has(bIdx) ? 'rotate(-90deg)' : 'none', transition: 'transform 0.2s' }} />
                                    {!expandedBlocks.has(bIdx) ? `Show Agent thought process (${restOfHistory.length} steps)` : 'Hide Agent thought process'}
                                  </button>

                                  {expandedBlocks.has(bIdx) && (
                                    <div className="reasoning-content">
                                      {restOfHistory.map((msg) => msg && (
                                        <div key={`hist-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || "").toLowerCase() === "user" ? "user" : ""}`} style={{ opacity: 0.8, transform: "scale(0.98)", transformOrigin: "left", marginBottom: "32px" }}>
                                          <div className="avatar" style={{ width: "28px", height: "28px" }}>{getAvatarIcon(msg.sender)}</div>
                                          <div className={`chat-bubble ${(msg.type || "").toLowerCase() === "agent" ? "agent" : (msg.type || "").toLowerCase() === "user" ? "user-msg" : "system"}`}>
                                            {msg.type === "agent" && getAgentHeaderStyle(msg.sender)}
                                            <div className="markdown-content">
                                              <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                                                {getVisibleContent(msg)}
                                              </ReactMarkdown>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              )}

                              {blockResults.map((msg) => msg && (
                                <div key={`res-${msg?.id || Math.random()}`} className={`message-row ${(msg.type || "").toLowerCase() === "user" ? "user" : ""}`} style={{ marginBottom: "64px" }}>
                                  <div className="avatar">{getAvatarIcon(msg.sender)}</div>
                                  <div className={`chat-bubble ${(msg.type || "").toLowerCase() === "agent" ? "agent" : (msg.type || "").toLowerCase() === "user" ? "user-msg" : "system"} ${msg.sender?.toLowerCase() === "resultinterpreter" ? "final-result" : ""}`}>
                                    {msg.type === "agent" && getAgentHeaderStyle(msg.sender)}
                                    <div className="markdown-content">
                                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                                        {getVisibleContent(msg)}
                                      </ReactMarkdown>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </>
                          )}
                        </div>
                      );
                    })}

                    {isRunning && (
                      <div className="message-row">
                        <div className="avatar"><Bot size={20} color="#60a5fa" /></div>
                        <div className="chat-bubble agent">
                          <div className="spinner-border" style={{ width: '16px', height: '16px', borderWidth: '0.15em', marginRight: '8px' }} />
                          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Agent ecosystem is thinking...</span>
                        </div>
                      </div>
                    )}
                  </>
                )}
                <div ref={chatEndRef} style={{ height: '20px' }} />
              </div>

              <TimingsBar lines={timings} />

              <div className="chat-input-wrapper">
                <div className="chat-input-container">
                  <textarea
                    ref={textareaRef}
                    rows="1"
                    placeholder="Send a message..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        runAnalysis();
                      }
                    }}
                  />
                  <button
                    className="send-btn"
                    onClick={runAnalysis}
                    disabled={!query.trim() || isUploading || isRunning}
                  >
                    <Play size={18} />
                  </button>
                </div>
              </div>
            </>
          )}

          {/* 2. Filesystem View */}
          {activeTab === 'fileviewer' && (
            <div className="file-viewer-container" style={{ padding: '24px', flex: 1 }}>
              <FileExplorer
                exploreFiles={exploreFiles}
                selectedFilePath={selectedFilePath}
                setSelectedFilePath={setSelectedFilePath}
                setExploreFiles={setExploreFiles}
              />
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
            </div>
          )}

          {/* 3. Source Code View */}
          {activeTab === 'code' && (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {isResizing && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, cursor: 'ns-resize' }} />
              )}
              <div style={{ flex: 1, minHeight: 0 }}>
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={editorCode}
                  onChange={(value) => setEditorCode(value)}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    automaticLayout: true,
                    scrollBeyondLastLine: false,
                    renderLineHighlight: 'all'
                  }}
                />
              </div>
              {editorOutput && (
                <div
                  className={`execution-terminal ${isTerminalMinimized ? 'minimized' : ''}`}
                  style={{ height: isTerminalMinimized ? '36px' : `${terminalHeight}px`, flexShrink: 0 }}
                >
                  <div className="terminal-resize-handle" onMouseDown={() => {
                    if (isTerminalMinimized) setIsTerminalMinimized(false);
                    setIsResizing(true);
                  }} />
                  <div className="terminal-header" onClick={() => setIsTerminalMinimized(!isTerminalMinimized)} style={{ cursor: 'pointer' }}>
                    <div className="terminal-title">
                      <Terminal size={14} /> Execution Output
                    </div>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button className="terminal-btn" onClick={(e) => { e.stopPropagation(); setIsTerminalMinimized(!isTerminalMinimized); }}>
                        {isTerminalMinimized ? <Maximize2 size={14} /> : <Minus size={14} />}
                      </button>
                      <button className="terminal-btn close" onClick={(e) => { e.stopPropagation(); setEditorOutput(''); }}><X size={14} /></button>
                    </div>
                  </div>
                  {!isTerminalMinimized && (
                    <div className="terminal-body">
                      {isCodeRunning && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px', color: '#60a5fa' }}>
                          <div className="spinner-border spinner-border-sm" />
                          <span>Process running...</span>
                        </div>
                      )}
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontOverflow: 'wrap' }}>{editorOutput}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* 4. Dataset Metadata View */}
          {activeTab === 'markdown' && (
            <div className="metadata-view-container" style={{ display: 'flex', height: '100%', background: 'rgba(0,0,0,0.2)' }}>
              {/* Metadata Sidebar */}
              <div className="metadata-sidebar" style={{ width: '280px', borderRight: '1px solid var(--glass-border)', padding: '24px', flexShrink: 0, overflowY: 'auto' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: '20px' }}>SELECT DATASET</div>
                {uploadedFiles.length > 0 ? (
                  uploadedFiles.map(f => (
                    <div
                      key={`md-list-${f}`}
                      className={`metadata-list-item ${selectedMetadataFile === f ? 'active' : ''}`}
                      onClick={() => setSelectedMetadataFile(f)}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '10px',
                        marginBottom: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        background: selectedMetadataFile === f ? 'rgba(96, 165, 250, 0.15)' : 'rgba(255,255,255,0.03)',
                        border: '1px solid',
                        borderColor: selectedMetadataFile === f ? 'rgba(96, 165, 250, 0.3)' : 'transparent',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', overflow: 'hidden', width: '100%' }}>
                        {f.endsWith('.parquet') ? <Layers size={16} color={selectedMetadataFile === f ? '#10b981' : 'var(--text-secondary)'} /> : <Database size={16} color={selectedMetadataFile === f ? '#60a5fa' : 'var(--text-secondary)'} />}
                        <span style={{
                          fontSize: '0.9rem',
                          color: selectedMetadataFile === f ? '#fff' : 'var(--text-secondary)',
                          fontWeight: selectedMetadataFile === f ? 600 : 400,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>{f}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ textAlign: 'center', opacity: 0.3, marginTop: '40px' }}>
                    <Database size={32} />
                    <p style={{ fontSize: '0.8rem', marginTop: '12px' }}>No files uploaded</p>
                  </div>
                )}
              </div>

              {/* Metadata Content Area */}
              <div className="md-content" style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                  {selectedMetadataFile ? (
                    <div style={{ paddingBottom: '100px' }}>
                      <div style={{
                        marginBottom: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        background: 'rgba(255,255,255,0.03)',
                        padding: '20px 28px',
                        borderRadius: '16px',
                        border: '1px solid var(--glass-border)',
                        backdropFilter: 'blur(10px)'
                      }}>
                        <div style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '12px',
                          background: selectedMetadataFile.endsWith('.parquet') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(96, 165, 250, 0.1)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          {selectedMetadataFile.endsWith('.parquet') ? <Layers size={24} color="#10b981" /> : <Database size={24} color="#60a5fa" />}
                        </div>
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.05em', marginBottom: '4px' }}>ACTIVE DATASET</div>
                          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>{selectedMetadataFile}</h1>
                        </div>
                      </div>
                      {/* Filter markdown content to show only the selected file section */}
                      {(() => {
                        // Clean content and split by file header
                        const sections = markdownContent.split(/## File: /);
                        const targetSection = sections.find(s => {
                          const lines = s.trim().split('\n');
                          if (lines.length === 0) return false;
                          const headerFilename = lines[0].trim();
                          // Exact match
                          if (headerFilename === selectedMetadataFile) return true;
                          // Base name match (fallback for extension mismatches)
                          const baseHeader = headerFilename.split('.')[0];
                          const baseSelected = selectedMetadataFile.split('.')[0];
                          return baseHeader === baseSelected && baseHeader.length > 0;
                        });

                        if (targetSection) {
                          const lines = targetSection.trim().split('\n');
                          const content = lines.slice(1).join('\n').trim();
                          return <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>;
                        }
                        return (
                          <div style={{ textAlign: 'center', marginTop: '60px', opacity: 0.5 }}>
                            <Database size={48} style={{ marginBottom: '16px' }} />
                            <p>Metadata not found for <strong>{selectedMetadataFile}</strong>.</p>
                            <p style={{ fontSize: '0.85rem' }}>Try re-uploading the file to regenerate its profile.</p>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', marginTop: '100px', opacity: 0.4 }}>
                      <Database size={64} />
                      <h3 style={{ marginTop: '20px' }}>Select a Dataset</h3>
                      <p>Pick a file from the list to view its analytical profile.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Plan Review Modal */}
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

export default function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
}
