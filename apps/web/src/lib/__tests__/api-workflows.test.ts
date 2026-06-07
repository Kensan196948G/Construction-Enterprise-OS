import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listWorkflowInstances,
  getPendingWorkflows,
  approveWorkflow,
  rejectWorkflow,
} from "../api/workflows";

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

describe("listWorkflowInstances", () => {
  it("sends GET to /workflow/instances without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true, data: [] }));

    await listWorkflowInstances();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/workflow/instances",
      expect.any(Object),
    );
  });

  it("appends page and per_page when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true, data: [] }));

    await listWorkflowInstances({ page: 2, per_page: 10 });

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=10");
  });
});

describe("getPendingWorkflows", () => {
  it("sends GET to /workflow/instances/pending", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true, data: [] }));

    await getPendingWorkflows();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/workflow/instances/pending",
      expect.any(Object),
    );
  });
});

describe("approveWorkflow", () => {
  it("sends POST to /workflow/instances/:id/approve", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true }));

    const result = await approveWorkflow("wf1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/workflow/instances/wf1/approve",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.success).toBe(true);
  });

  it("sends comment in body when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true }));

    await approveWorkflow("wf1", "Looks good");

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.comment).toBe("Looks good");
  });
});

describe("rejectWorkflow", () => {
  it("sends POST to /workflow/instances/:id/reject", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true }));

    await rejectWorkflow("wf1", "Missing docs");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/workflow/instances/wf1/reject",
      expect.objectContaining({ method: "POST" }),
    );
    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.comment).toBe("Missing docs");
  });
});
