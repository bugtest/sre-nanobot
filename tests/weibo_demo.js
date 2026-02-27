/**
 * 访问微博演示
 * 
 * 使用 Playwright 访问 weibo.com 并截图
 */

const { chromium } = require('playwright');

(async () => {
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║              访问微博 - Playwright 演示                  ║');
  console.log('╚══════════════════════════════════════════════════════════╝');
  console.log();

  // 启动浏览器
  console.log('🚀 启动浏览器...');
  const browser = await chromium.launch({
    headless: true,  // 无头模式
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();

  console.log('✅ 浏览器启动成功');
  console.log();

  // 访问微博
  console.log('🌐 访问微博...');
  console.log('📍 URL: https://weibo.com');
  
  try {
    await page.goto('https://weibo.com', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    console.log('✅ 页面加载成功');
    console.log('📄 页面标题:', await page.title());
    console.log('🔗 当前 URL:', page.url());
    console.log();

    // 等待页面稳定
    console.log('⏳ 等待页面稳定...');
    await page.waitForTimeout(3000);
    
    // 截图
    console.log('📸 截取全屏...');
    const screenshotPath = 'tests/screenshots/weibo-home.png';
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`✅ 截图保存：${screenshotPath}`);
    console.log();

    // 获取页面信息
    console.log('📊 获取页面信息...');
    const pageInfo = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        hasLogin: !!document.querySelector('[node-type="loginform"]') || 
                  !!document.querySelector('.woo-box-frame'),
        hasFeed: !!document.querySelector('[node-type="feed_list"]') ||
                 !!document.querySelector('.woo-box-flex'),
        links: Array.from(document.querySelectorAll('a')).slice(0, 20).map(a => ({
          text: a.textContent.trim().substring(0, 50),
          href: a.href
        })).filter(l => l.text && l.href.startsWith('http'))
      };
    });

    console.log('📄 页面标题:', pageInfo.title);
    console.log('🔗 当前 URL:', pageInfo.url);
    console.log('🔑 登录表单:', pageInfo.hasLogin ? '✅ 未登录' : '❌ 已登录或其他');
    console.log('📰 微博流:', pageInfo.hasFeed ? '✅ 存在' : '❌ 不存在');
    console.log();

    // 显示前 10 个链接
    if (pageInfo.links.length > 0) {
      console.log('🔗 页面链接（前 10 个）:');
      pageInfo.links.slice(0, 10).forEach((link, i) => {
        console.log(`   ${i+1}. ${link.text.substring(0, 30)}...`);
      });
      console.log();
    }

    // 性能指标
    console.log('⚡ 性能指标...');
    const performance = await page.evaluate(() => {
      const entries = performance.getEntriesByType('navigation')[0];
      if (!entries) return null;
      return {
        domContentLoaded: entries.domContentLoadedEventEnd - entries.startTime,
        loadComplete: entries.loadEventEnd - entries.startTime,
        resourceCount: performance.getEntriesByType('resource').length,
        transferSize: entries.transferSize || 0
      };
    });

    if (performance) {
      console.log('   ⚡ DOM 加载:', performance.domContentLoaded.toFixed(2) + 'ms');
      console.log('   ⚡ 完全加载:', performance.loadComplete.toFixed(2) + 'ms');
      console.log('   📦 资源数:', performance.resourceCount);
      console.log('   📊 传输大小:', (performance.transferSize / 1024).toFixed(2) + 'KB');
    } else {
      console.log('   ⚠️ 无法获取性能数据');
    }
    console.log();

    // 检查是否有登录弹窗
    console.log('🔍 检查登录状态...');
    const loginElements = await page.$$('a[href*="login"]');
    console.log(`   登录相关元素：${loginElements.length} 个`);
    
    // 检查热门微博
    const hotElements = await page.$$eval('.woo-box-flex, [node-type="feed_list"]', els => els.length);
    console.log(`   微博流元素：${hotElements} 个`);
    console.log();

    // 截取可见区域
    console.log('📸 截取可见区域...');
    await page.screenshot({
      path: 'tests/screenshots/weibo-viewport.png',
      fullPage: false
    });
    console.log('✅ 可见区域截图保存：tests/screenshots/weibo-viewport.png');
    console.log();

  } catch (error) {
    console.log('❌ 访问失败:', error.message);
    
    // 错误截图
    console.log('📸 截取错误页面...');
    await page.screenshot({
      path: 'tests/screenshots/weibo-error.png',
      fullPage: true
    });
    console.log('✅ 错误截图保存：tests/screenshots/weibo-error.png');
  }

  // 关闭浏览器
  console.log();
  console.log('🔒 关闭浏览器...');
  await browser.close();
  console.log('✅ 浏览器已关闭');

  // 总结
  console.log();
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║                    访问完成 ✅                           ║');
  console.log('╚══════════════════════════════════════════════════════════╝');
  console.log();
  console.log('📁 输出文件:');
  console.log('   - tests/screenshots/weibo-home.png (全屏截图)');
  console.log('   - tests/screenshots/weibo-viewport.png (可见区域)');
  console.log();
  console.log('═'.repeat(60));
  console.log('微博访问演示完成！');
  console.log();
})();
