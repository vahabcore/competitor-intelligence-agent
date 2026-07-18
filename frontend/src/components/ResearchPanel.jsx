import React, { useState } from 'react';
import { Card, Accordion } from 'react-bootstrap';

/**
 * Displays web research and internal KB results in collapsible panels.
 * `sources` is an array of { source, title, content } objects.
 */
const ResearchPanel = ({ sources, isStreaming }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <Card className="mb-3">
      <Card.Header className="d-flex align-items-center justify-content-between py-2">
        <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Research Sources</span>
        {isStreaming && (
          <span
            className="badge bg-warning text-dark"
            style={{ fontSize: '0.65rem' }}
          >
            ● Collecting...
          </span>
        )}
      </Card.Header>

      <Accordion flush>
        {sources.map((src, idx) => (
          <Accordion.Item eventKey={String(idx)} key={src.source + idx}>
            <Accordion.Header>
              <span style={{ fontSize: '0.85rem' }}>{src.title}</span>
            </Accordion.Header>
            <Accordion.Body
              style={{
                background: '#f8f9fa',
                fontSize: '0.8rem',
                whiteSpace: 'pre-wrap',
                maxHeight: '260px',
                overflowY: 'auto',
                fontFamily: 'monospace',
                lineHeight: 1.6,
              }}
            >
              {src.content || '(empty)'}
            </Accordion.Body>
          </Accordion.Item>
        ))}
      </Accordion>
    </Card>
  );
};

export default ResearchPanel;
