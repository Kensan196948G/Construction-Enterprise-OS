import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listDataSources,
  createDataSource,
  getDataSource,
  updateDataSource,
  deleteDataSource,
  testDataSourceConnection,
  listPipelines,
  runPipeline,
  listReports,
  generateReport,
  exportReport,
} from "../api/analytics";

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

describe("listDataSources", () => {
  it("sends GET to /analytics/datasources without params", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ items: [], total: 0, page: 1, per_page: 20 }),
    );

    await listDataSources();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources",
      expect.any(Object),
    );
  });

  it("appends query params when provided", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ items: [], total: 0, page: 2, per_page: 20 }),
    );

    await listDataSources({ organization_id: "org1", page: 2 });

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("organization_id=org1");
    expect(url).toContain("page=2");
  });
});

describe("createDataSource", () => {
  it("sends POST to /analytics/datasources", async () => {
    const ds = {
      organization_id: "org1",
      name: "DB Source",
      source_type: "postgresql",
      connection_config: { host: "localhost" },
      status: "active",
    };
    mockFetch.mockReturnValueOnce(mockResponse({ id: "ds1", ...ds }));

    await createDataSource(ds);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("getDataSource", () => {
  it("sends GET to /analytics/datasources/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        id: "ds1",
        name: "DB",
        source_type: "pg",
        status: "active",
        organization_id: "org1",
        connection_config: {},
      }),
    );

    await getDataSource("ds1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources/ds1",
      expect.any(Object),
    );
  });
});

describe("updateDataSource", () => {
  it("sends PUT to /analytics/datasources/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        id: "ds1",
        name: "Updated",
        source_type: "pg",
        status: "active",
        organization_id: "org1",
        connection_config: {},
      }),
    );

    await updateDataSource("ds1", { name: "Updated" });

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources/ds1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("deleteDataSource", () => {
  it("sends DELETE to /analytics/datasources/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null, 204));

    await deleteDataSource("ds1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources/ds1",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});

describe("testDataSourceConnection", () => {
  it("sends POST to test endpoint", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ success: true, message: "Connected", source_type: "pg" }),
    );

    const result = await testDataSourceConnection("ds1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/datasources/ds1/test",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.success).toBe(true);
  });
});

describe("listPipelines", () => {
  it("sends GET to /analytics/pipelines", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ items: [], total: 0, page: 1, per_page: 20 }),
    );

    await listPipelines();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/pipelines",
      expect.any(Object),
    );
  });
});

describe("runPipeline", () => {
  it("sends POST to /analytics/pipelines/:id/run", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({
        pipeline_id: "p1",
        status: "running",
        started_at: "2026-06-08T00:00:00",
      }),
    );

    const result = await runPipeline("p1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/pipelines/p1/run",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.pipeline_id).toBe("p1");
  });
});

describe("listReports", () => {
  it("sends GET to /analytics/reports", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ items: [], total: 0, page: 1, per_page: 20 }),
    );

    await listReports();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/reports",
      expect.any(Object),
    );
  });
});

describe("generateReport", () => {
  it("sends POST to /analytics/reports/:id/generate", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ report_id: "r1", data: [], summary: {} }),
    );

    const result = await generateReport("r1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/analytics/reports/r1/generate",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.report_id).toBe("r1");
  });
});

describe("exportReport", () => {
  it("sends POST with default json format", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ report_id: "r1", format: "json", content: "{}" }),
    );

    await exportReport("r1");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("format=json"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("allows csv format", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ report_id: "r1", format: "csv", content: "a,b" }),
    );

    await exportReport("r1", "csv");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("format=csv"),
      expect.objectContaining({ method: "POST" }),
    );
  });
});
