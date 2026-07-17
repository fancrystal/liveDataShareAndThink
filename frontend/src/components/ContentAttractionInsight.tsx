import type { RankingReport } from "../api/types";

export function ContentAttractionInsight({ insight }: { insight: RankingReport["attraction_insight"] | undefined }) {
  if (!insight) return null;
  const formats = Object.entries(insight.result.format_counts).map(([name, count]) => `${name} ${count}`).join(" · ");
  const hooks = Object.entries(insight.result.hook_patterns).map(([name, count]) => `${name} ${count}`).join(" · ");

  return (
    <section className="panel span-two">
      <div className="eyebrow">03 · 内容引流洞察</div>
      <h2>{insight.title}</h2>
      <p>{insight.summary}</p>
      <p>标题钩子：{hooks || "样本不足"}</p>
      <p>内容形式：{formats || "未公开"}</p>
      <ul>
        {insight.result.reusable_angles.map((angle) => <li key={angle}>{angle}</li>)}
      </ul>
      <small>证据：{insight.evidence.map((item) => item.summary).join("；")}</small>
    </section>
  );
}
