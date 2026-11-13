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
type Turn = { message?: string; result?: ChatResponse; pending?: boolean; error?: string };
const loadingStages = ["Buscando información relevante", "Comparando resultados con los procedimientos", "Preparando la respuesta"];
const examples: Array<{ id: string; title: string; progress: number; status: string }> = [];
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
  const [loadingStage, setLoadingStage] = useState(0);
  const [copied, setCopied] = useState(false);
  const transcript = useRef<HTMLDivElement>(null);
  const busy = useRef(false);
  const latest = turns.at(-1)?.result;
  const loadingLabel = loadingStages[loadingStage];

  useEffect(() => {
    if (!sending) { setLoadingStage(0); return; }
    const timer = window.setInterval(() => setLoadingStage(stage => (stage + 1) % loadingStages.length), 1800);
    return () => window.clearInterval(timer);
  }, [sending]);

  useEffect(() => {
    const controller = new AbortController();
    getChat(controller.signal).then(result => {
      if (!controller.signal.aborted && result.revision > 0) setTurns([]);
    }).catch(() => {
      if (!controller.signal.aborted) setError("No se pudo recuperar la última revisión. Recarga la página para intentarlo de nuevo.");
    }).finally(() => { if (!controller.signal.aborted) setRestoring(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight;
  }, [turns, sending]);

  async function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy.current || restoring) return;
    busy.current = true; setSending(true); setError("");
    setMessage("");
    setTurns(previous => [...previous, { message: trimmed, pending: true }]);
    try {
      const result = await sendChat(trimmed);
      setTurns(previous => previous.map((turn, index) => index === previous.length - 1 && turn.pending ? { message: trimmed, result } : turn));
    } catch (failure) {
      const message = failure instanceof Error ? failure.message : "No se pudo enviar el mensaje. Inténtalo otra vez.";
      setTurns(previous => previous.map((turn, index) => index === previous.length - 1 && turn.pending ? { message: trimmed, error: message } : turn));
      setError(message);
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
          {examples.map(ticket => <button className={`${styles.ticket} ${example?.id === ticket.id ? styles.selected : ""}`} key={ticket.id} onClick={() => { setExample(ticket); setRightOpen(true); setMobileOpen(false); }}>
            <span className={styles.tag}>{ticket.id} · DEMO</span><strong>{ticket.title}</strong>
            <div className={styles.progress}><span style={{ width: `${ticket.progress}%` }}/></div><small>{ticket.progress}% · {ticket.status}</small>
          </button>)}
          <div className={styles.sideFooter}><KnowledgeSearch/></div>
        </div>
      </aside>
      <section className={styles.chatPanel} aria-labelledby="chat-title">
        <div className={styles.panelHeader}><div className={styles.eyebrow}><Sparkles/> COPILOTO NEXOOPS</div><h1 id="chat-title">Armemos tu cambio.</h1><p>Describe tu requerimiento o consulta un procedimiento. El agente prepara un borrador con fuentes y datos pendientes.</p></div>
        <div className={styles.chatBody} ref={transcript} role="log" aria-label="Mensajes de la conversación" aria-live="polite">
          {!turns.length && !sending && <div className={styles.welcome} aria-hidden="true"/>}
          {turns.map(({ message: text, result, error: turnError }, i) => <div key={i}>
            {text && <div className={`${styles.message} ${styles.userMessage}`}><div className={styles.bubble}><strong>Tú</strong><p>{text}</p></div></div>}
            {result && <div className={styles.message}><div className={styles.aiAvatar}><Sparkles/></div><div className={styles.bubble}><strong>{text ? "Asistente OCD" : "Última revisión guardada"}</strong><AgentReply result={result}/></div></div>}
            {turnError && <p role="alert" className={styles.error}>{turnError}</p>}
          </div>)}
          {sending && <div role="status" aria-live="polite" className={styles.loading}><div className={styles.aiAvatar}><img className={styles.aiAvatarImage} src="/nexoops-chatbot.png" alt=""/></div><div className={styles.loadingText}>{loadingLabel}<div className={styles.loadingTrack}/></div></div>}
          {error && <p role="alert" className={styles.error}>{error}</p>}
        </div>
        <div className={styles.composer}>
          <div className={styles.quickPrompts}>{["¿Qué planes exige OCD-C02?", "¿Qué datos requiere un pase de microservicios?"].map(text => <button key={text} disabled={restoring || sending} onClick={() => { void ask(text); }}>{text}</button>)}</div>
          <form onSubmit={submit}><div className={styles.inputRow}>
            <textarea aria-label="Tu mensaje" aria-busy={sending} value={message} maxLength={12000} required rows={2} disabled={restoring || sending} onChange={e => setMessage(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void ask(message); } }} placeholder="Describe el cambio que quieres preparar…"/>
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
            {tab === "flow" && <><h3>Del requerimiento al ticket creado</h3><ol className={styles.flow}>{stages.map(([title, detail]) => <li key={title}><div><strong>{title}</strong><small>{detail}</small></div></li>)}</ol><p>El asistente valida la información, prepara el borrador y crea el ticket cuando la solicitud está lista.</p></>}
            {tab === "draft" && (example ? <><h3>{example.id} · {example.status}</h3><p>Vista de ejemplo. Selecciona «Mi borrador OCD» para consultar los datos y las validaciones de tu sesión.</p><button className={styles.secondaryButton} onClick={showDraft}>Ver mi borrador</button></> : latest?.revision ? <ReviewDetails result={latest}/> : <p>El borrador aparecerá cuando describas un cambio. Las consultas informativas no crean una revisión.</p>)}
            {tab === "schedule" && <><h3>Recursos y agenda</h3><p>No hay una integración de calendario disponible. Las fechas declaradas forman parte del borrador y no reservan una ventana.</p></>}
            {tab === "jira" && <><h3>Vista previa del ticket</h3><p>El ticket se creará cuando el asistente termine de validar el borrador.</p><pre>{JSON.stringify(example ?? latest?.draft ?? {}, null, 2)}</pre><button className={styles.secondaryButton} onClick={async () => { try { await navigator.clipboard.writeText(JSON.stringify(example ?? latest?.draft ?? {}, null, 2)); setCopied(true); } catch { setCopied(false); } }}>{copied ? "JSON copiado" : "Copiar JSON"}</button></>}
          </div>
        </div>
      </aside>
    </div>
  </main>;
}
