import { useState } from "react";
import type { VerticalResearch as Report } from "../api/types";

export function VerticalResearch({ onRun, report }: { onRun: (topic: string) => Promise<void>; report: Report | null }) {
  const [topic, setTopic] = useState("");
  return <section className="panel span-two"><div className="eyebrow">赛道爆款研究</div><h2>输入赛道，直接获得爆款日报</h2><label>赛道关键词<input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="例如：普拉提产后修复" /></label><button disabled={!topic.trim()} onClick={() => void onRun(topic.trim())}>开始爆款研究</button>{report && <div><h3>今日爆款：{report.ai_report.today_summary}</h3><p>{report.ai_report.disclosure}</p><h3>为什么爆</h3><ul>{report.ai_report.hot_reasons.map((item) => <li key={item}>{item}</li>)}</ul><h3>怎么复刻</h3><ul>{report.ai_report.replication_checklist.map((item) => <li key={item}>{item}</li>)}</ul><h3>Top 候选</h3>{report.top_candidates.map((item) => <p key={item.url}><a href={item.url}>{item.title}</a> · 热度 {item.score.toFixed(1)}</p>)}</div>}</section>;
}
