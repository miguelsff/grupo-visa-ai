export type Greeting = {
  id: string;
  name: string;
  message: string;
  created_at: string;
};

export type HelloResponse = { message: string; greetings: Greeting[] };
export type Health = {
  status: "ok";
  backend: "ok";
  sqlite: "ok";
  fts5: "ok";
  frontend: "ok" | "missing";
  document_count: number;
  greeting_count: number;
};
export type Integration = {
  name: string;
  status: "pending" | "configured";
  detail: string;
};
export type KnowledgeMatch = {
  code: string;
  title: string;
  url: string;
  version: string;
  excerpt: string;
};

export type ChatCitation = KnowledgeMatch & {
  point_id: string;
  record_key: string;
  source_id: string;
  origin: string;
  document_version: string | null;
  locator: string;
};

type Category = "microservicio" | "azure" | "red" | "identidad";

export type ChatResponse = {
  revision: number;
  status: "pending" | "reviewed" | "unavailable";
  answer: string;
  draft: {
    sensitive_detected: boolean;
    categories: Category[];
    category_messages: Partial<Record<Category, number>>;
    facts: Record<string, {
      scope: "comun" | Category;
      name: string;
      value: string;
      quote: string;
      message_id: number;
    }>;
  };
  collection: string | null;
  validations: {
    check: "V-01" | "V-02" | "V-03";
    rule_id: string;
    status: "CUMPLE" | "FALTA_INFORMACION" | "ERROR" | "NO_VERIFICABLE";
    detail: string;
    missing: string[];
    reference: ChatCitation;
  }[];
  sources: ChatCitation[];
  questions: string[];
  error: string | null;
};

async function chatRequest(options: RequestInit): Promise<ChatResponse> {
  const response = await fetch("/api/chat", {
    credentials: "same-origin",
    cache: "no-store",
    ...options,
  });
  if (response.status === 401) throw new Error("Inicia sesión para usar el chat.");
  if (response.status === 422) throw new Error("Escribe un mensaje de entre 1 y 12 000 caracteres.");
  const body = response.headers.get("content-type")?.includes("application/json")
    ? await response.json()
    : null;
  if (body && (response.ok || (response.status === 503 && body.status === "unavailable"))) return body;
  throw new Error(typeof body?.detail === "string" ? body.detail : "No se pudo completar la consulta.");
}

export function getChat(signal?: AbortSignal): Promise<ChatResponse> {
  return chatRequest({ method: "GET", signal });
}

export function sendChat(message: string, signal?: AbortSignal): Promise<ChatResponse> {
  return chatRequest({
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}/api${path}`, {
    ...options,
    cache: "no-store",
    signal: AbortSignal.timeout(8000),
  });
  if (!response.ok) {
    throw new Error(`La solicitud falló (${response.status}). Comprueba el estado de la aplicación.`);
  }
  return (await response.json()) as T;
}
