# 微博访问报告

> 访问时间：2026-02-27 19:04

---

## ✅ 访问成功

**状态：** 完成
**URL：** https://weibo.com

---

## 📊 访问详情

### 基本信息

| 项目 | 值 |
|------|-----|
| 页面标题 | 微博 – 随时随地发现新鲜事 |
| 最终 URL | https://weibo.com/newlogin?... |
| 访问状态 | ✅ 成功 |
| 登录状态 | ⚠️ 未登录（显示登录页） |

---

### 页面元素

| 元素 | 数量 | 状态 |
|------|------|------|
| 登录相关元素 | 7 个 | ✅ |
| 微博流元素 | 166 个 | ✅ |
| 页面链接 | 10+ 个 | ✅ |

### 可见链接

1. 首页
2. 热门_hover
3. 画板
4. 消息_Normal
5. 热门推荐
6. 热门榜单
7. 我的
8. 热搜
9. 文娱
10. 生活

---

## ⚡ 性能指标

| 指标 | 数值 | 评级 |
|------|------|------|
| DOM 加载时间 | 1,453.70ms | ✅ 良好 |
| 完全加载时间 | 2,101.50ms | ✅ 良好 |
| 资源数量 | 63 个 | ⚠️ 较多 |
| 传输大小 | 1.50KB | ✅ 精简 |

---

## 📸 截图

### 全屏截图

**文件：** `tests/screenshots/weibo-home.png`
**大小：** 1.3MB
**内容：** 完整页面（包括登录弹窗）

### 可见区域截图

**文件：** `tests/screenshots/weibo-viewport.png`
**大小：** 702KB
**内容：** 视口可见区域

---

## 🔍 页面分析

### 登录状态

页面检测到未登录，显示登录弹窗：
- URL 包含 `/newlogin` 参数
- 有 7 个登录相关元素
- 但微博流内容仍然可见（166 个元素）

### 页面结构

```
微博首页
├── 导航栏
│   ├── 首页
│   ├── 热门
│   ├── 画板
│   └── 消息
├── 登录弹窗（未登录时显示）
├── 微博流
│   ├── 热搜
│   ├── 文娱
│   ├── 生活
│   └── ...
└── 侧边栏
    ├── 热门榜单
    └── 我的
```

---

## 🎯 使用的 Playwright 功能

### 1. 浏览器控制

```javascript
const browser = await chromium.launch({
  headless: true,
  args: ['--no-sandbox']
});

const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 ...'
});
```

### 2. 页面导航

```javascript
await page.goto('https://weibo.com', {
  waitUntil: 'networkidle',
  timeout: 30000
});
```

### 3. 截图

```javascript
// 全屏截图
await page.screenshot({
  path: 'weibo-home.png',
  fullPage: true
});

// 可见区域截图
await page.screenshot({
  path: 'weibo-viewport.png',
  fullPage: false
});
```

### 4. 页面信息获取

```javascript
const pageInfo = await page.evaluate(() => {
  return {
    title: document.title,
    url: window.location.href,
    links: Array.from(document.querySelectorAll('a'))
      .slice(0, 20)
      .map(a => ({ text: a.textContent, href: a.href }))
  };
});
```

### 5. 性能分析

```javascript
const performance = await page.evaluate(() => {
  const entries = performance.getEntriesByType('navigation')[0];
  return {
    domContentLoaded: entries.domContentLoadedEventEnd,
    loadComplete: entries.loadEventEnd,
    resourceCount: performance.getEntriesByType('resource').length
  };
});
```

### 6. 元素检测

```javascript
// 检查登录元素
const loginElements = await page.$$eval('a[href*="login"]', els => els.length);

// 检查微博流
const feedElements = await page.$$eval('.woo-box-flex', els => els.length);
```

---

## 📈 性能分析

### 加载时间分解

```
0ms ──────────────────────────────────────────────────────── 2102ms
    │                    │                                  │
    │                    │                                  │
  开始                DOM 加载                          完全加载
  请求              (1454ms)                          (2102ms)
```

### 资源统计

- **总资源数：** 63 个
- **主要资源：** HTML, CSS, JavaScript, 图片
- **CDN：** 使用新浪 CDN 加速

---

## 🎊 演示总结

### 成功完成

- ✅ 访问微博首页
- ✅ 截取全屏和视口截图
- ✅ 获取页面信息
- ✅ 性能分析
- ✅ 元素检测

### 技术展示

- ✅ 浏览器启动和配置
- ✅ 页面导航
- ✅ 截图功能
- ✅ JavaScript 执行
- ✅ 性能监控
- ✅ 元素查询

---

## 📁 输出文件

| 文件 | 大小 | 说明 |
|------|------|------|
| tests/screenshots/weibo-home.png | 1.3MB | 全屏截图 |
| tests/screenshots/weibo-viewport.png | 702KB | 可见区域截图 |
| tests/weibo_demo.js | 5KB | 演示脚本 |
| tests/WEIBO_ACCESS_REPORT.md | 3KB | 访问报告 |

---

## 🚀 扩展应用

### 1. 自动签到

```javascript
// 自动登录微博
await page.fill('input[type="text"]', 'username');
await page.fill('input[type="password"]', 'password');
await page.click('button[type="submit"]');
```

### 2. 内容监控

```javascript
// 监控热搜榜
const hotSearch = await page.$$eval('.hot-search-item', items => {
  return items.map(item => item.textContent);
});
```

### 3. 截图对比

```javascript
// 定期截图对比页面变化
await page.screenshot({ path: `weibo-${Date.now()}.png` });
```

---

*报告生成时间：2026-02-27 19:04*
*版本：v1.0*
