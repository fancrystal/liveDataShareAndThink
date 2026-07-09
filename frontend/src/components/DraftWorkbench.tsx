import type { Draft } from "../api/types";

export function DraftWorkbench({ drafts }: { drafts: Draft[] }) {
  if (!drafts.length) return null;
  return (
    <section className="panel span-two">
      <div className="eyebrow">04 · 生成内容</div>
      <h2>三个原创角度</h2>
      <div className="draft-grid">
        {drafts.map((draft) => (
          <article className="draft" key={draft.id}>
            <span>{draft.variant}</span>
            <h3>{draft.current_version.title}</h3>
            <p>{draft.current_version.body}</p>
            <div className="tags">{draft.current_version.tags.map((tag) => <em key={tag}>#{tag}</em>)}</div>
          </article>
        ))}
      </div>
    </section>
  );
}

