import React, { useEffect, useMemo, useState } from 'react';
import { Typography, List, Tag, Progress } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import apiClient from '../api/apiClient';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState({ projects: 0, tasks: 0, completed: 0 });
  const [recentTasks, setRecentTasks] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projRes, taskRes, compRes, recentRes] = await Promise.all([
          apiClient.get('/projects/?limit=1'),
          apiClient.get('/tasks/?limit=1'),
          apiClient.get('/tasks/?status=completed&limit=1'),
          apiClient.get('/tasks/?limit=5&sort_by=created_at&sort_order=desc'),
        ]);

        setStats({
          projects: projRes.data.meta?.total ?? 0,
          tasks: taskRes.data.meta?.total ?? 0,
          completed: compRes.data.meta?.total ?? 0,
        });
        setRecentTasks(recentRes.data.data ?? []);
      } catch {
        setStats({ projects: 0, tasks: 0, completed: 0 });
      }
    };

    fetchData();
  }, []);

  const completionRate = useMemo(
    () => (stats.tasks > 0 ? Math.round((stats.completed / stats.tasks) * 100) : 0),
    [stats.completed, stats.tasks],
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <section className="page-hero">
        <div>
          <h2 className="page-title">Overview</h2>
          <div className="page-meta">Real-time insight into delivery, throughput, and completion.</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="accent-dot" />
          <Typography.Text style={{ color: 'var(--text-main)', fontWeight: 600 }}>Live Analytics</Typography.Text>
        </div>
      </section>

      <section className="stat-grid">
        <article className="stat-card">
          <div className="stat-label">Active Projects</div>
          <div className="stat-value">{stats.projects}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Total Tasks</div>
          <div className="stat-value">{stats.tasks}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value">{stats.completed}</div>
        </article>
      </section>

      <section className="dual-grid">
        <div className="glass-card panel">
          <Typography.Title level={4} style={{ marginTop: 0, color: '#fff' }}>Recent Activity</Typography.Title>
          <List
            dataSource={recentTasks}
            locale={{ emptyText: <span style={{ color: 'var(--text-dim)' }}>No recent activity</span> }}
            renderItem={(item: any) => (
              <List.Item style={{ borderBottom: '1px solid var(--line-soft)' }}>
                <List.Item.Meta
                  title={<span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{item.title}</span>}
                  description={
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 6 }}>
                      <Tag color={item.status === 'completed' ? 'success' : 'processing'}>
                        {item.status.replace('_', ' ').toUpperCase()}
                      </Tag>
                      <span style={{ color: 'var(--text-dim)', fontSize: 12 }}>
                        <ClockCircleOutlined style={{ marginRight: 5 }} />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </div>

        <div className="glass-card panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
          <Typography.Title level={4} style={{ color: '#fff', marginTop: 0 }}>Execution Score</Typography.Title>
          <Progress
            type="dashboard"
            percent={completionRate}
            strokeColor={{ '0%': '#56c8ff', '100%': '#ffc272' }}
            trailColor="rgba(255,255,255,0.12)"
            size={210}
          />
          <Typography.Text style={{ color: 'var(--text-dim)', marginTop: 8 }}>
            {stats.completed} of {stats.tasks} tasks completed
          </Typography.Text>
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
