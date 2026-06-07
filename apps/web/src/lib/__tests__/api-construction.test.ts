import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { listSchedules } from "../api/construction";

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

const mockScheduleList = {
  items: [
    {
      id: "s1",
      name: "Foundation Work",
      status: "in_progress",
      progress: 50,
    },
  ],
  total: 1,
  page: 1,
  per_page: 20,
};

describe("listSchedules", () => {
  it("sends GET to /construction/schedules without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockScheduleList));
    await listSchedules();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/construction/schedules",
      expect.any(Object),
    );
  });

  it("appends page and per_page params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockScheduleList));
    await listSchedules({ page: 2, per_page: 10 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=10");
  });

  it("returns schedule list with pagination", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockScheduleList));
    const result = await listSchedules();
    expect(result.items).toHaveLength(1);
    expect(result.items[0].id).toBe("s1");
    expect(result.total).toBe(1);
  });

  it("does not append query string when no params given", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockScheduleList));
    await listSchedules();
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toBe("/api/v1/construction/schedules");
  });
});
