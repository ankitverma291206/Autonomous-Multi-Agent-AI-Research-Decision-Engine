"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

type Report = {
  id: string;
  query: string;
  summary: string;
  recommendation: string;
  key_factors: string[];
  assumptions: string[];
  risks: string[];
  confidence: "low" | "medium" | "high";
  sources: { title: string; url: string }[];
  evidence_notice: string;
  mode: string;
  created_at: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [query, setQuery] = useState("");
  const [reports, setReports] = useState<Report[]>([]);
  const [selected, setSelected] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refreshReports = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/api/reports`, { cache: "no-store" });
      if (!response.ok) throw new Error("Could not load saved reports.");
      const data = await response.json();
      setReports(data.reports);
      if (data.reports.length) setSelected((current) => current ?? data.reports[0]);
    } catch {
      setError("Could not reach the API. Start the services with docker compose up --build.");
    }
  }, []);

  useEffect(() => { void refreshReports(); }, [refreshReports]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${apiUrl}/api/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error?.message ?? data.error?.details?.[0]?.message ?? "Report could not be created.");
      setSelected(data);
      setQuery("");
      await refreshReports();
      setSelected(data);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#"><span className="brand-mark">F</span><span>fieldnote<span className="brand-dot">.</span></span></a>
        <div className="top-meta"><span className="status-dot" /> Research workspace <span className="meta-divider">/</span> v0.1</div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-heading"><span>WORKSPACE</span><span className="count">{reports.length.toString().padStart(2, "0")}</span></div>
          <button className="new-button" onClick={() => { setSelected(null); setError(""); window.scrollTo({ top: 0, behavior: "smooth" }); }}><span>＋</span> New research brief</button>
          <div className="history-label">RECENT REPORTS</div>
          <nav className="report-list" aria-label="Saved reports">
            {reports.length === 0 && <p className="empty-history">Your saved reports will appear here.</p>}
            {reports.map((report) => (
              <button key={report.id} className={`history-item ${selected?.id === report.id ? "active" : ""}`} onClick={() => setSelected(report)}>
                <span className="history-icon">↗</span><span className="history-copy"><span className="history-title">{report.query}</span><span className="history-date">{new Date(report.created_at).toLocaleDateString()}</span></span>
              </button>
            ))}
          </nav>
          <div className="sidebar-bottom"><div className="avatar">AI</div><div><strong>Research engine</strong><span>Decision support · Preview</span></div></div>
        </aside>

        <section className="main-panel">
          <div className="content-wrap">
            <div className="eyebrow"><span className="eyebrow-line" /> EVIDENCE-LED DECISION SUPPORT</div>
            <h1>Make your next<br /><em>move with clarity.</em></h1>
            <p className="intro">Bring a complex question. Get a clear starting point for the research, risks, and decisions ahead.</p>

            <form className="query-card" onSubmit={submit}>
              <label htmlFor="research-query">WHAT ARE YOU TRYING TO DECIDE?</label>
              <textarea id="research-query" value={query} onChange={(event) => setQuery(event.target.value)} minLength={10} maxLength={2000} required placeholder="e.g. Should a mid-sized logistics company electrify its urban delivery fleet over the next five years?" />
              <div className="query-footer"><span>{query.length}/2000 characters</span><button className="submit-button" type="submit" disabled={busy || query.trim().length < 10}>{busy ? <><span className="spinner" /> Preparing brief</> : <>Build decision brief <span>↗</span></>}</button></div>
            </form>
            {error && <div className="error-banner" role="alert">{error}</div>}

            {selected ? <ReportView report={selected} /> : <div className="starter-note"><span className="sparkle">✳</span><div><strong>A useful first step, not the final answer.</strong><p>Start with a focused question. Your brief will organize the decision and surface what still needs evidence.</p></div></div>}
            <footer className="page-foot"><span>FIELDNOTE RESEARCH ENGINE</span><span>AI-generated analysis · Verify before deciding</span></footer>
          </div>
        </section>
      </div>
    </main>
  );
}

function ReportView({ report }: { report: Report }) {
  return (
    <article className="report-card">
      <div className="report-head"><div><div className="report-kicker">DECISION BRIEF <span>·</span> {new Date(report.created_at).toLocaleString()}</div><h2>{report.query}</h2></div><span className={`confidence confidence-${report.confidence}`}><span /> {report.confidence} confidence</span></div>
      <div className="summary-block"><div className="section-label">THE QUESTION</div><p>{report.summary}</p></div>
      <div className="recommendation"><div className="section-label">RECOMMENDED NEXT STEP</div><p>{report.recommendation}</p></div>
      <div className="report-columns"><div><div className="section-label">FACTORS TO WEIGH</div><ul>{report.key_factors.map((item, index) => <li key={item}><span className="list-index">0{index + 1}</span>{item}</li>)}</ul></div><div><div className="section-label">ASSUMPTIONS & RISKS</div><ul>{[...report.assumptions, ...report.risks].map((item, index) => <li key={item}><span className="bullet">•</span>{item}</li>)}</ul></div></div>
      <div className="evidence-note"><span className="note-icon">!</span><div><strong>Evidence status</strong><p>{report.evidence_notice}</p></div></div>
      <div className="report-foot"><span>GENERATED IN {report.mode.toUpperCase()} MODE</span><span>{report.sources.length} verified sources</span></div>
    </article>
  );
}
