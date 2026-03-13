/**
 * 开发服务器
 * 提供热重载、代理等功能
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// 配置
const config = {
  port: 8080,
  root: path.join(__dirname, '..'),
  watchDirs: ['core', 'app', 'services', 'css'],
  pythonPort: 5000
};

// MIME 类型
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// 客户端脚本（用于热重载）
const hotReloadScript = `
<script>
(function() {
  const ws = new WebSocket('ws://localhost:${config.port}/ws');
  ws.onmessage = function(event) {
    if (event.data === 'reload') {
      location.reload();
    }
  };
  ws.onclose = function() {
    console.log('[DevServer] Connection closed');
  };
})();
</script>
`;

// 文件缓存
const cache = new Map();

// 创建服务器
const server = http.createServer((req, res) => {
  // 处理 WebSocket 升级
  if (req.url === '/ws') {
    handleWebSocket(req, res);
    return;
  }

  // 处理 API 代理
  if (req.url.startsWith('/api/')) {
    proxyToPython(req, res);
    return;
  }

  // 处理静态文件
  let filePath = path.join(config.root, req.url === '/' ? 'index.html' : req.url);

  // 检查缓存
  if (cache.has(filePath)) {
    const cached = cache.get(filePath);
    res.writeHead(200, { 'Content-Type': cached.mime });
    res.end(cached.content);
    return;
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('File not found');
      } else {
        res.writeHead(500);
        res.end('Server error');
      }
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const mime = mimeTypes[ext] || 'application/octet-stream';

    // 对 HTML 文件注入热重载脚本
    if (ext === '.html') {
      content = content.toString().replace('</body>', hotReloadScript + '</body>');
    }

    // 缓存文件
    cache.set(filePath, { mime, content });

    res.writeHead(200, {
      'Content-Type': mime,
      'Cache-Control': 'no-cache'
    });
    res.end(content);
  });
});

// WebSocket 处理
const clients = new Set();

function handleWebSocket(req, res) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });

  clients.add(res);

  req.on('close', () => {
    clients.delete(res);
  });
}

// 代理到 Python 后端
function proxyToPython(req, res) {
  const options = {
    hostname: 'localhost',
    port: config.pythonPort,
    path: req.url,
    method: req.method,
    headers: req.headers
  };

  const proxy = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxy.on('error', (err) => {
    res.writeHead(502);
    res.end('Python server not available');
  });

  req.pipe(proxy);
}

// 文件监听
function watchFiles() {
  config.watchDirs.forEach(dir => {
    const dirPath = path.join(config.root, dir);
    if (!fs.existsSync(dirPath)) return;

    fs.watch(dirPath, { recursive: true }, (eventType, filename) => {
      if (filename) {
        console.log(`[Watch] ${eventType}: ${filename}`);

        // 清除缓存
        const filePath = path.join(dirPath, filename);
        cache.delete(filePath);

        // 通知客户端
        clients.forEach(client => {
          try {
            client.write('data: reload\n\n');
          } catch (e) {
            clients.delete(client);
          }
        });
      }
    });
  });

  console.log('[Watch] Watching files for changes...');
}

// 启动 Python 后端
function startPythonServer() {
  console.log('[Python] Starting backend server...');

  const python = exec('python server.py', {
    cwd: config.root
  });

  python.stdout.on('data', (data) => {
    console.log(`[Python] ${data.trim()}`);
  });

  python.stderr.on('data', (data) => {
    console.error(`[Python] ${data.trim()}`);
  });

  python.on('close', (code) => {
    console.log(`[Python] Server exited with code ${code}`);
  });

  return python;
}

// 启动服务器
server.listen(config.port, () => {
  console.log(`
╔══════════════════════════════════════════════════╗
║           MechForge AI Dev Server                ║
╠══════════════════════════════════════════════════╣
║  HTTP:  http://localhost:${config.port}                    ║
║  WS:    ws://localhost:${config.port}/ws                 ║
║  API:   http://localhost:${config.pythonPort}                  ║
╚══════════════════════════════════════════════════╝
  `);

  watchFiles();
  startPythonServer();
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n[DevServer] Shutting down...');
  server.close();
  process.exit(0);
});
