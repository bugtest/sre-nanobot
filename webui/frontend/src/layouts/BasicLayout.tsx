import React from 'react';
import { ProLayout } from '@ant-design/pro-layout';
import { Outlet } from 'umi';

const BasicLayout: React.FC = () => {
  return (
    <ProLayout
      title="SRE-NanoBot"
      logo="/logo.svg"
      layout="mix"
      fixSiderbar
      fixHeader
      headerTheme="light"
      navTheme="light"
      contentWidth="Fluid"
      route={{
        path: '/',
        routes: [
          {
            path: '/dashboard',
            name: 'Dashboard',
            icon: 'Dashboard',
          },
          {
            path: '/alerts',
            name: '告警中心',
            icon: 'Alert',
          },
          {
            path: '/incidents',
            name: '故障管理',
            icon: 'Bug',
          },
          {
            path: '/runbooks',
            name: '预案管理',
            icon: 'FileText',
          },
          {
            path: '/metrics',
            name: '监控指标',
            icon: 'LineChart',
          },
          {
            path: '/settings',
            name: '系统设置',
            icon: 'Setting',
          },
        ],
      }}
      location={{
        pathname: window.location.pathname,
      }}
      menuItemRender={(item, dom) => <a href={item.path}>{dom}</a>}
      footerRender={() => (
        <div style={{ textAlign: 'center', padding: '16px', color: '#999' }}>
          SRE-NanoBot v1.0.0 | © 2026
        </div>
      )}
    >
      <Outlet />
    </ProLayout>
  );
};

export default BasicLayout;
