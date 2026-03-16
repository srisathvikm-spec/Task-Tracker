import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography } from 'antd';
import {
  DashboardOutlined,
  ProjectOutlined,
  CheckSquareOutlined,
  TeamOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const { Header, Content } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { user, isAdmin, logout } = useAuth();

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/projects', icon: <ProjectOutlined />, label: 'Projects' },
    { key: '/tasks', icon: <CheckSquareOutlined />, label: 'Tasks' },
    ...(isAdmin ? [{ key: '/users', icon: <TeamOutlined />, label: 'Users' }] : []),
  ];

  return (
    <Layout className="app-shell" style={{ display: 'flex', flexDirection: 'row' }}>
      <aside className="shell-dock">
        <div className="dock-brand">
          <div className="dock-kicker">Control Center</div>
          <h1 className="dock-title">T Tracker</h1>
          <div className="dock-sub">Plan. Track. Deliver.</div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </aside>

      <section className="shell-main">
        <Header className="shell-topbar">
          <div className="topbar-left">
            <div className="topbar-kicker">Workspace</div>
            <Typography.Title level={3} className="topbar-title">
              Delivery Dashboard
            </Typography.Title>
          </div>

          <div className="topbar-user">
            <div style={{ textAlign: 'right' }}>
              <div className="topbar-kicker">Signed in</div>
              <div style={{ fontWeight: 700, color: '#fff' }}>{user?.name || 'User'}</div>
            </div>
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'logout',
                    icon: <LogoutOutlined />,
                    label: 'Logout',
                    danger: true,
                    onClick: () => {
                      logout();
                      navigate('/login');
                    },
                  },
                ],
              }}
              placement="bottomRight"
            >
              <span style={{ cursor: 'pointer' }}>
                <Avatar
                  size={44}
                  src={user?.avatar}
                  style={{
                    background: 'linear-gradient(135deg, #3ebeff, #ffc272)',
                    color: '#0f1a2d',
                    fontWeight: 800,
                  }}
                >
                  {user?.name?.[0]?.toUpperCase()}
                </Avatar>
              </span>
            </Dropdown>
          </div>
        </Header>

        <Content className="content-area">
          <div className="content-stage">
            <Outlet />
          </div>
        </Content>
      </section>
    </Layout>
  );
};

export default MainLayout;
