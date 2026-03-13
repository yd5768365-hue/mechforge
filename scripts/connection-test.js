/**
 * Connection Test - 连接诊断工具
 * 用于诊断前端与后端的连接问题
 */

(async function () {
  'use strict';

  console.log('═'.repeat(60));
  console.log('MechForge AI - Connection Diagnostic Tool');
  console.log('═'.repeat(60));
  console.log();

  // 1. 检查页面信息
  console.log('📄 Page Information:');
  console.log('  URL:', window.location.href);
  console.log('  Protocol:', window.location.protocol);
  console.log('  Host:', window.location.host);
  console.log('  Origin:', window.location.origin);
  console.log();

  // 2. 检查 APIClient 配置
  console.log('🔧 APIClient Configuration:');
  if (window.apiClient) {
    console.log('  Base URL:', apiClient.baseURL);
    console.log('  Is Local File:', apiClient.isLocalFile);
  } else {
    console.log('  ❌ apiClient not found!');
  }
  console.log();

  // 3. 测试 fetch API
  console.log('🌐 Testing Fetch API:');
  try {
    const testUrl = window.location.origin + '/api/health';
    console.log('  Testing:', testUrl);
    
    const response = await fetch(testUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('  ✅ Connection successful!');
      console.log('  Response:', JSON.stringify(data, null, 2));
    } else {
      console.log('  ❌ HTTP Error:', response.status, response.statusText);
    }
  } catch (error) {
    console.log('  ❌ Fetch Error:', error.message);
    console.log();
    console.log('💡 Possible causes:');
    console.log('  1. Backend server is not running');
    console.log('  2. CORS policy blocking the request');
    console.log('  3. Wrong port or URL');
    console.log('  4. Network connectivity issue');
  }
  console.log();

  // 4. 测试 APIClient 方法
  console.log('🔌 Testing APIClient Methods:');
  if (window.apiClient) {
    try {
      const health = await apiClient.checkConnection();
      if (health.ok) {
        console.log('  ✅ APIClient connection check passed');
      } else {
        console.log('  ❌ APIClient connection check failed:', health.error);
      }
    } catch (error) {
      console.log('  ❌ APIClient error:', error.message);
    }
  }
  console.log();

  // 5. 建议
  console.log('💡 Recommendations:');
  if (window.location.protocol === 'file:') {
    console.log('  ⚠️  You are running from file:// protocol');
    console.log('     Please use one of the following methods:');
    console.log('     1. Run: python desktop_app.py');
    console.log('     2. Run: python server.py and open http://localhost:5000');
    console.log('     3. Use a local server like: npx serve .');
  } else {
    console.log('  ✅ You are running from HTTP protocol');
    console.log('     If connection fails, check:');
    console.log('     1. Is the backend server running?');
    console.log('     2. Check server logs for errors');
    console.log('     3. Verify the port number matches');
  }
  console.log();
  console.log('═'.repeat(60));
})();
