import React from 'react';
import { Table, Button, Popconfirm, Space, Tag, Select } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import type { Task, TaskStatus } from '../types/task';

const STATUS_STYLES: Record<TaskStatus, { color: string; bg: string }> = {
  new: { color: '#56c8ff', bg: 'rgba(86, 200, 255, 0.18)' },
  not_started: { color: '#aebddd', bg: 'rgba(174, 189, 221, 0.18)' },
  in_progress: { color: '#ffc272', bg: 'rgba(255, 194, 114, 0.2)' },
  blocked: { color: '#ff7a88', bg: 'rgba(255, 122, 136, 0.2)' },
  completed: { color: '#59d39b', bg: 'rgba(89, 211, 155, 0.2)' },
};

interface Props {
  tasks: Task[];
  loading: boolean;
  canEdit: boolean;
  canDelete: boolean;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onStatusChange: (id: string, status: string) => void;
  onViewDetail: (id: string) => void;
}

const TaskTable: React.FC<Props> = ({ tasks, loading, canEdit, canDelete, onEdit, onDelete, onStatusChange, onViewDetail }) => {
  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      sorter: (a: Task, b: Task) => a.title.localeCompare(b.title),
      render: (title: string, record: Task) => (
        <button
          type="button"
          onClick={() => onViewDetail(record.id)}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-main)',
            fontSize: 15,
            fontWeight: 700,
            cursor: 'pointer',
            padding: 0,
          }}
        >
          {title}
        </button>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: TaskStatus) => (
        <Tag
          bordered={false}
          style={{
            color: STATUS_STYLES[status].color,
            backgroundColor: STATUS_STYLES[status].bg,
            borderRadius: 999,
            fontWeight: 700,
            paddingInline: 10,
          }}
        >
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Due Date',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (dueDate: string) => (dueDate ? new Date(dueDate).toLocaleDateString() : '-'),
    },
    {
      title: 'Change Status',
      key: 'change_status',
      render: (_: unknown, record: Task) => (
        <Select
          size="small"
          value={record.status}
          style={{ width: 150 }}
          onChange={(value) => onStatusChange(record.id, value)}
          options={['new', 'not_started', 'in_progress', 'blocked', 'completed'].map((status) => ({
            label: status.replace('_', ' '),
            value: status,
          }))}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: Task) => {
        if (!canEdit && !canDelete) return null;
        return (
          <Space>
            {canEdit && <Button icon={<EditOutlined />} size="small" onClick={() => onEdit(record)} />}
            {canDelete && (
              <Popconfirm title="Delete this task?" onConfirm={() => onDelete(record.id)}>
                <Button icon={<DeleteOutlined />} size="small" danger />
              </Popconfirm>
            )}
          </Space>
        );
      },
    },
  ];

  return <Table rowKey="id" dataSource={tasks} columns={columns} loading={loading} pagination={{ pageSize: 10 }} />;
};

export default TaskTable;
