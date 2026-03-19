import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { UrlForm } from './components/UrlForm'
import { ProgressCard } from './components/ProgressCard'
import { ClipGrid } from './components/ClipGrid'
import { useCreateJob, useJob, useRegenerateClip } from './hooks/useJob'
import './styles.css'

const queryClient = new QueryClient()

function App() {
  const [jobId, setJobId] = React.useState<string | undefined>()
  const createJob = useCreateJob()
  const jobQuery = useJob(jobId)
  const regenerate = useRegenerateClip(jobId)

  const handleSubmit = async (url: string) => {
    const job = await createJob.mutateAsync(url)
    setJobId(job.job_id)
  }

  const handleRegenerate = async (clipId: string) => {
    await regenerate.mutateAsync(clipId)
    await jobQuery.refetch()
  }

  return (
    <main className="app-shell">
      <header>
        <p className="eyebrow">AI short-form repurposing</p>
        <h1>TikTok Shorts Studio</h1>
        <p className="lede">Paste a YouTube URL to generate exactly 10 polished vertical clips with subtitles, semantic boundaries, and per-clip regeneration.</p>
      </header>

      <UrlForm onSubmit={handleSubmit} loading={createJob.isPending} />
      {jobQuery.data ? <ProgressCard job={jobQuery.data} /> : null}
      {jobQuery.data?.clips.length ? <ClipGrid clips={jobQuery.data.clips} onRegenerate={handleRegenerate} loading={regenerate.isPending} /> : null}
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
