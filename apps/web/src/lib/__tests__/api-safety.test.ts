import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listHazards,
  getOpenHazards,
  createHazard,
  updateHazard,
  listIncidents,
  getIncident,
  createIncident,
  listInspections,
  getInspectionStats,
  createInspection,
  completeInspection,
} from "../api/safety";

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

describe("listHazards", () => {
  it("sends GET to /safety/hazards without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listHazards();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/hazards",
      expect.any(Object),
    );
  });

  it("appends status and severity filters", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listHazards({ status: "open", severity: "high" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=open");
    expect(url).toContain("severity=high");
  });
});

describe("getOpenHazards", () => {
  it("sends GET to /safety/hazards/open", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getOpenHazards();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/hazards/open",
      expect.any(Object),
    );
  });
});

describe("createHazard", () => {
  it("sends POST to /safety/hazards", async () => {
    const hazard = {
      organization_id: "org1",
      title: "Fall risk",
      severity: "high" as const,
      status: "open" as const,
    };
    mockFetch.mockReturnValueOnce(mockResponse({ id: "h1", ...hazard }));

    await createHazard(hazard);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/hazards",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateHazard", () => {
  it("sends PUT to /safety/hazards/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        id: "h1",
        title: "Updated",
        organization_id: "org1",
        severity: "low" as const,
        status: "resolved" as const,
      }),
    );
    await updateHazard("h1", { status: "resolved" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/hazards/h1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("listIncidents", () => {
  it("sends GET to /safety/incidents", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listIncidents();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/incidents",
      expect.any(Object),
    );
  });
});

describe("getIncident", () => {
  it("sends GET to /safety/incidents/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        id: "i1",
        organization_id: "org1",
        title: "Incident",
        incident_type: "fall",
        severity: "moderate" as const,
        status: "open",
      }),
    );
    await getIncident("i1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/incidents/i1",
      expect.any(Object),
    );
  });
});

describe("createIncident", () => {
  it("sends POST to /safety/incidents", async () => {
    const incident = {
      organization_id: "org1",
      title: "Worker fall",
      incident_type: "fall",
      severity: "serious" as const,
      status: "open",
    };
    mockFetch.mockReturnValueOnce(mockResponse({ id: "i2", ...incident }));

    await createIncident(incident);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/incidents",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("listInspections", () => {
  it("sends GET to /safety/inspections", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listInspections();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/inspections",
      expect.any(Object),
    );
  });
});

describe("getInspectionStats", () => {
  it("sends GET to /safety/inspections/stats", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ total: 10, completed: 8, failed: 2 }),
    );
    const result = await getInspectionStats();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/inspections/stats",
      expect.any(Object),
    );
    expect(result.total).toBe(10);
  });
});

describe("createInspection", () => {
  it("sends POST to /safety/inspections", async () => {
    const inspection = {
      organization_id: "org1",
      inspection_type: "routine",
      status: "scheduled" as const,
    };
    mockFetch.mockReturnValueOnce(mockResponse({ id: "ins1", ...inspection }));

    await createInspection(inspection);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/inspections",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("completeInspection", () => {
  it("sends POST to /safety/inspections/:id/complete with score and notes", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        id: "ins1",
        organization_id: "org1",
        inspection_type: "routine",
        status: "completed" as const,
      }),
    );

    await completeInspection("ins1", { score: 95, notes: "All good" });

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/safety/inspections/ins1/complete",
      expect.objectContaining({ method: "POST" }),
    );
    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.score).toBe(95);
    expect(body.notes).toBe("All good");
  });
});
