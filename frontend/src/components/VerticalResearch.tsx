import { useState } from "react";
import type { PostPackage, VerticalResearch as Report } from "../api/types";
import { downloadPoster, PostImageRenderer } from "./PostImageRenderer";

export function VerticalResearch({ onRun, onPackage, report, post }: { onRun: (topic: string) => Promise<void>; onPackage: (topic: string, angle: string, runId: string) => Promise<void>; report: Report | null; post: PostPackage | null }) {
  const [topic, setTopic] = useState("");
  const [angle, setAngle] = useState("");
  const [isResearching, setIsResearching] = useState(false);
  const [isPackaging, setIsPackaging] = useState(false);
  const [copied, setCopied] = useState(false);

  const runResearch = async () => {
    setIsResearching(true);
    try {
      await onRun(topic.trim());
    } finally {
      setIsResearching(false);
    }
  };

  const buildPackage = async () => {
    if (!report) return;
    setIsPackaging(true);
    try {
      await onPackage(report.topic, angle.trim(), report.run_id);
    } finally {
      setIsPackaging(false);
    }
  };

  const copyPost = async () => {
    if (!post) return;
    await navigator.clipboard?.writeText(`${post.title}\n\n${post.caption}\n\n${post.tags.map((tag) => `#${tag}`).join(" ")}`);
    setCopied(true);
  };

  return <section className="panel span-two"><div className="eyebrow">赛道爆款研究</div><h2>输入赛道，直接获得爆款日报</h2><label>赛道关键词<input disabled={isResearching} value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="例如：普拉提产后修复" /></label><button disabled={!topic.trim() || isResearching} aria-busy={isResearching} onClick={() => void runResearch()}>{isResearching && <span className="spinner" aria-hidden="true" />} {isResearching ? "正在采集并分析…" : "开始爆款研究"}</button>{report && <div><h3>今日爆款：{report.ai_report.today_summary}</h3><p>{report.ai_report.disclosure}</p><h3>为什么爆</h3><ul>{report.ai_report.hot_reasons.map((item) => <li key={item}>{item}</li>)}</ul><h3>怎么复刻</h3><ul>{report.ai_report.replication_checklist.map((item) => <li key={item}>{item}</li>)}</ul><h3>Top 候选</h3>{report.top_candidates.map((item) => <p key={item.url}><a href={item.url}>{item.title}</a> · 热度 {item.score.toFixed(1)}</p>)}<label>创作方向<input disabled={isPackaging} value={angle} onChange={(event) => setAngle(event.target.value)} placeholder="例如：产后 6 周新手动作" /></label><button disabled={!angle.trim() || isPackaging} aria-busy={isPackaging} onClick={() => void buildPackage()}>{isPackaging && <span className="spinner" aria-hidden="true" />} {isPackaging ? "正在生成图文…" : "生成可发布图文"}</button></div>}{post && <div><h2>{post.title}</h2><p>{post.caption}</p><p>{post.tags.map((tag) => `#${tag}`).join(" ")}</p><div className="post-actions"><button onClick={() => void copyPost()}>{copied ? "已复制正文和标签" : "复制正文和标签"}</button><button onClick={() => post.pages.forEach((page, index) => downloadPoster(page, index, post.title))}>下载全部海报</button></div><div className="poster-grid">{post.pages.map((page, index) => <article className="poster-card" key={page.heading}><PostImageRenderer page={page} index={index} title={post.title} /><button onClick={() => downloadPoster(page, index, post.title)}>下载第 {index + 1} 张海报</button></article>)}</div></div>}</section>;
}
