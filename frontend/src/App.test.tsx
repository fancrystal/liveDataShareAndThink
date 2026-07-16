import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { App } from "./App";
import type { Api } from "./api/types";

afterEach(cleanup);

const fakeApi: Api = {
  async createProject(input) {
    return {
      id: "project-1",
      name: input.name,
      description: input.description,
      brand_profile: input.brand_profile
    };
  },
  async importFixture() {
    return { run_id: "run-1", status: "succeeded", notes_created: 3, metric_snapshots_created: 3 };
  },
  async importXiaohongshu() {
    return { run_id: "xhs-run", status: "succeeded", notes_created: 4, metric_snapshots_created: 4 };
  },
  async listNotes() {
    return [{
      id: "note-1",
      title: "Sensitive skin routine",
      url: "https://www.xiaohongshu.com/explore/note-1",
      content: "Start with fewer products.",
      content_type: "image",
      published_at: "2026-07-10T08:00:00Z",
      source: { adapter: "xiaohongshu-dom" },
      author: { id: "author-1", nickname: "Creator", followers: null },
      metric_snapshots: [{ id: "metric-1", collected_at: "2026-07-14T08:00:00Z", likes: 12000, favorites: 300, comments: 8, shares: null, followers: null }]
    }];
  },
  async rankNotes() {
    return {
      rankings: [{
        note_id: "note-1",
        title: "敏感肌别再盲买了",
        url: "https://example.test/note-1",
        score: {
          total: 91.2,
          engagement: 90,
          velocity: 92,
          cohort_relative: 88,
          author_efficiency: 96,
          confidence: "high",
          explanation: {}
        }
      }],
      insight: {
        id: "insight-1",
        title: "相对表现",
        summary: "识别高表现内容",
        confidence: "high",
        evidence: [{ id: "evidence-1", summary: "样本证据" }]
      }
    };
  },
  async createTopic() {
    return { id: "topic-1" };
  },
  async generateDrafts() {
    return [
      {
        id: "draft-1",
        variant: "practical",
        status: "pending_review",
        evidence_ids: ["evidence-1"],
        current_version: { id: "version-1", title: "敏感肌先做减法", body: "正文", tags: ["敏感肌"], cover_text: "先做减法" }
      },
      {
        id: "draft-2",
        variant: "story",
        status: "pending_review",
        evidence_ids: ["evidence-1"],
        current_version: { id: "version-2", title: "我也曾越护肤越红", body: "正文", tags: ["护肤"], cover_text: "真实经历" }
      },
      {
        id: "draft-3",
        variant: "contrarian",
        status: "pending_review",
        evidence_ids: ["evidence-1"],
        current_version: { id: "version-3", title: "泛红时别急着修护", body: "正文", tags: ["避坑"], cover_text: "先停再修" }
      }
    ];
  }
};

describe("content research workbench", () => {
  async function createProject(user: ReturnType<typeof userEvent.setup>) {
    await user.type(screen.getByLabelText("项目名称"), "护肤直播增长");
    await user.click(screen.getByRole("button", { name: "创建项目" }));
  }

  it("imports a Xiaohongshu keyword before analysis", async () => {
    const user = userEvent.setup();
    render(<App api={fakeApi} />);

    await createProject(user);
    await user.type(screen.getByLabelText("小红书关键词"), "敏感肌");
    await user.click(screen.getByRole("button", { name: "采集公开搜索结果" }));

    expect(await screen.findByText("已导入 4 条公开笔记")).toBeInTheDocument();
    expect(await screen.findByText("Sensitive skin routine")).toBeInTheDocument();
  });

  it("shows collection progress and prevents a duplicate Xiaohongshu import", async () => {
    let finishImport: (() => void) | undefined;
    const api: Api = {
      ...fakeApi,
      importXiaohongshu: () => new Promise((resolve) => {
        finishImport = () => resolve({ run_id: "xhs-run", status: "succeeded", notes_created: 4, metric_snapshots_created: 4 });
      })
    };
    const user = userEvent.setup();
    render(<App api={api} />);

    await createProject(user);
    await user.type(screen.getByLabelText("小红书关键词"), "敏感肌");
    const button = screen.getByRole("button", { name: "采集公开搜索结果" });
    await user.click(button);

    expect(screen.getByRole("button", { name: "采集中…" })).toBeDisabled();
    expect(screen.getByLabelText("小红书关键词")).toBeDisabled();
    finishImport?.();
    expect(await screen.findByText("已导入 4 条公开笔记")).toBeInTheDocument();
  });

  it("runs the fixed-sample workflow", async () => {
    const user = userEvent.setup();
    render(<App api={fakeApi} />);

    await user.type(screen.getByLabelText("项目名称"), "护肤直播增长");
    await user.click(screen.getByRole("button", { name: "创建项目" }));
    await user.click(screen.getByRole("button", { name: "导入固定样本" }));
    await user.click(screen.getByRole("button", { name: "运行分析" }));

    expect(await screen.findByText("敏感肌别再盲买了")).toBeInTheDocument();
    expect(screen.getByText(/置信度：high/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "生成三个草稿" }));
    expect(await screen.findByText("敏感肌先做减法")).toBeInTheDocument();
    expect(screen.getByText("泛红时别急着修护")).toBeInTheDocument();
  });
});
