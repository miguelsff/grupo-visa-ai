"use client";

import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { getChat, sendChat } from "../lib/api";
import type { ChatResponse } from "../lib/api";
import styles from "./page.module.css";

type Turn = { message?: string; result: ChatResponse };
const labels = {
  CUMPLE: "Cumple",
  FALTA_INFORMACION: "Falta información",
  ERROR: "Error",
  NO_VERIFICABLE: "No verificable",
};

function TurnDetails({ result }: { result: ChatResponse }) {
  const facts = Object.entries(result.draft.facts);
  return (
    <div className={styles.details}>
      {result.sources.length > 0 && <details>
        <summary>Fuentes ({result.sources.length})</summary>
        <ul>{result.sources.map((source) => <li key={source.point_id}>
          <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
          <small>{source.code} · versión {source.version} · {source.locator}</small>
          <p>{source.excerpt}</p>
        </li>)}</ul>
      </details>}
      {result.revision > 0 && facts.length > 0 && <details>
        <summary>Borrador · revisión {result.revision}</summary>
        <dl>{facts.map(([key, fact]) => <div key={key}><dt>{fact.name.replaceAll("_", " ")}</dt><dd>{fact.value}</dd></div>)}</dl>
      </details>}
      {result.questions.length > 0 && <details>
        <summary>Preguntas pendientes ({result.questions.length})</summary>
        <ul>{result.questions.map((question) => <li key={question}>{question}</li>)}</ul>
      </details>}
      {result.validations.length > 0 && <details>
        <summary>Validaciones ({result.validations.length})</summary>
        <ul>{result.validations.map((item, i) => <li key={`${item.check}-${item.rule_id}-${i}`}>
          <strong>{item.check} · {labels[item.status]}</strong>
          <p>{item.detail}</p>
          <a href={item.reference.url} target="_blank" rel="noreferrer">{item.reference.code} · {item.rule_id}</a>
        </li>)}</ul>
      </details>}
    </div>
  );
}

export default function ChatPanel() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [restoring, setRestoring] = useState(true);
  const [sending, setSending] = useState(false);
  const transcript = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    getChat(controller.signal)
      .then((result) => {
        if (!controller.signal.aborted && result.revision > 0) setTurns([{ result }]);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError("No se pudo recuperar la última revisión. Recarga la página para intentarlo de nuevo.");
      })
      .finally(() => { if (!controller.signal.aborted) setRestoring(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const node = transcript.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [turns]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = message.trim();
    if (!text || sending || restoring) return;
    setSending(true);
    setError("");
    try {
      const result = await sendChat(text);
      setTurns((previous) => [...previous, { message: text, result }]);
      setMessage("");
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "No se pudo enviar el mensaje. Inténtalo otra vez.");
    } finally {
      setSending(false);
    }
  }

  return (
    <section className={styles.panel} aria-labelledby="chat-title">
      <h2 id="chat-title">Conversación</h2>
      <div ref={transcript} className={styles.transcript} role="log" aria-label="Mensajes de la conversación">
        {turns.map(({ message, result }, i) => <div key={i} className={styles.turn}>
          {message && <div className={styles.userMessage}><strong>Tú</strong><p>{message}</p></div>}
          <div className={styles.agentMessage}>
            <strong>{message ? "Asistente OCD" : "Última revisión guardada"}</strong>
            <p>{result.answer}</p>
            {result.error && <p className={styles.error}>{result.error}</p>}
            <TurnDetails result={result} />
          </div>
        </div>)}
      </div>
      {!restoring && !turns.length && <p className={styles.empty}>Puedes empezar con «Hola» o describir un cambio.</p>}
      <form onSubmit={submit} className={styles.form}>
        <label htmlFor="chat-message">Tu mensaje</label>
        <textarea id="chat-message" rows={3} value={message} readOnly={sending} required maxLength={12000}
          onChange={(event) => setMessage(event.target.value)} placeholder="Escribe tu pregunta o solicitud…" />
        <div className={styles.composerActions}>
          <span role="status">{restoring ? "Recuperando la sesión…" : sending ? "El asistente está respondiendo…" : ""}</span>
          <button type="submit" disabled={restoring || sending || !message.trim()}>Enviar mensaje</button>
        </div>
      </form>
      {error && <p role="alert" className={styles.error}>{error}</p>}
    </section>
  );
}
