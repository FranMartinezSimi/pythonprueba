import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth
export const login = (email: string) => {
  return apiClient.post('/login/', { email })
}

// Tasks
export const getTasks = (userId: number) => {
  return apiClient.get(`/tasks/?user_id=${userId}`)
}

export const createTask = (task: {
  user: number
  title: string
  description: string
  status: string
  category: string
}) => {
  return apiClient.post('/tasks/', task)
}

export const deleteTask = (taskId: number) => {
  return apiClient.delete(`/tasks/${taskId}/`)
}

// SubTasks (creadas por IA en el backend)
export const updateSubTask = (subtaskId: number, data: {
  title?: string
  is_completed?: boolean
}) => {
  return apiClient.patch(`/subtasks/${subtaskId}/`, data)
}

export const deleteSubTask = (subtaskId: number) => {
  return apiClient.delete(`/subtasks/${subtaskId}/`)
}
