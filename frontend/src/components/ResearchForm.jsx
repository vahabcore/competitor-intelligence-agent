import React, { useState, useRef } from 'react';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';

const ResearchForm = ({ onReportGenerated, onStreamChunk, onResearchData, onStart, onStop }) => {
  const [competitorName, setCompetitorName] = useState('');
  const [userRequest, setUserRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!competitorName) return;

    // Abort any previous request
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    if (onStart) onStart();

    try {
      const response = await fetch('http://127.0.0.1:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          competitor_name: competitorName,
          user_request: userRequest || 'General Analysis',
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server error ${response.status}: ${errText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // Accumulate chunks into a buffer to handle partial SSE lines
        buffer += decoder.decode(value, { stream: true });

        // SSE events are separated by double newlines
        const events = buffer.split('\n\n');
        // Keep the last (potentially incomplete) segment in the buffer
        buffer = events.pop() ?? '';

        for (const event of events) {
          // Each event may have multiple lines; find the "data:" line
          for (const line of event.split('\n')) {
            if (!line.startsWith('data: ')) continue;
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              if (data.error) {
                setError(data.error);
              } else if (data.done) {
                // Stream finished
              } else if (data.research && onResearchData) {
                // Research source data (web or internal KB)
                onResearchData(data);
              } else if (data.status && onStreamChunk) {
                // Node progress messages
                onStreamChunk(data.status);
              } else if (data.chunk && onStreamChunk) {
                // LLM token stream
                onStreamChunk(data.chunk);
              } else if (data.final_report && onReportGenerated) {
                onReportGenerated(data.final_report);
              }
            } catch (parseErr) {
              console.warn('Failed to parse SSE data:', dataStr, parseErr);
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'An unexpected error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStop = () => {
    if (abortRef.current) abortRef.current.abort();
    setLoading(false);
    if (onStop) onStop();
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      {error && (
        <Alert variant="danger" className="rounded-0" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Form.Group className="mb-3">
        <Form.Label>Competitor Name</Form.Label>
        <Form.Control
          type="text"
          placeholder="e.g. Stripe, Salesforce"
          value={competitorName}
          onChange={(e) => setCompetitorName(e.target.value)}
          disabled={loading}
          required
        />
      </Form.Group>

      <Form.Group className="mb-4">
        <Form.Label>Focus Area / Request (Optional)</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="e.g. Pricing, features, recent news..."
          value={userRequest}
          onChange={(e) => setUserRequest(e.target.value)}
          disabled={loading}
        />
      </Form.Group>

      <div className="d-flex gap-2">
        <Button
          variant="primary"
          type="submit"
          disabled={loading || !competitorName}
          className="flex-grow-1"
        >
          {loading ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
              Generating...
            </>
          ) : (
            'Run Analysis'
          )}
        </Button>

        {loading && (
          <Button variant="outline-secondary" type="button" onClick={handleStop}>
            Stop
          </Button>
        )}
      </div>
    </Form>
  );
};

export default ResearchForm;
