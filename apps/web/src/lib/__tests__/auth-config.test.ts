import { describe, it, expect } from "vitest";
import { isAuthBypassEnabled } from "../auth-config";

describe("isAuthBypassEnabled", () => {
  it("returns true only for the exact string 'true'", () => {
    expect(isAuthBypassEnabled("true")).toBe(true);
  });

  it("fails closed (false) when the value is undefined — the production default", () => {
    expect(isAuthBypassEnabled(undefined)).toBe(false);
  });

  it("fails closed for an empty string", () => {
    expect(isAuthBypassEnabled("")).toBe(false);
  });

  it("fails closed for the literal string 'false'", () => {
    expect(isAuthBypassEnabled("false")).toBe(false);
  });

  it("does not accept truthy-looking values other than 'true'", () => {
    for (const v of ["TRUE", "True", "1", "yes", "on", " true", "true "]) {
      expect(isAuthBypassEnabled(v)).toBe(false);
    }
  });
});
