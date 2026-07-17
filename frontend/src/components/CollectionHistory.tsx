import type { CollectionRun } from "../api/types";

export function CollectionHistory({ runs }: { runs: CollectionRun[] }) {
  if (!runs.length) return null;
  return <section className="panel"><div className="eyebrow">采集历史</div><h2>数据来源</h2>{runs.map((run) => <p key={run.id}>{run.query} · {run.notes_created} 条 <small>({run.adapter} / {run.status})</small></p>)}</section>;
}
