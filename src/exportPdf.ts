import type { ResearchReport } from "./types";

// jsPDF's bundled fonts are Latin-1. Normalize every external string to a safe
// printable subset so punctuation cannot become stretched, clipped, or null-padded.
const clean = (value: string) => value
  .replace(/[\u2018\u2019\u201A\u201B]/g, "'")
  .replace(/[\u201C\u201D\u201E\u201F]/g, '"')
  .replace(/[\u2010-\u2015\u2212]/g, "-")
  .replace(/\u00D7/g, "x")
  .replace(/[\u00A0\u202F]/g, " ")
  .normalize("NFKD")
  .replace(/[^\x20-\x7E\n]/g, " ")
  .replace(/[ \t]+/g, " ")
  .trim();

const money = (value: number | null) => {
  if (value == null) return "Unavailable";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
};

const pct = (value: number | null) => value == null ? "Unavailable" : `${(value * 100).toFixed(1)}%`;
const multiple = (value: number | null) => value == null ? "Unavailable" : `${value.toFixed(1)}x`;

export const safeMemoCopy = (report: ResearchReport) => {
  const copy = [report.summary, ...report.thesis, ...report.risks].join(" ");
  const exposesRawValues = /\b[a-z]+(?:_[a-z]+)+\b/.test(copy)
    || /(?<![\d])\d+\.\d{4,}(?![\d])/.test(copy)
    || /(?<![$\d,])\d{10,}(?:\.0)?\b/.test(copy);
  if (!exposesRawValues) return { summary: report.summary, thesis: report.thesis, risks: report.risks };

  const summary = `${report.ticker} is screened as ${report.verdict.toLowerCase()} with ${report.confidence.toLowerCase()} confidence. Revenue growth of ${pct(report.financials.revenue_growth)}, a ${pct(report.financials.gross_margin)} gross margin, and ${money(report.financials.free_cash_flow)} in free cash flow are balanced against a ${multiple(report.valuation.price_to_sales)} sales multiple.`;
  const thesis = [
    `Revenue was ${money(report.financials.revenue)} on the ${report.financials.basis_label.toLowerCase()} basis, with growth of ${pct(report.financials.revenue_growth)}.`,
    `Gross margin was ${pct(report.financials.gross_margin)} and operating margin was ${pct(report.financials.operating_margin)}.`,
    `Free cash flow was ${money(report.financials.free_cash_flow)}, compared with cash of ${money(report.financials.cash)} and debt of ${money(report.financials.debt)}.`,
    `The shares trade at ${multiple(report.valuation.pe)} earnings and ${multiple(report.valuation.price_to_sales)} sales.`,
  ];
  const risks = [
    "Review the latest filing's Risk Factors section for company-specific operating and regulatory exposures.",
    "The valuation may compress if reported growth or margins weaken.",
    "A limited reporting period may not represent the durability of demand, pricing, or cash generation.",
    "Peer multiples are a screening tool; business mix and accounting comparability can differ materially.",
  ];
  return { summary, thesis, risks };
};

