"use client";

import { useEffect, useRef, useState } from "react";
import type { CSSProperties, FormEvent, KeyboardEvent, PointerEvent } from "react";
import { ArrowUp, ChevronLeft, ChevronRight, Menu, Moon, Sparkles, Sun, X } from "lucide-react";
import { getChat, publishChatRevision, sendChat } from "../lib/api";
import type { ChatResponse } from "../lib/api";
import AgentReply, { hasDetails, ReviewDetails } from "./agent-reply";
import KnowledgeSearch from "./KnowledgeSearch";
import styles from "./page.module.css";

type Turn = { message?: string; result?: ChatResponse; pending?: boolean; error?: string };
const loadingStages = ["Buscando información relevante", "Comparando resultados con los procedimientos", "Preparando la respuesta"];
const minWidth = 280;
const maxWidth = 480;

export default function Home() {
  const [dark, setDark] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);
  const [leftWidth, setLeftWidth] = useState(350);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [restoring, setRestoring] = useState(true);
  const [sending, setSending] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [publicationError, setPublicationError] = useState("");
  const [uncertain, setUncertain] = useState(false);
  const [loadingStage, setLoadingStage] = useState(0);
  const transcript = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const detailTrigger = useRef<HTMLButtonElement | null>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const busy = useRef(false);
  const current = [...turns].reverse().find(turn => turn.result)?.result;
  const currentRevision = current?.revision ?? 0;
  const previewIndex = turns.findLastIndex(turn => !!turn.result?.preview && turn.result.revision === currentRevision);
  const selectedResult = selected === null ? null : turns[selected]?.result;

  useEffect(() => {
    try { const saved = Number(localStorage.getItem("nexoops-sidebar-width")); if (saved >= minWidth && saved <= maxWidth) setLeftWidth(saved); } catch { /* La sesión funciona sin almacenamiento local. */ }
  }, []);
  useEffect(() => {
    if (!sending) { setLoadingStage(0); return; }
    const timer = window.setInterval(() => setLoadingStage(stage => (stage + 1) % loadingStages.length), 1800);
    return () => window.clearInterval(timer);
  }, [sending]);
  useEffect(() => {
    const controller = new AbortController();
    getChat(controller.signal).then(result => {
      if (!controller.signal.aborted && result.revision > 0) setTurns([{ result }]);
    }).catch(() => { if (!controller.signal.aborted) setUncertain(true); }).finally(() => { if (!controller.signal.aborted) setRestoring(false); });
    return () => controller.abort();
  }, []);
  useEffect(() => { if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight; }, [turns, sending]);
  useEffect(() => {
    if (!rightOpen) return;
    if (window.matchMedia("(max-width: 700px)").matches) closeButton.current?.focus();
    function onKey(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") { setRightOpen(false); detailTrigger.current?.focus(); }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [rightOpen, selected]);

  function resize(width: number) {
    const next = Math.max(minWidth, Math.min(maxWidth, width));
    setLeftWidth(next);
    try { localStorage.setItem("nexoops-sidebar-width", String(next)); } catch { /* Preferencia opcional. */ }
  }
  function startResize(event: PointerEvent<HTMLDivElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    const startX = event.clientX, startWidth = leftWidth;
    const element = event.currentTarget;
    function move(e: globalThis.PointerEvent) { resize(startWidth + e.clientX - startX); }
    function stop() { element.removeEventListener("pointermove", move); element.removeEventListener("pointerup", stop); element.removeEventListener("pointercancel", stop); }
    element.addEventListener("pointermove", move); element.addEventListener("pointerup", stop); element.addEventListener("pointercancel", stop);
  }
  function resizeKey(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") { event.preventDefault(); resize(leftWidth + (event.key === "ArrowLeft" ? -10 : 10)); }
    if (event.key === "Home") { event.preventDefault(); resize(minWidth); }
    if (event.key === "End") { event.preventDefault(); resize(maxWidth); }
  }
  async function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy.current || restoring) return;
    busy.current = true; setSending(true); setPublicationError(""); setMessage("");
    setTurns(previous => [...previous, { message: trimmed, pending: true }]);
    try {
      const result = await sendChat(trimmed);
      setUncertain(result.status === "unavailable");
      setTurns(previous => previous.map((turn, index) => index === previous.length - 1 && turn.pending ? { message: trimmed, result } : turn));
    } catch (failure) {
      setUncertain(true);
      setMessage(trimmed);
      const error = failure instanceof Error ? failure.message : "No se pudo enviar el mensaje. Inténtalo otra vez.";
      setTurns(previous => previous.map((turn, index) => index === previous.length - 1 && turn.pending ? { message: trimmed, error } : turn));
    } finally { busy.current = false; setSending(false); }
  }
  async function publish(index: number, revision: number) {
    if (busy.current || uncertain || message.trim() || index !== previewIndex || revision !== currentRevision) return;
    busy.current = true; setPublishing(true); setPublicationError("");
    try {
      const publication = await publishChatRevision(revision);
      setTurns(previous => previous.map(turn => turn.result?.revision === revision ? { ...turn, result: { ...turn.result, publication } } : turn));
    } catch (failure) { setPublicationError(failure instanceof Error ? failure.message : "No se pudo publicar. Inténtalo de nuevo."); }
    finally { busy.current = false; setPublishing(false); }
  }
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); void ask(message); }
  function openDetail(index: number, trigger: HTMLButtonElement) { detailTrigger.current = trigger; setSelected(index); setRightOpen(true); setMobileOpen(false); }
  function closeDetail() { setRightOpen(false); detailTrigger.current?.focus(); }
  const workspace = [styles.workspace, !leftOpen && styles.leftClosed, !rightOpen && styles.rightClosed, mobileOpen && styles.mobileOpen].filter(Boolean).join(" ");

  return <main className={`${styles.app} ${dark ? styles.dark : ""}`}>
    <header className={styles.topbar}>
      <div className={styles.brand}><button className={`${styles.iconButton} ${styles.mobileMenu}`} aria-label="Mostrar requerimientos" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}><Menu/></button><div className={styles.brandMark}>N</div><div><strong>NexoOPS</strong><small>GRUPO VISA AI · DEMOSTRACIÓN OCD</small></div></div>
      <div className={styles.topActions}><a href="/docs" target="_blank" rel="noreferrer">Explorar API ↗</a><button className={styles.iconButton} aria-label="Cambiar tema" onClick={() => setDark(!dark)}>{dark ? <Sun/> : <Moon/>}</button></div>
    </header>
    <div className={workspace} style={{ "--sidebar-width": `${leftWidth}px` } as CSSProperties}>
      {mobileOpen && <button className={styles.scrim} aria-label="Cerrar menú" onClick={() => setMobileOpen(false)}/>}
      <aside className={styles.sidebar} aria-label="Requerimientos y procedimientos">
        <div className={styles.sideTitle}><span className={styles.eyebrow}>REQUERIMIENTOS</span><button className={styles.iconButton} aria-label={leftOpen ? "Cerrar panel izquierdo" : "Abrir panel izquierdo"} onClick={() => { setLeftOpen(!leftOpen); setMobileOpen(false); }}>{leftOpen ? <ChevronLeft/> : <ChevronRight/>}</button></div>
        <div className={styles.sideContent}><div className={`${styles.ticket} ${styles.selected}`}><span className={styles.tag}>SESIÓN ACTUAL</span><strong>Mi borrador OCD</strong><small>{currentRevision ? `Revisión ${currentRevision}` : "Describe tu cambio para empezar"}</small></div><p className={styles.demoNote}>Una conversación y un borrador real por sesión del navegador.</p><details className={styles.workspaceInfo}><summary>Flujo, agenda y ejemplos</summary><h3>Flujo del requerimiento</h3><ol><li>Registrar el requerimiento.</li><li>Consultar los procedimientos.</li><li>Completar los datos pendientes.</li><li>Revisar el borrador y sus validaciones.</li></ol><h3>Recursos y agenda</h3><p>No hay integración de calendario. Las fechas declaradas no reservan una ventana.</p><h3>Ejemplos</h3><p>No hay ejemplos disponibles en esta demostración.</p></details><div className={styles.sideFooter}><KnowledgeSearch/></div></div>
        {leftOpen && <div className={styles.resizeHandle} role="separator" tabIndex={0} aria-label="Ajustar ancho del panel izquierdo" aria-orientation="vertical" aria-valuemin={minWidth} aria-valuemax={maxWidth} aria-valuenow={leftWidth} onPointerDown={startResize} onKeyDown={resizeKey}/>}
      </aside>
      <section className={styles.chatPanel} aria-labelledby="chat-title">
        <div className={styles.panelHeader}><div className={styles.eyebrow}><Sparkles/> COPILOTO NEXOOPS</div><h1 id="chat-title">Armemos tu cambio.</h1><p>Describe tu requerimiento o consulta un procedimiento. El agente prepara un borrador con fuentes y datos pendientes.</p></div>
        <div className={styles.chatBody} ref={transcript} role="log" aria-label="Mensajes de la conversación" aria-live="polite">
          {!turns.length && !sending && <div className={styles.welcome}>Empieza con una consulta o describe el cambio que necesitas preparar.</div>}
          {turns.map(({ message: text, result, error }, i) => <div key={i}>
            {text && <div className={`${styles.message} ${styles.userMessage}`}><div className={styles.bubble}><strong>Tú</strong><p>{text}</p></div></div>}
            {result && <div className={styles.message}><div className={styles.aiAvatar}><Sparkles/></div><div className={styles.bubble}><strong>{text ? "Asistente OCD" : "Última revisión guardada"}</strong><AgentReply result={result}/>
              {hasDetails(result) && <button className={styles.detailButton} aria-expanded={rightOpen && selected === i} onClick={event => openDetail(i, event.currentTarget)}>Ver detalle <ChevronRight size={16}/></button>}
              {result.preview && <div className={styles.preview}><div className={styles.previewLabel}>VISTA PREVIA DE JIRA · REVISIÓN {result.revision}</div><h3>{result.preview.title}</h3><p className={styles.destination}>{result.preview.project_key} · {result.preview.issue_type}</p><details><summary>Ver descripción aprobada</summary><p className={styles.previewDescription}>{result.preview.description}</p></details><p className={styles.pendingLine}>{result.preview.pending.length ? `Pendientes: ${result.preview.pending.join(" · ")}` : "Sin pendientes"}</p>
                {result.publication ? <a className={styles.primaryButton} href={result.publication.url} target="_blank" rel="noreferrer">Abrir ticket {result.publication.key} ↗</a> : i === previewIndex && result.revision === currentRevision ? <div className={styles.previewActions}><button className={styles.primaryButton} disabled={restoring || sending || publishing || uncertain || !!message.trim()} onClick={() => void publish(i, result.revision)}>{publishing ? "Publicando…" : "Publicar en Jira"}</button><button className={styles.secondaryButton} disabled={publishing || sending} onClick={() => composer.current?.focus()}>Seguir editando</button></div> : <p className={styles.demoNote}>Esta revisión ya no está vigente.</p>}
                {i === previewIndex && publicationError && <p role="alert" className={styles.error}>{publicationError}</p>}{i === previewIndex && uncertain && <p className={styles.error}>No se pudo confirmar el estado de la revisión. Envía una consulta para recuperarlo antes de publicar.</p>}
              </div>}
            </div></div>}
            {error && <p role="alert" className={styles.error}>{error}</p>}
          </div>)}
          {sending && <div role="status" className={styles.loading}><div className={styles.aiAvatar}><img className={styles.aiAvatarImage} src="/nexoops-chatbot.png" alt=""/></div><div className={styles.loadingText}>{loadingStages[loadingStage]}<div className={styles.loadingTrack}/></div></div>}
        </div>
        <div className={styles.composer}><div className={styles.quickPrompts}>{["¿Qué planes exige OCD-C02?", "¿Qué datos requiere un pase de microservicios?"].map(text => <button key={text} disabled={restoring || sending || publishing} onClick={() => void ask(text)}>{text}</button>)}</div><form onSubmit={submit}><div className={styles.inputRow}><textarea ref={composer} aria-label="Tu mensaje" aria-busy={sending} value={message} maxLength={12000} required rows={2} disabled={restoring || sending || publishing} onChange={e => setMessage(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void ask(message); } }} placeholder="Describe el cambio que quieres preparar…"/><button className={styles.send} type="submit" aria-label="Enviar mensaje" disabled={restoring || sending || publishing || !message.trim()}><ArrowUp/></button></div></form><div className={styles.hint}><span role="status">{restoring ? "Recuperando la sesión…" : sending ? "Consultando al agente…" : publishing ? "Publicando en Jira…" : "Verifica siempre los datos críticos."}</span><span>Enter para enviar · Mayús+Enter para otra línea</span></div></div>
      </section>
      <aside className={`${styles.canvasPanel} ${rightOpen ? "" : styles.collapsed}`} aria-label="Detalle del turno" aria-hidden={!rightOpen}>
        <div className={styles.canvasHead}><div><span className={styles.eyebrow}>DETALLE DEL TURNO</span><h2>{selectedResult?.revision ? `Revisión ${selectedResult.revision}` : "Fuentes y resultados"}</h2></div><button ref={closeButton} className={styles.iconButton} aria-label="Cerrar detalle" onClick={closeDetail}><X/></button></div>
        <div className={styles.canvasInner}>{selectedResult ? <ReviewDetails result={selectedResult}/> : <p>Selecciona «Ver detalle» en una respuesta.</p>}</div>
      </aside>
    </div>
  </main>;
}
