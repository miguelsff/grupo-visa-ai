"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { request } from "../lib/api";
import type { KnowledgeMatch } from "../lib/api";
import ChatPanel from "./ChatPanel";
import styles from "./page.module.css";

export default function Home() {
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<KnowledgeMatch[] | null>(null);
  const [searchError, setSearchError] = useState("");
  const [searching, setSearching] = useState(false);

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const term = query.trim();
    if (!term || searching) return;
    setSearching(true);
    setSearchError("");
    setMatches(null);
    try {
      setMatches(await request<KnowledgeMatch[]>(`/knowledge?q=${encodeURIComponent(term)}`));
    } catch {
      setSearchError("No se pudo consultar el procedimiento. Vuelve a intentar la búsqueda.");
    } finally {
      setSearching(false);
    }
  }

  return (
    <>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <a className={styles.brand} href="/" aria-label="Grupo VISA AI, inicio">V<span>·</span>AI</a>
          <span className={styles.project}>GRUPO VISA AI <span>/</span> ASISTENTE OCD</span>
        </div>
      </header>
      <main className={styles.main}>
        <section className={styles.hero} aria-labelledby="title">
          <h1 id="title">Asistente de <span>solicitudes OCD</span></h1>
          <p className={styles.intro}>Describe el cambio que necesitas preparar o pregunta qué exige un procedimiento.</p>
        </section>
        <div className={styles.columns}>
          <ChatPanel />
          <section className={styles.panel} aria-labelledby="knowledge-title">
            <h2 id="knowledge-title">Modelos operativos</h2>
            <form onSubmit={search} className={styles.form}>
              <label htmlFor="query">Busca un procedimiento</label>
              <div className={styles.inputRow}>
                <input id="query" value={query} onChange={(event) => setQuery(event.target.value)} required
                  maxLength={200} placeholder="Ej. Pase a producción" />
                <button disabled={searching || !query.trim()} type="submit">{searching ? "Buscando…" : "Buscar"}</button>
              </div>
            </form>
            {searchError && <p className={styles.error} role="alert">{searchError}</p>}
            <p role="status" className={styles.resultCount}>
              {searching ? "Consultando procedimientos…" : matches && (matches.length ? `Resultados: ${matches.length}` : "No se encontraron resultados.")}
            </p>
            {!!matches?.length && <ul className={styles.results}>
              {matches.map((match, index) => <li key={`${match.code}-${index}`}>
                <a href={match.url} target="_blank" rel="noreferrer">{match.title}</a>
                <p>{match.code} · versión {match.version}</p>
                <p>{match.excerpt}</p>
              </li>)}
            </ul>}
          </section>
        </div>
        <footer className={styles.footer}>
          <span>GRUPO VISA AI</span>
          <a href="/docs" target="_blank" rel="noreferrer">Explorar la API ↗</a>
        </footer>
      </main>
    </>
  );
}
