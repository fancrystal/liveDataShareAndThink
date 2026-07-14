import type { Note } from "../api/types";

export function NotesPreview({ notes }: { notes: Note[] }) {
  if (!notes.length) return null;

  return (
    <section className="panel notes-preview">
      <div className="eyebrow">采集结果</div>
      <h2>已导入笔记</h2>
      {notes.slice(0, 10).map((note) => {
        const latest = note.metric_snapshots.at(-1);
        return (
          <article key={note.id} className="note-card">
            <a href={note.url} target="_blank" rel="noreferrer">{note.title}</a>
            <p>{note.author.nickname} · {note.source.adapter}</p>
            <small>赞 {latest?.likes ?? "—"} · 收藏 {latest?.favorites ?? "—"}</small>
          </article>
        );
      })}
    </section>
  );
}
