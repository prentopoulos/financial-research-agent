export const FPS = 30;

export const COLORS = {
  ink: '#0e131c',
  paper: '#f7f8fa',
  white: '#ffffff',
  blue: '#306bd9',
  blueSoft: '#eaf1fb',
  muted: '#65758b',
  line: '#d5deea',
  green: '#18743f',
  red: '#a32626',
} as const;

export const SCENE = {
  premise: 105,       // 00:00.0 - 00:03.5
  ticker: 135,        // 00:03.5 - 00:08.0
  evidence: 165,      // 00:08.0 - 00:13.5
  math: 165,          // 00:13.5 - 00:19.0
  workspace: 360,     // 00:19.0 - 00:31.0
  chat: 390,          // 00:31.0 - 00:44.0
  trust: 105,         // 00:44.0 - 00:47.5
  close: 105,         // 00:47.5 - 00:51.0
} as const;

export const SCENE_START = {
  premise: 0,
  ticker: SCENE.premise,
  evidence: SCENE.premise + SCENE.ticker,
  math: SCENE.premise + SCENE.ticker + SCENE.evidence,
  workspace: SCENE.premise + SCENE.ticker + SCENE.evidence + SCENE.math,
  chat: SCENE.premise + SCENE.ticker + SCENE.evidence + SCENE.math + SCENE.workspace,
  trust: SCENE.premise + SCENE.ticker + SCENE.evidence + SCENE.math + SCENE.workspace + SCENE.chat,
  close: SCENE.premise + SCENE.ticker + SCENE.evidence + SCENE.math + SCENE.workspace + SCENE.chat + SCENE.trust,
} as const;

export const TOTAL_FRAMES = Object.values(SCENE).reduce((sum, frames) => sum + frames, 0);

export const EASE = {
  enter: {damping: 22, stiffness: 170, mass: 0.8},
  settle: {damping: 200, stiffness: 150, mass: 0.9},
} as const;
