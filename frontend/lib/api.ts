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
