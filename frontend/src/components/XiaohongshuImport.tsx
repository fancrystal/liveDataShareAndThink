import { useState } from "react";

import type { CollectionSummary } from "../api/types";

type Props = {
  enabled: boolean;
  summary: CollectionSummary | null;
  onImport: (keyword: string) => Promise<void>;
};

export function XiaohongshuImport({ enabled, summary, onImport }: Props) {
  const [keyword, setKeyword] = useState("");

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
          disabled={!enabled}
        />
      </label>
      <button disabled={!enabled || !keyword.trim()} onClick={() => void onImport(keyword.trim())}>
        采集公开搜索结果
      </button>
      {summary && <p className="import-result">已导入 {summary.notes_created} 条公开笔记</p>}
    </section>
  );
}
