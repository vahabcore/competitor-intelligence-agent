import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Alert, Spinner, Button } from 'react-bootstrap';

const API = 'http://127.0.0.1:8000';

// File-type icon (PDF / MD / TXT)
const FileIcon = ({ name }) => {
  const ext = name?.split('.').pop()?.toLowerCase();
  const colors = { pdf: '#e74c3c', md: '#3498db', txt: '#2ecc71', markdown: '#3498db' };
  const color = colors[ext] || '#95a5a6';
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 36,
        height: 36,
        borderRadius: 8,
        background: color + '22',
        color,
        fontWeight: 700,
        fontSize: '0.65rem',
        textTransform: 'uppercase',
        flexShrink: 0,
        letterSpacing: 0,
      }}
    >
      {ext || '?'}
    </span>
  );
};

const IngestForm = () => {
  const [documents, setDocuments] = useState([]);   // { name, chunks, on_disk }
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState(null);
  const [message, setMessage] = useState(null);     // { type: 'success'|'danger', text }
  const fileInputRef = useRef(null);

  // ── Fetch document list on mount ──────────────────────────────────────────
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/ingest/documents`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error('Failed to fetch documents', e);
    }
  }, []);

  useEffect(() => { fetchDocuments(); }, [fetchDocuments]);

  // ── Upload handler ────────────────────────────────────────────────────────
  const uploadFile = async (file) => {
    if (!file) return;
    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API}/api/ingest/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setMessage({ type: 'success', text: data.message });
      await fetchDocuments();
    } catch (e) {
      setMessage({ type: 'danger', text: e.message || 'Upload failed.' });
    } finally {
      setUploading(false);
      // Reset file input so the same file can be re-uploaded after deletion
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  // ── Drag-and-drop ─────────────────────────────────────────────────────────
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  };

  // ── Delete handler ────────────────────────────────────────────────────────
  const handleDelete = async (name) => {
    setDeletingDoc(name);
    setMessage(null);
    try {
      const res = await fetch(
        `${API}/api/ingest/documents/${encodeURIComponent(name)}`,
        { method: 'DELETE' }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setMessage({ type: 'success', text: data.message });
      await fetchDocuments();
    } catch (e) {
      setMessage({ type: 'danger', text: e.message || 'Delete failed.' });
    } finally {
      setDeletingDoc(null);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div>
      {/* ── Header blurb ──────────────────────────────── */}
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea22, #764ba222)',
          border: '1px solid #667eea44',
          borderRadius: 12,
          padding: '16px 20px',
          marginBottom: 20,
        }}
      >
        <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>
          📁 Your Comparison Data
        </div>
        <div style={{ fontSize: '0.83rem', color: '#555', lineHeight: 1.6 }}>
          Upload your <strong>internal product docs, pricing sheets, or feature lists</strong>.
          The AI agent will use this data to compare against competitors during analysis.
        </div>
      </div>

      {/* ── Flash message ─────────────────────────────── */}
      {message && (
        <Alert
          variant={message.type}
          dismissible
          onClose={() => setMessage(null)}
          className="py-2"
          style={{ fontSize: '0.85rem' }}
        >
          {message.text}
        </Alert>
      )}

      {/* ── Drop zone ─────────────────────────────────── */}
      <div
        onClick={() => !uploading && fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? '#667eea' : '#ccc'}`,
          borderRadius: 12,
          padding: '28px 20px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          background: dragOver ? '#667eea0d' : '#fafafa',
          transition: 'all 0.2s ease',
          marginBottom: 20,
          userSelect: 'none',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.md,.txt,.markdown"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          disabled={uploading}
        />
        {uploading ? (
          <>
            <Spinner animation="border" size="sm" className="me-2" />
            <span style={{ fontSize: '0.9rem', color: '#555' }}>Ingesting into knowledge base...</span>
          </>
        ) : (
          <>
            <div style={{ fontSize: '2rem', marginBottom: 6 }}>📄</div>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: 4 }}>
              Drop a file here or <span style={{ color: '#667eea', textDecoration: 'underline' }}>browse</span>
            </div>
            <div style={{ fontSize: '0.78rem', color: '#888' }}>
              Supports PDF, Markdown, and TXT files
            </div>
          </>
        )}
      </div>

      {/* ── Document list ─────────────────────────────── */}
      {documents.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '24px 0',
            fontSize: '0.85rem',
            color: '#aaa',
          }}
        >
          No documents ingested yet. Upload one above to get started.
        </div>
      ) : (
        <>
          <div
            style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#888',
              marginBottom: 8,
            }}
          >
            Ingested Documents ({documents.length})
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {documents.map((doc) => (
              <div
                key={doc.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '10px 14px',
                  border: '1px solid #e8e8e8',
                  borderRadius: 10,
                  background: '#fff',
                  transition: 'box-shadow 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'}
                onMouseLeave={e => e.currentTarget.style.boxShadow = 'none'}
              >
                <FileIcon name={doc.name} />

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontWeight: 600,
                      fontSize: '0.88rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                    title={doc.name}
                  >
                    {doc.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#888', marginTop: 1 }}>
                    {doc.chunks} chunk{doc.chunks !== 1 ? 's' : ''} in vector DB
                    {!doc.on_disk && (
                      <span style={{ color: '#e67e22', marginLeft: 6 }}>· file removed from disk</span>
                    )}
                  </div>
                </div>

                <Button
                  variant="outline-danger"
                  size="sm"
                  disabled={deletingDoc === doc.name}
                  onClick={() => handleDelete(doc.name)}
                  style={{ padding: '3px 10px', fontSize: '0.78rem', flexShrink: 0 }}
                >
                  {deletingDoc === doc.name ? (
                    <Spinner as="span" animation="border" size="sm" />
                  ) : (
                    '🗑 Remove'
                  )}
                </Button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default IngestForm;
