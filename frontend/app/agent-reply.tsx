import type { ChatResponse } from "../lib/api";
import styles from "./page.module.css";

const labels = {
  CUMPLE: "Cumple", FALTA_INFORMACION: "Falta información",
  ERROR: "Error", NO_VERIFICABLE: "No verificable",
};

export function hasDetails(result: ChatResponse) {
  return result.sources.length > 0 || Object.keys(result.draft.facts).length > 0 || result.questions.length > 0 || result.validations.length > 0 || (result.preview?.pending.length ?? 0) > 0;
}

export function ReviewDetails({ result }: { result: ChatResponse }) {
  const facts = Object.entries(result.draft.facts);
  return <div className={styles.details}>
    {!!result.sources.length && <details><summary>Fuentes ({result.sources.length})</summary>
      <ul>{result.sources.map(source => <li key={source.point_id}>
        <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
        <small>{source.code} · {source.origin} · versión {source.version} · {source.locator}</small>
        <p>{source.excerpt}</p>
      </li>)}</ul>
    </details>}
    {!!facts.length && <details><summary>Borrador · revisión {result.revision}</summary>
      <dl>{facts.map(([key, fact]) => <div key={key}>
        <dt>{fact.name.replaceAll("_", " ")}</dt><dd>{fact.value}</dd>
      </div>)}</dl>
    </details>}
    {!!result.preview?.pending.length && <details open><summary>Pendientes ({result.preview.pending.length})</summary>
      <ul>{result.preview.pending.map((pending, i) => <li key={`${pending}-${i}`}>{pending}</li>)}</ul>
    </details>}
    {!!result.questions.length && <details><summary>Preguntas pendientes ({result.questions.length})</summary>
      <ul>{result.questions.map(question => <li key={question}>{question}</li>)}</ul>
    </details>}
    {!!result.validations.length && <details><summary>Validaciones ({result.validations.length})</summary>
      <ul>{result.validations.map((item, i) => <li key={`${item.rule_id}-${i}`}>
        <strong>{item.check} · {labels[item.status]}</strong><p>{item.detail}</p>
        <a href={item.reference.url} target="_blank" rel="noreferrer">{item.reference.code} · {item.rule_id}</a>
      </li>)}</ul>
    </details>}
  </div>;
}

export default function AgentReply({ result }: { result: ChatResponse }) {
  return <><p>{result.answer}</p>
    {result.error && <p role="alert" className={styles.error}>{result.error}</p>}
  </>;
}
