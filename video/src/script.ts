import {SCENE_START} from './tokens';

export type Cue = {at: number; text: string};

export const CUES: Cue[] = [
  {at: SCENE_START.premise + 14, text: 'A ticker is not a thesis.'},
  {at: SCENE_START.ticker + 16, text: 'Start with the evidence.'},
  {at: SCENE_START.evidence + 12, text: 'Filings. Prices. Periods. Sources.'},
  {at: SCENE_START.math + 14, text: 'Let Python do the math.'},
  {at: SCENE_START.workspace + 20, text: 'A complete research memo. Built from live public data.'},
  {at: SCENE_START.chat + 12, text: 'Then ask the report.'},
  {at: SCENE_START.trust + 10, text: 'Every answer keeps its evidence.'},
  {at: SCENE_START.close + 10, text: 'Ledger. Research you can inspect.'},
];
