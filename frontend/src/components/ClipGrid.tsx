import type { Clip } from '../types/jobs'

const publicBase = import.meta.env.VITE_PUBLIC_BASE_URL ?? 'http://localhost:8000'

type Props = {
  clips: Clip[]
  onRegenerate: (clipId: string) => Promise<void>
  loading: boolean
}

export function ClipGrid({ clips, onRegenerate, loading }: Props) {
  return (
    <section className="grid">
      {clips.map((clip) => (
        <article key={clip.clip_id} className="card">
          <video controls preload="metadata" src={clip.file_path ? `${publicBase}${clip.file_path}` : undefined} />
          <div className="card-body">
            <div className="row row-spread">
              <h3>{clip.title}</h3>
              <span>{Math.round(clip.duration_seconds)}s</span>
            </div>
            <p>{clip.summary}</p>
            <small>{clip.transcript_excerpt}</small>
            <div className="row">
              <button onClick={() => onRegenerate(clip.clip_id)} disabled={loading}>Regenerate</button>
              <a href={clip.file_path ? `${publicBase}${clip.file_path}` : '#'} download>Download</a>
            </div>
          </div>
        </article>
      ))}
    </section>
  )
}
