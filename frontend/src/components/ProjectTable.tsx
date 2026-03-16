import React from 'react';
import { Table, Button, Popconfirm, Space, Typography } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import type { Project } from '../types/project';

interface Props {
  projects: Project[];
  loading: boolean;
  canEdit: boolean;
  canDelete: boolean;
  onEdit: (project: Project) => void;
  onDelete: (id: string) => void;
}

const ProjectTable: React.FC<Props> = ({ projects, loading, canEdit, canDelete, onEdit, onDelete }) => {
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: Project, b: Project) => a.name.localeCompare(b.name),
      render: (name: string) => <Typography.Text strong style={{ color: 'var(--text-main)' }}>{name}</Typography.Text>,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (description: string) => <span style={{ color: 'var(--text-dim)' }}>{description || '-'}</span>,
    },
    { title: 'Start Date', dataIndex: 'start_date', key: 'start_date' },
    { title: 'End Date', dataIndex: 'end_date', key: 'end_date' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: Project) => {
        if (!canEdit && !canDelete) return null;
        return (
          <Space>
            {canEdit && <Button icon={<EditOutlined />} size="small" onClick={() => onEdit(record)} />}
            {canDelete && (
              <Popconfirm title="Delete this project?" onConfirm={() => onDelete(record.id)}>
                <Button icon={<DeleteOutlined />} size="small" danger />
              </Popconfirm>
            )}
          </Space>
        );
      },
    },
  ];

  return <Table rowKey="id" dataSource={projects} columns={columns} loading={loading} pagination={{ pageSize: 10 }} />;
};

export default ProjectTable;
