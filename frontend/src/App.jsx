import React, { useState } from 'react';
import { Container, Row, Col, Navbar, Nav, Card } from 'react-bootstrap';
import ResearchForm from './components/ResearchForm';
import IngestForm from './components/IngestForm';
import ReportView from './components/ReportView';
import ResearchPanel from './components/ResearchPanel';

function App() {
  const [activeTab, setActiveTab] = useState('research');
  const [report, setReport] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [researchSources, setResearchSources] = useState([]); // [{source, title, content}]

  const handleStart = () => {
    setReport('');
    setResearchSources([]);
    setIsStreaming(true);
  };

  const handleStreamChunk = (chunk) => {
    setReport((prev) => prev + chunk);
  };

  const handleResearchData = (data) => {
    // data = { research: true, source, title, content }
    setResearchSources((prev) => {
      // Replace if same source already arrived (e.g. second pass), else append
      const exists = prev.findIndex((s) => s.source === data.source);
      if (exists !== -1) {
        const updated = [...prev];
        updated[exists] = data;
        return updated;
      }
      return [...prev, data];
    });
  };

  const handleReportGenerated = (finalReport) => {
    if (finalReport) setReport(finalReport);
    setIsStreaming(false);
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar expand="lg" className="px-4 py-3">
        <Navbar.Brand href="#home">Comp-Intel Agent</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link
              active={activeTab === 'research'}
              onClick={() => setActiveTab('research')}
            >
              Research
            </Nav.Link>
            <Nav.Link
              active={activeTab === 'ingest'}
              onClick={() => setActiveTab('ingest')}
            >
              Ingest
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Navbar>

      <Container fluid className="flex-grow-1 p-4">
        <Row className="h-100 justify-content-center">
          {activeTab === 'research' ? (
            <>
              {/* Left sidebar — form */}
              <Col lg={4} xl={3} className="mb-4 mb-lg-0">
                <Card className="h-100">
                  <Card.Header>New Analysis</Card.Header>
                  <Card.Body>
                    <ResearchForm
                      onReportGenerated={handleReportGenerated}
                      onStreamChunk={handleStreamChunk}
                      onResearchData={handleResearchData}
                      onStart={handleStart}
                      onStop={() => setIsStreaming(false)}
                    />
                  </Card.Body>
                </Card>
              </Col>

              {/* Right panel — research sources + report */}
              <Col lg={8} xl={9}>
                <ResearchPanel sources={researchSources} isStreaming={isStreaming} />
                <ReportView report={report} isStreaming={isStreaming} />
              </Col>
            </>
          ) : (
            <Col lg={6} xl={5}>
              <Card>
                <Card.Header>Document Ingestion</Card.Header>
                <Card.Body className="p-4">
                  <IngestForm />
                </Card.Body>
              </Card>
            </Col>
          )}
        </Row>
      </Container>
    </div>
  );
}

export default App;
