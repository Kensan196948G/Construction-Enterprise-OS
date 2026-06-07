import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { ApiError, apiRequest, get, post, put, del } from "../api-client";

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

describe("ApiError", () => {
  it("stores status and message", () => {
    const err = new ApiError(404, "Not Found");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not Found");
    expect(err.name).toBe("ApiError");
  });
});

describe("apiRequest", () => {
  it("calls fetch with correct URL and auth header when token exists", async () => {
    localStorage.setItem("auth_token", "test-token");
    mockFetch.mockReturnValueOnce(mockResponse({ data: "ok" }));

    await apiRequest("/test");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/test",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
          "Content-Type": "application/json",
        }),
      }),
    );
  });

  it("sends request without auth header when no token", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ data: "ok" }));

    await apiRequest("/test");

    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers.Authorization).toBeUndefined();
  });

  it("throws ApiError on non-OK response", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ detail: "bad request" }, 400));

    await expect(apiRequest("/test")).rejects.toBeInstanceOf(ApiError);
  });

  it("auto-refreshes token on 401 and retries", async () => {
    localStorage.setItem("auth_token", "expired-token");
    localStorage.setItem("auth_refresh_token", "valid-refresh");

    // First call: 401
    mockFetch.mockReturnValueOnce(mockResponse({}, 401));
    // Refresh call: success
    mockFetch.mockReturnValueOnce(
      mockResponse({
        data: {
          access_token: "new-token",
          refresh_token: "new-refresh",
        },
      }),
    );
    // Retry: success
    mockFetch.mockReturnValueOnce(mockResponse({ data: "ok" }));

    const result = await apiRequest<{ data: string }>("/protected");
    expect(result).toEqual({ data: "ok" });
    expect(localStorage.getItem("auth_token")).toBe("new-token");
  });

  it("throws 401 ApiError when refresh token is missing on 401", async () => {
    localStorage.setItem("auth_token", "expired-token");
    // No refresh token

    mockFetch.mockReturnValueOnce(mockResponse({}, 401));
    // Refresh call will find no refresh_token → returns null
    // But the refresh endpoint is called internally first
    mockFetch.mockReturnValueOnce(mockResponse({}, 401));

    await expect(apiRequest("/protected")).rejects.toMatchObject({
      status: 401,
    });
  });

  it("does not auto-refresh for /auth/* paths on 401", async () => {
    localStorage.setItem("auth_token", "bad-token");

    mockFetch.mockReturnValueOnce(mockResponse({}, 401));

    await expect(apiRequest("/auth/login")).rejects.toBeInstanceOf(ApiError);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
});

describe("HTTP helpers", () => {
  it("get() sends GET request", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ data: [] }));
    await get("/items");
    expect(mockFetch.mock.calls[0][0]).toBe("/api/v1/items");
    expect(mockFetch.mock.calls[0][1]).not.toHaveProperty("method");
  });

  it("post() sends POST with JSON body", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ data: {} }));
    await post("/items", { name: "test" });
    const opts = mockFetch.mock.calls[0][1];
    expect(opts.method).toBe("POST");
    expect(opts.body).toBe(JSON.stringify({ name: "test" }));
  });

  it("put() sends PUT with JSON body", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ data: {} }));
    await put("/items/1", { name: "updated" });
    expect(mockFetch.mock.calls[0][1].method).toBe("PUT");
  });

  it("del() sends DELETE request", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ success: true }));
    await del("/items/1");
    expect(mockFetch.mock.calls[0][1].method).toBe("DELETE");
  });
});
