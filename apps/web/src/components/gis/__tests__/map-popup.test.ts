import { describe, it, expect } from "vitest";
import { buildSitePopup, type MapSitePin } from "../map-popup";

function makePin(overrides: Partial<MapSitePin> = {}): MapSitePin {
  return {
    id: 1,
    name: "現場A",
    lat: 35.6,
    lng: 139.7,
    status: "active",
    workers: 0,
    alerts: 0,
    ...overrides,
  };
}

describe("buildSitePopup", () => {
  it("renders the site name as text", () => {
    const el = buildSitePopup(makePin({ name: "渋谷駅前再開発 C工区" }));

    expect(el.textContent).toContain("渋谷駅前再開発 C工区");
    expect(el.querySelector("p")).not.toBeNull();
  });

  it("treats an injected site name as inert text", () => {
    const malicious = '<img src=x onerror="window.__xss=1">';

    const el = buildSitePopup(makePin({ name: malicious }));

    expect(el.querySelector("img")).toBeNull();
    expect(el.querySelector("script")).toBeNull();
    expect(el.textContent).toContain(malicious);
    expect((window as unknown as { __xss?: number }).__xss).toBeUndefined();
  });

  it("shows worker and alert rows only when greater than zero", () => {
    const el = buildSitePopup(makePin({ workers: 3, alerts: 2 }));

    expect(el.textContent).toContain("作業員: 3名");
    expect(el.textContent).toContain("2件 アラート");
  });

  it("omits worker and alert rows when zero", () => {
    const el = buildSitePopup(makePin());

    expect(el.textContent).not.toContain("作業員");
    expect(el.textContent).not.toContain("アラート");
  });

  it("formats coordinates to four decimal places", () => {
    const el = buildSitePopup(makePin({ lat: 35.681236, lng: 139.767125 }));

    expect(el.textContent).toContain("35.6812, 139.7671");
  });
});
