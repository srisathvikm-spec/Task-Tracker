import React, { useState } from 'react';
import { Button, Typography, Divider, message } from 'antd';
import { LoginOutlined } from '@ant-design/icons';
import { useMsal } from '@azure/msal-react';
import { Navigate } from 'react-router-dom';
import { loginRequest } from '../auth/authProvider';
import { useAuth } from '../hooks/useAuth';

const LoginPage: React.FC = () => {
  const { instance } = useMsal();
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogin = async () => {
    setLoading(true);
    try {
      await instance.loginRedirect(loginRequest);
    } catch (err: any) {
      message.error(`Sign-in failed: ${err?.message ?? 'Unknown error'}`);
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <div className="login-panel">
        <Typography.Text className="dock-kicker">Secure Enterprise Access</Typography.Text>
        <Typography.Title
          level={1}
          style={{ margin: '10px 0 4px', color: '#fff', fontSize: 56, lineHeight: 0.95 }}
        >
          T Tracker
        </Typography.Title>
        <Typography.Text style={{ color: 'var(--text-dim)', fontSize: 16 }}>
          A premium workspace for high-velocity project delivery.
        </Typography.Text>

        <Divider style={{ borderColor: 'var(--line)', margin: '22px 0' }} />

        <Button
          type="primary"
          size="large"
          block
          icon={<LoginOutlined />}
          loading={loading}
          onClick={handleLogin}
        >
          Continue with Microsoft
        </Button>

        <div style={{ marginTop: 18, color: 'var(--text-dim)', fontSize: 13 }}>
          Use your organization account to continue.
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
