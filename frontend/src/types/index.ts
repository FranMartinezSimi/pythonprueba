export interface User {
  id: number
  email: string
  username: string
}

export interface SubTask {
  id?: number
  task?: number
  title: string
  is_completed: boolean
  created_at?: string
  updated_at?: string
}

export interface Task {
  id?: number
  user: number
  title: string
  description: string
  status: 'pending' | 'is_completed'
  category: 'work' | 'personal' | 'urgent'
  created_at?: string
  updated_at?: string
  subtasks?: SubTask[]
  subtasks_count?: number
  completed_subtasks_count?: number
}

export interface LoginResponse {
  id: number
  email: string
  username: string
}
