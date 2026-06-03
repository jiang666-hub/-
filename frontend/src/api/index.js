import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export function sendMessage(message, history = [], category = null) {
  const body = { message, history }
  if (category) body.category = category
  return api.post('/chat', body)
}

export function searchBooks(query, topK = 5) {
  return api.post('/search', { query, top_k: topK })
}

export function getBooks(category = null, page = 1) {
  const params = { page, size: 20 }
  if (category) params.category = category
  return api.get('/books', { params })
}

export function getBookDetail(bookId) {
  return api.get(`/books/${bookId}`)
}

export function getCategories() {
  return api.get('/categories')
}
