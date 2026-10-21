import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDownRight,
  BookOpen,
  Check,
  ChevronRight,
  Clock3,
  Download,
  ExternalLink,
  FileText,
  MessageSquareText,
  Search,
  ShieldAlert,
  X,
} from "lucide-react";
import type { Peer, ResearchReport } from "./types";
import { ResearchChat } from "./ResearchChat";

const API = "/api";
const reportSections = ["conclusion", "financials", "valuation", "risks", "sources", "trace"];

const money = (value: number | null, compact = true) => {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: value > 1000 ? 1 : 2,
  }).format(value);
};

const pct = (value: number | null) =>
  value == null ? "—" : `${(value * 100).toFixed(1)}%`;

const multiple = (value: number | null) =>
  value == null ? "—" : `${value.toFixed(1)}×`;

function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone?: "good" | "warn" }) {
  return (
    <div className="metric">
      <span className="eyebrow">{label}</span>
      <strong className={tone ? `metric-value ${tone}` : "metric-value"}>{value}</strong>
      <span className="metric-note">{note}</span>
    </div>
  );
}

function PeerRow({ peer, anchor }: { peer: Peer; anchor: boolean }) {
  return (
    <tr className={anchor ? "anchor-row" : undefined}>
      <th scope="row">
        <span className="ticker-cell">{peer.ticker}</span>
        <small>{peer.name}</small>
      </th>
      <td>{money(peer.market_cap)}</td>
      <td>{pct(peer.revenue_growth)}</td>
      <td>{pct(peer.gross_margin)}</td>
      <td>{multiple(peer.pe)}</td>
      <td>{multiple(peer.price_to_sales)}</td>
      <td>{pct(peer.fcf_yield)}</td>
    </tr>
  );
}

function LoadingState({ ticker }: { ticker: string }) {
  const stages = ["Resolve company identity", "Read SEC filing facts", "Retrieve market price", "Calculate valuation", "Compare peers", "Write cited memo"];
  return (
    <main className="loading-state" aria-live="polite" aria-busy="true">
      <div className="loading-mark"><span /></div>
      <p className="eyebrow">Research run in progress</p>
      <h1>Building the evidence file for {ticker}.</h1>
      <div className="stage-list">
        {stages.map((stage, index) => (
          <div key={stage} style={{ animationDelay: `${index * 120}ms` }}>
            <span>{String(index + 1).padStart(2, "0")}</span>{stage}
          </div>
        ))}
      </div>
    </main>
  );
}

