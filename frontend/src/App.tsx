import { useEffect, useState } from "react";

import type { Api, CollectionRun, CollectionSummary, Draft, Note, Project, RankingReport } from "./api/types";
import { DraftWorkbench } from "./components/DraftWorkbench";
import { ContentAttractionInsight } from "./components/ContentAttractionInsight";
import { CollectionHistory } from "./components/CollectionHistory";
import { ProjectPicker } from "./components/ProjectPicker";
import { ProjectForm } from "./components/ProjectForm";
import { RankingTable } from "./components/RankingTable";
import { NotesPreview } from "./components/NotesPreview";
import { SampleImport } from "./components/SampleImport";
import { XiaohongshuImport } from "./components/XiaohongshuImport";
import "./styles.css";

export function App({ api }: { api: Api }) {
  const [project, setProject] = useState<Project | null>(null);
  const [summary, setSummary] = useState<CollectionSummary | null>(null);
  const [report, setReport] = useState<RankingReport | null>(null);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [runs, setRuns] = useState<CollectionRun[]>([]);
  const [error, setError] = useState("");

  const guard = async (operation: () => Promise<void>) => {
    setError("");
    try {
      await operation();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "操作失败");
    }
  };

  useEffect(() => { void api.listProjects().then(setProjects).catch(() => undefined); }, [api]);
  const openProject = async (selected: Project) => guard(async () => {
    setProject(selected); setSummary(null); setReport(null); setDrafts([]);
    const [loadedNotes, loadedRuns] = await Promise.all([api.listNotes(selected.id), api.listCollectionRuns(selected.id)]);
    setNotes(loadedNotes); setRuns(loadedRuns);
  });

  return (
    <main>
      <header>
        <div>
          <span className="brand-mark">LDS</span>
          <p>LiveDataShareAndThink</p>
        </div>
        <h1>让每条内容，<br /><i>都有依据。</i></h1>
        <p className="lede">小红书内容引流 · 第一期固定样本工作台</p>
      </header>

      {error && <div role="alert" className="error">{error}</div>}
      <div className="workflow">
        <ProjectForm onCreate={async (input) => {
          const created = await api.createProject(input);
          setProject(created);
          setProjects((items) => [created, ...items]);
          return created;
        }} />
        <ProjectPicker projects={projects} onOpen={openProject} />
        <SampleImport
          enabled={Boolean(project)}
          summary={summary}
          onImport={() => guard(async () => {
            if (project) setSummary(await api.importFixture(project.id));
          })}
        />
        <XiaohongshuImport
          enabled={Boolean(project)}
          summary={summary}
          error={error}
          onImport={async (keyword) => guard(async () => {
            if (project) {
              setSummary(await api.importXiaohongshu(project.id, keyword));
              setNotes(await api.listNotes(project.id));
            }
          })}
        />
        <NotesPreview notes={notes} />
        <CollectionHistory runs={runs} />
        <section className="panel action-panel">
          <div className="eyebrow">运行分析</div>
          <h2>从数据到判断</h2>
          <button disabled={!summary} onClick={() => guard(async () => {
            if (project) setReport(await api.rankNotes(project.id));
          })}>运行分析</button>
        </section>
        <section className="panel action-panel">
          <div className="eyebrow">生成草稿</div>
          <h2>从判断到内容</h2>
          <button disabled={!report} onClick={() => guard(async () => {
            if (!project || !report) return;
            const topic = await api.createTopic(project.id, {
              title: "敏感肌直播前先做减法",
              target_audience: project.brand_profile.target_audience,
              content_goal: "live_preview",
              angle: "用两步自查降低试错",
              insight_id: report.insight.id
            });
            setDrafts(await api.generateDrafts(topic.id));
          })}>生成三个草稿</button>
        </section>
        <RankingTable report={report} />
        <ContentAttractionInsight insight={report?.attraction_insight} />
        <DraftWorkbench drafts={drafts} />
      </div>
    </main>
  );
}
