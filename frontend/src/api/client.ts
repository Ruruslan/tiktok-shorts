import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
const csrfToken = import.meta.env.VITE_CSRF_TOKEN ?? 'change-me-in-production'

export const api = axios.create({
  baseURL: apiBase,
  headers: {
    'X-CSRF-Token': csrfToken,
  },
})
