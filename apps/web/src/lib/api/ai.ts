import { get, post } from "../api-client";

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatResponse {
  message: ChatMessage;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  model?: string;
}

export interface RagResult {
  answer: string;
  sources: Array<{
    id: string;
    content: string;
    score: number;
    metadata: Record<string, unknown>;
  }>;
  query: string;
}

export interface EmbeddingResult {
  id: string;
  source_type: string;
  source_id: string;
  embedding?: number[];
  metadata?: Record<string, unknown>;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description?: string;
  template: string;
  variables: string[];
  category?: string;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function chat(
  messages: ChatMessage[],
  options?: { temperature?: number; max_tokens?: number },
) {
  return post<ChatResponse>("/ai/chat", { messages, ...options });
}

export function ragSearch(
  query: string,
  options?: { top_k?: number; filter?: Record<string, unknown> },
) {
  return post<RagResult>("/ai/rag/search", { query, ...options });
}

export function ragGenerate(query: string, context?: string) {
  return post<RagResult>("/ai/rag/generate", { query, context });
}

export function createEmbedding(
  source_type: string,
  source_id: string,
  content: string,
) {
  return post<EmbeddingResult>("/ai/embeddings", {
    source_type,
    source_id,
    content,
  });
}

export function searchEmbeddings(query: string, top_k = 10) {
  return post<{ results: EmbeddingResult[] }>("/ai/embeddings/search", {
    query,
    top_k,
  });
}

export function listPromptTemplates() {
  return get<ListResponse<PromptTemplate>>("/ai/prompts");
}

export function getPromptTemplate(id: string) {
  return get<PromptTemplate>(`/ai/prompts/${id}`);
}

export function createPromptTemplate(
  body: Omit<PromptTemplate, "id" | "created_at" | "updated_at">,
) {
  return post<PromptTemplate>("/ai/prompts", body);
}
