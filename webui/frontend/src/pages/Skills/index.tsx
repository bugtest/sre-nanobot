import React, { useState, useEffect } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Descriptions,
  Badge,
  Tooltip,
} from 'antd';
import {
  PlayCircleOutlined,
  ReloadOutlined,
  SettingOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { listSkills, executeSkill, reloadSkill, SkillInfo } from './api';

const SkillsPage: React.FC = () => {
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [executeModalVisible, setExecuteModalVisible] = useState(false);
  const [currentSkill, setCurrentSkill] = useState<SkillInfo | null>(null);
  const [executing, setExecuting] = useState(false);
  const [form] = Form.useForm();

  // 加载 Skills 列表
  const loadSkills = async () => {
    setLoading(true);
    try {
      const response = await listSkills();
      setSkills(response.skills || []);
    } catch (error) {
      message.error('加载 Skills 失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSkills();
  }, []);

  // 执行 Skill
  const handleExecute = async (values: any) => {
    if (!currentSkill) return;

    setExecuting(true);
    try {
      const result = await executeSkill(currentSkill.name, values);
      if (result.success) {
        message.success(`Skill "${currentSkill.name}" 执行成功`);
        setExecuteModalVisible(false);
        form.resetFields();
      } else {
        message.error(`执行失败：${result.error}`);
      }
    } catch (error) {
      message.error('执行失败');
    } finally {
      setExecuting(false);
    }
  };

  // 重新加载 Skill
  const handleReload = async (name: string) => {
    try {
      await reloadSkill(name);
      message.success(`Skill "${name}" 重新加载成功`);
      loadSkills();
    } catch (error) {
      message.error(`重新加载失败`);
    }
  };

  // 打开执行弹窗
  const showExecuteModal = (skill: SkillInfo) => {
    setCurrentSkill(skill);
    setExecuteModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: 'Skill 名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: SkillInfo) => (
        <Space>
          <span>{text}</span>
          <Tag color="blue">v{record.version}</Tag>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      render: (text: string) => text || 'Unknown',
    },
    {
      title: '状态',
      key: 'status',
      render: (_: any, record: SkillInfo) => (
        <Badge
          status={record.enabled ? 'success' : 'error'}
          text={record.enabled ? '已启用' : '已禁用'}
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: SkillInfo) => (
        <Space>
          <Tooltip title="执行 Skill">
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => showExecuteModal(record)}
            >
              执行
            </Button>
          </Tooltip>
          <Tooltip title="重新加载">
            <Button
              icon={<ReloadOutlined />}
              onClick={() => handleReload(record.name)}
            >
              重载
            </Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 执行表单渲染
  const renderExecuteForm = () => {
    if (!currentSkill) return null;

    // 根据不同 Skill 渲染不同表单
    if (currentSkill.name === 'sre_alert_handler') {
      return (
        <>
          <Form.Item
            name="alert"
            label="告警对象"
            rules={[{ required: true, message: '请输入告警对象' }]}
          >
            <Input.TextArea
              rows={4}
              placeholder='{"name":"PodCrashLooping","severity":"P1"}'
            />
          </Form.Item>
          <Form.Item name="auto_approve" label="自动审批" valuePropName="checked">
            <Select>
              <Select.Option value={true}>是</Select.Option>
              <Select.Option value={false}>否</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="notification" label="发送通知" valuePropName="checked">
            <Select>
              <Select.Option value={true}>是</Select.Option>
              <Select.Option value={false}>否</Select.Option>
            </Select>
          </Form.Item>
        </>
      );
    }

    if (currentSkill.name === 'sre_incident_analyzer') {
      return (
        <>
          <Form.Item
            name="incident_id"
            label="故障 ID"
            rules={[{ required: true, message: '请输入故障 ID' }]}
          >
            <Input placeholder="INC-001" />
          </Form.Item>
          <Form.Item name="depth" label="分析深度">
            <Select>
              <Select.Option value="shallow">快速分析</Select.Option>
              <Select.Option value="deep">深度分析</Select.Option>
            </Select>
          </Form.Item>
        </>
      );
    }

    return (
      <Form.Item label="参数" tooltip="该 Skill 暂无特定参数">
        <Input disabled placeholder="无参数" />
      </Form.Item>
    );
  };

  return (
    <PageContainer
      title="Skills 管理"
      subTitle="管理和执行 SRE 技能"
      onBack={() => window.history.back()}
    >
      <Card>
        <Table
          columns={columns}
          dataSource={skills}
          loading={loading}
          rowKey="name"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 执行弹窗 */}
      <Modal
        title={`执行 Skill: ${currentSkill?.name}`}
        open={executeModalVisible}
        onCancel={() => {
          setExecuteModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={handleExecute} layout="vertical">
          {renderExecuteForm()}
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={executing}>
                执行
              </Button>
              <Button
                onClick={() => {
                  setExecuteModalVisible(false);
                  form.resetFields();
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default SkillsPage;
