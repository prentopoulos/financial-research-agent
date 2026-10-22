import React from 'react';
import {Composition} from 'remotion';
import {LedgerLaunch} from './LedgerLaunch';
import {FPS, TOTAL_FRAMES} from './tokens';

export const Root: React.FC = () => (
  <>
    <Composition
      id="LedgerLaunch"
      component={LedgerLaunch}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="LedgerLaunchVertical"
      component={LedgerLaunch}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
    />
  </>
);
