import type { Project } from "../api/types";

export function ProjectPicker({ projects, onOpen }: { projects: Project[]; onOpen: (project: Project) => Promise<void> }) {
  if (!projects.length) return null;
  return <section className="panel"><div className="eyebrow">已有项目</div><h2>继续研究</h2>{projects.map((project) => <button key={project.id} onClick={() => void onOpen(project)}>打开：{project.name}</button>)}</section>;
}
