import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Space, Button, Input, Select, Typography, Badge, Modal, Descriptions } from 'antd';
import { SearchOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { Option } = Select;

interface Alert {
  id: string;
  name: string;
  severity: string;
  status: string;
  namespace: string;
  service: string;
  pod?: string;
  description: string;
  starts_at: string;
  duration: string;
}

const Alerts: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [searchText, setSearchText] = useState('');

  // 获取告警列表
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // 30 秒刷新
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/alerts');
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('获取告警失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 确认告警
  const handleAcknowledge = async (alertId: string) => {
    try {
      await axios.post(`/api/alerts/${alertId}/acknowledge`);
      Modal.success({
        title: '确认成功',
        content: '告警已确认',
      });
      fetchAlerts();
    } catch (error) {
      Modal.error({
        title: '确认失败',
        content: '确认告警时出错',
      });
    }
  };

  // 查看详情
  const handleViewDetail = (alert: Alert) => {
    setSelectedAlert(alert);
    setModalVisible(true);
  };

  // 过滤告警
  const filteredAlerts = alerts.filter(alert => {
    const matchStatus = filterStatus === 'all' || alert.status === filterStatus;
    const matchSeverity = filterSeverity === 'all' || alert.severity === filterSeverity;
    const matchSearch = searchText === '' || 
      alert.name.toLowerCase().includes(searchText.toLowerCase()) ||
      alert.service.toLowerCase().includes(searchText.toLowerCase());
    return matchStatus && matchSeverity && matchSearch;
  });

  // 表格列定义
  const columns = [
    {
      title: '告警名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Alert) => (
        <Space>
          {record.severity === 'P0' && <span>🚨</span>}
          {record.severity === 'P1' && <span>⚠️</span>}
          {record.severity === 'P2' && <span>⚡</span>}
          {record.severity === 'P3' && <span>ℹ️</span>}
          <strong>{text}</strong>
        </Space>
      ),
      sorter: (a: Alert, b: Alert) => a.name.localeCompare(b.name),
    },
    {
      title: '严重级别',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => {
        const colorMap: any = { P0: 'red', P1: 'orange', P2: 'yellow', P3: 'blue' };
        return <Tag color={colorMap[severity]}>{severity}</Tag>;
      },
      filters: [
        { text: 'P0', value: 'P0' },
        { text: 'P1', value: 'P1' },
        { text: 'P2', value: 'P2' },
        { text: 'P3', value: 'P3' },
      ],
      onFilter: (value: any, record: Alert) => record.severity === value,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        if (status === 'firing') {
          return <Badge status="processing" text="Firing" />;
        } else if (status === 'resolved') {
          return <Badge status="success" text="Resolved" />;
        }
        return <Badge status="default" text={status} />;
      },
      filters: [
        { text: 'Firing', value: 'firing' },
        { text: 'Resolved', value: 'resolved' },
      ],
      onFilter: (value: any, record: Alert) => record.status === value,
    },
    {
      title: '服务',
      dataIndex: 'service',
      key: 'service',
    },
    {
      title: '命名空间',
      dataIndex: 'namespace',
      key: 'namespace',
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Alert) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          {record.status === 'firing' && (
            <Button 
              type="primary" 
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => handleAcknowledge(record.id)}
            >
              确认
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            🚨 告警中心
          </Title>
          <Space>
            <Input
              placeholder="搜索告警..."
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            <Select
              style={{ width: 120 }}
              value={filterStatus}
              onChange={setFilterStatus}
            >
              <Option value="all">全部状态</Option>
              <Option value="firing">Firing</Option>
              <Option value="resolved">Resolved</Option>
            </Select>
            <Select
              style={{ width: 120 }}
              value={filterSeverity}
              onChange={setFilterSeverity}
            >
              <Option value="all">全部级别</Option>
              <Option value="P0">P0</Option>
              <Option value="P1">P1</Option>
              <Option value="P2">P2</Option>
              <Option value="P3">P3</Option>
            </Select>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={filteredAlerts}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条告警`,
          }}
        />
      </Card>

      {/* 告警详情弹窗 */}
      <Modal
        title="告警详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          selectedAlert?.status === 'firing' && (
            <Button
              key="acknowledge"
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => {
                if (selectedAlert) {
                  handleAcknowledge(selectedAlert.id);
                  setModalVisible(false);
                }
              }}
            >
              确认告警
            </Button>
          ),
          <Button
            key="close"
            onClick={() => setModalVisible(false)}
          >
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedAlert && (
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label="告警名称">{selectedAlert.name}</Descriptions.Item>
            <Descriptions.Item label="严重级别">
              <Tag color={selectedAlert.severity === 'P0' ? 'red' : selectedAlert.severity === 'P1' ? 'orange' : 'yellow'}>
                {selectedAlert.severity}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Badge status={selectedAlert.status === 'firing' ? 'processing' : 'success'} text={selectedAlert.status} />
            </Descriptions.Item>
            <Descriptions.Item label="命名空间">{selectedAlert.namespace}</Descriptions.Item>
            <Descriptions.Item label="服务">{selectedAlert.service}</Descriptions.Item>
            {selectedAlert.pod && (
              <Descriptions.Item label="Pod">{selectedAlert.pod}</Descriptions.Item>
            )}
            <Descriptions.Item label="描述">{selectedAlert.description}</Descriptions.Item>
            <Descriptions.Item label="开始时间">{selectedAlert.starts_at}</Descriptions.Item>
            <Descriptions.Item label="持续时间">{selectedAlert.duration}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Alerts;
