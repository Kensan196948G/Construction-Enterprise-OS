import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listBimModels,
  getBimModel,
  createBimModel,
  updateBimModel,
  deleteBimModel,
  getModelElements,
  searchElements,
  listPointClouds,
  createPointCloud,
  getPointCloud,
  updatePointCloud,
  deletePointCloud,
} from "../api/bim";

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

const mockModel = {
  id: "m1",
  organization_id: "org1",
  name: "Building A",
  file_path: "/models/a.ifc",
  status: "active",
};

describe("listBimModels", () => {
  it("sends GET to /bim/models without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listBimModels();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/models",
      expect.any(Object),
    );
  });

  it("appends organization_id and page params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listBimModels({ organization_id: "org1", page: 2 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("organization_id=org1");
    expect(url).toContain("page=2");
  });
});

describe("getBimModel", () => {
  it("sends GET to /bim/models/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockModel));
    const result = await getBimModel("m1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/models/m1",
      expect.any(Object),
    );
    expect(result.id).toBe("m1");
  });
});

describe("createBimModel", () => {
  it("sends POST to /bim/models", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockModel));
    await createBimModel({
      organization_id: "org1",
      name: "Building A",
      file_path: "/models/a.ifc",
      status: "active",
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/models",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateBimModel", () => {
  it("sends PUT to /bim/models/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ ...mockModel, name: "Updated" }));
    await updateBimModel("m1", { name: "Updated" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/models/m1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("deleteBimModel", () => {
  it("sends DELETE to /bim/models/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null, 204));
    await deleteBimModel("m1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/models/m1",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});

describe("getModelElements", () => {
  it("sends GET to /bim/:modelId/elements", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getModelElements("m1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/m1/elements",
      expect.any(Object),
    );
  });

  it("appends category and level filters", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await getModelElements("m1", { category: "Wall", level: "L1" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("category=Wall");
    expect(url).toContain("level=L1");
  });
});

describe("searchElements", () => {
  it("sends GET with query param", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await searchElements("door");
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("/api/v1/bim/elements/search");
    expect(url).toContain("query=door");
  });

  it("appends model_id when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse([]));
    await searchElements("door", "m1");
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("model_id=m1");
  });
});

describe("listPointClouds", () => {
  it("sends GET to /bim/pointclouds", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listPointClouds();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/pointclouds",
      expect.any(Object),
    );
  });
});

describe("createPointCloud", () => {
  it("sends POST to /bim/pointclouds", async () => {
    const pc = {
      organization_id: "org1",
      name: "Site Scan",
      file_path: "/clouds/scan.las",
      status: "active",
    };
    mockFetch.mockReturnValueOnce(mockResponse({ id: "pc1", ...pc }));
    await createPointCloud(pc);
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/pointclouds",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("getPointCloud", () => {
  it("sends GET to /bim/pointclouds/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "pc1", name: "Scan", organization_id: "org1", file_path: "/f", status: "active" }),
    );
    const result = await getPointCloud("pc1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/pointclouds/pc1",
      expect.any(Object),
    );
    expect(result.id).toBe("pc1");
  });
});

describe("updatePointCloud", () => {
  it("sends PUT to /bim/pointclouds/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "pc1", name: "Updated", organization_id: "org1", file_path: "/f", status: "active" }),
    );
    await updatePointCloud("pc1", { name: "Updated" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/pointclouds/pc1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("deletePointCloud", () => {
  it("sends DELETE to /bim/pointclouds/:id", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(null, 204));
    await deletePointCloud("pc1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/bim/pointclouds/pc1",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});
