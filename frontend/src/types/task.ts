/**
 * Core types – Task
 */

export type TaskStatus = 'new' | 'not_started' | 'in_progress' | 'blocked' | 'completed';

export interface UserSummary {
  id: string;
  name: string;
  email: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  due_date?: string;
  owner_id?: string;
  project_id: string;
  assigned_to?: UserSummary;
  created_at: string;
  updated_at?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
  project_id: string;
  assigned_to?: string;
}
