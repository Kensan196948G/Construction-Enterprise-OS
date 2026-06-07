import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  chat,
  ragSearch,
  ragGenerate,
  createEmbedding,
  searchEmbeddings,
  listPromptTemplates,
  getPromptTemplate,
  createPromptTemplate,
} from "../api/ai";

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

describe("chat", () => {
  it("sends POST to /ai/chat with messages", async () => {
    const response = {
      message: { role: "assistant", content: "Hello" },
      model: "gpt-4",
    };
    mockFetch.mockReturnValueOnce(mockResponse(response));

    const messages = [{ role: "user" as const, content: "Hi" }];
    const result = await chat(messages);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/chat",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ messages }),
      }),
    );
    expect(result).toEqual(response);
  });

  it("passes temperature and max_tokens options", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ message: { role: "assistant", content: "ok" } }),
    );

    await chat([{ role: "user", content: "test" }], {
      temperature: 0.5,
      max_tokens: 100,
    });

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.temperature).toBe(0.5);
    expect(body.max_tokens).toBe(100);
  });
});

describe("ragSearch", () => {
  it("sends POST to /ai/rag/search with query", async () => {
    const response = {
      answer: "The result",
      sources: [],
      query: "test query",
    };
    mockFetch.mockReturnValueOnce(mockResponse(response));

    const result = await ragSearch("test query");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/rag/search",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result).toEqual(response);
  });

  it("passes optional top_k and filter", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ answer: "", sources: [], query: "q" }),
    );

    await ragSearch("q", { top_k: 5, filter: { type: "doc" } });

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.top_k).toBe(5);
    expect(body.filter).toEqual({ type: "doc" });
  });
});

describe("ragGenerate", () => {
  it("sends POST to /ai/rag/generate", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse({ answer: "generated", sources: [], query: "q" }),
    );

    await ragGenerate("q", "some context");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/rag/generate",
      expect.objectContaining({ method: "POST" }),
    );
    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.query).toBe("q");
    expect(body.context).toBe("some context");
  });
});

describe("createEmbedding", () => {
  it("sends POST to /ai/embeddings with source info", async () => {
    const embedding = { id: "e1", source_type: "document", source_id: "d1" };
    mockFetch.mockReturnValueOnce(mockResponse(embedding));

    const result = await createEmbedding("document", "d1", "content text");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/embeddings",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result).toEqual(embedding);
  });
});

describe("searchEmbeddings", () => {
  it("sends POST with default top_k=10", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ results: [] }));

    await searchEmbeddings("search query");

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.top_k).toBe(10);
    expect(body.query).toBe("search query");
  });

  it("allows custom top_k", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ results: [] }));

    await searchEmbeddings("q", 5);

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.top_k).toBe(5);
  });
});

describe("listPromptTemplates", () => {
  it("sends GET to /ai/prompts", async () => {
    mockFetch.mockReturnValueOnce(mockResponse({ items: [], total: 0 }));

    await listPromptTemplates();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/prompts",
      expect.any(Object),
    );
  });
});

describe("getPromptTemplate", () => {
  it("sends GET to /ai/prompts/:id", async () => {
    const template = {
      id: "p1",
      name: "Template",
      template: "Hello {{name}}",
      variables: ["name"],
    };
    mockFetch.mockReturnValueOnce(mockResponse(template));

    const result = await getPromptTemplate("p1");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/prompts/p1",
      expect.any(Object),
    );
    expect(result).toEqual(template);
  });
});

describe("createPromptTemplate", () => {
  it("sends POST to /ai/prompts with template body", async () => {
    const newTemplate = {
      name: "New",
      template: "Hi {{user}}",
      variables: ["user"],
    };
    const created = { id: "p2", ...newTemplate };
    mockFetch.mockReturnValueOnce(mockResponse(created));

    const result = await createPromptTemplate(newTemplate);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/ai/prompts",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result).toEqual(created);
  });
});
