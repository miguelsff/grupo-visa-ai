export type AgentResult={answer:string;questions?:unknown[];draft?:unknown;sources?:Array<{title?:string;url?:string;point_id?:string;code?:string;version?:string;excerpt?:string}>;validations?:unknown[];revision?:number;status?:string;error?:string|null};
const show=(value:unknown)=>typeof value==="string"?value:JSON.stringify(value,null,2);
export default function AgentReply({result}:{result:AgentResult}){
 return <><div style={{whiteSpace:"pre-wrap"}}>{result.answer}</div>
 {result.error&&<p role="alert">{result.error}</p>}
 {!!result.questions?.length&&<details><summary>Preguntas pendientes ({result.questions.length})</summary>{result.questions.map((q,i)=><p key={i}>{show(q)}</p>)}</details>}
 {!!result.sources?.length&&<details className="sources"><summary>Fuentes consultadas ({result.sources.length})</summary>{result.sources.map((source,i)=><div key={source.point_id||i}>{source.url&&/^https?:\/\//i.test(source.url)?<a href={source.url} target="_blank" rel="noopener noreferrer">{source.title||"Fuente"}</a>:<b>{source.title||"Fuente"}</b>}<small>{source.code} {source.version}</small><p>{source.excerpt}</p></div>)}</details>}
 {!!result.validations?.length&&<details><summary>Validaciones ({result.validations.length})</summary><pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{show(result.validations)}</pre></details>}
 {result.draft!=null&&<details><summary>Borrador · revisión {result.revision??"—"}</summary><pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{show(result.draft)}</pre></details>}
 {result.status&&<small>Estado de revisión: {result.status}</small>}</>;
}
