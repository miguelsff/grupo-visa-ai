"use client";
import { useRef, useState } from "react";
import AgentReply, { type AgentResult } from "./agent-reply";
import TicketDetail, { TicketReviews } from "./ticket-detail";
import { Moon, Sun, ChevronLeft, ChevronRight, Search, Plus, MoreHorizontal, Check, Circle, Sparkles, ArrowUp, ArrowRight, FileText, CalendarClock, Code, Monitor, Terminal, MessagesSquare, Bell, Clock, Copy, TriangleAlert, GitBranch } from "lucide-react";

type Tab = "builder" | "flow" | "schedule" | "jira";
type TicketStatus = "En progreso" | "Coordinando recursos" | "Listo para Jira" | "Finalizado";
const statusOptions: Array<"Todos" | TicketStatus> = ["Todos", "En progreso", "Coordinando recursos", "Listo para Jira", "Finalizado"];
const statusClass: Record<TicketStatus,string> = {"En progreso":"in-progress","Coordinando recursos":"coordinating","Listo para Jira":"jira-ready","Finalizado":"finished"};
const initialTickets = [
  { id: "OCD-4092", title: "Actualización Microservicio Transferencias CCE", type: "OCD", progress: 68, status: "En progreso", active: true },
  { id: "ITSM-1104", title: "Apertura de Firewall Base de Datos Riesgos", type: "ITSM", progress: 100, status: "Listo para Jira" },
  { id: "OCD-4088", title: "Rollback Plan Motor de Fraude", type: "OCD", progress: 84, status: "Coordinando recursos" },
  { id: "OCD-4076", title: "Certificación QA Core Bancario", type: "OCD", progress: 100, status: "Finalizado" },
];
const steps = [
  ["Aprovisionar AKS", "Crear o validar el cluster, namespace y recursos del microservicio", "Completado", "98%"],
  ["Aprovisionar base de datos", "Preparar instancia, esquema, credenciales y conectividad", "Completado", "97%"],
  ["Configurar secretos y variables", "Registrar Key Vault, conexiones y parámetros por ambiente", "Completado", "98%"],
  ["Preparar artefactos de despliegue", "Validar imagen, tag, manifiestos y configuración del release", "Completado", "96%"],
  ["Ejecutar pre-check técnico", "Comprobar salud del cluster, dependencias y capacidad disponible", "Completado", "97%"],
  ["Aplicar cambio en Desarrollo", "Desplegar la versión y registrar evidencias del cambio", "Completado", "98%"],
  ["Ejecutar pruebas de humo", "Validar endpoints críticos, logs y conexión con servicios dependientes", "Completado", "95%"],
  ["Certificación QA", "Ejecutar casos funcionales y adjuntar resultado de certificación", "Completado", "94%"],
  ["Validar plan de rollback", "Confirmar script, versión anterior y criterios de reversa", "En edición", "92%"],
  ["Programar ventana de producción", "Validar disponibilidad de la ventana y bloquear calendarios", "Pendiente", "—"],
  ["Desplegar en Producción", "Ejecutar el runbook y monitorear el servicio durante el pase", "Pendiente", "—"],
  ["Ejecutar smoke test productivo", "Verificar transacciones críticas, métricas y alertas", "Pendiente", "—"],
  ["Cerrar OCD y adjuntar evidencias", "Registrar resultados finales, conformidades y cierre del cambio", "Pendiente", "—"],
];

