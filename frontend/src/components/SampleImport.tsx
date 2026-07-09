import type { CollectionSummary } from "../api/types";

export function SampleImport({
  enabled,
  summary,
  onImport
}: {
  enabled: boolean;
  summary: CollectionSummary | null;
  onImport: () => Promise<void>;
}) {
  return (
    <section className="panel">
      <div className="eyebrow">02 · 建立样本</div>
      <h2>固定样本</h2>
      <p>先用稳定样本验证产品核心，下一里程碑再接真实小红书登录。</p>
      <button disabled={!enabled} onClick={onImport}>导入固定样本</button>
      {summary && <p className="success">已导入 {summary.notes_created} 条笔记与 {summary.metric_snapshots_created} 个指标快照</p>}
    </section>
  );
}

