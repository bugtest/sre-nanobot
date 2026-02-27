import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Space, Button, Badge, Modal, Descriptions, Timeline, Typography } from 'antd';
import { BugOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;

interface Incident {
  id: string;
  severity: string;
  status: string;
  summary: string;
  root_cause: string;
  affected_services: string[];
  duration: string;
  user_impact: string;
  created_at: string;
  resolved_at?: string;
}

const Incidents: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  // 获取故障列表
  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/incidents');
      setIncidents(response.data.incidents);
    } catch (error) {
      console.error('获取故障列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 查看详情
  const handleViewDetail = (incident: Incident) => {
    setSelectedIncident(incident);
    setModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '故障 ID',
      dataIndex: 'id',
      key: 'id',
      render: (text: string) => <span style={{ fontFamily: 'monospace' }}>{text}</span>,
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
        if (status === 'investigating') {
          return <Badge status="processing" text="调查中" />;
        } else if (status === 'resolved') {
          return <Badge status="success" text="已解决" />;
        }
        return <Badge status="default" text={status} />;
      },
    },
    {
      title: '摘要',
      dataIndex: 'summary',
      key: 'summary',
      ellipsis: true,
    },
    {
      title: '影响服务',
      dataIndex: 'affected_services',
      key: 'affected_services',
      render: (services: string[]) => (
        <Space>
          {services.map((service: string) => (
            <Tag key={service}>{service}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: '用户影响',
      dataIndex: 'user_impact',
      key: 'user_impact',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Incident) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'investigating' && (
            <Button 
              type="primary" 
              size="small"
              icon={<CheckCircleOutlined />}
            >
              解决
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={2} style={{ margin: 0 }}>
            🐛 故障管理
          </Title>
          <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
            跟踪和管理所有故障事件
          </Paragraph>
        </div>

        <Table
          columns={columns}
          dataSource={incidents}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个故障`,
          }}
        />
      </Card>

      {/* 故障详情弹窗 */}
      <Modal
        title="故障详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button
            key="close"
            onClick={() => setModalVisible(false)}
          >
            关闭
          </Button>,
        ]}
        width={900}
      >
        {selectedIncident && (
          <>
            <Descriptions bordered column={1} size="small" style={{ marginBottom: 24 }}>
              <Descriptions.Item label="故障 ID">{selectedIncident.id}</Descriptions.Item>
              <Descriptions.Item label="严重级别">
                <Tag color={selectedIncident.severity === 'P0' ? 'red' : selectedIncident.severity === 'P1' ? 'orange' : 'yellow'}>
                  {selectedIncident.severity}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Badge status={selectedIncident.status === 'investigating' ? 'processing' : 'success'} text={selectedIncident.status} />
              </Descriptions.Item>
              <Descriptions.Item label="摘要">{selectedIncident.summary}</Descriptions.Item>
              <Descriptions.Item label="根因">{selectedIncident.root_cause}</Descriptions.Item>
              <Descriptions.Item label="影响服务">
                <Space>
                  {selectedIncident.affected_services.map((service: string) => (
                    <Tag key={service}>{service}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="持续时间">
                <Space>
                  <ClockCircleOutlined />
                  {selectedIncident.duration}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="用户影响">{selectedIncident.user_impact}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{selectedIncident.created_at}</Descriptions.Item>
              {selectedIncident.resolved_at && (
                <Descriptions.Item label="解决时间">{selectedIncident.resolved_at}</Descriptions.Item>
              )}
            </Descriptions>

            <Title level={5}>处理时间线</Title>
            <Timeline
              items={[
                {
                  color: 'red',
                  children: (
                    <div>
                      <strong>故障发生</strong>
                      <div style={{ fontSize: 12, color: '#999' }}>{selectedIncident.created_at}</div>
                    </div>
                  ),
                },
                {
                  color: 'blue',
                  children: (
                    <div>
                      <strong>开始调查</strong>
                      <div style={{ fontSize: 12, color: '#999' }}>自动检测并创建故障单</div>
                    </div>
                  ),
                },
                {
                  color: 'green',
                  children: (
                    <div>
                      <strong>根因分析完成</strong>
                      <div style={{ fontSize: 12, color: '#999' }}>识别根本原因：{selectedIncident.root_cause}</div>
                    </div>
                  ),
                },
                ...(selectedIncident.status === 'resolved' ? [
                  {
                    color: 'green',
                    children: (
                      <div>
                        <strong>故障解决</strong>
                        <div style={{ fontSize: 12, color: '#999' }}>{selectedIncident.resolved_at}</div>
                      </div>
                    ),
                  },
                ] : []),
              ]}
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default Incidents;
