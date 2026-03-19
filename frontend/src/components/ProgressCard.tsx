import type { Job } from '../types/jobs'

export function ProgressCard({ job }: { job: Job }) {
  return (
    <section className="panel">
      <div className="row row-spread">
        <div>
          <p className="eyebrow">Pipeline status</p>
          <h2>{job.status}</h2>
        </div>
        <strong>{job.progress}%</strong>
      </div>
      <div className="progress"><span style={{ width: `${job.progress}%` }} /></div>
      {job.error ? <p className="error">{job.error}</p> : null}
    </section>
  )
}
