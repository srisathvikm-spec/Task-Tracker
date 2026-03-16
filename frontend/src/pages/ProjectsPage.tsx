import React, { useEffect, useState } from 'react';
import { Button, Modal, Form, Input, DatePicker, message, Row, Col } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import ProjectTable from '../components/ProjectTable';
import apiClient from '../api/apiClient';
import { useAuth } from '../hooks/useAuth';
import type { Project } from '../types/project';
import dayjs from 'dayjs';

const ProjectsPage: React.FC = () => {
  const { isManager, isAdmin } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [form] = Form.useForm();
  const [search, setSearch] = useState('');

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (search) params.name = search;
      const { data } = await apiClient.get('/projects/', { params });
      setProjects(data.data ?? []);
    } catch {
      message.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [search]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (project: Project) => {
    setEditing(project);
    form.setFieldsValue({
      ...project,
      start_date: project.start_date ? dayjs(project.start_date) : undefined,
      end_date: project.end_date ? dayjs(project.end_date) : undefined,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        start_date: values.start_date?.format('YYYY-MM-DD'),
        end_date: values.end_date?.format('YYYY-MM-DD'),
      };

      if (editing) {
        await apiClient.put(`/projects/${editing.id}`, payload);
        message.success('Project updated');
      } else {
        await apiClient.post('/projects/', payload);
        message.success('Project created');
      }
      setModalOpen(false);
      fetchProjects();
    } catch {
      message.error('Unable to save project');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/projects/${id}`);
      message.success('Project deleted');
      fetchProjects();
    } catch {
      message.error('Delete operation failed');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <section className="page-hero">
        <div>
          <h2 className="page-title">Projects</h2>
          <div className="page-meta">Portfolio planning and lifecycle management in one place.</div>
        </div>
        {isManager && (
          <Button type="primary" icon={<PlusOutlined />} size="large" onClick={openCreate}>
            New Project
          </Button>
        )}
      </section>

      <section className="glass-card panel">
        <Row gutter={14}>
          <Col xs={24} md={10}>
            <Input
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by project name"
              allowClear
            />
          </Col>
        </Row>
      </section>

      <section className="glass-card panel" style={{ paddingTop: 10 }}>
        <ProjectTable
          projects={projects}
          loading={loading}
          canEdit={isManager}
          canDelete={isAdmin}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      </section>

      <Modal
        title={editing ? 'Update Project' : 'Create Project'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="name" label="Project Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} />
          </Form.Item>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="start_date" label="Start Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="end_date" label="End Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectsPage;
