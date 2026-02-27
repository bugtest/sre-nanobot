import { defineConfig } from 'umi';

export default defineConfig({
  title: 'SRE-NanoBot 智能运维平台',
  favicon: '/favicon.ico',
  logo: '/logo.svg',
  
  // 路由配置
  routes: [
    {
      path: '/',
      component: '@/layouts/BasicLayout',
      routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/dashboard', name: 'Dashboard', icon: 'Dashboard', component: '@/pages/Dashboard' },
        { path: '/alerts', name: '告警中心', icon: 'Alert', component: '@/pages/Alerts' },
        { path: '/incidents', name: '故障管理', icon: 'Bug', component: '@/pages/Incidents' },
        { path: '/runbooks', name: '预案管理', icon: 'FileText', component: '@/pages/Runbooks' },
        { path: '/metrics', name: '监控指标', icon: 'LineChart', component: '@/pages/Metrics' },
        { path: '/skills', name: 'Skills', icon: 'Thunderbolt', component: '@/pages/Skills' },
        { path: '/settings', name: '系统设置', icon: 'Setting', component: '@/pages/Settings' },
      ],
    },
  ],
  
  // npm 包配置
  npmClient: 'npm',
  
  // 代理配置
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
  
  // 插件配置
  plugins: [
    '@umijs/plugins/dist/antd',
    '@umijs/plugins/dist/model',
    '@umijs/plugins/dist/initial-state',
  ],
  
  antd: {},
  model: {},
  initialState: {},
  
  // 构建配置
  hash: true,
  publicPath: '/',
  
  // 开发配置
  devtool: 'source-map',
  
  // 主题配置
  theme: {
    'primary-color': '#1890ff',
    'border-radius-base': '4px',
  },
});
