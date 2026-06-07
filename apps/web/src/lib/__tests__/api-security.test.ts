import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  getSecurityDashboard,
  listVulnerabilities,
  getOpenVulnerabilities,
  createVulnerability,
  updateVulnerability,
  listIncidents,
  getActiveIncidents,
  getIncident,
  createIncident,
  updateIncident,
  addIncidentUpdate,
  listPolicies,
  getPolicy,
  createPolicy,
  updatePolicy,
  reviewPolicy,
} from "../api/security";

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

const mockVuln = {
  id: "v1",
  organization_id: "org1",
  title: "SQL Injection",
  severity: "high" as const,
  status: "open" as const,
};

const mockIncident = {
  id: "i1",
  organization_id: "org1",
  title: "Data Breach",
  incident_type: "breach",
  severity: "critical" as const,
  status: "active" as const,
};

const mockPolicy = {
  id: "pol1",
  organization_id: "org1",
  title: "Access Control Policy",
  policy_type: "access",
  status: "active" as const,
};

describe("getSecurityDashboard", () => {
  it("sends GET to /security/dashboard", async () => {
    const dash = {
      total_vulnerabilities: 10,
      open_vulnerabilities: 5,
      critical_vulnerabilities: 1,
      active_incidents: 2,
      recent_incidents: [],
      vulnerability_by_severity: {},
    };
    mockFetch.mockReturnValueOnce(mockResponse(dash));
    const result = await getSecurityDashboard();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/dashboard",
      expect.any(Object),
    );
    expect(result.total_vulnerabilities).toBe(10);
  });
});

describe("listVulnerabilities", () => {
  it("sends GET to /security/vulnerabilities without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listVulnerabilities();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/vulnerabilities",
      expect.any(Object),
    );
  });

  it("appends severity filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listVulnerabilities({ severity: "critical" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("severity=critical");
  });
});

describe("getOpenVulnerabilities", () => {
  it("sends GET to /security/vulnerabilities/open", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getOpenVulnerabilities();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/vulnerabilities/open",
      expect.any(Object),
    );
  });
});

describe("createVulnerability", () => {
  it("sends POST to /security/vulnerabilities", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockVuln));
    await createVulnerability({
      organization_id: "org1",
      title: "SQL Injection",
      severity: "high",
      status: "open",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/vulnerabilities",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateVulnerability", () => {
  it("sends PUT to /security/vulnerabilities/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ ...mockVuln, status: "resolved" }),
    );
    await updateVulnerability("v1", { status: "resolved" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/vulnerabilities/v1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("listIncidents", () => {
  it("sends GET to /security/incidents without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listIncidents();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents",
      expect.any(Object),
    );
  });

  it("appends status filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listIncidents({ status: "active" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=active");
  });
});

describe("getActiveIncidents", () => {
  it("sends GET to /security/incidents/active", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getActiveIncidents();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents/active",
      expect.any(Object),
    );
  });
});

describe("getIncident", () => {
  it("sends GET to /security/incidents/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockIncident));
    const result = await getIncident("i1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents/i1",
      expect.any(Object),
    );
    expect(result.id).toBe("i1");
  });
});

describe("createIncident", () => {
  it("sends POST to /security/incidents", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockIncident));
    await createIncident({
      organization_id: "org1",
      title: "Data Breach",
      incident_type: "breach",
      severity: "critical",
      status: "active",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateIncident", () => {
  it("sends PUT to /security/incidents/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ ...mockIncident, status: "resolved" }),
    );
    await updateIncident("i1", { status: "resolved" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents/i1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("addIncidentUpdate", () => {
  it("sends POST to /security/incidents/:id/updates", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "u1", incident_id: "i1", message: "Investigating..." }),
    );
    const result = await addIncidentUpdate("i1", "Investigating...");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/incidents/i1/updates",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.message).toBe("Investigating...");
  });
});

describe("listPolicies", () => {
  it("sends GET to /security/policies without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listPolicies();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/policies",
      expect.any(Object),
    );
  });

  it("appends status filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listPolicies({ status: "active" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=active");
  });
});

describe("getPolicy", () => {
  it("sends GET to /security/policies/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockPolicy));
    const result = await getPolicy("pol1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/policies/pol1",
      expect.any(Object),
    );
    expect(result.id).toBe("pol1");
  });
});

describe("createPolicy", () => {
  it("sends POST to /security/policies", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockPolicy));
    await createPolicy({
      organization_id: "org1",
      title: "Access Control Policy",
      policy_type: "access",
      status: "active",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/policies",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updatePolicy", () => {
  it("sends PUT to /security/policies/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ ...mockPolicy, status: "archived" }),
    );
    await updatePolicy("pol1", { status: "archived" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/policies/pol1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("reviewPolicy", () => {
  it("sends POST to /security/policies/:id/review", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockPolicy));
    await reviewPolicy("pol1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/security/policies/pol1/review",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
