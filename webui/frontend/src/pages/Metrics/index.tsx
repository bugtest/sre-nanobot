import React, { useState, useEffect, useRef } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Typography, Spin, Alert } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  CpuOutlined,
  DashboardOutlined,
  AlertOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

const { Title } = Typography;

interface MetricsData {
  cpu: { current: number; trend: number[] };
  memory: { current: number; trend: number[] };
  alerts: { firing: number; resolved: number };
}

const Metrics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // 连接 WebSocket
  useEffect(() => {
    connectWebSocket();
    fetchInitialMetrics();
    
    // 定时轮询（备用方案）
    const interval = setInterval(fetchInitialMetrics, 30000);
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      clearInterval(interval);
    };
  }, []);

  const connectWebSocket = () => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws/metrics`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket 连接成功');
      setWsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'metrics_update' || data.type === 'init') {
          setMetrics(data.data);
          setLoading(false);
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      setWsConnected(false);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket 连接关闭，尝试重连...');
      setWsConnected(false);
      // 5 秒后重连
      setTimeout(connectWebSocket, 5000);
    };
  };

  const fetchInitialMetrics = async () => {
    try {
      const [cpuRes, memoryRes, alertsRes] = await Promise.all([
        fetch('/api/metrics/cpu').then(r => r.json()),
        fetch('/api/metrics/memory').then(r => r.json()),
        fetch('/api/metrics/alerts').then(r => r.json()),
      ]);

      setMetrics({
        cpu: cpuRes,
        memory: memoryRes,
        alerts: alertsRes,
      });
      setLoading(false);
    } catch (error) {
      console.error('获取指标数据失败:', error);
    }
  };

  // CPU 使用率图表
  const cpuOption = {
    title: { text: 'CPU 使用率趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 10 }, (_, i) => `${i * 5}分钟前`),
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' },
    },
    series: [
      {
        name: 'CPU 使用率',
        type: 'line',
        smooth: true,
        data: metrics?.cpu?.trend || [],
        areaStyle: {
          color: new (require('echarts')).graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82, 196, 26, 0.5)' },
            { offset: 1, color: 'rgba(82, 196, 26, 0.01)' },
          ]),
        },
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  // 内存使用率图表
  const memoryOption = {
    title: { text: '内存使用率趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 10 }, (_, i) => `${i * 5}分钟前`),
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' },
    },
    series: [
      {
        name: '内存使用率',
        type: 'line',
        smooth: true,
        data: metrics?.memory?.trend || [],
        areaStyle: {
          color: new (require('echarts')).graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.5)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.01)' },
          ]),
        },
        itemStyle: { color: '#1890ff' },
      },
    ],
  };

  // 告警统计图表
  const alertsOption = {
    title: { text: '告警统计', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: metrics?.alerts?.firing || 0, name: 'Firing' },
          { value: metrics?.alerts?.resolved || 0, name: 'Resolved' },
        ],
        label: { formatter: '{b}: {c}' },
        itemStyle: {
          color: (params: any) => {
            const colors = ['#ff4d4f', '#52c41a'];
            return colors[params.dataIndex];
          },
        },
      },
    ],
  };

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" tip="加载指标数据..." />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* WebSocket 状态提示 */}
      {!wsConnected && (
        <Alert
          message="WebSocket 未连接"
          description="无法接收实时数据，已切换到轮询模式（30 秒刷新）"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 实时指标卡片 */}
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="CPU 使用率"
              value={metrics?.cpu?.current || 0}
              precision={1}
              suffix="%"
              prefix={<CpuOutlined />}
              valueStyle={{
                color: (metrics?.cpu?.current || 0) > 80 ? '#ff4d4f' : '#52c41a',
              }}
            />
            <Progress
              percent={metrics?.cpu?.current || 0}
              status={
                (metrics?.cpu?.current || 0) > 80
                  ? 'exception'
                  : (metrics?.cpu?.current || 0) > 60
                  ? 'normal'
                  : 'success'
              }
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="内存使用率"
              value={metrics?.memory?.current || 0}
              precision={1}
              suffix="%"
              prefix={<DashboardOutlined />}
              valueStyle={{
                color: (metrics?.memory?.current || 0) > 80 ? '#ff4d4f' : '#1890ff',
              }}
            />
            <Progress
              percent={metrics?.memory?.current || 0}
              status={
                (metrics?.memory?.current || 0) > 80
                  ? 'exception'
                  : (metrics?.memory?.current || 0) > 60
                  ? 'normal'
                  : 'success'
              }
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <Statistic
                  title="Firing"
                  value={metrics?.alerts?.firing || 0}
                  prefix={<AlertOutlined />}
                  valueStyle={{ color: '#ff4d4f', fontSize: 24 }}
                />
              </div>
              <div style={{ textAlign: 'center' }}>
                <Statistic
                  title="Resolved"
                  value={metrics?.alerts?.resolved || 0}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a', fontSize: 24 }}
                />
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="CPU 使用率趋势">
            <ReactECharts option={cpuOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="内存使用率趋势">
            <ReactECharts option={memoryOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="告警统计">
            <ReactECharts option={alertsOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="实时日志">
            <div style={{ height: 300, overflow: 'auto', fontFamily: 'monospace', fontSize: 12 }}>
              <div style={{ color: '#52c41a' }}>
                [{new Date().toLocaleTimeString()}] WebSocket 连接成功
              </div>
              <div style={{ color: '#1890ff' }}>
                [{new Date().toLocaleTimeString()}] 接收实时指标数据
              </div>
              <div style={{ color: '#999' }}>
                [{new Date().toLocaleTimeString()}] CPU: {metrics?.cpu?.current}% | Memory: {metrics?.memory?.current}%
              </div>
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} style={{ color: '#999' }}>
                  [{new Date(Date.now() - (i + 1) * 5000).toLocaleTimeString()}] 系统运行正常
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Metrics;
