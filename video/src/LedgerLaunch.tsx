import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  Series,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';
import '@fontsource/dm-sans/700.css';
import '@fontsource/instrument-serif/400.css';
import {COLORS, EASE, FPS, SCENE, SCENE_START, TOTAL_FRAMES} from './tokens';

const sans = '"DM Sans", Arial, sans-serif';
const serif = '"Instrument Serif", Georgia, serif';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const enter = (frame: number, delay = 0) => spring({
  frame: frame - delay,
  fps: FPS,
  config: EASE.enter,
});

const fadeWindow = (frame: number, duration: number, lead = 12, tail = 14) =>
  interpolate(frame, [0, lead, duration - tail, duration], [0, 1, 1, 0], clamp);

const LedgerMark: React.FC<{dark?: boolean; large?: boolean}> = ({dark = false, large = false}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: large ? 22 : 12}}>
    <div style={{
      width: large ? 68 : 36,
      height: large ? 68 : 36,
      display: 'grid',
      placeItems: 'center',
      color: dark ? COLORS.ink : COLORS.paper,
      background: dark ? COLORS.paper : COLORS.ink,
      fontFamily: serif,
      fontSize: large ? 48 : 26,
      lineHeight: 1,
    }}>L</div>
    <span style={{fontFamily: sans, fontSize: large ? 28 : 15, fontWeight: 700, letterSpacing: '.18em', color: dark ? COLORS.paper : COLORS.ink}}>LEDGER</span>
  </div>
);

const GlobalBackdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const phase = frame / TOTAL_FRAMES;
  const dark = frame < SCENE_START.ticker || frame >= SCENE_START.close;
  return (
    <AbsoluteFill style={{
      background: dark
        ? `radial-gradient(circle at ${30 + phase * 42}% 42%, #1b2a43 0%, ${COLORS.ink} 38%, #080b10 100%)`
        : `radial-gradient(circle at ${72 - phase * 30}% 24%, #eef4ff 0%, ${COLORS.paper} 38%, #f1f4f8 100%)`,
      transition: 'background 100ms linear',
      overflow: 'hidden',
    }}>
      <div style={{position: 'absolute', inset: 0, opacity: dark ? 0.055 : 0.16, backgroundImage: 'linear-gradient(rgba(101,117,139,.35) 1px, transparent 1px), linear-gradient(90deg, rgba(101,117,139,.35) 1px, transparent 1px)', backgroundSize: `${Math.round(width / 12)}px ${Math.round(height / 8)}px`, transform: `translate(${phase * 18}px, ${phase * 10}px)`}} />
      <div style={{position: 'absolute', left: '-15%', top: '58%', width: '52%', height: '22%', borderRadius: '50%', background: COLORS.blue, opacity: dark ? 0.1 : 0.055, filter: `blur(${Math.round(width * .055)}px)`, transform: `translateX(${phase * width * .48}px)`}} />
    </AbsoluteFill>
  );
};

const GlobalChrome: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const dark = frame < SCENE_START.ticker || frame >= SCENE_START.close;
  const progress = frame / (TOTAL_FRAMES - 1);
  const headerOpacity = interpolate(frame, [SCENE_START.close, SCENE_START.close + 18], [1, 0], clamp);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', color: dark ? COLORS.paper : COLORS.ink}}>
      <div style={{position: 'absolute', left: vertical ? 48 : 64, top: vertical ? 52 : 48, opacity: headerOpacity}}><LedgerMark dark={dark} /></div>
      <div style={{position: 'absolute', right: vertical ? 48 : 64, top: vertical ? 64 : 58, fontFamily: sans, fontSize: vertical ? 16 : 13, fontWeight: 600, letterSpacing: '.12em', color: dark ? '#b8c7dd' : COLORS.muted, opacity: headerOpacity}}>LIVE EVIDENCE · NVDA</div>
      <div style={{position: 'absolute', left: vertical ? 48 : 64, right: vertical ? 48 : 64, bottom: vertical ? 48 : 38, height: 2, background: dark ? '#25334a' : COLORS.line}}>
        <div style={{width: `${progress * 100}%`, height: '100%', background: COLORS.blue}} />
      </div>
    </AbsoluteFill>
  );
};

const EvidenceThread: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const reveal = interpolate(frame, [SCENE_START.ticker + 30, SCENE_START.evidence + 75], [0, 1], clamp);
  const retire = interpolate(frame, [SCENE_START.math + 100, SCENE_START.workspace + 35], [1, 0], clamp);
  const y = vertical ? height * .76 : height * .78;
  return (
    <div style={{position: 'absolute', left: vertical ? 54 : 90, top: y, width: (width - (vertical ? 108 : 180)) * reveal, height: 2, opacity: retire * reveal, background: COLORS.blue}}>
      <div style={{position: 'absolute', right: -7, top: -6, width: 14, height: 14, borderRadius: '50%', background: COLORS.blue, boxShadow: '0 0 0 8px rgba(48,107,217,.13)'}} />
    </div>
  );
};

const PremiseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const p = enter(frame, 8);
  const rule = interpolate(frame, [8, 62], [0, vertical ? width - 140 : 980], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{padding: vertical ? '0 64px' : '0 170px', justifyContent: 'center', color: COLORS.paper, opacity: fadeWindow(frame, SCENE.premise)}}>
      <div style={{fontFamily: sans, fontSize: vertical ? 20 : 18, fontWeight: 600, letterSpacing: '.14em', color: '#96a7bf', marginBottom: vertical ? 34 : 26, opacity: p}}>PUBLIC EQUITY RESEARCH</div>
      <div style={{fontFamily: serif, fontSize: vertical ? 126 : 148, lineHeight: .88, letterSpacing: '-.045em', maxWidth: vertical ? 850 : 1260, transform: `translateY(${(1 - p) * 42}px)`, opacity: p}}>
        A ticker is<br/><span style={{color: '#8db2ff'}}>not a thesis.</span>
      </div>
      <div style={{height: 2, width: rule, background: COLORS.blue, marginTop: vertical ? 62 : 54}} />
    </AbsoluteFill>
  );
};

const TickerScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const p = enter(frame, 4);
  const typed = Math.max(0, Math.min(4, Math.floor((frame - 34) / 7)));
  const ticker = 'NVDA'.slice(0, typed);
  const button = enter(frame, 68);
  return (
    <AbsoluteFill style={{padding: vertical ? '0 58px' : '0 190px', justifyContent: 'center', color: COLORS.ink, opacity: fadeWindow(frame, SCENE.ticker)}}>
      <div style={{fontFamily: serif, fontSize: vertical ? 92 : 112, lineHeight: .95, marginBottom: vertical ? 80 : 56, transform: `translateY(${(1 - p) * 28}px)`, opacity: p}}>Start with the evidence.</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr auto', width: '100%', border: `2px solid ${COLORS.ink}`, background: COLORS.white, height: vertical ? 124 : 104, boxShadow: '0 26px 70px rgba(14,19,28,.08)'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 24, padding: vertical ? '0 30px' : '0 34px', fontFamily: sans}}>
          <div style={{width: 20, height: 20, border: `3px solid ${COLORS.ink}`, borderRadius: '50%', position: 'relative'}}><span style={{position: 'absolute', width: 10, height: 3, background: COLORS.ink, right: -7, bottom: -3, transform: 'rotate(45deg)'}} /></div>
          <span style={{fontSize: vertical ? 34 : 28, fontWeight: 700, letterSpacing: '.12em'}}>{ticker}<span style={{color: COLORS.blue, opacity: frame % 16 < 8 ? 1 : 0}}>|</span></span>
        </div>
        <div style={{display: 'grid', placeItems: 'center', padding: vertical ? '0 34px' : '0 54px', minWidth: vertical ? 220 : 250, background: COLORS.blue, color: COLORS.white, fontFamily: sans, fontSize: vertical ? 21 : 17, fontWeight: 700, letterSpacing: '.09em', opacity: button}}>ANALYZE →</div>
      </div>
      <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 24, fontFamily: sans, fontSize: vertical ? 17 : 14, color: COLORS.muted, letterSpacing: '.08em'}}><span>SEC REPORTING ISSUER</span><span>LIVE · 2026-10-21</span></div>
    </AbsoluteFill>
  );
};

const EvidenceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const sources = [
    ['01', 'LATEST FILING', 'SEC · 2026-08-26'],
    ['02', 'COMPANY FACTS', 'SEC XBRL · VERIFIED'],
    ['03', 'PRICE HISTORY', 'YAHOO FINANCE · 1Y'],
  ];
  return (
    <AbsoluteFill style={{padding: vertical ? '180px 58px 170px' : '150px 150px 120px', color: COLORS.ink, opacity: fadeWindow(frame, SCENE.evidence)}}>
      <div style={{fontFamily: serif, fontSize: vertical ? 82 : 88, lineHeight: 1, maxWidth: 1000}}>Filings. Prices.<br/><span style={{color: COLORS.blue}}>Periods. Sources.</span></div>
      <div style={{display: 'grid', gridTemplateColumns: vertical ? '1fr' : 'repeat(3, 1fr)', gap: vertical ? 20 : 26, marginTop: vertical ? 86 : 78}}>
        {sources.map(([num, title, meta], i) => {
          const p = enter(frame, 34 + i * 14);
          return (
            <div key={title} style={{minHeight: vertical ? 182 : 230, borderTop: `2px solid ${COLORS.ink}`, borderBottom: `1px solid ${COLORS.line}`, padding: vertical ? '24px 8px' : '30px 8px 24px', display: 'flex', flexDirection: vertical ? 'row' : 'column', alignItems: vertical ? 'center' : 'stretch', gap: vertical ? 28 : 0, background: 'rgba(255,255,255,.54)', opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>
              <span style={{fontFamily: sans, fontSize: 14, color: COLORS.blue, fontWeight: 700}}>{num}</span>
              <strong style={{fontFamily: sans, fontSize: vertical ? 25 : 24, letterSpacing: '.06em', marginTop: vertical ? 0 : 'auto'}}>{title}</strong>
              <span style={{fontFamily: sans, fontSize: vertical ? 17 : 14, color: COLORS.muted, marginTop: vertical ? 0 : 12, marginLeft: vertical ? 'auto' : 0}}>{meta}</span>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', right: vertical ? 58 : 150, bottom: vertical ? 180 : 118, display: 'flex', gap: 11, alignItems: 'center', fontFamily: sans, fontSize: vertical ? 18 : 15, fontWeight: 600, letterSpacing: '.08em', color: COLORS.green}}><span style={{width: 10, height: 10, borderRadius: '50%', background: COLORS.green}}/>PRIMARY SOURCES RETAINED</div>
    </AbsoluteFill>
  );
};

type MetricProps = {label: string; value: number; prefix?: string; suffix?: string; decimals?: number; note: string; tone?: 'good' | 'warn'};
const Metric: React.FC<MetricProps & {progress: number}> = ({label, value, prefix = '', suffix = '', decimals = 1, note, tone, progress}) => {
  const shown = value * progress;
  return (
    <div style={{borderTop: `2px solid ${COLORS.ink}`, borderRight: `1px solid ${COLORS.line}`, borderBottom: `1px solid ${COLORS.line}`, padding: '26px 24px', background: 'rgba(255,255,255,.7)', minHeight: 220, display: 'flex', flexDirection: 'column'}}>
      <span style={{fontFamily: sans, fontSize: 14, color: COLORS.muted, fontWeight: 700, letterSpacing: '.1em'}}>{label}</span>
      <strong style={{fontFamily: serif, fontSize: 62, fontWeight: 400, lineHeight: 1, marginTop: 'auto', color: tone === 'good' ? COLORS.green : tone === 'warn' ? COLORS.red : COLORS.ink}}>{prefix}{shown.toFixed(decimals)}{suffix}</strong>
      <span style={{fontFamily: sans, fontSize: 13, color: COLORS.muted, marginTop: 13}}>{note}</span>
    </div>
  );
};

const MathScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const count = interpolate(frame, [28, 105], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const metrics: MetricProps[] = [
    {label: 'REVENUE GROWTH', value: 40.3, suffix: '%', note: 'Trailing 12 months', tone: 'good'},
    {label: 'GROSS MARGIN', value: 74.7, suffix: '%', note: 'Reported · GAAP'},
    {label: 'FREE CASH FLOW', value: 127.0, prefix: '$', suffix: 'B', note: 'Operating cash less capex'},
    {label: 'PRICE / SALES', value: 17.6, suffix: '×', note: 'Calculated in Python', tone: 'warn'},
  ];
  return (
    <AbsoluteFill style={{padding: vertical ? '170px 52px 150px' : '138px 132px 110px', color: COLORS.ink, opacity: fadeWindow(frame, SCENE.math)}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'end', gap: 40}}>
        <div style={{fontFamily: serif, fontSize: vertical ? 80 : 92, lineHeight: .95}}>Let Python<br/><span style={{color: COLORS.blue}}>do the math.</span></div>
        {!vertical && <div style={{fontFamily: sans, fontSize: 15, color: COLORS.muted, maxWidth: 350, lineHeight: 1.55, textAlign: 'right'}}>Language interprets.<br/>Code calculates.</div>}
      </div>
      <div style={{display: 'grid', gridTemplateColumns: vertical ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)', marginTop: vertical ? 80 : 72, borderLeft: `1px solid ${COLORS.line}`}}>
        {metrics.map((metric, i) => {
          const delay = i * .06;
          const metricProgress = Math.max(0, Math.min(1, (count - delay) / (1 - delay)));
          return <Metric key={metric.label} {...metric} progress={metricProgress} />;
        })}
      </div>
      <div style={{marginTop: 24, fontFamily: sans, fontSize: vertical ? 17 : 14, fontWeight: 600, letterSpacing: '.08em', color: COLORS.green}}>✓ PERIODS NORMALIZED · ✓ UNITS CHECKED · ✓ FIGURES LOCKED</div>
    </AbsoluteFill>
  );
};

const AppFrame: React.FC<{frame: number; focus?: 'report' | 'chat'}> = ({frame, focus = 'report'}) => {
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const reveal = enter(frame, 8);
  const scale = vertical ? .79 : 1;
  const canvasW = vertical ? 1160 : 1600;
  const canvasH = vertical ? 1320 : 780;
  const chatWidth = focus === 'chat' ? (vertical ? 520 : 500) : (vertical ? 290 : 310);
  const reportShift = focus === 'chat' ? (vertical ? -60 : -90) : 0;
  const shotDuration = focus === 'chat' ? SCENE.chat : SCENE.workspace;
  const cameraDrift = interpolate(frame, [0, shotDuration], [0, 1], clamp);
  const cameraScale = scale * (1 + cameraDrift * .025);
  return (
    <div style={{position: 'absolute', left: '50%', top: vertical ? '52%' : '61%', width: canvasW, height: canvasH, transform: `translate(-50%, -50%) translateY(${(1 - reveal) * 60 - cameraDrift * 10}px) scale(${cameraScale})`, opacity: reveal, background: COLORS.white, border: `1px solid ${COLORS.ink}`, boxShadow: '0 40px 120px rgba(14,19,28,.20)', overflow: 'hidden', fontFamily: sans}}>
      <div style={{height: 62, borderBottom: `1px solid ${COLORS.ink}`, display: 'grid', gridTemplateColumns: vertical ? '240px 1fr' : '220px 1fr 420px 150px', alignItems: 'center'}}>
        <div style={{height: '100%', borderRight: `1px solid ${COLORS.line}`, display: 'flex', alignItems: 'center', padding: '0 22px'}}><LedgerMark /></div>
        {!vertical && <div style={{paddingLeft: 28, color: COLORS.muted, fontSize: 12, letterSpacing: '.1em'}}>PUBLIC EQUITY RESEARCH AGENT</div>}
        <div style={{margin: '0 18px', height: 40, border: `1px solid ${COLORS.ink}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingLeft: 18, fontWeight: 700, letterSpacing: '.08em'}}><span>⌕ &nbsp; NVDA</span><span style={{height: '100%', display: 'grid', placeItems: 'center', background: COLORS.blue, color: COLORS.white, padding: '0 24px', fontSize: 12}}>ANALYZE →</span></div>
        {!vertical && <div style={{fontSize: 11, color: COLORS.green, fontWeight: 700}}>● &nbsp; LIVE · 2026-10-21</div>}
      </div>
      <div style={{height: 'calc(100% - 62px)', display: 'grid', gridTemplateColumns: vertical ? `170px 1fr ${chatWidth}px` : `210px 1fr ${chatWidth}px`, transition: 'grid-template-columns .2s linear'}}>
        <div style={{borderRight: `1px solid ${COLORS.line}`, padding: '32px 24px', display: 'flex', flexDirection: 'column'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 12, paddingBottom: 26, borderBottom: `1px solid ${COLORS.line}`}}><span style={{width: 40, height: 40, borderRadius: '50%', display: 'grid', placeItems: 'center', color: 'white', background: COLORS.blue, fontSize: 12, fontWeight: 700}}>NV</span><div><b>NVDA</b><small style={{display: 'block', color: COLORS.muted, marginTop: 5}}>Nasdaq</small></div></div>
          {['01  CONCLUSION', '02  FINANCIALS', '03  VALUATION', '04  RISKS', '05  SOURCES'].map((item, i) => <div key={item} style={{padding: '18px 0', color: i === 0 ? COLORS.ink : COLORS.muted, fontSize: 11, letterSpacing: '.05em', borderLeft: i === 0 ? `12px solid ${COLORS.blue}` : '12px solid transparent', marginLeft: -24, paddingLeft: 12}}>{item}</div>)}
          <div style={{marginTop: 'auto', borderTop: `1px solid ${COLORS.line}`, paddingTop: 14, fontSize: 10, color: COLORS.muted}}>Run 773f812e<br/><span style={{display: 'inline-block', marginTop: 7}}>32.6s total</span></div>
        </div>
        <div style={{minWidth: 0, transform: `translateX(${reportShift}px)`, transition: 'transform .2s linear'}}>
          <div style={{padding: vertical ? '72px 42px 38px' : '62px 66px 34px', borderBottom: `1px solid ${COLORS.ink}`}}>
            <div style={{fontSize: 11, color: COLORS.muted, letterSpacing: '.08em'}}>EQUITY RESEARCH / 2026-10-21</div>
            <div style={{fontSize: 13, fontWeight: 700, letterSpacing: '.08em', marginTop: 60}}>NVIDIA CORP</div>
            <div style={{fontFamily: serif, fontSize: vertical ? 66 : 78, lineHeight: .85, letterSpacing: '-.035em', marginTop: 18}}>Fairly valued<br/>at today’s price.</div>
            <div style={{display: 'grid', gridTemplateColumns: '10px 1fr', gap: 16, marginTop: 34, maxWidth: 760, fontSize: 13, lineHeight: 1.55}}><span style={{width: 9, height: 9, borderRadius: '50%', background: COLORS.blue, marginTop: 5}}/><span>NVIDIA pairs 40.30% revenue growth and exceptional margins with a valuation premium at 17.61× sales.</span></div>
          </div>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)'}}>
            {[['SHARE PRICE','$221.36'],['REVENUE GROWTH','40.3%'],['GROSS MARGIN','74.7%'],['P / E','27.7×']].map(([label, value], i) => <div key={label} style={{height: 136, padding: 22, borderRight: `1px solid ${COLORS.line}`, borderBottom: `1px solid ${COLORS.ink}`}}><span style={{fontSize: 10, color: COLORS.muted, letterSpacing: '.08em'}}>{label}</span><strong style={{display: 'block', fontFamily: serif, fontSize: 38, fontWeight: 400, marginTop: 30, color: i === 1 ? COLORS.green : i === 3 ? COLORS.red : COLORS.ink}}>{value}</strong></div>)}
          </div>
          <div style={{padding: '42px 48px', display: 'grid', gridTemplateColumns: '55px 260px 1fr', gap: 28}}><span style={{fontSize: 11, color: COLORS.blue, fontWeight: 700}}>01</span><div><span style={{fontSize: 11, color: COLORS.muted, letterSpacing: '.1em'}}>INVESTMENT CASE</span><h2 style={{fontFamily: serif, fontWeight: 400, fontSize: 40, lineHeight: 1, margin: '14px 0 0'}}>What the<br/>numbers say</h2></div><div style={{borderTop: `1px solid ${COLORS.ink}`}}>{['Scale and growth', 'Exceptional profitability', 'Cash flow strength'].map((x, i) => <div key={x} style={{padding: '17px 0', borderBottom: `1px solid ${COLORS.line}`, fontSize: 13}}><span style={{color: COLORS.muted, marginRight: 18}}>0{i + 1}</span>{x}</div>)}</div></div>
        </div>
        <div style={{borderLeft: `1px solid ${COLORS.line}`, padding: '20px 22px', background: COLORS.white, position: 'relative', zIndex: 2}}>
          <div style={{display: 'flex', gap: 28, height: 42, alignItems: 'center', borderBottom: `1px solid ${COLORS.ink}`, fontSize: 11, fontWeight: 700}}><span style={{borderBottom: `2px solid ${COLORS.blue}`, height: '100%', display: 'grid', placeItems: 'center'}}>ASK</span><span style={{color: COLORS.muted}}>TRACE</span><span style={{marginLeft: 'auto', color: COLORS.muted}}>↗ EXPAND</span></div>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', border: `1px solid ${COLORS.ink}`, marginTop: 18}}><span style={{background: COLORS.ink, color: COLORS.white, padding: '11px 0', textAlign: 'center', fontSize: 10, fontWeight: 700}}>REPORT</span><span style={{padding: '11px 0', textAlign: 'center', fontSize: 10, color: COLORS.muted}}>EXPLORE</span></div>
          <div style={{fontSize: 10, color: COLORS.muted, letterSpacing: '.08em', marginTop: 24}}>REPORT-SCOPED ANALYST</div>
          <div style={{fontFamily: serif, fontSize: 28, marginTop: 8}}>Ask about NVDA</div>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: 5, padding: '16px 0', marginTop: 12, borderTop: `1px solid ${COLORS.line}`, borderBottom: `1px solid ${COLORS.line}`}}>{['COMPANY','FINANCIALS','VALUATION','PEERS','RISKS','SOURCES'].map(x => <span key={x} style={{fontSize: 8, color: COLORS.muted, padding: '5px 6px', border: `1px solid ${COLORS.line}`}}>{x}</span>)}</div>
          {focus === 'report' ? <>
            <div style={{fontFamily: serif, fontSize: 20, lineHeight: 1.2, marginTop: 26}}>Questions are answered from this report’s verified facts and evidence ledger.</div>
            <div style={{fontSize: 10, color: COLORS.muted, lineHeight: 1.5, marginTop: 12}}>No browsing, trading, uploads, or persistent conversation memory.</div>
          </> : <ChatTranscript frame={frame} />}
          <div style={{position: 'absolute', left: 22, right: 22, bottom: 24, height: 72, border: `1px solid ${COLORS.ink}`, display: 'flex', alignItems: 'center', padding: '0 15px', color: COLORS.muted, fontSize: 11}}>Ask about NVDA<span style={{marginLeft: 'auto', width: 42, height: 42, display: 'grid', placeItems: 'center', background: COLORS.blueSoft, color: COLORS.blue}}>↑</span></div>
        </div>
      </div>
    </div>
  );
};

const ChatTranscript: React.FC<{frame: number}> = ({frame}) => {
  const q = enter(frame, 28);
  const a = enter(frame, 70);
  return (
    <div style={{marginTop: 22, fontSize: 11, lineHeight: 1.52}}>
      <div style={{padding: '0 0 15px 14px', borderLeft: `2px solid ${COLORS.ink}`, opacity: q, transform: `translateY(${(1 - q) * 12}px)`}}><b style={{fontSize: 9, color: COLORS.muted, letterSpacing: '.08em'}}>YOU</b><div style={{marginTop: 7}}>Why is NVDA fairly valued?</div></div>
      <div style={{padding: '0 0 15px 14px', marginTop: 18, borderLeft: `2px solid ${COLORS.blue}`, opacity: a, transform: `translateY(${(1 - a) * 12}px)`}}><b style={{fontSize: 9, color: COLORS.blue, letterSpacing: '.08em'}}>LEDGER</b><div style={{marginTop: 7}}>Growth and margins are exceptional, but 17.61× sales and a 2.38% FCF yield already price in substantial execution.</div><div style={{display: 'flex', gap: 6, marginTop: 12}}><span style={{border: `1px solid ${COLORS.line}`, padding: '4px 7px'}}>[1]</span><span style={{border: `1px solid ${COLORS.line}`, padding: '4px 7px'}}>[2]</span><span style={{border: `1px solid ${COLORS.line}`, padding: '4px 7px'}}>[4]</span></div></div>
    </div>
  );
};

const WorkspaceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {height, width} = useVideoConfig();
  const vertical = height > width;
  const titleP = enter(frame, 8);
  return (
    <AbsoluteFill style={{color: COLORS.ink, opacity: fadeWindow(frame, SCENE.workspace)}}>
      <div style={{position: 'absolute', left: vertical ? 56 : 120, top: vertical ? 142 : 118, zIndex: 4, maxWidth: vertical ? 760 : 1050, opacity: titleP, transform: `translateY(${(1 - titleP) * 24}px)`}}>
        <div style={{fontFamily: serif, fontSize: vertical ? 70 : 76, lineHeight: .95}}>A complete research memo.</div>
        <div style={{fontFamily: sans, fontSize: vertical ? 18 : 15, color: COLORS.muted, marginTop: 14, letterSpacing: '.03em'}}>BUILT FROM LIVE PUBLIC DATA</div>
      </div>
      <AppFrame frame={frame} />
    </AbsoluteFill>
  );
};

const typeOn = (text: string, frame: number, start: number, cadence = 1.25) =>
  text.slice(0, Math.max(0, Math.min(text.length, Math.floor((frame - start) / cadence))));

const SourceChip: React.FC<{children: React.ReactNode; active?: boolean}> = ({children, active = false}) => (
  <span style={{
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 28,
    padding: '0 9px',
    border: `1px solid ${active ? COLORS.blue : COLORS.line}`,
    background: active ? COLORS.blueSoft : COLORS.white,
    color: active ? COLORS.blue : COLORS.muted,
    fontSize: 9,
    fontWeight: 700,
    letterSpacing: '.06em',
  }}>{children}</span>
);

const InteractiveChatStage: React.FC<{frame: number}> = ({frame}) => {
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const reveal = enter(frame, 8);
  const canvasW = vertical ? 1160 : 1650;
  const canvasH = vertical ? 1080 : 790;
  const scale = vertical ? .86 : 1;
  const exploreProgress = interpolate(frame, [148, 184], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const explore = frame >= 168;
  const reportOpacity = interpolate(frame, [145, 171], [1, 0], clamp);
  const exploreOpacity = interpolate(frame, [165, 191], [0, 1], clamp);
  const reportQuestion = typeOn('Why is NVDA fairly valued?', frame, 24, 1.15);
  const exploreQuestion = typeOn('What could move the thesis next?', frame, 191, 1.05);
  const reportAnswer = enter(frame, 72);
  const reportSources = enter(frame, 112);
  const searchOne = enter(frame, 231);
  const searchTwo = enter(frame, 244);
  const searchThree = enter(frame, 257);
  const exploreAnswer = enter(frame, 286);
  const exploreSources = enter(frame, 326);
  const revenueActive = frame >= 72 && frame < 111;
  const valuationActive = frame >= 105 && frame < 148;
  const cursorVisible = interpolate(frame, [132, 143, 186, 197], [0, 1, 1, 0], clamp);
  const cursorX = interpolate(exploreProgress, [0, 1], [vertical ? 490 : 835, vertical ? 655 : 1000]);
  const cursorY = 54;
  const camera = interpolate(frame, [0, SCENE.chat], [0, 1], clamp);

  return (
    <div style={{
      position: 'absolute',
      left: '50%',
      top: vertical ? '56%' : '62%',
      width: canvasW,
      height: canvasH,
      transform: `translate(-50%, -50%) translateY(${(1 - reveal) * 55 - camera * 8}px) scale(${scale * (1 + camera * .018)})`,
      opacity: reveal,
      overflow: 'hidden',
      background: COLORS.white,
      border: `1px solid ${COLORS.ink}`,
      boxShadow: '0 44px 130px rgba(14,19,28,.22)',
      fontFamily: sans,
      color: COLORS.ink,
    }}>
      <div style={{height: 64, display: 'grid', gridTemplateColumns: vertical ? '270px 1fr 160px' : '250px 1fr 190px', alignItems: 'center', borderBottom: `1px solid ${COLORS.ink}`}}>
        <div style={{height: '100%', display: 'flex', alignItems: 'center', paddingLeft: 22, borderRight: `1px solid ${COLORS.line}`}}><LedgerMark /></div>
        <div style={{paddingLeft: 26, fontSize: 11, color: COLORS.muted, fontWeight: 700, letterSpacing: '.1em'}}>NVDA / RESEARCH CONVERSATION</div>
        <div style={{fontSize: 10, color: COLORS.green, fontWeight: 700, letterSpacing: '.08em'}}>● LIVE EVIDENCE</div>
      </div>

      <div style={{height: 'calc(100% - 64px)', display: 'grid', gridTemplateColumns: vertical ? '380px 1fr' : '520px 1fr'}}>
        <div style={{borderRight: `1px solid ${COLORS.ink}`, padding: vertical ? '42px 34px' : '44px 40px', background: '#fbfcfd', display: 'flex', flexDirection: 'column'}}>
          <div style={{fontSize: 10, color: COLORS.muted, letterSpacing: '.1em'}}>ACTIVE REPORT</div>
          <div style={{display: 'flex', alignItems: 'center', gap: 13, marginTop: 18}}>
            <span style={{width: 44, height: 44, borderRadius: '50%', display: 'grid', placeItems: 'center', color: COLORS.white, background: COLORS.blue, fontSize: 12, fontWeight: 700}}>NV</span>
            <div><strong style={{fontSize: 15}}>NVIDIA CORP</strong><span style={{display: 'block', marginTop: 5, fontSize: 10, color: COLORS.muted}}>NVDA · NASDAQ</span></div>
          </div>
          <div style={{fontFamily: serif, fontSize: vertical ? 39 : 44, lineHeight: .98, marginTop: 42}}>Fairly valued<br/>at today’s price.</div>
          <div style={{height: 2, width: '100%', background: COLORS.ink, margin: '34px 0 18px'}} />
          {[
            ['REVENUE GROWTH', '40.30%', revenueActive],
            ['GROSS MARGIN', '74.67%', revenueActive],
            ['PRICE / SALES', '17.61×', valuationActive],
            ['FCF YIELD', '2.38%', valuationActive],
          ].map(([label, value, active]) => (
            <div key={String(label)} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', minHeight: 58, padding: '0 12px', margin: '0 -12px', borderBottom: `1px solid ${COLORS.line}`, background: active ? COLORS.blueSoft : 'transparent', boxShadow: active ? `inset 3px 0 0 ${COLORS.blue}` : 'none', transition: 'background 80ms linear'}}>
              <span style={{fontSize: 10, color: active ? COLORS.blue : COLORS.muted, fontWeight: 700, letterSpacing: '.08em'}}>{label}</span>
              <strong style={{fontFamily: serif, fontSize: 27, fontWeight: 400}}>{value}</strong>
            </div>
          ))}
          <div style={{marginTop: 'auto', paddingTop: 20, borderTop: `1px solid ${COLORS.line}`, fontSize: 10, lineHeight: 1.55, color: COLORS.muted}}>Verdict and figures remain fixed while Explore checks current public context.</div>
        </div>

        <div style={{position: 'relative', padding: vertical ? '34px 38px 30px' : '32px 44px 28px', overflow: 'hidden'}}>
          <div style={{display: 'flex', alignItems: 'start', justifyContent: 'space-between', borderBottom: `1px solid ${COLORS.line}`, paddingBottom: 22}}>
            <div>
              <div style={{fontSize: 10, color: COLORS.muted, fontWeight: 700, letterSpacing: '.1em'}}>{explore ? 'LIVE PUBLIC-MARKET ANALYST' : 'REPORT-SCOPED ANALYST'}</div>
              <div style={{fontFamily: serif, fontSize: vertical ? 36 : 40, marginTop: 7}}>{explore ? 'Explore NVDA' : 'Ask about NVDA'}</div>
            </div>
            <div style={{position: 'relative', width: 330, height: 46, display: 'grid', gridTemplateColumns: '1fr 1fr', border: `1px solid ${COLORS.ink}`, background: COLORS.white}}>
              <div style={{position: 'absolute', top: 3, bottom: 3, left: 3, width: 'calc(50% - 3px)', background: COLORS.ink, transform: `translateX(${exploreProgress * 100}%)`}} />
              <span style={{position: 'relative', zIndex: 1, display: 'grid', placeItems: 'center', color: exploreProgress < .5 ? COLORS.white : COLORS.muted, fontSize: 10, fontWeight: 700, letterSpacing: '.08em'}}>REPORT</span>
              <span style={{position: 'relative', zIndex: 1, display: 'grid', placeItems: 'center', color: exploreProgress >= .5 ? COLORS.white : COLORS.muted, fontSize: 10, fontWeight: 700, letterSpacing: '.08em'}}>EXPLORE</span>
            </div>
          </div>

          <div style={{position: 'absolute', left: 44, right: 44, top: 132, bottom: 30, opacity: reportOpacity, transform: `translateX(${-exploreProgress * 42}px)`}}>
            <div style={{maxWidth: '78%', marginLeft: 'auto', border: `1px solid ${COLORS.ink}`, padding: '15px 18px', fontSize: 15, lineHeight: 1.4, background: COLORS.white}}>
              {reportQuestion}<span style={{color: COLORS.blue, opacity: frame % 14 < 8 && frame < 64 ? 1 : 0}}>|</span>
            </div>
            <div style={{display: 'grid', gridTemplateColumns: '32px 1fr', gap: 14, marginTop: 28, opacity: reportAnswer, transform: `translateY(${(1 - reportAnswer) * 16}px)`}}>
              <div style={{width: 32, height: 32, display: 'grid', placeItems: 'center', background: COLORS.ink, color: COLORS.white, fontFamily: serif, fontSize: 22}}>L</div>
              <div>
                <div style={{fontSize: 10, color: COLORS.blue, fontWeight: 700, letterSpacing: '.1em'}}>LEDGER · REPORT</div>
                <div style={{fontFamily: serif, fontSize: vertical ? 29 : 32, lineHeight: 1.16, marginTop: 11, maxWidth: 760}}>Growth and margins are exceptional. But the valuation already assumes sustained execution.</div>
                <div style={{fontSize: 13, lineHeight: 1.6, color: COLORS.muted, marginTop: 16, maxWidth: 760}}>Revenue grew 40.30% and gross margin reached 74.67%, while 17.61× sales and a 2.38% FCF yield leave less room for disappointment.</div>
                <div style={{display: 'flex', flexWrap: 'wrap', gap: 7, marginTop: 18, opacity: reportSources}}>
                  <SourceChip active={revenueActive}>[1] FINANCIALS · SEC</SourceChip>
                  <SourceChip active={valuationActive}>[2] VALUATION · PYTHON</SourceChip>
                  <SourceChip>[3] PRICE · YAHOO FINANCE</SourceChip>
                </div>
              </div>
            </div>
          </div>

          <div style={{position: 'absolute', left: 44, right: 44, top: 132, bottom: 30, opacity: exploreOpacity, transform: `translateX(${(1 - exploreProgress) * 42}px)`}}>
            <div style={{maxWidth: '78%', marginLeft: 'auto', border: `1px solid ${COLORS.blue}`, padding: '15px 18px', fontSize: 15, lineHeight: 1.4, background: COLORS.blueSoft}}>
              {exploreQuestion}<span style={{color: COLORS.blue, opacity: frame % 14 < 8 && frame < 236 ? 1 : 0}}>|</span>
            </div>
            <div style={{display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 24}}>
              {[
                ['SEC FILINGS', searchOne],
                ['NVIDIA IR', searchTwo],
                ['PUBLIC MARKET NEWS', searchThree],
              ].map(([label, progress]) => <div key={String(label)} style={{opacity: Number(progress), transform: `translateY(${(1 - Number(progress)) * 10}px)`}}><SourceChip active>{String(label)} · ✓</SourceChip></div>)}
            </div>
            <div style={{display: 'grid', gridTemplateColumns: '32px 1fr', gap: 14, marginTop: 27, opacity: exploreAnswer, transform: `translateY(${(1 - exploreAnswer) * 16}px)`}}>
              <div style={{width: 32, height: 32, display: 'grid', placeItems: 'center', background: COLORS.blue, color: COLORS.white, fontFamily: serif, fontSize: 22}}>L</div>
              <div>
                <div style={{fontSize: 10, color: COLORS.blue, fontWeight: 700, letterSpacing: '.1em'}}>LEDGER · EXPLORE</div>
                <div style={{fontFamily: serif, fontSize: vertical ? 28 : 31, lineHeight: 1.16, marginTop: 10, maxWidth: 780}}>Watch export restrictions, customer concentration, and the pace of AI infrastructure spending.</div>
                <div style={{fontSize: 13, lineHeight: 1.55, color: COLORS.muted, marginTop: 14, maxWidth: 780}}>Explore adds cited public context around the report. It cannot rewrite the calculated verdict.</div>
                <div style={{display: 'flex', gap: 7, marginTop: 17, opacity: exploreSources}}>
                  <SourceChip>[1] NVIDIA FILINGS</SourceChip>
                  <SourceChip>[2] NVIDIA IR</SourceChip>
                  <SourceChip>[3] PUBLIC SOURCES</SourceChip>
                </div>
              </div>
            </div>
            <div style={{position: 'absolute', left: 46, bottom: 0, color: COLORS.green, fontSize: 9, fontWeight: 700, letterSpacing: '.09em', opacity: exploreSources}}>✓ LIVE WEB SEARCH · ✓ CITED CLAIMS · ✓ REPORT VERDICT LOCKED</div>
          </div>

          <div style={{position: 'absolute', left: cursorX, top: cursorY, opacity: cursorVisible, zIndex: 8, transform: `scale(${.92 + Math.sin(frame * .35) * .04})`}}>
            <div style={{width: 0, height: 0, borderTop: '18px solid transparent', borderBottom: '4px solid transparent', borderLeft: `26px solid ${COLORS.blue}`, transform: 'rotate(-42deg)', filter: 'drop-shadow(0 3px 3px rgba(14,19,28,.2))'}} />
            <div style={{position: 'absolute', left: -7, top: -7, width: 42, height: 42, borderRadius: '50%', border: `2px solid ${COLORS.blue}`, opacity: interpolate(frame, [166, 172, 186], [0, 1, 0], clamp), transform: `scale(${interpolate(frame, [166, 186], [.4, 1.35], clamp)})`}} />
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {height, width} = useVideoConfig();
  const vertical = height > width;
  const titleP = enter(frame, 5);
  const exploreTitle = interpolate(frame, [154, 180], [0, 1], clamp);
  return (
    <AbsoluteFill style={{color: COLORS.ink, opacity: fadeWindow(frame, SCENE.chat)}}>
      <div style={{position: 'absolute', left: vertical ? 56 : 120, top: vertical ? 142 : 108, zIndex: 4, opacity: titleP, transform: `translateY(${(1 - titleP) * 20}px)`}}>
        <div style={{position: 'relative', height: vertical ? 84 : 92, minWidth: vertical ? 780 : 900, overflow: 'hidden'}}>
          <div style={{position: 'absolute', inset: 0, fontFamily: serif, fontSize: vertical ? 72 : 82, opacity: 1 - exploreTitle, transform: `translateY(${-exploreTitle * 110}px)`}}>Ask the report.</div>
          <div style={{position: 'absolute', inset: 0, fontFamily: serif, fontSize: vertical ? 72 : 82, opacity: exploreTitle, transform: `translateY(${(1 - exploreTitle) * 110}px)`}}>Explore what changed.</div>
        </div>
        <div style={{fontFamily: sans, fontSize: vertical ? 16 : 13, color: COLORS.muted, marginTop: 6, letterSpacing: '.08em'}}>ONE CONVERSATION · TWO EVIDENCE BOUNDARIES</div>
      </div>
      <InteractiveChatStage frame={frame} />
    </AbsoluteFill>
  );
};

const TrustScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const checks = [
    ['01', 'CALCULATIONS', 'Python owns every ratio and verdict.'],
    ['02', 'CITATIONS', 'Sources stay attached to every claim.'],
    ['03', 'BOUNDARIES', 'No trading. No private portfolio access.'],
  ];
  return (
    <AbsoluteFill style={{padding: vertical ? '180px 58px 140px' : '150px 150px 120px', color: COLORS.ink, opacity: fadeWindow(frame, SCENE.trust)}}>
      <div style={{fontFamily: serif, fontSize: vertical ? 82 : 94, lineHeight: .94}}>Every answer<br/><span style={{color: COLORS.blue}}>keeps its evidence.</span></div>
      <div style={{display: 'grid', gridTemplateColumns: vertical ? '1fr' : 'repeat(3, 1fr)', gap: vertical ? 18 : 30, marginTop: vertical ? 84 : 74}}>
        {checks.map(([n, title, body], i) => {
          const p = enter(frame, 30 + i * 10);
          return <div key={title} style={{padding: vertical ? '24px 0' : '26px 0', borderTop: `2px solid ${COLORS.ink}`, opacity: p, transform: `translateY(${(1 - p) * 18}px)`}}><span style={{fontFamily: sans, color: COLORS.blue, fontSize: 13, fontWeight: 700}}>{n}</span><strong style={{display: 'block', fontFamily: sans, fontSize: vertical ? 23 : 20, letterSpacing: '.08em', marginTop: vertical ? 0 : 46}}>{title}</strong><p style={{fontFamily: sans, color: COLORS.muted, fontSize: vertical ? 17 : 14, lineHeight: 1.5, margin: '12px 0 0'}}>{body}</p></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const CloseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {height, width} = useVideoConfig();
  const vertical = height > width;
  const p = enter(frame, 5);
  const line = interpolate(frame, [12, 64], [0, vertical ? width - 160 : 780], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', color: COLORS.paper, textAlign: 'center', opacity: interpolate(frame, [0, 12], [0, 1], clamp)}}>
      <div style={{transform: `translateY(${(1 - p) * 26}px)`, opacity: p}}><LedgerMark dark large /></div>
      <div style={{fontFamily: serif, fontSize: vertical ? 94 : 104, lineHeight: 1, marginTop: 54}}>Research you can inspect.</div>
      <div style={{width: line, height: 2, background: COLORS.blue, marginTop: 44}} />
      <div style={{fontFamily: sans, fontSize: vertical ? 18 : 14, color: '#aab8cb', letterSpacing: '.11em', marginTop: 26}}>LIVE EVIDENCE · DETERMINISTIC MATH · CITED ANSWERS</div>
      <div style={{fontFamily: sans, fontSize: vertical ? 15 : 12, color: '#718199', marginTop: 22}}>Research aid. Not investment advice.</div>
    </AbsoluteFill>
  );
};

export const LedgerLaunch: React.FC = () => (
  <AbsoluteFill style={{fontFamily: sans}}>
    <GlobalBackdrop />
    <Audio src={staticFile('ledger/audio/ledger-score.wav')} volume={0.72} />
    <EvidenceThread />
    <Series>
      <Series.Sequence durationInFrames={SCENE.premise}><PremiseScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.ticker}><TickerScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.evidence}><EvidenceScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.math}><MathScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.workspace}><WorkspaceScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.chat}><ChatScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.trust}><TrustScene /></Series.Sequence>
      <Series.Sequence durationInFrames={SCENE.close}><CloseScene /></Series.Sequence>
    </Series>
    <GlobalChrome />
  </AbsoluteFill>
);
