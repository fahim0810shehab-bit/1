import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import './index.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = async (endpoint, options = {}) => {
  const token = localStorage.getItem('nsu_token');
  const headers = { ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
};

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('nsu_token'));
  const [view, setView] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [transcripts, setTranscripts] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedTranscript, setSelectedTranscript] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsLevel, setSettingsLevel] = useState(3);
  const reportRef = useRef(null);

  useEffect(() => {
    if (token) {
      api('/auth/me').then(u => { setUser(u); setLoading(false); }).catch(() => { localStorage.removeItem('nsu_token'); setToken(null); setLoading(false); });
    } else { setLoading(false); }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      api('/transcripts').then(setTranscripts).catch(() => {});
      api('/history').then(setHistory).catch(() => {});
    }
  }, [user, token]);

  const handleLogin = useCallback(async (credentialResponse) => {
    try {
      const payload = JSON.parse(atob(credentialResponse.credential.split('.')[1]));
      const res = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: payload.email, name: payload.name, picture: payload.picture || '' })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Login failed');
      }
      const data = await res.json();
      localStorage.setItem('nsu_token', data.token);
      setToken(data.token);
      setUser(data.user);
    } catch (err) {
      console.error('Login error:', err);
      alert('Login failed: ' + err.message);
    }
  }, []);

  const handleLogout = () => { localStorage.removeItem('nsu_token'); setToken(null); setUser(null); setView('dashboard'); };

  const handleUpload = async (file, level) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_URL}/transcripts/upload?level=${level}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      setSelectedTranscript(data);
      setView('results');
      api('/transcripts').then(setTranscripts).catch(() => {});
      api('/history').then(setHistory).catch(() => {});
    } catch (err) { alert('Upload error: ' + err.message); }
  };

  const loadTranscript = async (id) => {
    try {
      const data = await api(`/transcripts/${id}`);
      setSelectedTranscript({ transcript_id: data.id, result: data.audit_result });
      setView('results');
    } catch (err) { alert('Failed to load transcript'); }
  };

  const deleteHistoryEntry = async (id) => {
    try {
      await api(`/history/${id}`, { method: 'DELETE' });
      setHistory(prev => prev.filter(h => h.id !== id));
    } catch (err) { alert('Failed to delete'); }
  };

  const exportPDF = async () => {
    if (!selectedTranscript || !selectedTranscript.transcript_id) {
      alert('No transcript selected');
      return;
    }
    try {
      const res = await fetch(`${API_URL}/export/pdf/${selectedTranscript.transcript_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `NSU_Audit_Report_${selectedTranscript.transcript_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to export PDF: ' + err.message);
    }
  };

  if (loading) return <LoadingScreen />;
  if (!user) return <LoginPage onLogin={handleLogin} />;

  return (
    <div className="min-h-screen flex">
      <Sidebar user={user} view={view} setView={setView} onLogout={handleLogout} open={sidebarOpen} setOpen={setSidebarOpen} />
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        <div className="p-6 max-w-7xl mx-auto">
          <AnimatePresence mode="wait">
            {view === 'dashboard' && (
              <motion.div key="dashboard" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
                <Dashboard onUpload={handleUpload} transcripts={transcripts} onLoadTranscript={loadTranscript} settingsLevel={settingsLevel} setSettingsLevel={setSettingsLevel} />
              </motion.div>
            )}
            {view === 'results' && selectedTranscript && (
              <motion.div key="results" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
                <ResultsView result={selectedTranscript.result} reportRef={reportRef} onExport={exportPDF} onBack={() => setView('dashboard')} />
              </motion.div>
            )}
            {view === 'history' && (
              <motion.div key="history" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
                <HistoryView history={history} onLoad={loadTranscript} onDelete={deleteHistoryEntry} />
              </motion.div>
            )}
            {view === 'settings' && (
              <motion.div key="settings" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
                <SettingsView level={settingsLevel} setLevel={setSettingsLevel} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }} className="w-12 h-12 border-4 border-white/20 border-t-nsu-accent rounded-full" />
    </div>
  );
}

function LoginPage({ onLogin }) {
  const googleBtnRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      if (window.google && googleBtnRef.current) {
        window.google.accounts.id.initialize({
          client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
          callback: onLogin
        });
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: 'filled_blue',
          size: 'large',
          text: 'signin_with',
          shape: 'pill',
          width: 300
        });
        clearInterval(interval);
      }
    }, 500);
    return () => clearInterval(interval);
  }, [onLogin]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-10 max-w-md w-full text-center">
        <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 3, repeat: Infinity }} className="mb-8">
          <div className="text-6xl mb-4">🎓</div>
          <h1 className="text-3xl font-bold text-white mb-2">NSU Academic Audit</h1>
          <p className="text-white/60 text-sm">Upload your transcript and get instant analysis</p>
        </motion.div>
        <div className="space-y-4">
          <div ref={googleBtnRef} className="flex justify-center" />
          <p className="text-white/40 text-xs">Sign in with your Google account</p>
        </div>
        <div className="mt-8 grid grid-cols-3 gap-3 text-center">
          <div className="glass p-3 rounded-lg"><div className="text-2xl mb-1">📊</div><p className="text-white/70 text-xs">CGPA Calc</p></div>
          <div className="glass p-3 rounded-lg"><div className="text-2xl mb-1">📋</div><p className="text-white/70 text-xs">Audit</p></div>
          <div className="glass p-3 rounded-lg"><div className="text-2xl mb-1">📄</div><p className="text-white/70 text-xs">PDF Export</p></div>
        </div>
      </motion.div>
    </div>
  );
}

