import { useMutation, useQuery } from '@tanstack/react-query'

import { api } from '../api/client'
import type { Job } from '../types/jobs'

export function useCreateJob() {
  return useMutation({
    mutationFn: async (youtubeUrl: string) => {
      const response = await api.post<Job>('/jobs', { youtube_url: youtubeUrl })
      return response.data
    },
  })
}

export function useJob(jobId?: string) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: async () => {
      const response = await api.get<Job>(`/jobs/${jobId}`)
      return response.data
    },
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status && ['completed', 'failed'].includes(status) ? false : 3000
    },
  })
}

export function useRegenerateClip(jobId?: string) {
  return useMutation({
    mutationFn: async (clipId: string) => {
      const response = await api.post<Job>(`/jobs/${jobId}/regenerate`, { clip_id: clipId })
      return response.data
    },
  })
}
