import React, { useEffect, useState } from 'react';
import {
  Drawer,
  Typography,
  Tag,
  Space,
  List,
  Avatar,
  Input,
  Button,
  Timeline,
  Tabs,
  message,
} from 'antd';
import {
  SendOutlined,
  HistoryOutlined,
  CommentOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import apiClient from '../api/apiClient';
import type { Task, TaskStatus } from '../types/task';

const { TextArea } = Input;

interface Props {
  taskId: string | null;
  onClose: () => void;
}

const STATUS_COLORS: Record<TaskStatus, string> = {
  new: 'blue',
  not_started: 'default',
  in_progress: 'processing',
  blocked: 'error',
  completed: 'success',
};

const TaskDetailDrawer: React.FC<Props> = ({ taskId, onClose }) => {
  const [task, setTask] = useState<Task | null>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    if (!taskId) return;
    setLoading(true);
    try {
      const [taskRes, commentRes, activityRes] = await Promise.all([
        apiClient.get(`/tasks/${taskId}`),
        apiClient.get(`/tasks/${taskId}/comments`),
        apiClient.get(`/tasks/${taskId}/activity`),
      ]);
      setTask(taskRes.data.data);
      setComments(commentRes.data.data ?? []);
      setActivity(activityRes.data.data ?? []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [taskId]);

  const handleAddComment = async () => {
    if (!newComment.trim() || !taskId) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/tasks/${taskId}/comments`, { content: newComment });
      setNewComment('');
      const { data } = await apiClient.get(`/tasks/${taskId}/comments`);
      setComments(data.data ?? []);
      message.success('Comment posted');
    } catch {
      message.error('Failed to post comment');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Drawer
      title={
        <Space>
          <Typography.Title level={4} style={{ margin: 0 }}>Task Detail</Typography.Title>
          {task ? <Tag color={STATUS_COLORS[task.status]}>{task.status.replace('_', ' ').toUpperCase()}</Tag> : null}
        </Space>
      }
      width={560}
      onClose={onClose}
      open={!!taskId}
    >
      {loading ? (
        <div style={{ padding: '30px 0' }}>Loading details...</div>
      ) : task ? (
        <div>
          <Typography.Title level={3} style={{ marginTop: 0 }}>{task.title}</Typography.Title>
          <Typography.Paragraph style={{ color: 'var(--text-dim)' }}>
            {task.description || 'No description provided.'}
          </Typography.Paragraph>

          <Space size={30} wrap style={{ marginBottom: 20 }}>
            <div>
              <Typography.Text type="secondary" style={{ display: 'block' }}>Due Date</Typography.Text>
              <Typography.Text><CalendarOutlined /> {task.due_date || 'N/A'}</Typography.Text>
            </div>
            <div>
              <Typography.Text type="secondary" style={{ display: 'block' }}>Created At</Typography.Text>
              <Typography.Text><ClockCircleOutlined /> {new Date(task.created_at).toLocaleDateString()}</Typography.Text>
            </div>
          </Space>

          <Tabs
            defaultActiveKey="comments"
            items={[
              {
                key: 'comments',
                label: (
                  <span>
                    <CommentOutlined /> Comments
                  </span>
                ),
                children: (
                  <>
                    <List
                      dataSource={comments}
                      locale={{ emptyText: 'No comments yet.' }}
                      renderItem={(item) => (
                        <List.Item style={{ borderBottom: '1px solid var(--line-soft)' }}>
                          <List.Item.Meta
                            avatar={<Avatar>{item.author_id ? 'U' : 'A'}</Avatar>}
                            title={<Typography.Text strong>User {item.author_id?.slice(0, 4) || 'Anon'}</Typography.Text>}
                            description={
                              <>
                                <div style={{ marginTop: 4 }}>{item.content}</div>
                                <Typography.Text style={{ fontSize: 12, color: 'var(--text-dim)' }}>
                                  {new Date(item.created_at).toLocaleString()}
                                </Typography.Text>
                              </>
                            }
                          />
                        </List.Item>
                      )}
                    />
                    <div style={{ marginTop: 14 }}>
                      <TextArea
                        rows={3}
                        placeholder="Write a comment"
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                      />
                      <Button
                        type="primary"
                        icon={<SendOutlined />}
                        style={{ marginTop: 10 }}
                        onClick={handleAddComment}
                        loading={submitting}
                      >
                        Post Comment
                      </Button>
                    </div>
                  </>
                ),
              },
              {
                key: 'activity',
                label: (
                  <span>
                    <HistoryOutlined /> Activity
                  </span>
                ),
                children: (
                  <Timeline
                    items={activity.map((item) => ({
                      children: (
                        <div>
                          <Typography.Text strong>{item.action}</Typography.Text>
                          <div style={{ color: 'var(--text-dim)', marginTop: 4 }}>{item.details}</div>
                          <Typography.Text style={{ color: 'var(--text-dim)', fontSize: 12 }}>
                            {new Date(item.created_at).toLocaleString()}
                          </Typography.Text>
                        </div>
                      ),
                    }))}
                  />
                ),
              },
            ]}
          />
        </div>
      ) : (
        <div>Select a task to view details</div>
      )}
    </Drawer>
  );
};

export default TaskDetailDrawer;