function Sidebar({ user, view, setView, onLogout, open, setOpen }) {
  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'history', icon: '📜', label: 'History' },
    { id: 'settings', icon: '⚙️', label: 'Settings' }
  ];

  return (
    <motion.aside animate={{ width: open ? 256 : 80 }} className="fixed left-0 top-0 h-full glass z-50 flex flex-col">
      <div className="p-4 flex items-center justify-between border-b border-white/10">
        {open && <h2 className="text-white font-bold text-lg gradient-text">NSU Audit</h2>}
        <button onClick={() => setOpen(!open)} className="text-white/60 hover:text-white p-2 rounded-lg hover:bg-white/10 transition">
          {open ? '◀' : '▶'}
        </button>
      </div>
      <nav className="flex-1 p-3 space-y-2">
        {navItems.map(item => (
          <button key={item.id} onClick={() => setView(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${view === item.id ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10 hover:text-white'}`}>
            <span className="text-xl">{item.icon}</span>
            {open && <span className="font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 mb-3">
          {user.picture ? <img src={user.picture} alt="" className="w-10 h-10 rounded-full" /> : <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-white">👤</div>}
          {open && <div><p className="text-white text-sm font-medium truncate">{user.name}</p><p className="text-white/40 text-xs truncate">{user.email}</p></div>}
        </div>
        <button onClick={onLogout} className="w-full px-4 py-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition text-sm">
          {open ? 'Sign Out' : '🚪'}
        </button>
      </div>
    </motion.aside>
  );
}

function Dashboard({ onUpload, transcripts, onLoadTranscript, settingsLevel, setSettingsLevel }) {
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    try { await onUpload(acceptedFiles[0], settingsLevel); } finally { setUploading(false); }
  }, [onUpload, settingsLevel]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/pdf': ['.pdf'], 'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'] },
    maxSize: 1024 * 1024,
    multiple: false
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-white/60">Upload your transcript to get started</p>
      </div>
      <motion.div {...getRootProps()} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
        className={`glass-card p-12 text-center cursor-pointer mb-8 border-2 border-dashed transition ${isDragActive ? 'border-nsu-accent bg-white/10' : 'border-white/20'}`}>
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }} className="w-12 h-12 border-4 border-white/20 border-t-nsu-accent rounded-full mb-4" />
            <p className="text-white/80">Processing transcript...</p>
          </div>
        ) : (
          <>
            <div className="text-5xl mb-4">📁</div>
            <p className="text-white text-xl font-medium mb-2">{isDragActive ? 'Drop your file here' : 'Drag & drop your transcript'}</p>
            <p className="text-white/50 text-sm">Supports CSV, PDF, and Images (max 1MB)</p>
            <div className="mt-4 flex justify-center gap-3">
              <span className="glass px-3 py-1 rounded-full text-white/70 text-xs">CSV</span>
              <span className="glass px-3 py-1 rounded-full text-white/70 text-xs">PDF</span>
              <span className="glass px-3 py-1 rounded-full text-white/70 text-xs">Image</span>
            </div>
          </>
        )}
      </motion.div>
      <div className="mb-4 flex items-center gap-3">
        <label className="text-white/60 text-sm">Analysis Level:</label>
        <select value={settingsLevel} onChange={e => setSettingsLevel(Number(e.target.value))}
          className="glass-input px-3 py-2 rounded-lg text-sm">
          <option value={1}>Level 1 - Basic</option>
          <option value={2}>Level 2 - Intermediate</option>
          <option value={3}>Level 3 - Full (Default)</option>
        </select>
      </div>
      {transcripts.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">Recent Transcripts</h2>
          <div className="grid gap-4">
            {transcripts.slice(0, 5).map(t => (
              <motion.div key={t.id} whileHover={{ scale: 1.01 }} onClick={() => onLoadTranscript(t.id)}
                className="glass-card p-4 cursor-pointer flex justify-between items-center">
                <div>
                  <p className="text-white font-medium">{t.filename}</p>
                  <p className="text-white/50 text-sm">{t.program_detected || 'Unknown'} · {t.uploaded_at?.split('T')[0]}</p>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${t.academic_standing === 'GOOD STANDING' ? 'standing-good' : 'standing-probation'}`}>{t.cgpa?.toFixed(2) || 'N/A'}</p>
                  <p className="text-white/40 text-xs">{t.academic_standing}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ResultsView({ result, reportRef, onExport, onBack }) {
  const [activeTab, setActiveTab] = useState('overview');
  if (!result) return <p className="text-white">No results available</p>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6 no-print">
        <button onClick={onBack} className="text-white/60 hover:text-white flex items-center gap-2">← Back</button>
        <div className="flex gap-3">
          <button onClick={onExport} className="glass px-4 py-2 rounded-lg text-white hover:bg-white/15 transition flex items-center gap-2">📄 Export PDF</button>
        </div>
      </div>
      <div ref={reportRef}>
        <div className="glass-card p-8 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white mb-1">Academic Audit Report</h1>
              <p className="text-white/50 text-sm">Generated: {new Date().toLocaleDateString()} · Level {result.level_used || 3}</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold gradient-text">{result.cgpa?.toFixed(2)}</p>
              <p className={`text-sm font-medium ${result.academic_standing === 'GOOD STANDING' ? 'standing-good' : 'standing-probation'}`}>{result.academic_standing}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard label="Credits Earned" value={result.credits_earned?.toFixed(1)} color="green" />
            <StatCard label="Credits Remaining" value={result.credits_remaining?.toFixed(1)} color="yellow" />
            <StatCard label="Failed" value={result.failed_credits?.toFixed(1)} color="red" />
            <StatCard label="Program" value={result.program} color="blue" />
          </div>
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-white/70">Graduation Progress</span>
              <span className="text-white">{result.progress_percent?.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-3">
              <div className="progress-bar h-3" style={{ width: `${result.progress_percent || 0}%` }} />
            </div>
            <p className="text-white/50 text-xs mt-1">~{result.estimated_semesters} semesters remaining</p>
          </div>
          {result.major && <p className="text-white/70 text-sm mb-4">Detected Major: <span className="text-white font-medium">{result.major}</span></p>}
        </div>
        <div className="flex gap-2 mb-4 no-print">
          {['overview', 'courses', 'missing', 'waivers'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm capitalize transition ${activeTab === tab ? 'bg-white/15 text-white' : 'text-white/60 hover:bg-white/10'}`}>{tab}</button>
          ))}
        </div>
        {activeTab === 'overview' && result.category_progress && (
          <div className="grid gap-4">
            {Object.entries(result.category_progress).map(([cat, data]) => (
              <div key={cat} className="glass-card p-4">
                <div className="flex justify-between mb-2">
                  <span className="text-white font-medium">{cat}</span>
                  <span className="text-white/70 text-sm">{data.completed}/{data.required} credits</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div className="progress-bar h-2" style={{ width: `${data.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'courses' && (
          <div className="glass-card p-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-white/10 text-left">
                <th className="pb-2 text-white/60">Code</th><th className="pb-2 text-white/60">Title</th>
                <th className="pb-2 text-white/60">Credits</th><th className="pb-2 text-white/60">Grade</th>
                <th className="pb-2 text-white/60">Valid</th>
              </tr></thead>
              <tbody>
                {(selectedTranscriptCourses || []).map((c, i) => (
                  <tr key={i} className="border-b border-white/5">
                    <td className="py-2 text-white">{c.course_code}</td>
                    <td className="py-2 text-white/80">{c.course_title}</td>
                    <td className="py-2 text-white/80">{c.credits}</td>
                    <td className="py-2 text-white">{c.grade}</td>
                    <td className="py-2">{c.is_valid_nsu ? '✓' : '✗'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab === 'missing' && result.missing_courses && (
          <div className="glass-card p-4">
            <h3 className="text-white font-medium mb-3">Missing Required Courses ({result.missing_courses.length})</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {result.missing_courses.map(c => <div key={c} className="glass px-3 py-2 rounded-lg text-white/80 text-sm">{c}</div>)}
            </div>
          </div>
        )}
        {activeTab === 'waivers' && result.waiver_status && (
          <div className="glass-card p-4">
            <h3 className="text-white font-medium mb-3">Waiver Status</h3>
            <div className="space-y-2">
              {Object.entries(result.waiver_status).map(([code, status]) => (
                <div key={code} className="flex justify-between items-center glass px-4 py-3 rounded-lg">
                  <span className="text-white">{code}</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${status === 'COMPLETED' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'}`}>{status}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {result.invalid_courses && result.invalid_courses.length > 0 && (
          <div className="glass-card p-4 mt-4 border border-red-500/30">
            <h3 className="text-red-300 font-medium mb-2">⚠ Invalid NSU Courses Detected</h3>
            {result.invalid_courses.map((c, i) => (
              <p key={i} className="text-red-200/80 text-sm">{c.course_code} - {c.credits} credits - Grade: {c.grade}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  const colors = { green: 'text-green-400', yellow: 'text-yellow-400', red: 'text-red-400', blue: 'text-blue-400' };
  return (
    <div className="glass p-3 rounded-xl text-center">
      <p className="text-2xl font-bold text-white">{value || '—'}</p>
      <p className={`text-xs ${colors[color] || 'text-white/60'}`}>{label}</p>
    </div>
  );
}

function HistoryView({ history, onLoad, onDelete }) {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-6">History</h1>
      {history.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <div className="text-5xl mb-4">📜</div>
          <p className="text-white/60">No history yet. Upload a transcript to get started.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {history.map(h => (
            <motion.div key={h.id} whileHover={{ scale: 1.01 }} className="glass-card p-4 flex justify-between items-center">
              <div className="cursor-pointer flex-1" onClick={() => h.transcript_id && onLoad(h.transcript_id)}>
                <p className="text-white font-medium">{h.filename || 'Unknown'}</p>
                <p className="text-white/50 text-sm">{h.program || 'Unknown'} · Level {h.level_used} · {h.timestamp?.split('T')[0]}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-white font-bold">{h.cgpa?.toFixed(2)}</p>
                </div>
                <button onClick={() => onDelete(h.id)} className="text-red-400 hover:text-red-300 p-2 rounded-lg hover:bg-red-500/10">🗑</button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function SettingsView({ level, setLevel }) {
  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-6">Settings</h1>
      <div className="glass-card p-6 max-w-md">
        <h3 className="text-white font-medium mb-4">Analysis Level</h3>
        <p className="text-white/50 text-sm mb-4">Choose the default analysis depth. Level 3 is recommended.</p>
        <div className="space-y-3">
          {[{ v: 1, l: 'Level 1 - Basic', d: 'Credit tally only' }, { v: 2, l: 'Level 2 - Intermediate', d: 'CGPA + waivers' }, { v: 3, l: 'Level 3 - Full (Default)', d: 'Complete audit with deficiency report' }].map(opt => (
            <label key={opt.v} className={`flex items-center gap-3 p-4 rounded-xl cursor-pointer transition ${level === opt.v ? 'bg-white/15 border border-nsu-accent' : 'glass hover:bg-white/10'}`}>
              <input type="radio" name="level" value={opt.v} checked={level === opt.v} onChange={() => setLevel(opt.v)} className="accent-blue-400" />
              <div>
                <p className="text-white font-medium">{opt.l}</p>
                <p className="text-white/50 text-sm">{opt.d}</p>
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

const selectedTranscriptCourses = null;

export default App;
