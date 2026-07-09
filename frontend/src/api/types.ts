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
export type Score = {
  total: number;
  engagement: number;
  velocity: number;
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
  importFixture(projectId: string): Promise<CollectionSummary>;
  rankNotes(projectId: string): Promise<RankingReport>;
  createTopic(projectId: string, input: Record<string, string>): Promise<Topic>;
  generateDrafts(topicId: string): Promise<Draft[]>;
}

