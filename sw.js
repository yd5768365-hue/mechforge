/**
 * Service Worker - 缓存策略优化
 * 提供离线支持和资源缓存
 */

const CACHE_NAME = 'mechforge-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/styles-modular.css',
  '/css/variables.css',
  '/css/layout.css',
  '/css/chat.css',
  '/css/panels.css',
  '/css/components.css',
  '/css/effects.css',
  '/css/utilities.css',
  '/css/industrial-theme.css',
  '/css/chat-markdown.css',
  '/experience.css',
  '/core/event-bus.js',
  '/core/utils.js',
  '/core/api-client.js',
  '/core/logger.js',
  '/core/storage.js',
  '/core/error-handler.js',
  '/core/theme.js',
  '/core/event-manager.js',
  '/core/module-loader.js',
  '/core/performance-monitor.js',
  '/core/cache-manager.js',
  '/core/dom-utils.js',
  '/core/animation-engine.js',
  '/core/notification-manager.js',
  '/core/store.js',
  '/app/main.js',
  '/app/ui/window-control.js',
  '/app/ui/particles.js',
  '/app/ui/mascot.js',
  '/app/ui/mode-indicator.js',
  '/app/chat/chat-ui.js',
  '/app/chat/chat-handler.js',
  '/app/chat/chat-features.js',
  '/app/knowledge/knowledge-ui.js',
  '/app/cae/cae-workbench.js',
  '/app/settings/status-bar.js',
  '/app/settings/api-switcher.js',
  '/dj-whale.png'
];

// 安装：预缓存静态资源
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((error) => {
        console.error('[SW] Cache failed:', error);
      })
  );
  self.skipWaiting();
});

// 激活：清理旧缓存
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// 拦截请求：缓存优先策略
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非 GET 请求和外部请求
  if (request.method !== 'GET' || !url.pathname.startsWith('/')) {
    return;
  }

  // API 请求：网络优先
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // 静态资源：缓存优先
  event.respondWith(cacheFirst(request));
});

/**
 * 缓存优先策略
 */
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    // 后台更新缓存
    fetch(request).then((response) => {
      if (response.ok) {
        cache.put(request, response.clone());
      }
    }).catch(() => {});
    return cached;
  }

  // 未缓存，从网络获取
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[SW] Fetch failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

/**
 * 网络优先策略
 */
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }
    throw error;
  }
}

// 消息处理
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
