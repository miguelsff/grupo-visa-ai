"use client";

import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ArrowUp, CalendarClock, ChevronLeft, ChevronRight, Code, FileText, GitBranch, Menu, Moon, Sparkles, Sun } from "lucide-react";
import { getChat, sendChat } from "../lib/api";
import type { ChatResponse } from "../lib/api";
import AgentReply, { ReviewDetails } from "./agent-reply";
import KnowledgeSearch from "./KnowledgeSearch";
import styles from "./page.module.css";

type Tab = "draft" | "flow" | "schedule" | "jira";
type Turn = { message?: string; result: ChatResponse };
const examples = [
  { id: "OCD-4092", title: "Actualización Microservicio Transferencias CCE", progress: 68, status: "En progreso" },
  { id: "ITSM-1104", title: "Apertura de Firewall Base de Datos Riesgos", progress: 100, status: "Listo para Jira" },
  { id: "OCD-4088", title: "Rollback Plan Motor de Fraude", progress: 84, status: "Coordinando recursos" },
  { id: "OCD-4076", title: "Certificación QA Core Bancario", progress: 100, status: "Finalizado" },
];
const stages = [
  ["Registrar el requerimiento", "Describe el objetivo, el alcance y los datos del cambio."],
  ["Consultar los procedimientos", "El agente recupera las fuentes documentales aplicables."],
  ["Completar los datos", "Las preguntas mantienen pendientes los datos desconocidos."],
  ["Revisar el borrador", "V-01, V-02 y V-03 comprueban completitud, consistencia y trazabilidad."],
];

