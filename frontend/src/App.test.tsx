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
  async listProjects() {
    return [];
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
  async listCollectionRuns() {
    return [];
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
      },
      attraction_insight: {
        id: "attraction-1",
        title: "内容引流模式",
        summary: "基于公开样本归纳可复用结构。",
        confidence: "high",
        result: { hook_patterns: { directive: 2 }, format_counts: { image: 2 }, reusable_angles: ["选题 A"] },
        evidence: [{ id: "attraction-evidence-1", summary: "内容样本：敏感肌先做减法" }]
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
  },
  async runVerticalResearch(_projectId, topic) {
    return { topic, run_id: "run-vertical-1", collection_date: "today", top_candidates: [{ title: "产后修复先做什么", url: "https://example.test/1", score: 90 }], ai_report: { today_summary: "低门槛修复动作受关注", hot_reasons: ["明确人群"], replication_checklist: ["写清痛点"], disclosure: "发布时间未公开" } };
  },
  async createPostPackage() { return { title: "产后修复先做这一步", caption: "正文", tags: ["产后修复"], pages: Array.from({ length: 5 }, (_, index) => ({ heading: `第${index + 1}页`, body: "内容" })) }; }
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

  it("runs vertical hot-content research from one topic input", async () => {
    const user = userEvent.setup();
    render(<App api={fakeApi} />);
    await user.type(screen.getByLabelText("赛道关键词"), "普拉提产后修复");
    await user.click(screen.getByRole("button", { name: "开始爆款研究" }));
    expect(await screen.findByText(/今日爆款：低门槛修复动作受关注/)).toBeInTheDocument();
    expect(screen.getByText("产后修复先做什么")).toBeInTheDocument();
  });

  it("provides download and copy controls for a generated five-page post", async () => {
    const user = userEvent.setup();
    render(<App api={fakeApi} />);

    await user.type(screen.getByLabelText("赛道关键词"), "北京火锅");
    await user.click(screen.getByRole("button", { name: "开始爆款研究" }));
    await user.type(await screen.findByLabelText("创作方向"), "探店");
    await user.click(screen.getByRole("button", { name: "生成可发布图文" }));

    expect(await screen.findByRole("button", { name: "下载全部海报" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "下载第 1 张海报" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "复制正文和标签" })).toBeInTheDocument();
  });

  it("shows progress and prevents duplicate vertical research while waiting", async () => {
    let finishResearch: (() => void) | undefined;
    const api: Api = {
      ...fakeApi,
      runVerticalResearch: (_projectId, topic) => new Promise((resolve) => {
        finishResearch = () => resolve({ topic, run_id: "run-vertical-2", collection_date: "today", top_candidates: [], ai_report: { today_summary: "分析完成", hot_reasons: [], replication_checklist: [], disclosure: "发布时间未公开" } });
      })
    };
    const user = userEvent.setup();
    render(<App api={api} />);

    await user.type(screen.getByLabelText("赛道关键词"), "北京火锅");
    await user.click(screen.getByRole("button", { name: "开始爆款研究" }));

    expect(screen.getByRole("button", { name: "正在采集并分析…" })).toBeDisabled();
    expect(screen.getByLabelText("赛道关键词")).toBeDisabled();
    finishResearch?.();
    expect(await screen.findByText(/今日爆款：分析完成/)).toBeInTheDocument();
  });

  it("reopens an existing project and shows its collection history", async () => {
    const api: Api = {
      ...fakeApi,
      listProjects: async () => [{
        id: "existing-project", name: "已有项目", description: "历史数据", brand_profile: {
          name: "品牌", positioning: "定位", target_audience: "用户", tone: "友好", core_value: "价值", forbidden_terms: []
        }
      }],
      listCollectionRuns: async () => [{
        id: "run-1", adapter: "xiaohongshu-dom", query: "敏感肌", status: "succeeded",
        started_at: "2026-07-17T10:00:00Z", finished_at: "2026-07-17T10:01:00Z", notes_created: 20, metric_snapshots_created: 20
      }]
    };
    const user = userEvent.setup();
    render(<App api={api} />);

    await user.click(await screen.findByRole("button", { name: "打开：已有项目" }));

    expect(await screen.findByText("敏感肌 · 20 条")).toBeInTheDocument();
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
    expect(screen.getByText("内容引流模式")).toBeInTheDocument();
  });
});