function App() {
  const [query, setQuery] = useState("NVDA");
  const [activeTicker, setActiveTicker] = useState("NVDA");
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState("conclusion");
  const [exportedFile, setExportedFile] = useState("");
  const [railMode, setRailMode] = useState<"chat" | "trace">("chat");
  const [mobileRailOpen, setMobileRailOpen] = useState(false);
  const tickerInput = useRef<HTMLInputElement>(null);
  const askButton = useRef<HTMLButtonElement>(null);

  const runResearch = async (ticker: string) => {
    const clean = ticker.trim().toUpperCase();
    if (!clean) return;
    setLoading(true);
    setError(null);
    setActiveTicker(clean);
    try {
      const response = await fetch(`${API}/research/${encodeURIComponent(clean)}`, { method: "POST" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Research run failed.");
      setReport(payload);
      setRailMode("chat");
      setMobileRailOpen(false);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Research run failed.");
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial retrieval intentionally begins when the browser client is ready.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void runResearch("NVDA");
  }, []);

  useEffect(() => {
    const sectionIds = reportSections.slice(0, -1);
    let animationFrame = 0;

    const syncSectionToScroll = () => {
      cancelAnimationFrame(animationFrame);
      animationFrame = requestAnimationFrame(() => {
        const pageBottom = window.scrollY + window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const isCompactLayout = window.innerWidth < 1180;

        if (pageBottom >= documentHeight - 2) {
          setActiveSection(isCompactLayout ? "trace" : sectionIds[sectionIds.length - 1]);
          return;
        }

        const anchor = Math.min(190, window.innerHeight * 0.28);
        let current = sectionIds[0];

        for (const sectionId of sectionIds) {
          const section = document.getElementById(sectionId);
          if (section && section.getBoundingClientRect().top <= anchor) current = sectionId;
        }

        if (isCompactLayout) {
          const trace = document.getElementById("trace");
          if (trace && trace.getBoundingClientRect().top <= anchor) current = "trace";
        }

        setActiveSection((previous) => previous === current ? previous : current);
      });
    };

    syncSectionToScroll();
    window.addEventListener("scroll", syncSectionToScroll, { passive: true });
    window.addEventListener("resize", syncSectionToScroll);
    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("scroll", syncSectionToScroll);
      window.removeEventListener("resize", syncSectionToScroll);
    };
  }, [report]);

  useEffect(() => {
    if (!mobileRailOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMobileRailOpen(false);
        askButton.current?.focus();
      }
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [mobileRailOpen]);

  const elapsed = useMemo(
    () => report?.trace.reduce((total, step) => total + step.latency_ms, 0) ?? 0,
    [report],
  );

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void runResearch(query);
  };

  const exportReport = () => {
    if (!report) return;
    const lines = [
      `# ${report.company_name} (${report.ticker})`,
      `Generated ${report.generated_at} UTC`,
      "",
      `## ${report.verdict}`,
      `Confidence: ${report.confidence}`,
      report.summary,
      "",
      "## Financials",
      `- Evidence basis: ${report.financials.basis_label}`,
      `- Source form: ${report.financials.source_form}`,
      `- Limited reporting history: ${report.financials.limited_history ? "Yes" : "No"}`,
      `- Revenue: ${money(report.financials.revenue, false)}`,
      `- Revenue growth: ${pct(report.financials.revenue_growth)}`,
      `- Gross margin: ${pct(report.financials.gross_margin)}`,
      `- Operating margin: ${pct(report.financials.operating_margin)}`,
      `- Net margin: ${pct(report.financials.net_margin)}`,
      `- Free cash flow: ${money(report.financials.free_cash_flow, false)}`,
      `- Cash: ${money(report.financials.cash, false)}`,
      `- Debt: ${money(report.financials.debt, false)}`,
      "",
      "## Investment case",
      ...report.thesis.map((item) => `- ${item}`),
      "",
      "## Peer comparison",
      "| Company | Market cap | Revenue growth | Gross margin | P/E | P/S | FCF yield |",
      "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
      ...report.peers.map((peer) => `| ${peer.ticker} | ${money(peer.market_cap)} | ${pct(peer.revenue_growth)} | ${pct(peer.gross_margin)} | ${multiple(peer.pe)} | ${multiple(peer.price_to_sales)} | ${pct(peer.fcf_yield)} |`),
      "",
      "## Risks",
      ...report.risks.map((item) => `- ${item}`),
      "",
      "## Methodology",
      report.methodology,
      "",
      `Model: ${report.model.enabled ? `${report.model.provider} / ${report.model.name}` : "Deterministic fallback (no model credits used)"}`,
      `Model tokens: ${report.model.input_tokens + report.model.output_tokens}`,
      "",
      "## Run trace",
      ...report.trace.map((step) => `- ${step.name}: ${step.status} (${step.latency_ms} ms) — ${step.detail}`),
      "",
      "## Sources",
      ...report.citations.map((source, index) => `${index + 1}. [${source.label}](${source.url}) — ${source.source}; retrieved ${source.retrieved_at}`),
    ];
    const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/markdown" }));
    const link = document.createElement("a");
    link.href = url;
    const filename = `${report.ticker.toLowerCase()}-research-${report.generated_at.slice(0, 10)}.md`;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    setExportedFile(filename);
  };

  return (
    <div className="app-shell">
      <header className="masthead">
        <a className="brand" href="#top" aria-label="Ledger home">
          <span className="brand-mark">L</span>
          <span>LEDGER</span>
        </a>
        <div className="product-label">Public equity research agent</div>
        <form className="ticker-search" onSubmit={submit} role="search">
          <Search size={16} aria-hidden="true" />
          <label className="sr-only" htmlFor="ticker">Company ticker</label>
          <input ref={tickerInput} id="ticker" value={query} onChange={(event) => setQuery(event.target.value.toUpperCase().replace(/[^A-Z0-9.-]/g, ""))} placeholder="AAPL or XNDU" maxLength={8} pattern="[A-Za-z][A-Za-z0-9.-]{0,7}" title="Enter an SEC-listed ticker such as AAPL or XNDU" required autoComplete="off" />
          <button type="submit" disabled={loading}>{loading ? "Running" : "Analyze"}<ChevronRight size={15} /></button>
        </form>
        <div className={`data-state ${error ? "failed" : loading ? "retrieving" : "live"}`}><span /> {error ? "Retrieval failed" : loading ? "Retrieving" : `Live · ${report?.valuation.as_of ?? "ready"}`}</div>
      </header>

      {loading ? <LoadingState ticker={activeTicker} /> : error ? (
        <main className="error-state" role="alert" aria-live="assertive">
          <ShieldAlert size={28} />
          <p className="eyebrow">Live retrieval failed</p>
          <h1>We could not complete this research run.</h1>
          <p>{error}</p>
          <button onClick={() => { tickerInput.current?.focus(); tickerInput.current?.select(); }}>Edit ticker</button>
        </main>
      ) : report ? (
        <div className="research-layout" id="top">
          <aside className="index-rail" aria-label="Report sections">
            <div className="rail-company">
              <span className="ticker-seal">{report.ticker.slice(0, 2)}</span>
              <div><strong>{report.ticker}</strong><small>{report.exchange}</small></div>
            </div>
            <nav>
              {reportSections.map((section, index) => (
                <a key={section} href={`#${section}`} className={activeSection === section ? "active" : ""} aria-current={activeSection === section ? "location" : undefined} onClick={() => setActiveSection(section)}>
                  <span>{String(index + 1).padStart(2, "0")}</span>{section}
                </a>
              ))}
            </nav>
            <div className="rail-foot">
              <span>Run {report.run_id.slice(0, 8)}</span>
              <span>{(elapsed / 1000).toFixed(1)}s total</span>
            </div>
          </aside>

          <nav className="mobile-report-nav" aria-label="Report sections">
            {reportSections.map((section) => <a key={section} href={`#${section}`} aria-current={activeSection === section ? "location" : undefined}>{section}</a>)}
          </nav>

          <main className="report">
            <section className="report-head" id="conclusion">
              <div className="report-kicker">
                <span>Equity research / {report.generated_at.slice(0, 10)}</span>
                <div className="report-actions">
                  <button ref={askButton} onClick={() => { setRailMode("chat"); setMobileRailOpen(true); }}><MessageSquareText size={15} /> Ask Ledger</button>
                  <button onClick={exportReport}><Download size={15} /> Export memo</button>
                </div>
              </div>
              <span className="sr-only" aria-live="polite">{exportedFile ? `Exported ${exportedFile}` : ""}</span>
              <p className="company-name">{report.company_name}</p>
              <h1>{report.verdict}<br /><em>at today’s price.</em></h1>
              <div className="verdict-line">
                <span className={`verdict-dot ${report.verdict.toLowerCase().replace(" ", "-")}`} />
                <p>{report.summary}</p>
                <div><span>Confidence</span><strong>{report.confidence}</strong></div>
              </div>
            </section>

            <section className="metric-band" aria-label="Key metrics">
              <Metric label="Share price" value={money(report.valuation.price, false)} note={`As of ${report.valuation.as_of}`} />
              <Metric label="Revenue growth" value={pct(report.financials.revenue_growth)} note={report.financials.basis_label} tone="good" />
              <Metric label="Gross margin" value={pct(report.financials.gross_margin)} note="Reported, GAAP" />
              <Metric label="P / E" value={multiple(report.valuation.pe)} note="Trailing reported earnings" tone="warn" />
            </section>

            <section className="memo-section thesis-section">
              <div className="section-number">01</div>
              <div className="section-title"><span className="eyebrow">Investment case</span><h2>What the numbers say</h2></div>
              <div className="thesis-list">
                {report.thesis.map((item, index) => (
                  <article key={item}><span>{String(index + 1).padStart(2, "0")}</span><p>{item}</p></article>
                ))}
              </div>
            </section>

            <section className="memo-section" id="financials">
              <div className="section-number">02</div>
              <div className="section-title"><span className="eyebrow">Financial profile</span><h2>Growth with a cash engine</h2></div>
              <div className="financial-grid">
                <div><span>Revenue</span><strong>{money(report.financials.revenue)}</strong><small>{report.financials.basis_label}</small></div>
                <div><span>Free cash flow</span><strong>{money(report.financials.free_cash_flow)}</strong><small>Operating cash less capex</small></div>
                <div><span>Operating margin</span><strong>{pct(report.financials.operating_margin)}</strong><small>Reported, GAAP</small></div>
                <div><span>Net margin</span><strong>{pct(report.financials.net_margin)}</strong><small>Reported, GAAP</small></div>
                <div><span>Cash</span><strong>{money(report.financials.cash)}</strong><small>Latest reported balance</small></div>
                <div><span>Debt</span><strong>{money(report.financials.debt)}</strong><small>Current + long-term debt</small></div>
              </div>
              <p className={`basis-note ${report.financials.limited_history ? "limited" : ""}`}>
                <BookOpen size={16} />
                <span><strong>{report.financials.source_form}</strong> · {report.financials.basis_label}.{report.financials.limited_history ? " Limited-history mode caps confidence at Low." : ""}</span>
              </p>
            </section>

            <section className="memo-section" id="valuation">
              <div className="section-number">03</div>
              <div className="section-title"><span className="eyebrow">Relative valuation</span><h2>The premium in context</h2></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Company</th><th>Market cap</th><th>Revenue growth</th><th>Gross margin</th><th>P / E</th><th>P / S</th><th>FCF yield</th></tr></thead>
                  <tbody>{report.peers.map((peer) => <PeerRow key={peer.ticker} peer={peer} anchor={peer.ticker === report.ticker} />)}</tbody>
                </table>
              </div>
              <p className="table-hint">Swipe horizontally to compare all seven metrics.</p>
              <p className="method-note"><BookOpen size={16} /> {report.methodology}</p>
            </section>

            <section className="memo-section risks-section" id="risks">
              <div className="section-number">04</div>
              <div className="section-title"><span className="eyebrow">Risk register</span><h2>What could break the case</h2></div>
              <div className="risk-list">
                {report.risks.map((risk, index) => <article key={risk}><span>R{index + 1}</span><p>{risk}</p><ArrowDownRight size={19} /></article>)}
              </div>
            </section>

            <section className="memo-section sources-section" id="sources">
              <div className="section-number">05</div>
              <div className="section-title"><span className="eyebrow">Evidence ledger</span><h2>Primary sources</h2></div>
              <div className="source-list">
                {report.citations.map((citation) => (
                  <a key={citation.url} href={citation.url} target="_blank" rel="noreferrer">
                    <FileText size={18} /><div><strong>{citation.label}</strong><span>{citation.source} · retrieved {citation.retrieved_at.slice(0, 10)}</span></div><ExternalLink size={16} />
                  </a>
                ))}
              </div>
            </section>
          </main>

          <aside className={`evidence-rail ${mobileRailOpen ? "rail-open" : ""}`} id="trace" aria-label="Research assistant and run trace">
            <div className="rail-controls">
              <div role="tablist" aria-label="Evidence rail">
                <button role="tab" aria-selected={railMode === "chat"} onClick={() => setRailMode("chat")}><MessageSquareText size={14} /> Ask</button>
                <button role="tab" aria-selected={railMode === "trace"} onClick={() => setRailMode("trace")}><FileText size={14} /> Trace</button>
              </div>
              <button className="rail-close" type="button" onClick={() => { setMobileRailOpen(false); askButton.current?.focus(); }} aria-label="Close research assistant"><X size={18} /></button>
            </div>
            {railMode === "chat" ? <ResearchChat key={report.run_id} report={report} focusComposer={mobileRailOpen} /> : <>
              <div className="trace-head"><FileText size={17} /><div><h2 id="trace-title">Run trace</h2><span>Public data only</span></div></div>
              <div className="trace-list">
                {report.trace.map((step, index) => (
                  <div key={step.name}>
                    <span className="trace-icon">{step.status === "completed" ? <Check size={13} /> : "!"}<span className="sr-only">{step.status}</span></span>
                    <div><strong>{step.name}</strong><p>{step.detail}</p><small><Clock3 size={11} /> {step.latency_ms} ms</small></div>
                    {index < report.trace.length - 1 && <i />}
                  </div>
                ))}
              </div>
              <div className="run-stats">
                <span>Model<strong>{report.model.enabled ? report.model.name : "Fallback"}</strong></span>
                <span>Model tokens<strong>{(report.model.input_tokens + report.model.output_tokens).toLocaleString()}</strong></span>
                <span>Sources<strong>{report.citations.length}</strong></span>
                <span>Failed steps<strong>{report.trace.filter((step) => step.status === "failed").length}</strong></span>
              </div>
              {report.model.fallback_reason && <p className="model-note">{report.model.fallback_reason}</p>}
              <p className="disclaimer">Research aid, not investment advice. Verify primary filings before making a decision.</p>
            </>}
          </aside>
        </div>
      ) : null}
    </div>
  );
}

export default App;
