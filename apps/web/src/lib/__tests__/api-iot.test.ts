import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { listDevices, listAlerts, acknowledgeAlert } from "../api/iot";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});

function mockResponse(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  });
}

describe("listDevices", () => {
  it("sends GET to /iot/devices without params", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, data: { devices: [], total: 0 } }),
    );
    await listDevices();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/iot/devices",
      expect.any(Object),
    );
  });

  it("appends page and per_page params", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, data: { devices: [], total: 0 } }),
    );
    await listDevices({ page: 2, per_page: 5 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=5");
  });

  it("returns devices list", async () => {
    const device = {
      id: "d1",
      name: "Sensor A",
      device_type: "temperature",
      status: "online" as const,
    };
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, data: { devices: [device], total: 1 } }),
    );
    const result = await listDevices();
    expect(result.data.devices).toHaveLength(1);
    expect(result.data.devices[0].id).toBe("d1");
  });
});

describe("listAlerts", () => {
  it("sends GET to /iot/alerts", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, data: { alerts: [], total: 0 } }),
    );
    await listAlerts();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/iot/alerts",
      expect.any(Object),
    );
  });

  it("appends page param when provided", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, data: { alerts: [], total: 0 } }),
    );
    await listAlerts({ page: 3 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=3");
  });
});

describe("acknowledgeAlert", () => {
  it("sends POST to /iot/alerts/:id/acknowledge", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true }));
    const result = await acknowledgeAlert("a1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/iot/alerts/a1/acknowledge",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.success).toBe(true);
  });
});
