"use client";

import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { request } from "../lib/api";
import type { Greeting, Health, HelloResponse, Integration, KnowledgeMatch } from "../lib/api";
import styles from "./page.module.css";

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [greetings, setGreetings] = useState<Greeting[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [name, setName] = useState("Equipo VISA");
  const [query, setQuery] = useState("microservicios");
  const [matches, setMatches] = useState<KnowledgeMatch[] | null>(null);
  const [reply, setReply] = useState("");
  const [error, setError] = useState("");
  const [searchError, setSearchError] = useState("");
  const [sending, setSending] = useState(false);
  const [searching, setSearching] = useState(false);

  const refresh = useCallback(async () => {
    const [status, hello, external] = await Promise.all([
      request<Health>("/health"),
      request<HelloResponse>("/hello"),
      request<Integration[]>("/integrations"),
    ]);
    setHealth(status);
    setGreetings(hello.greetings);
    setIntegrations(external);
  }, []);

  useEffect(() => {
    refresh().catch(() => setError("No fue posible conectar con la API. Vuelve a comprobar la conexión."));
  }, [refresh]);

  async function sendHello(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSending(true);
    setError("");
    setReply("");
    try {
      const greeting = await request<Greeting>("/hello", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      setReply(greeting.message);
      await refresh();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "No fue posible guardar el saludo.");
    } finally {
      setSending(false);
    }
  }

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearching(true);
    setSearchError("");
    try {
      setMatches(await request<KnowledgeMatch[]>(`/knowledge?q=${encodeURIComponent(query)}`));
    } catch {
      setSearchError("No fue posible consultar el conocimiento local. Inténtalo otra vez.");
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
          <span className={styles.environment}>ENTORNO LOCAL</span>
        </div>
      </header>
      <main className={styles.main}>
        <section className={styles.hero} aria-labelledby="title">
          <p className={styles.eyebrow}>ETAPA 01 · BASE DEL PROYECTO</p>
          <h1 id="title">Todo empieza con un<br /><span>hola mundo.</span></h1>
          <p className={styles.intro}>Una base conectada para construir el asistente OCD.<br />Prueba la interfaz, la API y el almacenamiento local.</p>
          <p className={styles.stack}>NEXT.JS <span>→</span> FASTAPI <span>→</span> SQLITE</p>
        </section>

        <section className={styles.statusGrid} aria-label="Estado de los componentes">
          {[
            ["01", "Interfaz", "Next.js + TypeScript", health?.frontend === "ok"],
            ["02", "API", "Python + FastAPI", health?.backend === "ok"],
            ["03", "Persistencia", "SQLite + FTS5", health?.sqlite === "ok"],
          ].map(([number, label, technology, ready]) => (
            <article key={String(label)} className={styles.statusCard}>
              <span className={styles.cardNumber}>{number}</span>
              <div><h2>{label}</h2><p>{technology}</p></div>
              <span className={`${styles.badge} ${ready ? styles.ready : styles.waiting}`}>
                {ready ? "Disponible" : error ? "Sin conexión" : "Comprobando"}
              </span>
            </article>
          ))}
        </section>

        <div className={styles.columns}>
          <section className={styles.panel} aria-labelledby="hello-title">
            <p className={styles.panelLabel}>PRUEBA DE CONEXIÓN</p>
            <h2 id="hello-title">Envía tu primer saludo</h2>
            <p className={styles.description}>La API responde y guarda el saludo en la base local.</p>
            <form onSubmit={sendHello} className={styles.form}>
              <label htmlFor="name">¿Cómo te llamas?</label>
              <div className={styles.inputRow}>
                <input id="name" value={name} onChange={(event) => setName(event.target.value)} required maxLength={80} autoComplete="given-name" />
                <button disabled={sending || !name.trim()} type="submit">{sending ? "Enviando…" : "Enviar saludo"}</button>
              </div>
            </form>
            <div role="status" className={styles.reply}>{reply || "Tu respuesta aparecerá aquí."}</div>
            {error && <div role="alert" className={styles.error}><p>{error}</p><button type="button" onClick={() => { setError(""); refresh().catch(() => setError("La API sigue sin responder. Revisa los contenedores.")); }}>Comprobar conexión</button></div>}
            <div className={styles.historyHeader}><h3>Últimos saludos</h3><span>{health?.greeting_count ?? "—"} guardados</span></div>
            {greetings.length === 0 ? <p className={styles.empty}>Todavía no hay saludos. Empieza con el tuyo.</p> : (
              <ul className={styles.history}>
                {greetings.map((greeting) => <li key={greeting.id}><span className={styles.avatar} aria-hidden="true">{greeting.name.charAt(0).toUpperCase()}</span><div><strong>{greeting.name}</strong><p>{greeting.message}</p></div></li>)}
              </ul>
            )}
          </section>

          <div className={styles.sideColumn}>
            <section className={styles.panel} aria-labelledby="knowledge-title">
              <p className={styles.panelLabel}>CONOCIMIENTO LOCAL</p>
              <h2 id="knowledge-title">Modelos operativos</h2>
              <p className={styles.description}>{health ? `${health.document_count} documentos` : "Documentos"} del repositorio, disponibles para búsqueda textual.</p>
              <form onSubmit={search} className={styles.form}>
                <label htmlFor="query">Busca un procedimiento</label>
                <div className={styles.inputRow}><input id="query" value={query} onChange={(event) => setQuery(event.target.value)} required maxLength={200} /><button disabled={searching || !query.trim()} type="submit">{searching ? "Buscando…" : "Buscar"}</button></div>
              </form>
              {searchError && <p className={styles.error} role="alert">{searchError}</p>}
              <div aria-live="polite">
                {matches && <p className={styles.resultCount}>{matches.length} documentos encontrados</p>}
                {matches && <ul className={styles.results}>{matches.map((match) => <li key={match.code}><a href={match.url} target="_blank" rel="noreferrer">{match.code} · versión {match.version}</a><p>{match.title}</p></li>)}</ul>}
              </div>
            </section>
            <section className={styles.integrations} aria-labelledby="integration-title">
              <h2 id="integration-title">Siguiente etapa</h2>
              <p>El agente y las conexiones externas se incorporarán sobre esta base.</p>
              <ul>{integrations.map((integration) => <li key={integration.name}><strong>{integration.name}</strong><span title={integration.detail}>{integration.status === "configured" ? "Por verificar" : "Pendiente"}</span></li>)}</ul>
              <p className={styles.note}>Esta prueba funciona sin credenciales externas.</p>
            </section>
          </div>
        </div>
        <footer className={styles.footer}><span>GRUPO VISA AI</span><span>Base local · Docker Compose · Etapa 1</span><a href="/docs" target="_blank" rel="noreferrer">Explorar la API ↗</a></footer>
      </main>
    </>
  );
}
