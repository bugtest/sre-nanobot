import { request } from 'umi';

export interface SkillInfo {
  name: string;
  description: string;
  version: string;
  author: string;
  enabled: boolean;
  config?: Record<string, any>;
}

export interface SkillExecutionResult {
  success: boolean;
  error?: string;
  [key: string]: any;
}

/**
 * 获取 Skills 列表
 */
export async function listSkills(): Promise<{ skills: SkillInfo[] }> {
  return request('/api/skills');
}

/**
 * 获取单个 Skill 信息
 */
export async function getSkillInfo(name: string): Promise<SkillInfo> {
  return request(`/api/skills/${name}`);
}

/**
 * 执行 Skill
 */
export async function executeSkill(
  name: string,
  params: Record<string, any>
): Promise<SkillExecutionResult> {
  return request(`/api/skills/${name}/execute`, {
    method: 'POST',
    data: params,
  });
}

/**
 * 获取 Skill 状态
 */
export async function getSkillStatus(name: string): Promise<{ enabled: boolean; config: Record<string, any> }> {
  return request(`/api/skills/${name}/status`);
}

/**
 * 更新 Skill 配置
 */
export async function updateSkillConfig(
  name: string,
  config: Record<string, any>
): Promise<{ success: boolean }> {
  return request(`/api/skills/${name}/config`, {
    method: 'PUT',
    data: config,
  });
}

/**
 * 重新加载 Skill
 */
export async function reloadSkill(name: string): Promise<{ success: boolean }> {
  return request(`/api/skills/${name}/reload`, {
    method: 'POST',
  });
}
