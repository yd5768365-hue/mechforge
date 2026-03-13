/**
 * @fileoverview Service Worker 注册模块
 * @description 注册和管理 Service Worker
 * @module ServiceWorkerManager
 * @version 1.0.0
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const CONFIG = {
    swPath: '/sw.js',
    scope: '/',
    updateInterval: 60 * 60 * 1000 // 1小时检查更新
  };

  // ==================== 状态 ====================
  let registration = null;
  let isUpdateAvailable = false;

  // ==================== 初始化 ====================

  /**
   * 初始化 Service Worker
   * @returns {Promise<boolean>} 是否成功注册
   */
  async function init() {
    if (!('serviceWorker' in navigator)) {
      console.log('[SW] Service Worker not supported');
      return false;
    }

    try {
      registration = await navigator.serviceWorker.register(CONFIG.swPath, {
        scope: CONFIG.scope
      });

      console.log('[SW] Registered:', registration.scope);

      // 监听更新
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;

        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('[SW] Update available');
            isUpdateAvailable = true;
            showUpdateNotification();
          }
        });
      });

      // 定期检查更新
      setInterval(checkForUpdates, CONFIG.updateInterval);

      // 监听消息
      navigator.serviceWorker.addEventListener('message', handleMessage);

      return true;
    } catch (error) {
      console.error('[SW] Registration failed:', error);
      return false;
    }
  }

  /**
   * 处理 Service Worker 消息
   * @param {MessageEvent} event - 消息事件
   */
  function handleMessage(event) {
    const { type, data } = event.data;

    switch (type) {
      case 'CACHE_UPDATED':
        console.log('[SW] Cache updated:', data);
        break;

      case 'OFFLINE_READY':
        console.log('[SW] App is ready for offline use');
        break;

      case 'SYNC_COMPLETE':
        console.log('[SW] Background sync complete');
        break;

      default:
        console.log('[SW] Received message:', type, data);
    }
  }

  // ==================== 更新管理 ====================

  /**
   * 检查更新
   */
  async function checkForUpdates() {
    if (!registration) return;

    try {
      await registration.update();
      console.log('[SW] Update check complete');
    } catch (error) {
      console.error('[SW] Update check failed:', error);
    }
  }

  /**
   * 跳过等待并激活新 Service Worker
   */
  async function skipWaiting() {
    if (!registration || !registration.waiting) return;

    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  }

  /**
   * 显示更新通知
   */
  function showUpdateNotification() {
    // 可以在这里显示更新提示 UI
    if (window.eventBus) {
      eventBus.emit(Events.SYSTEM_MESSAGE, {
        message: '新版本可用，点击刷新更新',
        type: 'info',
        action: {
          label: '刷新',
          handler: () => {
            skipWaiting();
            window.location.reload();
          }
        }
      });
    }
  }

  // ==================== 缓存管理 ====================

  /**
   * 清理所有缓存
   * @returns {Promise<void>}
   */
  async function clearCaches() {
    if (!registration) return;

    const messageChannel = new MessageChannel();

    return new Promise((resolve, reject) => {
      messageChannel.port1.onmessage = (event) => {
        if (event.data.success) {
          resolve();
        } else {
          reject(new Error(event.data.error));
        }
      };

      registration.active?.postMessage(
        { type: 'CLEAR_CACHES' },
        [messageChannel.port2]
      );
    });
  }

  /**
   * 获取缓存状态
   * @returns {Promise<Array<{name: string, count: number}>>}
   */
  async function getCacheStatus() {
    if (!registration) return [];

    const messageChannel = new MessageChannel();

    return new Promise((resolve) => {
      messageChannel.port1.onmessage = (event) => {
        resolve(event.data.status || []);
      };

      registration.active?.postMessage(
        { type: 'GET_CACHE_STATUS' },
        [messageChannel.port2]
      );
    });
  }

  /**
   * 预缓存资源
   * @param {string[]} urls - 要缓存的 URL 列表
   * @returns {Promise<void>}
   */
  async function precache(urls) {
    if (!registration) return;

    const messageChannel = new MessageChannel();

    return new Promise((resolve, reject) => {
      messageChannel.port1.onmessage = (event) => {
        if (event.data.success) {
          resolve();
        } else {
          reject(new Error(event.data.error));
        }
      };

      registration.active?.postMessage(
        { type: 'PRECACHE', payload: { urls } },
        [messageChannel.port2]
      );
    });
  }

  // ==================== 后台同步 ====================

  /**
   * 注册后台同步
   * @param {string} tag - 同步标签
   * @returns {Promise<void>}
   */
  async function registerSync(tag) {
    if (!registration || !registration.sync) {
      console.log('[SW] Background sync not supported');
      return;
    }

    try {
      await registration.sync.register(tag);
      console.log('[SW] Sync registered:', tag);
    } catch (error) {
      console.error('[SW] Sync registration failed:', error);
    }
  }

  // ==================== 通知 ====================

  /**
   * 请求通知权限
   * @returns {Promise<boolean>}
   */
  async function requestNotificationPermission() {
    if (!('Notification' in window)) {
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  /**
   * 显示通知
   * @param {string} title - 标题
   * @param {NotificationOptions} options - 选项
   */
  async function showNotification(title, options = {}) {
    if (!registration || Notification.permission !== 'granted') {
      return;
    }

    try {
      await registration.showNotification(title, {
        icon: '/dj-whale.png',
        badge: '/dj-whale.png',
        ...options
      });
    } catch (error) {
      console.error('[SW] Show notification failed:', error);
    }
  }

  // ==================== 状态查询 ====================

  /**
   * 检查是否支持 Service Worker
   * @returns {boolean}
   */
  function isSupported() {
    return 'serviceWorker' in navigator;
  }

  /**
   * 检查是否有更新可用
   * @returns {boolean}
   */
  function hasUpdate() {
    return isUpdateAvailable;
  }

  /**
   * 获取注册状态
   * @returns {ServiceWorkerRegistration|null}
   */
  function getRegistration() {
    return registration;
  }

  // ==================== 导出 ====================
  window.ServiceWorkerManager = {
    init,
    checkForUpdates,
    skipWaiting,
    clearCaches,
    getCacheStatus,
    precache,
    registerSync,
    requestNotificationPermission,
    showNotification,
    isSupported,
    hasUpdate,
    getRegistration
  };
})();
