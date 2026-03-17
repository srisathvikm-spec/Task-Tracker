import React, { useEffect, useState } from 'react';
import {
  Table,
  Typography,
  Select,
  Tag,
  message,
  Space,
  Badge,
  Button,
  Modal,
  Form,
  Input,
  Popconfirm,
  Tooltip,
  Switch,
  Alert,
} from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import apiClient from '../api/apiClient';
import { useAuth } from '../hooks/useAuth';
import type { User, Role } from '../types/user';

const UsersPage: React.FC = () => {
  const { isAdmin, isManager, isReadOnlyUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [creatingForm] = Form.useForm();
  const [editingForm] = Form.useForm();
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const parseApiError = (err: any, fallback: string) => err?.response?.data?.detail || fallback;

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, rolesRes] = await Promise.all([
        apiClient.get('/users/'),
        apiClient.get('/users/roles/all'),
      ]);
      setUsers(usersRes.data.data ?? []);
      setRoles(rolesRes.data.data ?? rolesRes.data ?? []);
    } catch {
      message.error('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateUser = async () => {
    try {
      const values = await creatingForm.validateFields();
      setSubmitting(true);
      await apiClient.post('/users/', {
        name: values.name,
        email: values.email,
        role_id: values.role_id,
      });
      message.success('User created');
      setCreateOpen(false);
      creatingForm.resetFields();
      fetchData();
    } catch (err: any) {
      message.error(parseApiError(err, 'Failed to create user'));
    } finally {
      setSubmitting(false);
    }
  };

  const openEdit = (user: User) => {
    setEditingUser(user);
    editingForm.setFieldsValue({
      name: user.name,
      email: user.email,
      is_active: user.is_active,
      role_ids: user.roles.map((r) => r.id),
    });
    setEditOpen(true);
  };

  const handleEditUser = async () => {
    if (!editingUser) return;
    try {
      const values = await editingForm.validateFields();
      setSubmitting(true);
      await apiClient.patch(`/users/${editingUser.id}`, {
        name: values.name,
        email: values.email,
        is_active: values.is_active,
        role_ids: values.role_ids,
      });
      message.success('User updated');
      setEditOpen(false);
      setEditingUser(null);
      editingForm.resetFields();
      fetchData();
    } catch (err: any) {
      message.error(parseApiError(err, 'Failed to update user'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    try {
      await apiClient.delete(`/users/${userId}`);
      message.success('User deleted');
      fetchData();
    } catch (err: any) {
      message.error(parseApiError(err, 'Failed to delete user'));
    }
  };

  const handleRemoveRole = async (userId: string, roleId: string) => {
    try {
      await apiClient.delete(`/users/${userId}/role/${roleId}`);
      message.success('Role removed');
      fetchData();
    } catch (err: any) {
      message.error(parseApiError(err, 'Failed to remove role'));
    }
  };

  const columns = [
    {
      title: 'User Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Typography.Text strong style={{ color: 'var(--text-main)' }}>{text}</Typography.Text>,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (text: string) => <Typography.Text style={{ color: 'var(--text-dim)' }}>{text}</Typography.Text>,
    },
    {
      title: 'Roles',
      key: 'roles',
      render: (_: unknown, record: User) => (
        <Space size={[0, 6]} wrap>
          {record.roles.map((role) => (
            <Tooltip key={role.id} title={(isManager && !isReadOnlyUser) ? (record.roles.length <= 1 ? 'User must have at least one role' : 'Click x to remove role') : 'View only'}>
              <Tag
                color="processing"
                bordered={false}
                closable={isManager && !isReadOnlyUser && record.roles.length > 1}
                onClose={(e) => {
                  e.preventDefault();
                  handleRemoveRole(record.id, role.id);
                }}
              >
                {role.name.toUpperCase()}
              </Tag>
            </Tooltip>
          ))}
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Badge status={isActive ? 'success' : 'error'} text={isActive ? 'Active' : 'Disabled'} />
      ),
    },
    ...(isManager && !isReadOnlyUser ? [
      {
        title: 'Edit',
        key: 'edit',
        render: (_: unknown, record: User) => (
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(record)} />
        ),
      },
    ] : []),
    ...(isAdmin ? [
      {
        title: 'Delete',
        key: 'delete',
        render: (_: unknown, record: User) => (
          <Popconfirm title="Delete this user?" onConfirm={() => handleDeleteUser(record.id)}>
            <Button danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        ),
      },
    ] : []),
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {isReadOnlyUser && (
        <Alert
          message="View Only Access"
          description="You have read-only access to the Users page. You can view user information but cannot make changes."
          type="info"
          showIcon
        />
      )}

      <section className="page-hero">
        <div>
          <h2 className="page-title">Users</h2>
          <div className="page-meta">Govern permissions, assign roles, and maintain secure access.</div>
        </div>
        {(isManager && !isReadOnlyUser) && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              creatingForm.resetFields();
              setCreateOpen(true);
            }}
          >
            Create User
          </Button>
        )}
      </section>

      <section className="glass-card panel" style={{ paddingTop: 10 }}>
        <Table rowKey="id" dataSource={users} columns={columns} loading={loading} pagination={{ pageSize: 10 }} />
      </section>

      <Modal
        title="Create User"
        open={createOpen}
        onOk={handleCreateUser}
        okText="Create"
        okButtonProps={{ loading: submitting }}
        onCancel={() => {
          setCreateOpen(false);
          creatingForm.resetFields();
        }}
      >
        <Form form={creatingForm} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Name is required' }]}>
            <Input placeholder="Enter name" disabled={isReadOnlyUser} />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Email is required' }, { type: 'email', message: 'Enter a valid email' }]}>
            <Input placeholder="Enter email" disabled={isReadOnlyUser} />
          </Form.Item>
          <Form.Item name="role_id" label="Role" rules={[{ required: true, message: 'Role is required' }]}>
            <Select
              placeholder="Select role"
              disabled={isReadOnlyUser}
              options={roles.map((role) => ({ label: role.name, value: role.id }))}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Edit User"
        open={editOpen}
        onOk={handleEditUser}
        okText="Update"
        okButtonProps={{ loading: submitting, disabled: isReadOnlyUser }}
        onCancel={() => {
          setEditOpen(false);
          setEditingUser(null);
          editingForm.resetFields();
        }}
      >
        <Form form={editingForm} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Name is required' }]}>
            <Input placeholder="Enter name" disabled={isReadOnlyUser} />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Email is required' }, { type: 'email', message: 'Enter a valid email' }]}>
            <Input placeholder="Enter email" disabled={isReadOnlyUser} />
          </Form.Item>
          <Form.Item name="is_active" label="Status" valuePropName="checked">
            <Switch checkedChildren="Active" unCheckedChildren="Disabled" disabled={isReadOnlyUser} />
          </Form.Item>
          <Form.Item
            name="role_ids"
            label="Roles"
            rules={[{ required: true, message: 'At least one role is required' }]}
          >
            <Select
              mode="multiple"
              placeholder="Select roles"
              disabled={isReadOnlyUser}
              options={roles.map((role) => ({ label: role.name, value: role.id }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersPage;
