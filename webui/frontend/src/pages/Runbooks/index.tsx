import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Space, Button, Modal, Descriptions, Typography, Progress, Tooltip } from 'antd';
import { FileTextOutlined, PlayCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;

interface Runbook {
  id: string;
  name: string;
  version: string;
  description: string;
  severity: string;
  triggers: string[];
  execution_count: number;
  success_rate: number;
}

const Runbooks: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [runbooks, setRunbooks] = useState<Runbook[]>([]);
  const [selectedRunbook, setSelectedRunbook] = useState<Runbook | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [executing, setExecuting] = useState(false);

  // 获取预案列表
  useEffect(() => {
    fetchRunbooks();
  }, []);

  const fetchRunbooks = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/runbooks');
      setRunbooks(response.data.runbooks);
    } catch (error) {
      console.error('获取预案列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 执行预案
  const handleExecute = async (runbookId: string) => {
    setExecuting(true);
    try {
      const response = await axios.post(`/api/runbooks/${runbookId}/execute`);
      Modal.success({
        title: '执行成功',
        content: `预案执行成功，执行 ID: ${response.data.execution_id}`,
      });
    } catch (error) {
      Modal.error({
        title: '执行失败',
        content: '执行预案时出错',
      });
    } finally {
      setExecuting(false);
    }
  };

  // 查看详情
  const handleViewDetail = (runbook: Runbook) => {
    setSelectedRunbook(runbook);
    setModalVisible(true);
  };

  // 获取风险等级颜色
  const getSeverityColor = (severity: string) => {
    const colorMap: any = {
      low: 'green',
      medium: 'orange',
      high: 'red',
    };
    return colorMap[severity] || 'default';
  };

  // 表格列定义
  const columns = [
    {
      title: '预案 ID',
      dataIndex: 'id',
      key: 'id',
      render: (text: string) => <span style={{ fontFamily: 'monospace' }}>{text}</span>,
    },
    {
      title: '预案名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Runbook) => (
        <Space>
          <FileTextOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: '风险等级',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>{severity.toUpperCase()}</Tag>
      ),
    },
    {
      title: '触发条件',
      dataIndex: 'triggers',
      key: 'triggers',
      render: (triggers: string[]) => (
        <Space>
          {triggers.slice(0, 2).map((trigger: string) => (
            <Tag key={trigger}>{trigger}</Tag>
          ))}
          {triggers.length > 2 && (
            <Tooltip title={triggers.slice(2).join(', ')}>
              <Tag>+{triggers.length - 2}</Tag>
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '执行次数',
      dataIndex: 'execution_count',
      key: 'execution_count',
    },
    {
      title: '成功率',
      dataIndex: 'success_rate',
      key: 'success_rate',
      render: (rate: number) => (
        <Space>
          <Progress
            percent={rate}
            size="small"
            status={rate >= 90 ? 'success' : rate >= 70 ? 'normal' : 'exception'}
            style={{ width: 100 }}
          />
          <span>{rate}%</span>
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Runbook) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button 
            type="primary" 
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(record.id)}
            loading={executing}
          >
            执行
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={2} style={{ margin: 0 }}>
            📋 预案管理
          </Title>
        </div>

        <Table
          columns={columns}
          dataSource={runbooks}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个预案`,
          }}
        />
      </Card>

      {/* 预案详情弹窗 */}
      <Modal
        title="预案详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button
            key="execute"
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={() => {
              if (selectedRunbook) {
                handleExecute(selectedRunbook.id);
                setModalVisible(false);
              }
            }}
            loading={executing}
          >
            执行预案
          </Button>,
          <Button
            key="close"
            onClick={() => setModalVisible(false)}
          >
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedRunbook && (
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label="预案 ID">{selectedRunbook.id}</Descriptions.Item>
            <Descriptions.Item label="预案名称">{selectedRunbook.name}</Descriptions.Item>
            <Descriptions.Item label="版本">{selectedRunbook.version}</Descriptions.Item>
            <Descriptions.Item label="描述">{selectedRunbook.description}</Descriptions.Item>
            <Descriptions.Item label="风险等级">
              <Tag color={getSeverityColor(selectedRunbook.severity)}>
                {selectedRunbook.severity.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="触发条件">
              <Space>
                {selectedRunbook.triggers.map((trigger: string) => (
                  <Tag key={trigger}>{trigger}</Tag>
                ))}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="执行次数">
              <Space>
                <PlayCircleOutlined />
                {selectedRunbook.execution_count} 次
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="成功率">
              <Space>
                <Progress
                  percent={selectedRunbook.success_rate}
                  size="small"
                  status={selectedRunbook.success_rate >= 90 ? 'success' : 'normal'}
                  style={{ width: 150 }}
                />
                <span>{selectedRunbook.success_rate}%</span>
              </Space>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Runbooks;
