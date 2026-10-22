# Ledger launch film

Editable Remotion source for the 51-second Ledger product film. The cut uses exact values from the
live NVIDIA report generated on 2026-10-21 and mirrors the shipped product’s typography, color, and
research workspace.

```powershell
cd video
npm install
npm run audio
npm run studio
```

Render the landscape and vertical cuts:

```powershell
npm run render:all
```

Outputs are written to `video/out/`. Read [CREATIVE_DIRECTION.md](CREATIVE_DIRECTION.md) for the
reference analysis, storyboard, and source rules.
