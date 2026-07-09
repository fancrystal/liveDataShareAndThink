import { useState } from "react";

import type { Project, ProjectCreate } from "../api/types";

export function ProjectForm({
  onCreate
}: {
  onCreate: (input: ProjectCreate) => Promise<Project>;
}) {
  const [name, setName] = useState("");
  return (
    <section className="panel">
      <div className="eyebrow">01 · 定义研究</div>
      <h2>研究项目</h2>
      <label>
        项目名称
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：护肤直播增长" />
      </label>
      <button
        disabled={!name.trim()}
        onClick={() =>
          onCreate({
            name,
            description: "固定样本垂直切片",
            brand_profile: {
              name,
              positioning: "数据驱动的小红书直播引流",
              target_audience: "希望降低内容试错成本的用户",
              tone: "专业、克制、友好",
              core_value: "让内容决策有证据",
              forbidden_terms: ["根治", "百分百有效"]
            }
          })
        }
      >
        创建项目
      </button>
    </section>
  );
}

