export type ProjectCreate = {
  name: string;
  description: string;
  brand_profile: {
    name: string;
    positioning: string;
    target_audience: string;
    tone: string;
    core_value: string;
    forbidden_terms: string[];
  };
};

export type Project = ProjectCreate & { id: string };
export type CollectionSummary = {
  run_id: string;
  status: string;
  notes_created: number;
  metric_snapshots_created: number;
};
export type CollectionRun = {
  id: string;
  adapter: string;
  query: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  notes_created: number;
  metric_snapshots_created: number;
};
export type VerticalResearch = {
  topic: string;
  run_id: string;
  collection_date: string;
  top_candidates: { title: string; url: string; score: number }[];
  ai_report: { today_summary: string; hot_reasons: string[]; replication_checklist: string[]; disclosure: string };
};
export type PostPackage = { title: string; caption: string; tags: string[]; pages: { heading: string; body: string }[] };
export type MetricSnapshot = {
  id: string;
  collected_at: string;
  likes: number | null;
  favorites: number | null;
  comments: number | null;
  shares: number | null;
  followers: number | null;
};
export type Note = {
  id: string;
  title: string;
  url: string;
  content: string;
  content_type: string;
  published_at: string | null;
  source: { adapter: string };
  author: { id: string; nickname: string; followers: number | null };
  metric_snapshots: MetricSnapshot[];
};
export type Score = {
  total: number;
  engagement: number;
  velocity: number | null;
  cohort_relative: number;
  author_efficiency: number | null;
  confidence: string;
  explanation: Record<string, unknown>;
};
export type RankingReport = {
  rankings: { note_id: string; title: string; url: string; score: Score }[];
  insight: {
    id: string;
    title: string;
    summary: string;
    confidence: string;
    evidence: { id: string; summary: string }[];
  };
  attraction_insight: {
    id: string;
    title: string;
    summary: string;
    confidence: string;
    result: { hook_patterns: Record<string, number>; format_counts: Record<string, number>; reusable_angles: string[] };
    evidence: { id: string; summary: string }[];
  };
};
export type Topic = { id: string };
export type Draft = {
  id: string;
  variant: string;
  status: string;
  evidence_ids: string[];
  current_version: {
    id: string;
    title: string;
    body: string;
    tags: string[];
    cover_text: string;
  };
};

export interface Api {
  createProject(input: ProjectCreate): Promise<Project>;
  listProjects(): Promise<Project[]>;
  importFixture(projectId: string): Promise<CollectionSummary>;
  importXiaohongshu(projectId: string, keyword: string): Promise<CollectionSummary>;
  listNotes(projectId: string): Promise<Note[]>;
  listCollectionRuns(projectId: string): Promise<CollectionRun[]>;
  rankNotes(projectId: string): Promise<RankingReport>;
  createTopic(projectId: string, input: Record<string, string>): Promise<Topic>;
  generateDrafts(topicId: string): Promise<Draft[]>;
  runVerticalResearch(projectId: string, topic: string): Promise<VerticalResearch>;
  createPostPackage(projectId: string, topic: string, angle: string, runId: string): Promise<PostPackage>;
}
