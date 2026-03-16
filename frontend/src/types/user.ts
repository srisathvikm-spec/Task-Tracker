/**
 * Core types – User
 */

export interface Role {
  id: string;
  name: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  roles: Role[];
  avatar?: string;
}
