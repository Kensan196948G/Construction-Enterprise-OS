import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { listDocuments } from "../api/documents";

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

const mockDocumentList = {
  success: true,
  data: {
    documents: [
      {
        id: "doc1",
        name: "Design Drawing v1.pdf",
        file_type: "pdf",
        file_size: 1024000,
        status: "approved" as const,
        updated_at: "2026-06-08T00:00:00",
      },
    ],
    pagination: { page: 1, per_page: 20, total: 1, total_pages: 1 },
  },
};

describe("listDocuments", () => {
  it("sends GET to /documents without params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockDocumentList));

    await listDocuments();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/documents",
      expect.any(Object),
    );
  });

  it("appends page and per_page params", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockDocumentList));

    await listDocuments({ page: 2, per_page: 10 });

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=10");
  });

  it("returns document list with pagination", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockDocumentList));

    const result = await listDocuments();

    expect(result.success).toBe(true);
    expect(result.data.documents).toHaveLength(1);
    expect(result.data.documents[0].id).toBe("doc1");
    expect(result.data.pagination.total).toBe(1);
  });

  it("does not append query string when no params given", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(mockDocumentList));

    await listDocuments();

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toBe("/api/v1/documents");
  });
});
