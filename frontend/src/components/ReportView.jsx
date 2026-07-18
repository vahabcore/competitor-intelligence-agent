import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Card } from 'react-bootstrap';

const ReportView = ({ report, isStreaming }) => {
  if (!report) {
    return (
      <Card className="h-100 border-0 bg-light d-flex align-items-center justify-content-center p-5">
        <div className="text-muted text-uppercase" style={{ letterSpacing: '0.05em', fontSize: '0.85rem' }}>
          No report generated yet — run an analysis to get started
        </div>
      </Card>
    );
  }

  return (
    <Card className="h-100">
      <Card.Header className="d-flex align-items-center justify-content-between">
        <span>Analysis Report</span>
        {isStreaming && (
          <span className="badge bg-primary ms-2" style={{ fontSize: '0.7rem', animation: 'pulse 1.5s infinite' }}>
            ● Live
          </span>
        )}
      </Card.Header>
      <Card.Body
        className="overflow-auto p-4 markdown-body"
        style={{ maxHeight: '80vh' }}
      >
        <ReactMarkdown>{report}</ReactMarkdown>
        {isStreaming && (
          <span
            style={{
              display: 'inline-block',
              width: '2px',
              height: '1.1em',
              background: 'currentColor',
              marginLeft: '2px',
              verticalAlign: 'text-bottom',
              animation: 'blink 1s step-start infinite',
            }}
          />
        )}
      </Card.Body>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </Card>
  );
};

export default ReportView;
