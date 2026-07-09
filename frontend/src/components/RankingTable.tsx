import type { RankingReport } from "../api/types";

export function RankingTable({ report }: { report: RankingReport | null }) {
  if (!report) return null;
  return (
    <section className="panel span-two">
      <div className="eyebrow">03 · 识别机会</div>
      <div className="section-heading">
        <h2>相对表现榜</h2>
        <span className="confidence">置信度：{report.insight.confidence}</span>
      </div>
      <div className="ranking-list">
        {report.rankings.map((item, index) => (
          <article className="ranking" key={item.note_id}>
            <span className="rank">0{index + 1}</span>
            <div>
              <a href={item.url}>{item.title}</a>
              <small>互动 {item.score.engagement} · 速度 {item.score.velocity} · 账号效率 {item.score.author_efficiency ?? "未知"}</small>
            </div>
            <strong>{item.score.total}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

