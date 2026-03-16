import React, { useEffect, useState } from 'react';
import { Button, message, Input, Select, Space, Row, Col } from 'antd';
import { PlusOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import TaskTable from '../components/TaskTable';
import TaskForm from '../components/TaskForm';
import TaskDetailDrawer from '../components/TaskDetailDrawer';
import apiClient from '../api/apiClient';
import { useAuth } from '../hooks/useAuth';
import type { Task, TaskCreate } from '../types/task';
import type { Project } from '../types/project';

const TasksPage: React.FC = () => {
  const { isManager, isAdmin } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [projectFilter, setProjectFilter] = useState<string | undefined>();
  const [sortBy, setSortBy] = useState('created_at');

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params: any = { sort_by: sortBy, sort_order: 'desc' };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (projectFilter) params.project_id = projectFilter;

      const { data } = await apiClient.get('/tasks/', { params });
      setTasks(data.data ?? []);
    } catch {
      message.error('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    const { data } = await apiClient.get('/projects/');
    setProjects(data.data ?? []);
  };

  useEffect(() => {
    fetchTasks();
    fetchProjects();
  }, [statusFilter, projectFilter, sortBy]);

  const handleSubmit = async (values: TaskCreate) => {
    try {
      if (editing) {
        await apiClient.put(`/tasks/${editing.id}`, values);
        message.success('Task updated');
      } else {
        await apiClient.post('/tasks/', values);
        message.success('Task created');
      }
      setModalOpen(false);
      fetchTasks();
    } catch {
      message.error('Unable to save task');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/tasks/${id}`);
      message.success('Task deleted');
      fetchTasks();
    } catch {
      message.error('Delete failed');
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await apiClient.patch(`/tasks/${id}/status`, { status });
      message.success('Status updated');
      fetchTasks();
    } catch {
      message.error('Status update failed');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <section className="page-hero">
        <div>
          <h2 className="page-title">Tasks</h2>
          <div className="page-meta">Execution board for priorities, status, and due timelines.</div>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchTasks}>Refresh</Button>
          {isManager && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); setModalOpen(true); }}>
              New Task
            </Button>
          )}
        </Space>
      </section>

      <section className="glass-card panel">
        <Row gutter={[12, 12]}>
          <Col xs={24} md={8}>
            <Input
              prefix={<SearchOutlined />}
              placeholder="Search tasks"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onPressEnter={fetchTasks}
              allowClear
            />
          </Col>
          <Col xs={12} md={5}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: '100%' }}
              onChange={setStatusFilter}
              options={[
                { label: 'New', value: 'new' },
                { label: 'Not Started', value: 'not_started' },
                { label: 'In Progress', value: 'in_progress' },
                { label: 'Blocked', value: 'blocked' },
                { label: 'Completed', value: 'completed' },
              ]}
            />
          </Col>
          <Col xs={12} md={5}>
            <Select
              placeholder="Project"
              allowClear
              style={{ width: '100%' }}
              onChange={setProjectFilter}
              options={projects.map((p) => ({ label: p.name, value: p.id }))}
            />
          </Col>
          <Col xs={24} md={6}>
            <Select
              value={sortBy}
              style={{ width: '100%' }}
              onChange={setSortBy}
              options={[
                { label: 'Recently Added', value: 'created_at' },
                { label: 'Due Date', value: 'due_date' },
                { label: 'Status', value: 'status' },
              ]}
            />
          </Col>
        </Row>
      </section>

      <section className="glass-card panel" style={{ paddingTop: 10 }}>
        <TaskTable
          tasks={tasks}
          loading={loading}
          canEdit={isManager}
          canDelete={isAdmin}
          onEdit={(task) => { setEditing(task); setModalOpen(true); }}
          onDelete={handleDelete}
          onStatusChange={handleStatusChange}
          onViewDetail={setSelectedTaskId}
        />
      </section>

      <TaskForm
        open={modalOpen}
        task={editing}
        projects={projects}
        onSubmit={handleSubmit}
        onCancel={() => setModalOpen(false)}
      />

      <TaskDetailDrawer taskId={selectedTaskId} onClose={() => setSelectedTaskId(null)} />
    </div>
  );
};

export default TasksPage;
