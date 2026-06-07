import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  listNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  listTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  listPolicies,
  createPolicy,
  updatePolicy,
} from "../api/notification";

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

describe("listNotifications", () => {
  it("sends GET to /notification without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listNotifications();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification",
      expect.any(Object),
    );
  });

  it("appends page param when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listNotifications({ page: 2 });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
  });

  it("appends status filter when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listNotifications({ status: "unread" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("status=unread");
  });
});

describe("getUnreadCount", () => {
  it("sends GET to /notification/unread-count", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ count: 5 }));
    const result = await getUnreadCount();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/unread-count",
      expect.any(Object),
    );
    expect(result.count).toBe(5);
  });
});

describe("markAsRead", () => {
  it("sends PUT to /notification/:id/read", async () => {
    const n = { id: "n1", user_id: "u1", title: "Test", notification_type: "info", priority: "normal" as const, status: "read" as const };
    mockFetch.mockReturnValueOnce(mockResponse(n));
    await markAsRead("n1");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/n1/read",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("markAllAsRead", () => {
  it("sends POST to /notification/read-all", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ updated: 3 }));
    const result = await markAllAsRead();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/read-all",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.updated).toBe(3);
  });
});

describe("listTemplates", () => {
  it("sends GET to /notification/templates without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listTemplates();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/templates",
      expect.any(Object),
    );
  });

  it("appends template_type when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listTemplates({ template_type: "email" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("template_type=email");
  });
});

describe("getTemplate", () => {
  it("sends GET to /notification/templates/:code", async () => {
    const tmpl = { id: "t1", code: "welcome", name: "Welcome", template_type: "email" };
    mockFetch.mockReturnValueOnce(mockResponse(tmpl));
    const result = await getTemplate("welcome");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/templates/welcome",
      expect.any(Object),
    );
    expect(result.code).toBe("welcome");
  });
});

describe("createTemplate", () => {
  it("sends POST to /notification/templates", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "t1", code: "welcome", name: "Welcome", template_type: "email" }),
    );
    await createTemplate({ code: "welcome", name: "Welcome", template_type: "email" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/templates",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updateTemplate", () => {
  it("sends PUT to /notification/templates/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "t1", code: "welcome", name: "Updated", template_type: "email" }),
    );
    await updateTemplate("t1", { name: "Updated" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/templates/t1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});

describe("listPolicies", () => {
  it("sends GET to /notification/policies without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listPolicies();
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/policies",
      expect.any(Object),
    );
  });

  it("appends organization_id when provided", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));
    await listPolicies({ organization_id: "org1" });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("organization_id=org1");
  });
});

describe("createPolicy", () => {
  it("sends POST to /notification/policies", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "p1", organization_id: "org1", name: "Policy A", event_type: "alert", channels: ["email"] }),
    );
    await createPolicy({
      organization_id: "org1",
      name: "Policy A",
      event_type: "alert",
      channels: ["email"],
    });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/policies",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("updatePolicy", () => {
  it("sends PUT to /notification/policies/:id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ id: "p1", organization_id: "org1", name: "Updated", event_type: "alert", channels: ["email"] }),
    );
    await updatePolicy("p1", { name: "Updated" });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/notification/policies/p1",
      expect.objectContaining({ method: "PUT" }),
    );
  });
});
