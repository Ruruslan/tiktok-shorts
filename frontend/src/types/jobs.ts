export type Clip = {
  clip_id: string
  title: string
  summary: string
  start_seconds: number
  end_seconds: number
  duration_seconds: number
  transcript_excerpt: string
  file_path?: string | null
  subtitles_path?: string | null
}

export type Job = {
  job_id: string
  source_url: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  error?: string | null
  clips: Clip[]
}
