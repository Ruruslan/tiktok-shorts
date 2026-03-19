import { FormEvent, useState } from 'react'

type Props = {
  onSubmit: (url: string) => Promise<void>
  loading: boolean
}

export function UrlForm({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!/^https:\/\/(www\.)?(youtube\.com|youtu\.be)\/.+/.test(url)) {
      setError('Enter a valid HTTPS YouTube URL.')
      return
    }
    setError('')
    await onSubmit(url)
  }

  return (
    <form className="panel" onSubmit={submit}>
      <label htmlFor="youtube-url">YouTube video URL</label>
      <div className="row">
        <input id="youtube-url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://www.youtube.com/watch?v=..." />
        <button type="submit" disabled={loading}>{loading ? 'Processing…' : 'Generate 10 clips'}</button>
      </div>
      {error ? <p className="error">{error}</p> : <p className="hint">Supports long-form YouTube videos up to the configured duration limit.</p>}
    </form>
  )
}
