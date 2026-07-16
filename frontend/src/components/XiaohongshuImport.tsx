import { useState } from "react";

import type { CollectionSummary } from "../api/types";

type Props = {
  enabled: boolean;
  summary: CollectionSummary | null;
  error: string;
  onImport: (keyword: string) => Promise<void>;
};

export function XiaohongshuImport({ enabled, summary, error, onImport }: Props) {
  const [keyword, setKeyword] = useState("");
  const [isCollecting, setIsCollecting] = useState(false);
  const proxyUnavailable = error.includes("本地采集代理未启动");

  const collect = async () => {
    setIsCollecting(true);
    try {
      await onImport(keyword.trim());
    } finally {
      setIsCollecting(false);
    }
  };

  return (
    <section className="panel">
      <div className="eyebrow">02 · 真实采集</div>
      <h2>小红书公开搜索</h2>
      <p>使用本机已登录会话，只读取公开搜索结果，不执行互动操作。</p>
      <label>
        小红书关键词
        <input
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="例如：敏感肌"
          disabled={!enabled || isCollecting}
        />
      </label>
      <button disabled={!enabled || !keyword.trim() || isCollecting} onClick={() => void collect()}>
        {isCollecting ? "采集中…" : "采集公开搜索结果"}
      </button>
      {summary && <p className="import-result">已导入 {summary.notes_created} 条公开笔记</p>}
      {proxyUnavailable && <p className="hint">请在项目目录运行：<code>python -m app.collection.proxy_runner</code></p>}
    </section>
  );
}