export async function downloadResearchPdf(report: ResearchReport): Promise<string> {
  const { jsPDF } = await import("jspdf");
  const memo = safeMemoCopy(report);
  const doc = new jsPDF({ unit: "pt", format: "a4", compress: true });
  doc.setProperties({
    title: clean(`${report.company_name} (${report.ticker}) research report`),
    subject: "Evidence-led public equity research",
    author: "Ledger",
    creator: "Ledger Financial Research Agent",
  });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 54;
  const contentWidth = pageWidth - margin * 2;
  const ink = "#111827";
  const muted = "#657184";
  const blue = "#2563d9";
  const line = "#d8dee7";
  let y = margin;

  const addPage = () => { doc.addPage(); y = margin; };
  const ensureRoom = (height: number) => {
    if (y + height <= pageHeight - margin) return false;
    addPage();
    return true;
  };
  const rule = () => {
    doc.setDrawColor(line); doc.setLineWidth(0.6); doc.line(margin, y, pageWidth - margin, y); y += 18;
  };
  const label = (text: string) => {
    doc.setFont("helvetica", "bold"); doc.setFontSize(8); doc.setTextColor(muted);
    doc.text(clean(text).toUpperCase(), margin, y, { charSpace: 1.1 }); y += 16;
  };
  const heading = (text: string) => {
    doc.setFont("times", "normal"); doc.setFontSize(25); doc.setTextColor(ink);
    y += 16; doc.text(clean(text), margin, y); y += 32;
  };
  const section = (sectionLabel: string, title: string, minimumBodyHeight = 48) => {
    ensureRoom(80 + minimumBodyHeight);
    label(sectionLabel);
    heading(title);
  };
  const paragraph = (text: string, size = 10.5, indent = 0) => {
    doc.setFont("helvetica", "normal"); doc.setFontSize(size); doc.setTextColor(ink);
    const lines = doc.splitTextToSize(clean(text), contentWidth - indent);
    const height = lines.length * (size * 1.45);
    ensureRoom(height + 8);
    doc.text(lines, margin + indent, y, { lineHeightFactor: 1.45 });
    y += height + 8;
  };
  const numberedList = (items: string[], prefix = "") => {
    items.forEach((item, index) => {
      const safeItem = clean(item);
      doc.setFont("helvetica", "normal"); doc.setFontSize(10);
      const lines = doc.splitTextToSize(safeItem, contentWidth - 32);
      const itemHeight = Math.max(30, lines.length * 14.5 + 8);
      ensureRoom(itemHeight);
      doc.setFont("helvetica", "bold"); doc.setFontSize(8.5); doc.setTextColor(blue);
      doc.text(`${prefix}${index + 1}`.padStart(2, "0"), margin, y);
      doc.setFont("helvetica", "normal"); doc.setFontSize(10); doc.setTextColor(ink);
      doc.text(lines, margin + 32, y, { lineHeightFactor: 1.45 });
      y += itemHeight;
    });
  };

  doc.setFillColor(ink); doc.rect(margin, y, 28, 28, "F");
  doc.setFont("times", "normal"); doc.setFontSize(18); doc.setTextColor("#ffffff"); doc.text("L", margin + 9, y + 20);
  doc.setFont("helvetica", "bold"); doc.setFontSize(9); doc.setTextColor(ink); doc.text("LEDGER", margin + 40, y + 18, { charSpace: 1.8 });
  doc.setFont("helvetica", "normal"); doc.setTextColor(muted); doc.text(`PUBLIC EQUITY RESEARCH / ${report.generated_at.slice(0, 10)}`, pageWidth - margin, y + 18, { align: "right" });
  y += 54; rule(); label(`${report.company_name} / ${report.ticker}`); y += 18;
  doc.setFont("times", "normal"); doc.setFontSize(34); doc.setTextColor(ink); doc.text(clean(`${report.verdict} at today's price.`), margin, y); y += 44;
  paragraph(memo.summary, 11.5);

  ensureRoom(82);
  const metrics = [
    ["Share price", money(report.valuation.price)],
    ["Revenue growth", pct(report.financials.revenue_growth)],
    ["Gross margin", pct(report.financials.gross_margin)],
    ["P / E", multiple(report.valuation.pe)],
  ];
  const metricWidth = contentWidth / metrics.length;
  metrics.forEach(([metricLabel, value], index) => {
    const x = margin + index * metricWidth;
    doc.setDrawColor(line); doc.rect(x, y, metricWidth, 62);
    doc.setFont("helvetica", "bold"); doc.setFontSize(7.5); doc.setTextColor(muted); doc.text(metricLabel.toUpperCase(), x + 10, y + 16);
    doc.setFont("times", "normal"); doc.setFontSize(19); doc.setTextColor(ink); doc.text(clean(value), x + 10, y + 44);
  });
  y += 88;

  section("01 Investment case", "What the numbers say", 130); numberedList(memo.thesis); y += 8;

  ensureRoom(106);
  label("Report frame");
  const reportFrame = [
    ["Confidence", report.confidence, "Evidence basis", report.financials.basis_label],
    ["Market cap", money(report.valuation.market_cap), "Cited records", String(report.citations.length)],
  ];
  reportFrame.forEach(([leftLabel, leftValue, rightLabel, rightValue]) => {
    doc.setDrawColor(line); doc.line(margin, y + 22, pageWidth - margin, y + 22);
    doc.setFont("helvetica", "normal"); doc.setFontSize(8.5); doc.setTextColor(muted);
    doc.text(clean(leftLabel), margin, y + 13); doc.text(clean(rightLabel), margin + 264, y + 13);
    doc.setFont("helvetica", "bold"); doc.setTextColor(ink);
    doc.text(clean(leftValue), margin + 82, y + 13);
    doc.text(clean(rightValue), pageWidth - margin, y + 13, { align: "right" });
    y += 34;
  });
  y += 12;

  section("02 Financial profile", "Reported fundamentals", 150);
  const financialRows = [
    ["Evidence basis", report.financials.basis_label],
    ["Revenue", money(report.financials.revenue)],
    ["Free cash flow", money(report.financials.free_cash_flow)],
    ["Operating margin", pct(report.financials.operating_margin)],
    ["Net margin", pct(report.financials.net_margin)],
    ["Cash / debt", `${money(report.financials.cash)} / ${money(report.financials.debt)}`],
  ];
  financialRows.forEach(([rowLabel, value]) => {
    ensureRoom(28); doc.setDrawColor(line); doc.line(margin, y + 17, pageWidth - margin, y + 17);
    doc.setFont("helvetica", "normal"); doc.setFontSize(9); doc.setTextColor(muted); doc.text(clean(rowLabel), margin, y + 11);
    doc.setFont("helvetica", "bold"); doc.setTextColor(ink); doc.text(clean(value), pageWidth - margin, y + 11, { align: "right" }); y += 28;
  });
  y += 14;

  section("03 Relative valuation", "Verified peer comparison", 96);
  const columns = [margin, margin + 92, margin + 192, margin + 285, margin + 372, margin + 438];
  const headers = ["Company", "Market cap", "Growth", "Gross margin", "P / E", "P / S"];
  doc.setFont("helvetica", "bold"); doc.setFontSize(7.5); doc.setTextColor(muted);
  headers.forEach((header, index) => doc.text(header.toUpperCase(), columns[index], y)); y += 13;
  report.peers.forEach((peer) => {
    ensureRoom(25); doc.setDrawColor(line); doc.line(margin, y + 17, pageWidth - margin, y + 17);
    const values = [peer.ticker, money(peer.market_cap), pct(peer.revenue_growth), pct(peer.gross_margin), multiple(peer.pe), multiple(peer.price_to_sales)];
    doc.setFont("helvetica", peer.ticker === report.ticker ? "bold" : "normal"); doc.setFontSize(8.5); doc.setTextColor(peer.ticker === report.ticker ? blue : ink);
    values.forEach((value, index) => doc.text(clean(value), columns[index], y + 11)); y += 25;
  });
  y += 20;

  section("04 Risk register", "What could break the case", 120); numberedList(memo.risks, "R"); y += 8;
  ensureRoom(86); label("05 Methodology"); paragraph(report.methodology, 9.25); y += 8;

  const sourceWidth = contentWidth;
  section("06 Sources", "Evidence ledger", 96);
  report.citations.forEach((source, index) => {
    const x = margin;
    const textX = x + 25;
    doc.setFont("helvetica", "bold"); doc.setFontSize(8);
    const titleLines = doc.splitTextToSize(clean(source.label), sourceWidth - 25) as string[];
    doc.setFont("helvetica", "normal"); doc.setFontSize(7.25);
    const metadata = doc.splitTextToSize(clean(`${source.source} / retrieved ${source.retrieved_at.slice(0, 10)}`), sourceWidth - 25) as string[];
    doc.setFontSize(6.5);
    const urlLines = doc.splitTextToSize(clean(source.url), sourceWidth - 25) as string[];
    const sourceRowHeight = Math.max(54, titleLines.length * 10 + metadata.length * 9.5 + urlLines.length * 8.5 + 18);
    if (y + sourceRowHeight > pageHeight - margin) {
      addPage();
      label("06 Sources / continued");
      y += 4;
    }
    const rowY = y;
    doc.setFont("helvetica", "bold"); doc.setFontSize(8); doc.setTextColor(blue);
    doc.text(String(index + 1).padStart(2, "0"), x, rowY);
    doc.setTextColor(ink);
    titleLines.forEach((titleLine, lineIndex) => {
      doc.textWithLink(titleLine, textX, rowY + lineIndex * 10, { url: source.url });
    });
    doc.setFont("helvetica", "normal"); doc.setFontSize(7.25); doc.setTextColor(muted);
    const metadataY = rowY + titleLines.length * 10 + 3;
    doc.text(metadata, textX, metadataY, { lineHeightFactor: 1.3 });
    doc.setFontSize(6.5); doc.setTextColor(blue);
    const urlY = metadataY + metadata.length * 9.5 + 3;
    urlLines.forEach((urlLine, lineIndex) => {
      doc.textWithLink(urlLine, textX, urlY + lineIndex * 8.5, { url: source.url });
    });
    doc.setDrawColor(line); doc.line(textX, rowY + sourceRowHeight - 8, pageWidth - margin, rowY + sourceRowHeight - 8);
    y += sourceRowHeight;
  });

  const totalPages = doc.getNumberOfPages();
  for (let page = 1; page <= totalPages; page += 1) {
    doc.setPage(page);
    if (page > 1) {
      doc.setFont("helvetica", "bold"); doc.setFontSize(7.5); doc.setTextColor(muted);
      doc.text(clean(`LEDGER / ${report.ticker}`), margin, 28, { charSpace: 1.1 });
      doc.setFont("helvetica", "normal");
      doc.text(clean(report.generated_at.slice(0, 10)), pageWidth - margin, 28, { align: "right" });
      doc.setDrawColor(line); doc.line(margin, 40, pageWidth - margin, 40);
    }
    doc.setDrawColor(line); doc.line(margin, pageHeight - 34, pageWidth - margin, pageHeight - 34);
    doc.setFont("helvetica", "normal"); doc.setFontSize(7.5); doc.setTextColor(muted);
    doc.text("Research aid - verify primary filings before making a decision.", margin, pageHeight - 20);
    doc.text(`${page} / ${totalPages}`, pageWidth - margin, pageHeight - 20, { align: "right" });
  }

  const filename = `${report.ticker.toLowerCase()}-research-${report.generated_at.slice(0, 10)}.pdf`;
  doc.save(filename);
  return filename;
}
