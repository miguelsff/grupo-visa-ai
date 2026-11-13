"use client";
import { useState } from "react";
import { Check, Copy, FileText } from "lucide-react";

export type Ticket = { id:string; title:string; type:string; status:string; progress:number };
const records:Record<string,{service:string; instructions:string[]; reviews:string[]}> = {
  "OCD-4092":{service:"Motor de Transferencias CCE",instructions:["Validar pruebas funcionales del Motor de Transferencias CCE","Desplegar la versión aprobada del Motor de Transferencias CCE","Restaurar la versión anterior del Motor de Transferencias CCE","Ejecutar pipeline del Motor de Transferencias CCE","Monitorear transacciones CCE y tasa de errores"],reviews:["Completado","En revisión","Pendiente"]},
  "ITSM-1104":{service:"Base de Datos Riesgos",instructions:["Validar origen, destino y puerto de la solicitud de firewall","Aplicar la regla aprobada para Base de Datos Riesgos","Retirar la regla y restaurar la configuración previa","Validar conectividad mediante pruebas de red","Monitorear conexiones y registros del firewall"],reviews:["Sin información","Sin información","Sin información"]},
  "OCD-4088":{service:"Motor de Fraude",instructions:["Certificar la reversión del Motor de Fraude","Ejecutar el plan aprobado del Motor de Fraude","Recuperar la versión estable del Motor de Fraude","Ejecutar las comprobaciones automatizadas del rollback","Monitorear alertas y decisiones del Motor de Fraude"],reviews:["Sin información","Sin información","Sin información"]},
  "OCD-4076":{service:"Core Bancario",instructions:["Revisar evidencias de certificación QA del Core Bancario"],reviews:["Sin información","Completado","Sin información"]}
};
export function TicketReviews({ticket}:{ticket:Ticket}){
  return <span className="review-status">{(records[ticket.id]?.reviews??["Pendiente","Pendiente","Pendiente"]).map((state,i)=><span key={i} className={state==="Completado"?"review-done":state==="En revisión"?"review-current":"review-pending"}>{state==="Completado"&&<Check/>}{["Desarrollo","Certificación","Producción"][i]} · {state}</span>)}</span>;
}
export default function TicketDetail({ticket,tab}:{ticket:Ticket;tab:string}){
  const [published,setPublished]=useState(false);
  const record=records[ticket.id]??{service:ticket.title,instructions:[],reviews:[]};
  const payload=JSON.stringify({key:ticket.id,summary:ticket.title,type:ticket.type,status:ticket.status,service:record.service},null,2);
  if(tab==="builder")return <div className="instruction-builder"><div className="builder-intro"><div><span className="eyebrow">INSTRUCCIONES DEL REQUERIMIENTO</span><h3>Runbook de {ticket.id}</h3><p>{record.service}</p></div></div>{record.instructions.map((instruction,i)=><section className="instruction-section" key={instruction}><div className="instruction-heading"><span>{["CERTIFICACIÓN","PRODUCCIÓN","REVERSIÓN","AUTOMATIZADAS","POST DEPLOY"][i]}</span></div><div className="instruction-row"><FileText/><div className="instruction-main"><b>{instruction}</b><small>Responsable: por asignar</small></div></div></section>)}</div>;
  if(tab==="schedule")return <div className="schedule"><div className="window-card"><span>AGENDA DE {ticket.id}</span><strong>{record.service}</strong><p>No hay una ventana ni recursos registrados para este requerimiento.</p></div></div>;
  if(tab==="jira")return <div className="jira-view"><div className="payload"><div className="payload-head"><span>{ticket.id} · VISTA PREVIA</span><button onClick={()=>navigator.clipboard.writeText(payload)}><Copy/>Copiar JSON</button></div><pre>{payload}</pre></div><button className="publish" onClick={()=>setPublished(true)} disabled={published}>{published?"Publicación simulada de "+ticket.id:"Simular publicación de "+ticket.id}</button></div>;
  return null;
}
