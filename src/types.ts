export type Citation = {
  label: string;
  url: string;
  source: string;
  retrieved_at: string;
};

export type Financials = {
  fiscal_year: number;
  period_end: string;
  basis: "annual" | "ttm" | "prospectus" | "interim_annualized";
  basis_label: string;
  source_form: string;
  source_url: string | null;
  limited_history: boolean;
  revenue: number | null;
  revenue_growth: number | null;
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  free_cash_flow: number | null;
  cash: number | null;
  debt: number | null;
};

export type Valuation = {
  price: number | null;
  market_cap: number | null;
  pe: number | null;
  price_to_sales: number | null;
  fcf_yield: number | null;
  as_of: string;
};

export type Peer = {
  ticker: string;
  name: string;
  price: number | null;
  market_cap: number | null;
  revenue_growth: number | null;
  gross_margin: number | null;
  pe: number | null;
  price_to_sales: number | null;
  fcf_yield: number | null;
};

export type TraceStep = {
  name: string;
  status: "completed" | "failed";
  latency_ms: number;
  detail: string;
};

export type ModelRun = {
  enabled: boolean;
  provider: string;
  name: string;
  input_tokens: number;
  output_tokens: number;
  fallback_reason: string | null;
};

export type ResearchReport = {
  run_id: string;
  ticker: string;
  company_name: string;
  exchange: string;
  generated_at: string;
  verdict: "Undervalued" | "Fairly valued" | "Expensive" | "Insufficient evidence";
  confidence: "Low" | "Moderate" | "High";
  summary: string;
  thesis: string[];
  risks: string[];
  financials: Financials;
  valuation: Valuation;
  peers: Peer[];
  citations: Citation[];
  trace: TraceStep[];
  model: ModelRun;
  methodology: string;
};

export type ChatEvidence = {
  fact_id: string;
  label: string;
  value: string;
  source_ids: string[];
};

export type ChatResponse = {
  run_id: string;
  ticker: string;
  answer: string;
  evidence: ChatEvidence[];
  citations: Citation[];
  suggested_questions: string[];
  model: ModelRun;
};
