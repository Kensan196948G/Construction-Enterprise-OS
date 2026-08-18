# Construction Enterprise OS — brand spec

Extracted from the attached `Construction-Enterprise-OS---Standalone-_1_.html` (the platform's own dashboard system). No values guessed; all tokens derived from the app's CSS variables and palette.

## Tokens (OKLch)

```css
:root {
  --bg:        oklch(0.984 0.003 247.9); /* #f8fafc */
  --surface:   oklch(1.000 0.000 89.9);  /* #ffffff */
  --fg:        oklch(0.208 0.040 265.8); /* #0f172a */
  --muted:     oklch(0.554 0.041 257.4); /* #64748b */
  --border:    oklch(0.929 0.013 255.5); /* #e2e8f0 */
  --accent:    oklch(0.505 0.212 262.9); /* #1a56db */

  /* state colors */
  --ok:        oklch(0.627 0.170 149.2); /* #16a34a */
  --warn:      oklch(0.705 0.187 47.6);  /* #f97316 */
  --danger:    oklch(0.577 0.215 27.3);  /* #dc2626 */

  /* dark-surface variants (app dark mode) */
  --surface-dark: oklch(0.279 0.037 260.0); /* #1e293b */
  --border-dark:  oklch(0.372 0.039 257.3); /* #334155 */
  --muted-dark:   oklch(0.711 0.035 256.8); /* #94a3b8 */
  --accent-dark:  oklch(0.623 0.188 259.8); /* #3b82f6 */
}
```

## Font stacks

- **Display / Body:** `'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', system-ui, sans-serif` (single family, utilitarian/data-dense brief — weight contrast 400/500/700/800 carries hierarchy).
- **Mono:** `'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace` — all numerics, labels, eyebrows, KPI values.

## Observed rules

1. **Slate + blue.** Near-black navy text `#0f172a` on near-white `#f8fafc`; a single saturated blue accent `#1a56db` does all primary signaling.
2. **Dark surfaces are navy, not gray.** Inverted panels use `#0f172a`/`#1e293b` with a lighter blue `#3b82f6` accent.
3. **Numbers always in JetBrains Mono**, labels/body in Noto Sans JP — a hard split between value and prose.
4. **State = color pair, not decoration.** Green/amber/red encode status (稼働/警戒/危険) with a matching 10% tint background.
5. **Flat cards with a 1px border and 12px radius** — no heavy shadows; density over ornament.

## One-line summary

A technical, data-dense enterprise-OS aesthetic: near-white/ navy slate surfaces, one blue accent, Noto Sans JP + JetBrains Mono, status communicated by restrained color pairs.
