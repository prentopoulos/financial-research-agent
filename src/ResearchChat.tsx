import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { ArrowUp, ExternalLink, RotateCcw } from "lucide-react";
import type { ChatEvidence, ChatResponse, Citation, ResearchReport } from "./types";

type Message = {
  role: "user" | "assistant";
  content: string;
  evidence?: ChatEvidence[];
  citations?: Citation[];
  modelLabel?: string;
};

const starterQuestions = (ticker: string) => [
  `Why did ${ticker} receive this valuation verdict?`,
  "How does revenue growth compare with the selected peers?",
  "What are the biggest evidence limitations?",
];

export function ResearchChat({ report, focusComposer = false }: { report: ResearchReport; focusComposer?: boolean }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [suggestions, setSuggestions] = useState(starterQuestions(report.ticker));
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const transcript = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    transcript.current?.scrollTo({ top: transcript.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  useEffect(() => {
    if (focusComposer) composer.current?.focus();
  }, [focusComposer]);

  const ask = async (question: string) => {
    const clean = question.trim();
    if (!clean || pending) return;
    const history = messages.map(({ role, content }) => ({ role, content })).slice(-8);
    const userMessage: Message = { role: "user", content: clean };
    setMessages((current) => [...current, userMessage]);
    setDraft("");
    setError("");
    setPending(true);
    try {
      const response = await fetch(`/api/research/${report.run_id}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: clean, history }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "The research assistant could not answer.");
      const result = payload as ChatResponse;
      setMessages((current) => [...current, {
        role: "assistant",
        content: result.answer,
        evidence: result.evidence,
        citations: result.citations,
        modelLabel: result.model.enabled ? `${result.model.name} · evidence verified` : "Deterministic · report facts only",
      }]);
      setSuggestions(result.suggested_questions);
    } catch (reason) {
      setMessages((current) => current.slice(0, -1));
      setError(reason instanceof Error ? reason.message : "The research assistant could not answer.");
    } finally {
      setPending(false);
    }
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void ask(draft);
  };

  const keyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void ask(draft);
    }
  };

  const clear = () => {
    setMessages([]);
    setSuggestions(starterQuestions(report.ticker));
    setError("");
    setDraft("");
  };

  return (
    <div className="research-chat">
      <div className="chat-intro">
        <div>
          <span>Report-scoped analyst</span>
          <strong>Ask about {report.ticker}</strong>
        </div>
        {messages.length > 0 && <button type="button" onClick={clear} aria-label="Clear conversation"><RotateCcw size={14} /> Clear</button>}
      </div>

      <div className="ontology-strip" aria-label="Available research context">
        <span>Company</span><span>Financials</span><span>Valuation</span><span>Peers</span><span>Risks</span><span>Sources</span>
      </div>

      <div className="chat-transcript" ref={transcript} aria-live="polite">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>Questions are answered from this report’s verified facts and evidence ledger.</p>
            <small>No browsing, trading, uploads, or persistent conversation memory.</small>
          </div>
        ) : messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className={`chat-message ${message.role}`}>
            <span>{message.role === "user" ? "You" : "Ledger"}</span>
            <p>{message.content}</p>
            {message.evidence && message.evidence.length > 0 && (
              <details>
                <summary>Evidence used · {message.evidence.length}</summary>
                <div className="chat-evidence">
                  {message.evidence.map((fact) => <div key={fact.fact_id}><span>{fact.label}</span><strong>{fact.value}</strong></div>)}
                </div>
              </details>
            )}
            {message.citations && message.citations.length > 0 && (
              <div className="chat-citations">
                {message.citations.map((citation, citationIndex) => (
                  <a key={citation.url} href={citation.url} target="_blank" rel="noreferrer" title={citation.label}>
                    {citationIndex + 1}<ExternalLink size={10} />
                  </a>
                ))}
              </div>
            )}
            {message.modelLabel && <small className="chat-model">{message.modelLabel}</small>}
          </article>
        ))}
        {pending && <div className="chat-thinking"><span /><span /><span /><em>Checking the report ontology</em></div>}
      </div>

      {error && <p className="chat-error" role="alert">{error}</p>}

      <div className="chat-suggestions" aria-label="Suggested questions">
        {suggestions.map((suggestion) => <button type="button" key={suggestion} onClick={() => void ask(suggestion)} disabled={pending}>{suggestion}</button>)}
      </div>

      <form className="chat-composer" onSubmit={submit}>
        <label className="sr-only" htmlFor="research-question">Ask about this report</label>
        <textarea
          ref={composer}
          id="research-question"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={keyDown}
          placeholder={`Ask about ${report.ticker}…`}
          maxLength={600}
          rows={2}
          disabled={pending}
        />
        <button type="submit" disabled={pending || !draft.trim()} aria-label="Send question"><ArrowUp size={17} /></button>
      </form>
      <p className="chat-boundary">Public report context only · 24 questions per run · Shift+Enter for a new line</p>
    </div>
  );
}
