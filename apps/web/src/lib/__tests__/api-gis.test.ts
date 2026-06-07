import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { listSites, sitesFromGeoJSON } from "../api/gis";

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

const mockGeoJSONResponse = {
  success: true,
  data: {
    type: "FeatureCollection" as const,
    features: [
      {
        type: "Feature" as const,
        geometry: {
          type: "Point",
          coordinates: [139.691648, 35.689488] as [number, number],
        },
        properties: {
          id: "site1",
          name: "Tokyo Site",
          site_type: "construction",
          status: "active",
          address: "Tokyo",
          project_id: "proj1",
        },
      },
    ],
  },
  meta: { total: 1, page: 1, per_page: 20 },
};

describe("listSites", () => {
  it("sends GET to /gis/sites without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockGeoJSONResponse));
    await listSites();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/gis/sites",
      expect.any(Object),
    );
  });

  it("appends page and per_page params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockGeoJSONResponse));
    await listSites({ page: 2, per_page: 10 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=10");
  });

  it("returns GeoJSON FeatureCollection response", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockGeoJSONResponse));
    const result = await listSites();
    expect(result.success).toBe(true);
    expect(result.data.type).toBe("FeatureCollection");
    expect(result.data.features).toHaveLength(1);
  });
});

describe("sitesFromGeoJSON", () => {
  it("maps GeoJSON Point features to GisSite objects", () => {
    const sites = sitesFromGeoJSON(mockGeoJSONResponse);
    expect(sites).toHaveLength(1);
    expect(sites[0].id).toBe("site1");
    expect(sites[0].name).toBe("Tokyo Site");
    expect(sites[0].longitude).toBeCloseTo(139.691648);
    expect(sites[0].latitude).toBeCloseTo(35.689488);
    expect(sites[0].site_type).toBe("construction");
    expect(sites[0].project_id).toBe("proj1");
  });

  it("returns empty array when success is false", () => {
    const result = sitesFromGeoJSON({ ...mockGeoJSONResponse, success: false });
    expect(result).toEqual([]);
  });

  it("returns zero coordinates for null geometry features", () => {
    const response = {
      ...mockGeoJSONResponse,
      data: {
        ...mockGeoJSONResponse.data,
        features: [
          {
            type: "Feature" as const,
            geometry: null,
            properties: { id: "s2", name: "No Geo" },
          },
        ],
      },
    };
    const sites = sitesFromGeoJSON(response);
    expect(sites[0].latitude).toBe(0);
    expect(sites[0].longitude).toBe(0);
  });
});
