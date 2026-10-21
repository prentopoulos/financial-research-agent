"""Generate Ledger's four branded, self-contained documentation diagrams."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"

TOKENS = """
  <style>
    .paper{fill:#fff}.dots{fill:url(#dots);opacity:.38}.zone{fill:#f8fafc;stroke:#d9e1ec;stroke-width:1}
    .zone-title{font:600 9px 'DM Sans',Arial,sans-serif;letter-spacing:1.8px;fill:#53657d}
    .title{font:400 34px 'Instrument Serif',Georgia,serif;fill:#0e131c}.subtitle{font:400 12px 'DM Sans',Arial,sans-serif;fill:#53657d}
    .node{fill:#fff;stroke:#0e131c;stroke-width:1}.node-soft{fill:#f8fafc;stroke:#9aa8ba;stroke-width:1}
    .node-focus{fill:#edf3fc;stroke:#306bd9;stroke-width:1.4}.node-dash{fill:#fff;stroke:#9aa8ba;stroke-width:1;stroke-dasharray:5 4}
    .tag{fill:none;stroke:#9aa8ba;stroke-width:.8}.tag-focus{fill:none;stroke:#306bd9;stroke-width:.8}
    .tag-text{font:600 7px 'DM Sans',Arial,sans-serif;letter-spacing:1px;fill:#53657d}.tag-text-focus{fill:#306bd9}
    .node-name{font:600 13px 'DM Sans',Arial,sans-serif;fill:#0e131c}.node-sub{font:400 9px 'DM Sans',Arial,sans-serif;fill:#53657d}
    .connector{fill:none;stroke:#66768b;stroke-width:1.15;marker-end:url(#arrow)}.connector-link{fill:none;stroke:#306bd9;stroke-width:1.25;marker-end:url(#arrow-blue)}
    .connector-dash{fill:none;stroke:#66768b;stroke-width:1;stroke-dasharray:5 4;marker-end:url(#arrow)}
    .edge-mask{fill:#fff}.edge-label{font:600 7px 'DM Sans',Arial,sans-serif;letter-spacing:.8px;fill:#53657d;text-anchor:middle}
    .rule{stroke:#d9e1ec;stroke-width:1}.small{font:400 9px 'DM Sans',Arial,sans-serif;fill:#53657d}.strong{font-weight:600;fill:#0e131c}
  </style>
"""

DEFS = """
  <defs>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#d9e1ec"/></pattern>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><path d="M0 0L8 3L0 6Z" fill="#66768b"/></marker>
    <marker id="arrow-blue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><path d="M0 0L8 3L0 6Z" fill="#306bd9"/></marker>
  </defs>
"""


def html(title: str, eyebrow: str, svg: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&amp;family=Instrument+Serif:ital@0;1&amp;display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:40px;background:#fff;color:#0e131c;font-family:'DM Sans',Arial,sans-serif}}main{{width:min(1200px,100%)}}p{{margin:0 0 8px;color:#53657d;font-size:11px;font-weight:600;letter-spacing:.16em;text-transform:uppercase}}h1{{margin:0 0 24px;font:400 36px/1.05 'Instrument Serif',Georgia,serif}}svg{{display:block;width:100%;min-width:900px}}</style>
</head><body><main><p>{eyebrow}</p><h1>{title}</h1>{svg}</main></body></html>
"""


ARCHITECTURE = f"""<svg viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="arch-title arch-desc">
<title id="arch-title">Ledger system architecture</title><desc id="arch-desc">Browser requests enter a local FastAPI and LangGraph runtime. Python owns financial calculations and the verdict. Public evidence, OpenAI, and optional LangSmith tracing remain external services.</desc>
{DEFS}{TOKENS}<rect class="paper" width="1000" height="560"/><rect class="dots" width="1000" height="560"/>
<text x="40" y="48" class="title">A bounded research system</text><text x="40" y="72" class="subtitle">The model can explain evidence. It cannot author figures or the verdict.</text>
<rect x="32" y="104" width="168" height="360" rx="8" class="zone"/><text x="48" y="128" class="zone-title">CLIENT</text>
<rect x="232" y="104" width="520" height="360" rx="8" class="zone"/><text x="248" y="128" class="zone-title">LOCAL LEDGER RUNTIME</text>
<rect x="784" y="104" width="184" height="360" rx="8" class="zone"/><text x="800" y="128" class="zone-title">PUBLIC SERVICES</text>

<path d="M168 268H276" class="connector-link"/><path d="M436 184H476V172H520" class="connector"/><path d="M436 196H488V260H520" class="connector"/><path d="M436 208H500V348H520" class="connector"/>
<path d="M808 192H736V172H688" class="connector-link"/><path d="M608 204V300H436" class="connector"/><path d="M436 332H480V188H520" class="connector-dash"/>
<path d="M808 292H724V184H688" class="connector-dash"/><path d="M808 304H736V260H688" class="connector-link"/><path d="M808 316H748V348H688" class="connector-link"/>
<path d="M436 212V424H808" class="connector-dash"/>
<rect x="194" y="250" width="64" height="14" class="edge-mask"/><text x="226" y="260" class="edge-label">HTTPS JSON</text>
<rect x="710" y="156" width="72" height="14" class="edge-mask"/><text x="746" y="166" class="edge-label">SEC + PRICES</text>
<rect x="710" y="288" width="58" height="14" class="edge-mask"/><text x="739" y="298" class="edge-label">MODEL API</text>
<rect x="586" y="410" width="56" height="14" class="edge-mask"/><text x="614" y="420" class="edge-label">TRACES</text>

<g><rect x="56" y="232" width="112" height="72" rx="6" class="node-soft"/><rect x="66" y="242" width="28" height="13" rx="2" class="tag"/><text x="80" y="252" text-anchor="middle" class="tag-text">USER</text><text x="112" y="275" text-anchor="middle" class="node-name">Browser</text><text x="112" y="291" text-anchor="middle" class="node-sub">React dashboard</text></g>
<g><rect x="276" y="164" width="160" height="64" rx="6" class="node-focus"/><rect x="286" y="174" width="32" height="13" rx="2" class="tag-focus"/><text x="302" y="184" text-anchor="middle" class="tag-text tag-text-focus">API</text><text x="356" y="199" text-anchor="middle" class="node-name">FastAPI gateway</text><text x="356" y="215" text-anchor="middle" class="node-sub">guards + run store</text></g>
<g><rect x="276" y="300" width="160" height="64" rx="6" class="node"/><rect x="286" y="310" width="44" height="13" rx="2" class="tag"/><text x="308" y="320" text-anchor="middle" class="tag-text">CODE</text><text x="356" y="335" text-anchor="middle" class="node-name">Python analysis</text><text x="356" y="351" text-anchor="middle" class="node-sub">metrics + verdict</text></g>
<g><rect x="520" y="140" width="168" height="64" rx="6" class="node"/><text x="604" y="171" text-anchor="middle" class="node-name">Research graph</text><text x="604" y="188" text-anchor="middle" class="node-sub">retrieve + compare + write</text></g>
<g><rect x="520" y="228" width="168" height="64" rx="6" class="node"/><text x="604" y="259" text-anchor="middle" class="node-name">Report chat</text><text x="604" y="276" text-anchor="middle" class="node-sub">verified snapshot only</text></g>
<g><rect x="520" y="316" width="168" height="64" rx="6" class="node"/><text x="604" y="347" text-anchor="middle" class="node-name">Explore graph</text><text x="604" y="364" text-anchor="middle" class="node-sub">one cited web search</text></g>
<g><rect x="808" y="152" width="136" height="80" rx="6" class="node-soft"/><text x="876" y="184" text-anchor="middle" class="node-name">Evidence APIs</text><text x="876" y="202" text-anchor="middle" class="node-sub">SEC EDGAR + prices</text><text x="876" y="217" text-anchor="middle" class="node-sub">public, live</text></g>
<g><rect x="808" y="272" width="136" height="64" rx="6" class="node-soft"/><text x="876" y="302" text-anchor="middle" class="node-name">OpenAI</text><text x="876" y="319" text-anchor="middle" class="node-sub">optional language layer</text></g>
<g><rect x="808" y="392" width="136" height="64" rx="6" class="node-dash"/><text x="876" y="421" text-anchor="middle" class="node-name">LangSmith</text><text x="876" y="438" text-anchor="middle" class="node-sub">optional observability</text></g>
<line x1="40" y1="496" x2="960" y2="496" class="rule"/><text x="40" y="520" class="small strong">Ownership rule</text><text x="136" y="520" class="small">Python calculates. LangGraph routes. Models interpret. Sources prove.</text>
</svg>"""


DATA_FLOW = f"""<svg viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="flow-title flow-desc">
<title id="flow-title">Ledger research data flow</title><desc id="flow-desc">A ticker becomes a cited report through live public evidence, normalized periods, Python calculations, peer verification, and optional model-assisted writing.</desc>
{DEFS}{TOKENS}<rect class="paper" width="1000" height="560"/><rect class="dots" width="1000" height="560"/>
<text x="40" y="48" class="title">From ticker to cited report</text><text x="40" y="72" class="subtitle">Every number keeps its source, reporting period, and retrieval time.</text>
<rect x="32" y="112" width="936" height="104" fill="#f8fafc"/><rect x="32" y="216" width="936" height="136" fill="#fff"/><rect x="32" y="352" width="936" height="112" fill="#f8fafc"/>
<line x1="32" y1="112" x2="968" y2="112" class="rule"/><line x1="32" y1="216" x2="968" y2="216" class="rule"/><line x1="32" y1="352" x2="968" y2="352" class="rule"/><line x1="32" y1="464" x2="968" y2="464" class="rule"/>
<text x="48" y="136" class="zone-title">PUBLIC EVIDENCE</text><text x="48" y="240" class="zone-title">DETERMINISTIC ANALYSIS</text><text x="48" y="376" class="zone-title">LANGUAGE + DELIVERY</text>
<path d="M188 168H236" class="connector-link"/><path d="M372 168H412V280H456" class="connector-link"/><path d="M592 280H636" class="connector"/><path d="M772 280H840" class="connector"/><path d="M892 312V368" class="connector"/><path d="M704 368V328H824V292H840" class="connector-dash"/><path d="M772 400H840" class="connector-dash"/>
<rect x="194" y="151" width="36" height="14" class="edge-mask"/><text x="212" y="161" class="edge-label">LOOKUP</text><rect x="392" y="202" width="48" height="14" class="edge-mask"/><text x="416" y="212" class="edge-label">FACTS</text><rect x="598" y="263" width="32" height="14" class="edge-mask"/><text x="614" y="273" class="edge-label">RATIOS</text><rect x="784" y="352" width="48" height="14" class="edge-mask"/><text x="808" y="362" class="edge-label">VERIFIED</text>
<g><rect x="64" y="144" width="124" height="48" rx="6" class="node-soft"/><text x="126" y="166" text-anchor="middle" class="node-name">Ticker</text><text x="126" y="182" text-anchor="middle" class="node-sub">user input</text></g>
<g><rect x="236" y="136" width="136" height="64" rx="6" class="node"/><text x="304" y="164" text-anchor="middle" class="node-name">Retrieve</text><text x="304" y="181" text-anchor="middle" class="node-sub">SEC + market history</text><text x="304" y="194" text-anchor="middle" class="node-sub">live public endpoints</text></g>
<g><rect x="456" y="248" width="136" height="64" rx="6" class="node"/><text x="524" y="276" text-anchor="middle" class="node-name">Normalize periods</text><text x="524" y="293" text-anchor="middle" class="node-sub">annual + quarterly facts</text><text x="524" y="306" text-anchor="middle" class="node-sub">Python</text></g>
<g><rect x="636" y="248" width="136" height="64" rx="6" class="node-focus"/><text x="704" y="276" text-anchor="middle" class="node-name">Calculate + decide</text><text x="704" y="293" text-anchor="middle" class="node-sub">ratios + valuation verdict</text><text x="704" y="306" text-anchor="middle" class="node-sub">Python owns output</text></g>
<g><rect x="840" y="248" width="104" height="64" rx="6" class="node"/><text x="892" y="276" text-anchor="middle" class="node-name">Verify peers</text><text x="892" y="293" text-anchor="middle" class="node-sub">resolve + retrieve</text><text x="892" y="306" text-anchor="middle" class="node-sub">no invented values</text></g>
<g><rect x="636" y="368" width="136" height="64" rx="6" class="node-dash"/><text x="704" y="396" text-anchor="middle" class="node-name">Model writer</text><text x="704" y="413" text-anchor="middle" class="node-sub">optional prose + peers</text><text x="704" y="426" text-anchor="middle" class="node-sub">cannot alter figures</text></g>
<g><rect x="840" y="368" width="104" height="64" rx="6" class="node-focus"/><text x="892" y="396" text-anchor="middle" class="node-name">Cited report</text><text x="892" y="413" text-anchor="middle" class="node-sub">web + MD + PDF</text><text x="892" y="426" text-anchor="middle" class="node-sub">chat-ready snapshot</text></g>
<line x1="40" y1="496" x2="960" y2="496" class="rule"/><text x="40" y="520" class="small strong">Failure behavior</text><text x="144" y="520" class="small">Missing evidence lowers confidence or stops the report; it is never filled with simulated company data.</text>
</svg>"""


# A Venn view makes the access-triangle rule legible at README scale. The matrix
# beside it preserves the exact runtime configuration for each live workflow.
SECURITY = f"""<svg viewBox="0 0 1000 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="security-title security-desc">
<title id="security-title">Ledger access triangle and runtime matrix</title><desc id="security-desc">Three overlapping capability sets show that a session may combine at most two. The shared center is blocked. The matrix shows that current modes accept bounded input and use approved egress without sensitive data.</desc>
{DEFS}{TOKENS}<rect class="paper" width="1000" height="560"/><rect class="dots" width="1000" height="560"/>
<text x="40" y="48" class="title">Two capabilities maximum</text><text x="40" y="72" class="subtitle">The three-way overlap never starts. Current modes operate only in the input + egress intersection.</text>

<text x="40" y="116" class="zone-title">ACCESS TRIANGLE / VENN VIEW</text>
<circle cx="180" cy="224" r="104" fill="#edf3fc" fill-opacity=".86" stroke="#306bd9" stroke-width="1.2"/>
<circle cx="116" cy="324" r="104" fill="#f8fafc" fill-opacity=".88" stroke="#9aa8ba" stroke-width="1.2"/>
<circle cx="244" cy="324" r="104" fill="#fff" fill-opacity=".76" stroke="#0e131c" stroke-width="1.2"/>
<text x="180" y="166" text-anchor="middle" class="node-name">Untrusted input</text><text x="180" y="183" text-anchor="middle" class="node-sub">bounded questions + tickers</text>
<text x="82" y="352" text-anchor="middle" class="node-name">Sensitive data</text><text x="82" y="369" text-anchor="middle" class="node-sub">absent today</text>
<text x="278" y="352" text-anchor="middle" class="node-name">Way out</text><text x="278" y="369" text-anchor="middle" class="node-sub">approved HTTPS</text>
<circle cx="180" cy="292" r="42" fill="#306bd9" stroke="#0e131c" stroke-width="1"/>
<text x="180" y="288" text-anchor="middle" font-family="'DM Sans',Arial,sans-serif" font-size="12" font-weight="700" fill="#fff">3 / 3</text><text x="180" y="306" text-anchor="middle" font-family="'DM Sans',Arial,sans-serif" font-size="9" font-weight="600" letter-spacing="1" fill="#fff">BLOCKED</text>
<rect x="116" y="440" width="128" height="40" rx="6" class="node-focus"/><text x="180" y="457" text-anchor="middle" class="node-name">Any 2 / 3 allowed</text><text x="180" y="472" text-anchor="middle" class="node-sub">enforced at runtime</text>

<rect x="380" y="116" width="580" height="336" rx="8" fill="#fff" stroke="#d9e1ec"/>
<rect x="380" y="116" width="580" height="64" fill="#f8fafc"/><line x1="380" y1="180" x2="960" y2="180" class="rule"/>
<line x1="540" y1="116" x2="540" y2="452" class="rule"/><line x1="660" y1="116" x2="660" y2="452" class="rule"/><line x1="780" y1="116" x2="780" y2="452" class="rule"/><line x1="880" y1="116" x2="880" y2="452" class="rule"/>
<text x="400" y="153" class="zone-title">MODE</text><text x="600" y="146" text-anchor="middle" class="tag-text">UNTRUSTED</text><text x="600" y="158" text-anchor="middle" class="tag-text">INPUT</text><text x="720" y="146" text-anchor="middle" class="tag-text">SENSITIVE</text><text x="720" y="158" text-anchor="middle" class="tag-text">DATA</text><text x="830" y="146" text-anchor="middle" class="tag-text">WAY OUT</text><text x="920" y="146" text-anchor="middle" class="tag-text">COUNT</text>
<g font-family="'DM Sans',Arial,sans-serif"><line x1="380" y1="248" x2="960" y2="248" class="rule"/><line x1="380" y1="316" x2="960" y2="316" class="rule"/><line x1="380" y1="384" x2="960" y2="384" class="rule"/>
<text x="400" y="210" class="node-name">Research run</text><text x="400" y="226" class="node-sub">ticker to report</text><text x="600" y="216" text-anchor="middle" class="small strong">BOUNDED</text><text x="720" y="216" text-anchor="middle" class="small">ABSENT</text><text x="830" y="216" text-anchor="middle" class="small strong">HTTPS</text><text x="920" y="216" text-anchor="middle" class="node-name">2 / 3</text>
<text x="400" y="278" class="node-name">Report chat</text><text x="400" y="294" class="node-sub">verified snapshot</text><text x="600" y="284" text-anchor="middle" class="small strong">BOUNDED</text><text x="720" y="284" text-anchor="middle" class="small">ABSENT</text><text x="830" y="284" text-anchor="middle" class="small strong">MODEL</text><text x="920" y="284" text-anchor="middle" class="node-name">2 / 3</text>
<text x="400" y="346" class="node-name">Explore</text><text x="400" y="362" class="node-sub">public web context</text><text x="600" y="352" text-anchor="middle" class="small strong">BOUNDED</text><text x="720" y="352" text-anchor="middle" class="small">ABSENT</text><text x="830" y="352" text-anchor="middle" class="small strong">WEB + MODEL</text><text x="920" y="352" text-anchor="middle" class="node-name">2 / 3</text>
<rect x="388" y="392" width="564" height="52" rx="4" fill="#edf3fc" stroke="#306bd9"/><text x="404" y="416" class="node-name">Rejected configuration</text><text x="404" y="433" class="node-sub">Input + sensitive data + egress cannot enter a graph.</text><text x="914" y="423" text-anchor="middle" font-family="'DM Sans',Arial,sans-serif" font-size="8" font-weight="700" fill="#0e131c">3 / 3 BLOCKED</text></g>
<line x1="40" y1="496" x2="960" y2="496" class="rule"/><text x="40" y="520" class="small strong">Current boundary</text><text x="140" y="520" class="small">Public-company evidence only. No portfolios, brokerage accounts, files, messages, or trading tools.</text>
</svg>"""


AXONOMETRIC = f"""<svg viewBox="0 0 1000 660" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exploded-title exploded-desc">
<title id="exploded-title">Exploded axonometric view of Ledger</title><desc id="exploded-desc">Four separated parts show the interface, agent orchestration, deterministic analysis core, and public evidence foundation as one assembled research system.</desc>
{DEFS}{TOKENS}<rect class="paper" width="1000" height="660"/><rect class="dots" width="1000" height="660"/>
<style>
  .trace{{fill:none;stroke:#9aa8ba;stroke-width:.8;stroke-dasharray:4 4}}.face-top{{fill:#fff;stroke:#0e131c;stroke-width:1.2}}.face-left{{fill:#eef1f5;stroke:#0e131c;stroke-width:1.2}}.face-right{{fill:#d9e1ec;stroke:#0e131c;stroke-width:1.2}}
  .focus-top{{fill:#edf3fc;stroke:#306bd9;stroke-width:1.4}}.focus-left{{fill:#c9dafa;stroke:#306bd9;stroke-width:1.2}}.focus-right{{fill:#9ebbef;stroke:#306bd9;stroke-width:1.2}}.detail{{fill:none;stroke:#66768b;stroke-width:.8}}.leader{{stroke:#66768b;stroke-width:.8}}.dot{{fill:#66768b}}.focal-line{{stroke:#306bd9}}.focal-dot{{fill:#306bd9}}
</style>
<text x="40" y="48" class="title">Ledger, pulled apart</text><text x="40" y="72" class="subtitle">Four parts form one system. The deterministic core remains the load-bearing layer.</text>

<g data-exploded data-origin="420 440" data-gap="110">
  <line x1="300" y1="480" x2="300" y2="170" class="trace" data-role="trace"/><line x1="680" y1="550" x2="680" y2="240" class="trace" data-role="trace"/>

  <g data-part="evidence" data-name="Evidence foundation" data-rect="0 0 260 120 0" data-z="0" data-t="20" data-level="0">
    <path d="M420 420L680 550L560 610L300 480Z" class="face-top" data-role="silhouette"/><path d="M300 480L560 610L560 630L300 500Z" class="face-left"/><path d="M680 550L560 610L560 630L680 570Z" class="face-right"/>
    <path d="M374 456L466 502L438 516L346 470ZM506 522L598 568L570 582L478 536Z" class="detail"/>
    <g data-role="label"><circle cx="680" cy="560" r="2" class="dot"/><line x1="686" y1="560" x2="748" y2="560" class="leader" data-role="leader"/><text x="760" y="555" class="node-name" data-role="name">Evidence foundation</text><text x="760" y="573" class="node-sub">SEC EDGAR + market history</text></g>
  </g>

  <g data-part="analysis" data-name="Deterministic core" data-rect="0 0 260 120 0" data-z="110" data-t="20" data-level="1" data-focal="true">
    <path d="M420 310L680 440L560 500L300 370Z" class="focus-top" data-role="silhouette"/><path d="M300 370L560 500L560 520L300 390Z" class="focus-left"/><path d="M680 440L560 500L560 520L680 460Z" class="focus-right"/>
    <path d="M374 348L520 421L486 438L340 365ZM540 431L624 473L600 485L516 443Z" class="detail focal-line"/>
    <g data-role="label"><circle cx="680" cy="450" r="2" class="focal-dot"/><line x1="686" y1="450" x2="748" y2="450" class="leader focal-line" data-role="leader"/><text x="760" y="445" class="node-name" data-role="name">Deterministic core</text><text x="760" y="463" class="node-sub" fill="#306bd9">Python metrics + verdict</text></g>
  </g>

  <g data-part="orchestration" data-name="Agent orchestration" data-rect="0 0 260 120 0" data-z="220" data-t="20" data-level="2">
    <path d="M420 200L680 330L560 390L300 260Z" class="face-top" data-role="silhouette"/><path d="M300 260L560 390L560 410L300 280Z" class="face-left"/><path d="M680 330L560 390L560 410L680 350Z" class="face-right"/>
    <path d="M354 251L416 282L394 293L332 262ZM438 293L500 324L478 335L416 304ZM522 335L584 366L562 377L500 346Z" class="detail"/>
    <g data-role="label"><circle cx="680" cy="340" r="2" class="dot"/><line x1="686" y1="340" x2="748" y2="340" class="leader" data-role="leader"/><text x="760" y="335" class="node-name" data-role="name">Agent orchestration</text><text x="760" y="353" class="node-sub">three bounded LangGraph flows</text></g>
  </g>

  <g data-part="interface" data-name="Research workspace" data-rect="0 0 260 120 0" data-z="330" data-t="20" data-level="3">
    <path d="M420 90L680 220L560 280L300 150Z" class="face-top" data-role="silhouette"/><path d="M300 150L560 280L560 300L300 170Z" class="face-left"/><path d="M680 220L560 280L560 300L680 240Z" class="face-right"/>
    <path d="M396 116L610 223L564 246L350 139ZM382 151L470 195M486 203L552 236" class="detail"/>
    <g data-role="label"><circle cx="680" cy="230" r="2" class="dot"/><line x1="686" y1="230" x2="748" y2="230" class="leader" data-role="leader"/><text x="760" y="225" class="node-name" data-role="name">Research workspace</text><text x="760" y="243" class="node-sub">report + conversation + export</text></g>
  </g>
</g>
<line x1="40" y1="616" x2="960" y2="616" class="rule"/><text x="40" y="640" class="small strong">Assembly rule</text><text x="132" y="640" class="small">Evidence supports calculation; calculation constrains agents; agents serve the interface.</text>
</svg>"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "system-architecture.html": html("A bounded research system", "Architecture / Ledger", ARCHITECTURE),
        "exploded-system.html": html("Ledger, pulled apart", "Exploded system / Ledger", AXONOMETRIC),
        "research-data-flow.html": html("From ticker to cited report", "Data flow / Ledger", DATA_FLOW),
        "access-triangle-matrix.html": html("No session gets all three capabilities", "Security matrix / Ledger", SECURITY),
    }
    for name, content in diagrams.items():
        target = OUT / name
        target.write_text(content, encoding="utf-8", newline="\n")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
