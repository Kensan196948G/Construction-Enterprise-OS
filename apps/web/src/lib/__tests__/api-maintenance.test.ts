import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listMaintenanceRecords,
  getOverdueRecords,
  getMaintenanceRecord,
  createMaintenanceRecord,
  updateMaintenanceRecord,
  listInspections,
  getUpcomingInspections,
  getOverdueInspections,
  getInspection,
  createInspection,
  updateInspection,
  listDisasters,
  getDisaster,
  createDisaster,
  updateDisaster,
  createRecoveryPlan,
  getRecoveryPlan,
  updateRecoveryPlan,
} from "../api/maintenance";

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

const mockRecord = {
  id: "r1",
  organization_id: "org1",
  title: "HVAC Maintenance",
  maintenance_type: "preventive",
  status: "scheduled" as const,
};

describe("listMaintenanceRecords", () => {
  it("sends GET to /maintenance/records without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listMaintenanceRecords();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/records",
      expect.any(Object),
    );
  });

  it("appends status filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listMaintenanceRecords({ status: "overdue" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=overdue");
  });
});

describe("getOverdueRecords", () => {
  it("sends GET to /maintenance/records/overdue", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getOverdueRecords();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/records/overdue",
      expect.any(Object),
    );
  });
});

describe("getMaintenanceRecord", () => {
  it("sends GET to /maintenance/records/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockRecord));
    const result = await getMaintenanceRecord("r1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/records/r1",
      expect.any(Object),
    );
    expect(result.id).toBe("r1");
  });
});

describe("createMaintenanceRecord", () => {
  it("sends POST to /maintenance/records", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockRecord));
    await createMaintenanceRecord({
      organization_id: "org1",
      title: "HVAC Maintenance",
      maintenance_type: "preventive",
      status: "scheduled",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/records",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateMaintenanceRecord", () => {
  it("sends PUT to /maintenance/records/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ ...mockRecord, status: "completed" }),
    );
    await updateMaintenanceRecord("r1", { status: "completed" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/records/r1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("listInspections", () => {
  it("sends GET to /maintenance/inspections without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listInspections();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections",
      expect.any(Object),
    );
  });

  it("appends organization_id when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listInspections({ organization_id: "org1" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("organization_id=org1");
  });
});

describe("getUpcomingInspections", () => {
  it("sends GET to /maintenance/inspections/upcoming", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getUpcomingInspections();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections/upcoming",
      expect.any(Object),
    );
  });
});

describe("getOverdueInspections", () => {
  it("sends GET to /maintenance/inspections/overdue", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getOverdueInspections();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections/overdue",
      expect.any(Object),
    );
  });
});

describe("getInspection", () => {
  it("sends GET to /maintenance/inspections/:id", async () => {
    const insp = {
      id: "i1",
      organization_id: "org1",
      inspection_type: "safety",
      status: "scheduled" as const,
    };
    mockFetch.mockReturnValueOnce(mockResponse(insp));
    const result = await getInspection("i1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections/i1",
      expect.any(Object),
    );
    expect(result.id).toBe("i1");
  });
});

describe("createInspection", () => {
  it("sends POST to /maintenance/inspections", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "i1", organization_id: "org1", inspection_type: "safety", status: "scheduled" }),
    );
    await createInspection({ organization_id: "org1", inspection_type: "safety", status: "scheduled" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateInspection", () => {
  it("sends PUT to /maintenance/inspections/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "i1", organization_id: "org1", inspection_type: "safety", status: "completed" }),
    );
    await updateInspection("i1", { status: "completed" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/inspections/i1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("listDisasters", () => {
  it("sends GET to /maintenance/disasters without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listDisasters();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/disasters",
      expect.any(Object),
    );
  });

  it("appends disaster_type filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listDisasters({ disaster_type: "flood" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("disaster_type=flood");
  });
});

describe("getDisaster", () => {
  it("sends GET to /maintenance/disasters/:id", async () => {
    const d = {
      id: "d1",
      organization_id: "org1",
      disaster_type: "flood",
      title: "Flood Event",
      severity: "major" as const,
      status: "active" as const,
    };
    mockFetch.mockReturnValueOnce(mockResponse(d));
    const result = await getDisaster("d1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/disasters/d1",
      expect.any(Object),
    );
    expect(result.id).toBe("d1");
  });
});

describe("createDisaster", () => {
  it("sends POST to /maintenance/disasters", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "d1", organization_id: "org1", disaster_type: "flood", title: "Flood", severity: "major", status: "active" }),
    );
    await createDisaster({
      organization_id: "org1",
      disaster_type: "flood",
      title: "Flood Event",
      severity: "major",
      status: "active",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/disasters",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateDisaster", () => {
  it("sends PUT to /maintenance/disasters/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "d1", organization_id: "org1", disaster_type: "flood", title: "Flood", severity: "major", status: "resolved" }),
    );
    await updateDisaster("d1", { status: "resolved" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/disasters/d1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("createRecoveryPlan", () => {
  it("sends POST to /maintenance/disasters/:id/recovery-plans", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "rp1", disaster_id: "d1", title: "Recovery Plan", status: "draft", priority: 1 }),
    );
    await createRecoveryPlan("d1", { title: "Recovery Plan", status: "draft", priority: 1 });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/disasters/d1/recovery-plans",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("getRecoveryPlan", () => {
  it("sends GET to /maintenance/recovery-plans/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "rp1", disaster_id: "d1", title: "Recovery Plan", status: "draft", priority: 1 }),
    );
    const result = await getRecoveryPlan("rp1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/recovery-plans/rp1",
      expect.any(Object),
    );
    expect(result.id).toBe("rp1");
  });
});

describe("updateRecoveryPlan", () => {
  it("sends PUT to /maintenance/recovery-plans/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "rp1", disaster_id: "d1", title: "Recovery Plan", status: "active", priority: 1 }),
    );
    await updateRecoveryPlan("rp1", { status: "active" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/maintenance/recovery-plans/rp1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});
