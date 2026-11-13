"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { request } from "../lib/api";
import type { KnowledgeMatch } from "../lib/api";
import styles from "./page.module.css";

export default function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<KnowledgeMatch[] | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true); setError(""); setMatches(null);
    try { setMatches(await request<KnowledgeMatch[]>(`/knowledge?q=${encodeURIComponent(query.trim())}`)); }
    catch { setError("No se pudo consultar el procedimiento. Vuelve a intentar la búsqueda."); }
    finally { setLoading(false); }
  }
  return <section aria-labelledby="knowledge-title">
    <form className={styles.searchForm} onSubmit={search}>
      <label id="knowledge-title" htmlFor="query">Buscar procedimientos</label>
      <input id="query" maxLength={200} required value={query} onChange={e => setQuery(e.target.value)} placeholder="Ej. Microservicios"/>
      <button className={styles.secondaryButton} disabled={loading || !query.trim()}>{loading ? "Buscando…" : "Buscar"}</button>
    </form>
    {error && <p role="alert" className={styles.error}>{error}</p>}
    <p role="status" className={styles.status}>{loading ? "Consultando procedimientos…" : matches && (matches.length ? `Resultados: ${matches.length}` : "No se encontraron resultados.")}</p>
    {!!matches?.length && <ul className={styles.searchResults}>{matches.map((match, i) => <li key={`${match.code}-${i}`}>
      <a href={match.url} target="_blank" rel="noreferrer">{match.title}</a><small>{match.code} · versión {match.version}</small><p>{match.excerpt}</p>
    </li>)}</ul>}
  </section>;
}
