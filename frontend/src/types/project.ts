/**
 * Core types – Project
 */

export interface UserSummary {
  id: string;
  name: string;
  email: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  owner_id: string;
  owner?: UserSummary;
  created_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}
