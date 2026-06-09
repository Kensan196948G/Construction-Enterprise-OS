/**
 * Auth bypass configuration (development-only escape hatch).
 *
 * SECURITY: The dashboard auth guard is enforced by default. The bypass is
 * opt-in and only activates when `NEXT_PUBLIC_AUTH_BYPASS` is the exact string
 * `"true"`. Any other value — including `undefined` (the production default) —
 * keeps the guard active. This guarantees that forgetting to set the variable,
 * or setting it to an unexpected value, fails closed (secure), not open.
 *
 * Usage:
 *   - Production / staging: leave `NEXT_PUBLIC_AUTH_BYPASS` unset → guard ON.
 *   - Local development demo: set `NEXT_PUBLIC_AUTH_BYPASS=true` → guard OFF.
 *
 * Implemented as a pure function so the decision is unit-testable without
 * depending on the build-time `process.env` inlining performed by Next.js.
 */
export function isAuthBypassEnabled(
  raw: string | undefined = process.env.NEXT_PUBLIC_AUTH_BYPASS,
): boolean {
  return raw === "true";
}
