import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Space, Button, Progress } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  // 获取 Dashboard 数据
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // 30 秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, alertsRes] = await Promise.all([
        axios.get('/api/dashboard/stats'),
        axios.get('/api/alerts?limit=5'),
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data.alerts);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 告警表格列定义
  const alertColumns = [
    {
      title: '告警名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Space>
          {record.severity === 'P0' && <span>🚨</span>}
          {record.severity === 'P1' && <span>⚠️</span>}
          {record.severity === 'P2' && <span>⚡</span>}
          {text}
        </Space>
      ),
    },
    {
      title: '严重级别',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => {
        const colorMap: any = { P0: 'red', P1: 'orange', P2: 'yellow', P3: 'blue' };
        return <Tag color={colorMap[severity]}>{severity}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const config: any = {
          firing: { color: 'red', icon: <SyncOutlined spin /> },
          resolved: { color: 'green', icon: <CheckCircleOutlined /> },
        };
        const { color, icon } = config[status] || {};
        return <Tag color={color}>{icon} {status}</Tag>;
      },
    },
    {
      title: '服务',
      dataIndex: 'service',
      key: 'service',
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="small">
          <Button type="link" size="small">查看</Button>
          {record.status === 'firing' && <Button type="link" size="small">确认</Button>}
        </Space>
      ),
    },
  ];

  // 告警趋势图表配置
  const alertChartOption = {
    title: { text: '告警趋势（最近 7 天）' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '告警数量',
        type: 'line',
        data: stats?.metrics?.alerts?.last_7_days || [5, 8, 3, 12, 7, 9, 5],
        smooth: true,
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#1890ff' },
      },
    ],
  };

  // 告警分布图表配置
  const severityChartOption = {
    title: { text: '告警级别分布' },
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: Object.entries(stats?.metrics?.alerts?.by_severity || { P0: 0, P1: 8, P2: 25, P3: 16 }).map(([key, value]) => ({
          name: key,
          value,
        })),
        label: { formatter: '{b}: {c}' },
      },
    ],
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="今日告警"
              value={stats?.alerts?.total || 12}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
            <Progress
              percent={((stats?.alerts?.resolved || 7) / (stats?.alerts?.total || 12)) * 100}
              status="active"
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="处理中故障"
              value={stats?.incidents?.investigating || 1}
              valueStyle={{ color: '#cf1322' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              已解决：{stats?.incidents?.resolved || 1}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="自动修复"
              value={stats?.autofix?.total_executions || 51}
              suffix={`成功率 ${stats?.autofix?.success_rate || 94.1}%`}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="系统可用性"
              value={stats?.availability?.today || 99.9}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              本周：{stats?.availability?.this_week || 99.95}%
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="告警趋势" loading={loading}>
            <ReactECharts option={alertChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="告警级别分布" loading={loading}>
            <ReactECharts option={severityChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 实时告警 */}
      <Card
        title="实时告警"
        loading={loading}
        style={{ marginTop: 24 }}
        extra={<Button type="primary">查看全部</Button>}
      >
        <Table
          columns={alertColumns}
          dataSource={alerts}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Dashboard;
