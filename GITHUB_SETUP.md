# GitHub 仓库设置指南

## 🚀 推送到 GitHub

### 方式 1：使用推送脚本（推荐）

```bash
cd /home/ubuntu/.openclaw/workspace/sre-nanobot
./push-to-github.sh
```

然后根据提示输入 GitHub 凭证。

---

### 方式 2：手动推送

```bash
# 进入项目目录
cd /home/ubuntu/.openclaw/workspace/sre-nanobot

# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add -A

# 提交
git commit -m "Initial commit: SRE-NanoBot"

# 设置主分支
git branch -M main

# 添加远程仓库
git remote add origin https://github.com/bugtest/sre-nanobot.git

# 推送（需要认证）
git push -u origin main
```

---

### 方式 3：使用 SSH（推荐用于频繁推送）

**1. 生成 SSH 密钥（如果没有）：**

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**2. 添加 SSH 密钥到 GitHub：**

```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub
```

然后到 GitHub：Settings → SSH and GPG keys → New SSH key

**3. 使用 SSH 远程仓库：**

```bash
git remote set-url origin git@github.com:bugtest/sre-nanobot.git
git push -u origin main
```

---

### 方式 4：使用 GitHub CLI

**1. 安装 GitHub CLI：**

```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh
```

**2. 认证：**

```bash
gh auth login
```

**3. 创建并推送：**

```bash
# 创建仓库
gh repo create bugtest/sre-nanobot --public --source=. --remote=origin --push
```

---

## 🔐 认证方式

### Personal Access Token (PAT)

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - ✅ repo（完整仓库权限）
   - ✅ workflow（CI/CD）
4. 生成 token
5. 推送时使用 token 作为密码

```bash
Username: your_username
Password: ghp_xxxxxxxxxxxx  # 你的 PAT
```

---

## 📁 推荐的文件结构

推送前确保以下文件完整：

```
sre-nanobot/
├── README.md                    # ✅ 项目说明
├── pyproject.toml               # ✅ Python 包配置
├── config.example.json          # ✅ 配置示例
├── verify.sh                    # ✅ 验证脚本
├── test_*.py                    # ✅ 测试脚本
├── push-to-github.sh            # ✅ 推送脚本
├── sre_nanobot/                 # ✅ 核心代码
│   ├── mcp/
│   ├── agents/
│   ├── integrations/
│   ├── runbooks/
│   └── skills/
├── webui/                       # ✅ WebUI
│   ├── backend/
│   └── frontend/
└── docs/                        # ✅ 文档
    ├── 阶段 1-完成报告.md
    ├── 阶段 2-测试报告.md
    ├── 阶段 3-完成报告.md
    ├── 阶段 4-预案库完善.md
    ├── 阶段 5-飞书集成.md
    ├── 阶段 6-WebUI 开发.md
    ├── 集成测试报告.md
    ├── 飞书集成指南.md
    └── 项目总结.md
```

---

## 📝 .gitignore 建议

创建 `.gitignore` 文件，排除以下内容：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# Node.js
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试
.pytest_cache/
.coverage
htmlcov/

# 日志
*.log

# 敏感信息
config.json
*.key
*.pem
```

---

## 🎯 推送后检查

### 1. 检查仓库

访问：https://github.com/bugtest/sre-nanobot

确认：
- ✅ 所有文件已上传
- ✅ README.md 正常显示
- ✅ 目录结构正确

### 2. 设置仓库信息

- **Description**: "基于 NanoBot 的智能运维 Agent 平台"
- **Website**: (可选)
- **Topics**: `sre`, `kubernetes`, `devops`, `automation`, `aio ps`, `nanobot`

### 3. 设置可见性

- Public（公开）- 推荐
- Private（私有）

### 4. 添加协作者（可选）

Settings → Collaborators → Add people

---

## 🔄 后续更新

### 日常推送

```bash
git add -A
git commit -m "描述你的更改"
git push
```

### 查看状态

```bash
git status
git log --oneline
git remote -v
```

---

## 📞 常见问题

### Q: 推送失败 "Permission denied"

**A:** 检查认证：
- HTTPS: 使用 Personal Access Token
- SSH: 确保 SSH 密钥已添加到 GitHub

### Q: 仓库太大无法推送

**A:** 排除大文件：
```bash
# 检查大文件
git rev-parse --short HEAD | xargs -I {} git ls-tree -r {} | awk '{print $4}' | sort | uniq

# 使用 git-lfs 管理大文件
```

### Q: 如何更新远程仓库

**A:** 
```bash
git remote set-url origin https://github.com/bugtest/sre-nanobot.git
git push -f origin main
```

---

*最后更新：2026-02-27*