export default function Home() {
  const [dark, setDark] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);
  const [example, setExample] = useState<(typeof examples)[number] | null>(null);
  const [tab, setTab] = useState<Tab>("draft");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [restoring, setRestoring] = useState(true);
  const [sending, setSending] = useState(false);
  const [copied, setCopied] = useState(false);
  const transcript = useRef<HTMLDivElement>(null);
  const busy = useRef(false);
  const latest = turns.at(-1)?.result;

  useEffect(() => {
    const controller = new AbortController();
    getChat(controller.signal).then(result => {
      if (!controller.signal.aborted && result.revision > 0) setTurns([{ result }]);
    }).catch(() => {
      if (!controller.signal.aborted) setError("No se pudo recuperar la última revisión. Recarga la página para intentarlo de nuevo.");
    }).finally(() => { if (!controller.signal.aborted) setRestoring(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight;
  }, [turns, sending]);

  async function ask(text: string) {
    if (!text.trim() || busy.current || restoring) return;
    busy.current = true; setSending(true); setError("");
    try {
      const result = await sendChat(text.trim());
      setTurns(previous => [...previous, { message: text.trim(), result }]);
      setMessage("");
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "No se pudo enviar el mensaje. Inténtalo otra vez.");
    } finally { busy.current = false; setSending(false); }
  }

  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); void ask(message); }
  function showDraft() { setExample(null); setRightOpen(true); setMobileOpen(false); }
  const workspace = [styles.workspace, !leftOpen && styles.leftClosed, !rightOpen && styles.rightClosed, mobileOpen && styles.mobileOpen].filter(Boolean).join(" ");

  return <main className={`${styles.app} ${dark ? styles.dark : ""}`}>
    <header className={styles.topbar}>
      <div className={styles.brand}>
        <button className={`${styles.iconButton} ${styles.mobileMenu}`} aria-label="Mostrar requerimientos" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}><Menu/></button>
        <div className={styles.brandMark}>N</div><div><strong>NexoOPS</strong><small>GRUPO VISA AI · DEMOSTRACIÓN OCD</small></div>
      </div>
      <div className={styles.topActions}><a href="/docs" target="_blank" rel="noreferrer">Explorar API ↗</a>
        <button className={styles.iconButton} aria-label="Cambiar tema" onClick={() => setDark(!dark)}>{dark ? <Sun/> : <Moon/>}</button>
      </div>
    </header>
    <div className={workspace}>
      <aside className={styles.sidebar} aria-label="Requerimientos y procedimientos">
        <div className={styles.sideTitle}><span className={styles.eyebrow}>REQUERIMIENTOS</span><button className={styles.iconButton} aria-label={leftOpen ? "Cerrar panel izquierdo" : "Abrir panel izquierdo"} onClick={() => { setLeftOpen(!leftOpen); setMobileOpen(false); }}>{leftOpen ? <ChevronLeft/> : <ChevronRight/>}</button></div>
        <div className={styles.sideContent}>
          <button className={`${styles.ticket} ${!example ? styles.selected : ""}`} onClick={showDraft}><span className={styles.tag}>SESIÓN ACTUAL</span><strong>Mi borrador OCD</strong><small>{latest?.revision ? `Revisión ${latest.revision}` : "Describe tu cambio para empezar"}</small></button>
          <p className={styles.demoNote}>Una conversación y un borrador real por sesión del navegador.</p>
          <div className={styles.eyebrow}>EJEMPLOS DE INTERFAZ</div>
          {examples.map(ticket => <button className={`${styles.ticket} ${example?.id === ticket.id ? styles.selected : ""}`} key={ticket.id} onClick={() => { setExample(ticket); setRightOpen(true); setMobileOpen(false); }}>
            <span className={styles.tag}>{ticket.id} · DEMO</span><strong>{ticket.title}</strong>
            <div className={styles.progress}><span style={{ width: `${ticket.progress}%` }}/></div><small>{ticket.progress}% · {ticket.status}</small>
          </button>)}
          <p className={styles.demoNote}>Estos ejemplos no son tickets consultados en Jira y no cambian tu conversación.</p>
          <div className={styles.sideFooter}><KnowledgeSearch/></div>
        </div>
      </aside>
      <section className={styles.chatPanel} aria-labelledby="chat-title">
        <div className={styles.panelHeader}><div className={styles.eyebrow}><Sparkles/> COPILOTO NEXOOPS</div><h1 id="chat-title">Armemos tu cambio.</h1><p>Describe tu requerimiento o consulta un procedimiento. El agente prepara un borrador con fuentes y datos pendientes.</p></div>
        <div className={styles.chatBody} ref={transcript} role="log" aria-label="Mensajes de la conversación" aria-live="polite">
          {!turns.length && <div className={styles.welcome}><p>Puedes empezar con «Hola» o preguntar «¿Qué planes exige OCD-C02?».</p><p>Las revisiones son comprobaciones documentales. El asistente no crea tickets ni ejecuta cambios.</p></div>}
          {turns.map(({ message: text, result }, i) => <div key={i}>
            {text && <div className={`${styles.message} ${styles.userMessage}`}><div className={styles.bubble}><strong>Tú</strong><p>{text}</p></div></div>}
            <div className={styles.message}><div className={styles.aiAvatar}><Sparkles/></div><div className={styles.bubble}><strong>{text ? "Asistente OCD" : "Última revisión guardada"}</strong><AgentReply result={result}/></div></div>
          </div>)}
          {sending && <div role="status" className={styles.message}><div className={styles.aiAvatar}><Sparkles/></div><div className={styles.bubble}>El agente está revisando tu requerimiento…</div></div>}
          {error && <p role="alert" className={styles.error}>{error}</p>}
        </div>
        <div className={styles.composer}>
          <div className={styles.quickPrompts}>{["¿Qué planes exige OCD-C02?", "¿Qué datos requiere un pase de microservicios?"].map(text => <button key={text} disabled={restoring || sending} onClick={() => { void ask(text); }}>{text}</button>)}</div>
          <form onSubmit={submit}><div className={styles.inputRow}>
            <textarea aria-label="Tu mensaje" value={message} maxLength={12000} required rows={2} readOnly={sending} onChange={e => setMessage(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void ask(message); } }} placeholder="Describe el cambio que quieres preparar…"/>
            <button className={styles.send} type="submit" aria-label="Enviar mensaje" disabled={restoring || sending || !message.trim()}><ArrowUp/></button>
          </div></form>
          <div className={styles.hint}><span role="status">{restoring ? "Recuperando la sesión…" : sending ? "Consultando al agente…" : "Verifica siempre los datos críticos."}</span><span>Enter para enviar · Mayús+Enter para otra línea</span></div>
        </div>
      </section>
      <aside className={`${styles.canvasPanel} ${rightOpen ? "" : styles.collapsed}`} aria-label="Detalle OCD">
        <div className={styles.canvasHead}><div><span className={styles.eyebrow}>{example ? "EJEMPLO DE INTERFAZ" : "BORRADOR DE TU SESIÓN"}</span><h2>{example?.title ?? "Tu solicitud OCD"}</h2></div><button className={styles.iconButton} aria-label={rightOpen ? "Cerrar panel OCD" : "Abrir panel OCD"} aria-expanded={rightOpen} onClick={() => setRightOpen(!rightOpen)}>{rightOpen ? <ChevronRight/> : <ChevronLeft/>}</button></div>
        <div className={styles.canvasContent}>
          <nav className={styles.tabs} aria-label="Vistas del requerimiento">{([["draft", FileText, "Borrador"], ["flow", GitBranch, "Flujo"], ["schedule", CalendarClock, "Agenda"], ["jira", Code, "Vista previa"]] as const).map(([key, Icon, label]) => <button key={key} className={tab === key ? styles.activeTab : ""} aria-pressed={tab === key} onClick={() => setTab(key)}><Icon/>{label}</button>)}</nav>
          <div className={styles.canvasInner}>
            {example && <p className={styles.demoNote}>Demostración visual: {example.id}. Los estados y porcentajes son datos de ejemplo.</p>}
            {tab === "flow" && <><h3>Del requerimiento al borrador validado</h3><ol className={styles.flow}>{stages.map(([title, detail]) => <li key={title}><div><strong>{title}</strong><small>{detail}</small></div></li>)}</ol><p>Crear tickets, coordinar recursos y ejecutar cambios quedan fuera de esta demostración.</p></>}
            {tab === "draft" && (example ? <><h3>{example.id} · {example.status}</h3><p>Vista de ejemplo. Selecciona «Mi borrador OCD» para consultar los datos y las validaciones de tu sesión.</p><button className={styles.secondaryButton} onClick={showDraft}>Ver mi borrador</button></> : latest?.revision ? <ReviewDetails result={latest}/> : <p>El borrador aparecerá cuando describas un cambio. Las consultas informativas no crean una revisión.</p>)}
            {tab === "schedule" && <><h3>Recursos y agenda</h3><p>No hay una integración de calendario disponible. Las fechas declaradas forman parte del borrador y no reservan una ventana.</p></>}
            {tab === "jira" && <><h3>Vista previa documental</h3><p>Esta vista no publica ni crea tickets.</p><pre>{JSON.stringify(example ?? latest?.draft ?? {}, null, 2)}</pre><button className={styles.secondaryButton} onClick={async () => { try { await navigator.clipboard.writeText(JSON.stringify(example ?? latest?.draft ?? {}, null, 2)); setCopied(true); } catch { setCopied(false); } }}>{copied ? "JSON copiado" : "Copiar JSON"}</button></>}
          </div>
        </div>
      </aside>
    </div>
  </main>;
}
