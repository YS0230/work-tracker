import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Token 管理
let authToken = localStorage.getItem('authToken')

// 設置 token
export const setAuthToken = (token) => {
  authToken = token
  localStorage.setItem('authToken', token)
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
    localStorage.removeItem('authToken')
  }
}

// 清除 token
export const clearAuthToken = () => {
  setAuthToken(null)
}

// 檢查 token 是否存在
export const hasAuthToken = () => {
  return !!authToken
}

// 初始化時設置 token
if (authToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
}

// 請求攔截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const errorCode = error.response?.data?.code
      if (errorCode === 'NO_TOKEN' || errorCode === 'INVALID_TOKEN') {
        clearAuthToken()
        // 觸發登入對話框
        window.dispatchEvent(new CustomEvent('auth-required'))
      }
    }
    return Promise.reject(error)
  }
)

// 類別相關 API
export const categoryApi = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams()
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryString.append(key, params[key])
      }
    })
    const url = queryString.toString() ? `/categories?${queryString.toString()}` : '/categories'
    return api.get(url)
  },
  create: (data) => api.post('/categories', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`)
}

// 任務相關 API
export const taskApi = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams()
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryString.append(key, params[key])
      }
    })
    const url = queryString.toString() ? `/tasks?${queryString.toString()}` : '/tasks'
    return api.get(url)
  },
  getIncomplete: () => api.get('/tasks/incomplete'),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`)
}

// 工作紀錄相關 API
export const workLogApi = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams()
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryString.append(key, params[key])
      }
    })
    const url = queryString.toString() ? `/work-logs?${queryString.toString()}` : '/work-logs'
    return api.get(url)
  },
  create: (data) => api.post('/work-logs', data),
  update: (id, data) => api.put(`/work-logs/${id}`, data),
  delete: (id) => api.delete(`/work-logs/${id}`)
}

// 認證相關 API
export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password })
}

export default api