export default function Home() {
  const [tickets,setTickets]=useState(initialTickets);
  const inputRef=useRef<HTMLInputElement>(null);
  const [conversations,setConversations]=useState<Record<string,Array<{role:"user"|"assistant";text:string;result?:AgentResult}>>>({});
  const [tab,setTab]=useState<Tab>("flow"),[channel,setChannel]=useState("web"),[aligned,setAligned]=useState(false),[published,setPublished]=useState(false),[message,setMessage]=useState(""),[light,setLight]=useState(false),[leftOpen,setLeftOpen]=useState(true),[rightOpen,setRightOpen]=useState(false),[statusFilter,setStatusFilter]=useState<"Todos" | TicketStatus>("Todos"),[ticketSearch,setTicketSearch]=useState(""),[selectedTicket,setSelectedTicket]=useState(tickets[0]);
  const inFlight=useRef(new Set<string>());
  const [pending,setPending]=useState<Record<string,boolean>>({});
  const [errors,setErrors]=useState<Record<string,string>>({});
  const filteredTickets=tickets.filter(t=>(statusFilter==="Todos"||t.status===statusFilter)&&`${t.id} ${t.title}`.toLocaleLowerCase("es").includes(ticketSearch.toLocaleLowerCase("es")));
  const chat=conversations[selectedTicket.id]??[];
  const createChat=()=>{
    const ticket={id:"REQ-"+crypto.randomUUID().slice(0,8).toUpperCase(),title:"Nuevo requerimiento",type:"REQ",progress:0,status:"En progreso"};
    setTickets(current=>[ticket,...current]);setSelectedTicket(ticket);setMessage("");setStatusFilter("Todos");setTicketSearch("");setChannel("web");setRightOpen(false);setTab("flow");
    requestAnimationFrame(()=>inputRef.current?.focus());
  };
  const ask=async(text:string)=>{
    const id=selectedTicket.id;
    if(!text.trim()||inFlight.current.has(id))return;
    inFlight.current.add(id);setPending(p=>({...p,[id]:true}));setErrors(e=>({...e,[id]:""}));
    setConversations(current=>({...current,[id]:[...(current[id]??[]),{role:"user",text:text.trim()}]}));
    if(selectedTicket.title==="Nuevo requerimiento"){
      const updated={...selectedTicket,title:text.trim()};
      setSelectedTicket(updated);setTickets(current=>current.map(t=>t.id===id?updated:t));
    }
    setMessage("");
    try{
      const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text,conversationId:id})});
      const data=await response.json();
      if(!response.ok)throw new Error(data.error||"No se pudo procesar el mensaje.");
      setConversations(current=>({...current,[id]:[...(current[id]??[]),{role:"assistant",text:data.answer,result:data}]}));
    }catch(error){setErrors(e=>({...e,[id]:error instanceof Error?error.message:"Error de conexión."}));}
    finally{inFlight.current.delete(id);setPending(p=>({...p,[id]:false}));}
  };
  return <main className={light?"app light":"app"}>
    <header className="topbar"><div className="brand"><div className="brand-mark">N</div><div><strong>Nexo<span>OPS</span></strong><small>Omnichannel Banking AI</small></div></div><div className="channel-switcher"><span className="channel-label">CANAL EN VIVO</span>{([["web",Monitor,"Control Center"],["vscode",Terminal,"VS Code Copilot"],["teams",MessagesSquare,"Microsoft Teams"]] as const).map(([k,Icon,l])=><button key={k} className={channel===k?"channel active":"channel"} onClick={()=>setChannel(k)}><Icon/>{l}</button>)}</div><div className="top-actions"><button className="icon-btn" onClick={()=>setLight(!light)} aria-label="Cambiar tema">{light?<Moon size={18}/>:<Sun size={18}/>}</button><div className="avatar">AM</div><div className="user"><b>Ana Morales</b><span>Change Manager</span></div></div></header>
    <div className={`workspace ${leftOpen?"":"left-closed"} ${rightOpen?"":"right-closed"}`}><aside className={`sidebar ${leftOpen?"":"collapsed"}`}><div className="side-title"><span>MIS TICKETS</span><button aria-label={leftOpen?"Cerrar panel izquierdo":"Abrir panel izquierdo"} onClick={()=>setLeftOpen(!leftOpen)}>{leftOpen?<ChevronLeft/>:<ChevronRight/>}</button></div><label className="search"><Search/><input aria-label="Buscar tickets" placeholder="Buscar tickets..." value={ticketSearch} onChange={e=>setTicketSearch(e.target.value)}/></label><div className="tickets-heading"><span>REQUERIMIENTOS</span><button type="button" aria-label="Nuevo requerimiento" onClick={createChat}><Plus/></button></div><div className="ticket-filters" aria-label="Filtrar tickets por estado">{statusOptions.map(option=><button key={option} type="button" className={statusFilter===option?"filter-active":""} onClick={()=>setStatusFilter(option)} aria-pressed={statusFilter===option}>{option}</button>)}</div><div className="ticket-list">{filteredTickets.length===0&&<p className="ticket-empty">No hay tickets para este filtro.</p>}{filteredTickets.map(t=><div className={`ticket ${selectedTicket.id===t.id?"selected":""} ${statusClass[t.status as TicketStatus]}`} key={t.id} onClick={()=>{setSelectedTicket(t);setMessage("");setRightOpen(true)}} role="button" tabIndex={0} onKeyDown={e=>(e.key==="Enter"||e.key===" ")&&(e.preventDefault(),setSelectedTicket(t),setMessage(""),setRightOpen(true))}><div className="ticket-head"><span className={`tag ${t.type.toLowerCase()}`}>{t.type}</span><code>{t.id}</code><span className="more"><MoreHorizontal/></span></div><h4>{t.title}</h4><div className="progress"><i style={{width:`${t.progress}%`}}/></div><div className="ticket-foot"><span>{t.progress}%</span><span className={`ticket-status ${statusClass[t.status as TicketStatus]}`}>{t.status==="Finalizado"||t.status==="Listo para Jira"?<Check/>:<Circle/>}{t.status}</span></div></div>)}</div><div className="side-bottom"><div className="mini-label">NEXOOPS AI ENGINE</div><div className="ai-status"><span className="pulse cyan-bg"/> RAG Engine <b>v2.4</b><small>12,400 tickets indexados</small></div></div></aside>
    <section className="chat-panel"><div className="panel-header"><div><div className="eyebrow"><span className="spark"><Sparkles/></span> COPILOTO NEXOOPS</div><h2>Armemos tu cambio, Ana.</h2><p>Describe tu requerimiento para iniciar la revisión con el agente.</p></div><button className="more-btn" aria-label="Más opciones del chat"><MoreHorizontal/></button></div><div className="chat-body"><div className="date-sep"><span>HOY, 10:42 AM</span></div><div className="message ai"><div className="ai-avatar"><Sparkles/></div><div><div className="bubble"><p>Bienvenido(a), Ana. ¿Con qué requerimiento te puedo apoyar el día de hoy?</p><p>Puedo ayudarte a registrar un cambio, preparar un OCD, revisar instrucciones o coordinar la ventana de pase.</p><div className="sources"><div className="source-title"><Sparkles/> FUENTES DE BASE DE CONOCIMIENTO </div>Confluence y Base de datos de requerimientos/pases del banco <span className="approved"><Check/> Aprobados por CAB al 100% en el primer intento</span></div></div><span className="msg-time">10:42 AM · NexoOPS AI</span></div></div>{chat.map((m,i)=><div className={m.role==="user"?"message user-msg":"message ai"} key={i}>{m.role==="assistant"&&<div className="ai-avatar"><Sparkles/></div>}<div className="bubble">{m.result?<AgentReply result={m.result}/>:m.text}</div>{m.role==="user"&&<div className="user-mini">AM</div>}</div>)}{pending[selectedTicket.id]&&<div role="status" className="message ai"><div className="bubble">El agente está revisando tu requerimiento…</div></div>}{errors[selectedTicket.id]&&<div role="alert" className="bubble">{errors[selectedTicket.id]}<p>Tu mensaje se conserva en la conversación. Puedes volver a enviarlo.</p></div>}{channel!=="web"&&<div className="channel-card"><div className="channel-card-head"><b>{channel==="vscode"?<Terminal/>:<MessagesSquare/>}{channel==="vscode"?"VS Code · GitHub Copilot":"Microsoft Teams Bot"}</b><span>EN VIVO</span></div>{channel==="vscode"?<><code>@nexoops genera la OCD para este PR #412</code><p><Check/> Leí 8 archivos modificados y 14 commits<br/><Check/> Match encontrado: OCD-3810 (98%)<br/><b><ArrowRight/> Borrador OCD-4092 creado en Control Center</b></p></>:<><p><Bell/> Tienes una ejecución asignada para <b>OCD-4092</b><br/>este sábado a las 23:00 hrs.</p><button onClick={()=>{setAligned(true);setChannel("web")}}><Check/> Confirmar hora</button><button className="outline"><Clock/> Sugerir cambio</button></>}</div>}</div><div className="composer"><div className="quick-prompts"><button onClick={()=>ask("Autocompletar Plan de Rollback según estándar del banco")}><Sparkles/> Autocompletar rollback</button><button onClick={()=>ask("¿Quién es el aprobador y ejecutor DBA de turno?")}><Search/> Buscar aprobador DBA</button><button onClick={()=>ask("Validar checklist de cumplimiento y subir a Jira")}><Check/> Validar y subir a Jira</button></div><div className="input-row"><button className="attach" aria-label="Adjuntar archivo"><Plus/></button><input ref={inputRef} aria-label="Mensaje al agente" value={message} onChange={e=>setMessage(e.target.value)} onKeyDown={e=>e.key==="Enter"&&message&&ask(message)} placeholder="Describe el cambio que quieres armar..."/><button disabled={pending[selectedTicket.id]||!message.trim()} aria-label="Enviar mensaje" className="send" onClick={()=>message&&ask(message)}><ArrowUp/></button></div><div className="composer-hint">NexoOPS puede cometer errores. Verifica siempre los datos críticos. <span>Enter para enviar</span></div></div></section>
    <section className={`canvas-panel ${rightOpen?"":"collapsed"}`}><div className="canvas-head"><div><div className="eyebrow">{selectedTicket.type} <code>{selectedTicket.id}</code><span className={`detail-status ${statusClass[selectedTicket.status as TicketStatus]}`}>{selectedTicket.status}</span><TicketReviews ticket={selectedTicket}/></div><h2>{selectedTicket.title.split(" ").slice(0,2).join(" ")}<br/>{selectedTicket.title.split(" ").slice(2).join(" ")}</h2></div><button className="share" aria-label={rightOpen?"Cerrar panel OCD":"Abrir panel OCD"} onClick={()=>setRightOpen(!rightOpen)}>{rightOpen?<ChevronRight/>:<ChevronLeft/>}</button></div><div className="tabs">{([["flow",GitBranch,"Flujo del requerimiento"],["builder",FileText,"Constructor OCD"],["schedule",CalendarClock,"Recursos y agenda"],["jira",Code,"Vista previa Jira"]] as const).map(([k,Icon,l])=><button key={k} onClick={()=>setTab(k)} className={tab===k?"tab active":"tab"}><Icon/>{l}</button>)}</div>{tab==="flow"?<OcdFlow/>:<TicketDetail key={selectedTicket.id} ticket={selectedTicket} tab={tab}/>}</section></div>
  </main>;
}
function OcdFlow(){
  const stages=[
    ["1","Registrar requerimiento","El usuario registra el requerimiento de cambio y define el tipo de pase.","Usuario","user"],
    ["2","Validar y preparar el pase","Analizar requerimiento · Validar lineamientos del banco · Recopilar información técnica · Definir tipo de pase","Agente de IA","agent"],
    ["3","Gestionar en Jira","Crear Historia de Usuario · Crear ticket OCD · Adjuntar información y evidencias","Agente de IA","agent"],
    ["4","Ejecutar pruebas automatizadas","Detectar artefactos de prueba, como pipelines, tests y OAT, y registrar el resultado.","Agente de IA","agent"],
    ["5","Programar pase","Consultar disponibilidad · Proponer ventana · Programar el pase en iTopCalendar","Agente de IA","agent"],
    ["6","Gestionar conformidades","Solicitante · LT · CL-QE · PO · OPS confirman la ejecución","Agente de IA","agent"],
    ["7","Pase listo","El pase queda registrado, con conformidades aprobadas y listo para ejecución.","Resultado final","ready"],
  ];
  return <div className="ocd-flow"><div className="flow-header"><div><span className="eyebrow">FLUJO DEL REQUERIMIENTO</span><h3>Del requerimiento a la programación</h3><p>Validación, pruebas automáticas y coordinación de conformidades en un solo flujo.</p></div><span className="flow-counter">7 etapas</span></div><div className="flow-steps">{stages.map(([number,title,desc,owner,kind],index)=><div className={'flow-stage '+kind} key={title}><div className="flow-number">{number}</div><div className="flow-stage-body"><h4>{title}</h4><p>{desc}</p><span className="flow-owner">{kind==='user'?<Monitor/>:kind==='ready'?<Check/>:<Sparkles/>}{owner}</span></div>{index<stages.length-1&&<ArrowRight className="flow-arrow"/>}</div>)}</div><div className="flow-footer"><div><b>Participantes y responsabilidades</b><span>Usuario registra y valida · Agente de IA automatiza, prueba, programa y coordina · LT, CL-QE, PO y OPS dan conformidad.</span></div><div><b>Sistemas integrados</b><span>Jira · Azure (pipelines/tests) · iTopCalendar · Microsoft Teams.</span></div></div></div>;
}function InstructionBuilder(){
  const groups=[
    ["CERTIFICACIÓN","Validar el cambio en Desarrollo antes de solicitar la ventana",[["Ejecutar pruebas funcionales del API-Pagos-QR","QA · Diego Rojas","Completada"],["Adjuntar evidencias de certificación QA","QA · Diego Rojas","Pendiente"]]],
    ["PRODUCCIÓN","Instrucciones para ejecutar el pase en la ventana aprobada",[["Pre-check de AKS, base de datos y dependencias","DevOps · Lucía Vargas","Pendiente"],["Desplegar API-Pagos-QR-Prod v2.18.4","DevOps · Lucía Vargas","Pendiente"],["Validar transacción de prueba y monitoreo","QA · Diego Rojas","Pendiente"]]],
    ["REVERSIÓN","Pasos para regresar a la versión estable ante una falla",[["Restaurar imagen anterior y configuración estable","DevOps · Lucía Vargas","Pendiente"],["Validar recuperación de transacciones","DBA · Carlos Mendoza","Pendiente"]]],
    ["AUTOMATIZADAS","Acciones ejecutadas por las integraciones de NexoOPS",[["Crear respaldo y registrar evidencia en Jira","NexoOPS AI","Automática"],["Notificar resultado a CAB y responsables","Teams Bot","Automática"]]],
    ["POST DEPLOY · MONITOREO SINTÉTICO","Verificación posterior al despliegue",[["Monitorear errores, latencia y disponibilidad durante 30 min","OPS · Patricia S.","Pendiente"]]],
  ];
  return <div className="instruction-builder"><div className="builder-intro"><div><span className="eyebrow">INSTRUCCIONES DEL CAMBIO</span><h3>Arma el runbook de OCD-4092</h3><p>Organiza las instrucciones que deberán ejecutar y validar los equipos.</p></div><button className="add-instruction"><Plus/> Agregar instrucción</button></div>{groups.map(([title,desc,items])=><section className="instruction-section" key={String(title)}><div className="instruction-heading"><div><span>{title}</span><p>{desc}</p></div><button aria-label={'Agregar instrucción en '+title}><Plus/></button></div><div className="instruction-list">{(items as string[][]).map(([name,owner,state])=><div className="instruction-row" key={name}><div className="instruction-bullet"><Check/></div><div className="instruction-main"><b>{name}</b><small>{owner}</small></div><span className={'instruction-state '+(state==='Completada'?'done':state==='Automática'?'auto':'')}>{state}</span><button className="instruction-more" aria-label={'Más opciones para '+name}><MoreHorizontal/></button></div>)}</div></section>)}</div>;
}function Schedule({aligned,onAlign}:{aligned:boolean;onAlign:()=>void}){return <div className="schedule"><div className="window-card"><span>VENTANA DE CAMBIO PROPUESTA</span><strong>{aligned?"Sábado 14 Nov · 23:30 – 02:00 HRS":"Sábado 14 Nov · 23:00 – 01:30 HRS"}</strong><small>Zona horaria: America/Lima · Ventana no congelada</small></div><div className="resource-list">{[["CM","Carlos Mendoza","DBA Oracle","Confirmado","confirmed"],["LV","Lucía Vargas","Ingeniero DevOps / Cloud","Confirmado","confirmed"],["DR","Diego Rojas","Analista QA Certificador",aligned?"Confirmado":"Conflicto a las 23:00",aligned?"confirmed":"conflict"]].map(r=><div className="resource" key={r[1]}><div className="resource-avatar">{r[0]}</div><div><b>{r[1]}</b><span>{r[2]}</span></div><em className={r[4]}>{r[4]==="confirmed"?<Check/>:<TriangleAlert/>}{r[3]}</em></div>)}</div><button className="align-btn" onClick={onAlign}>{aligned?<Check/>:<Sparkles/>}{aligned?"Recursos 100% alineados":"Alinear y notificar recursos con IA"}<span><ArrowRight/></span></button>{aligned&&<div className="success-note"><Check/> Ventana movida 30 min. Teams, Slack y correo notificados.</div>}</div>}
function Jira({published,onPublish}:{published:boolean;onPublish:()=>void}){return <div className="jira-view"><div className="payload"><div className="payload-head"><span>JIRA SERVICE MANAGEMENT · PAYLOAD</span><button><Copy/> Copiar JSON</button></div><pre>{`{
  "project": "BANKOPS",
  "issueType": "Cambio estándar",
  "summary": "Actualización Microservicio Transferencias CCE",
  "service": "API-Pagos-QR-Prod",
  "risk": "Alto",
  "window": "2026-11-14T23:00:00-05:00",
  "rollbackPlan": "OCD-3992.standard",
  "cabApproval": "Pending"
}`}</pre></div>{published?<div className="published"><div className="check-large"><Check/></div><h3>OCD publicada correctamente</h3><p><code>JIRA-OCD-4092</code> · Link creado y calendario bloqueado</p><b>Ahorraste 2.5 horas de gestión</b><small>Notificaciones enviadas a 3 recursos y CAB.</small></div>:<button className="publish" onClick={onPublish}><Code/> Publicar OCD en Jira y bloquear calendarios <span><ArrowRight/></span></button>}</div>}
