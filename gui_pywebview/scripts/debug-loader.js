/**
 * Debug Loader - 帮助诊断资源加载问题
 */

(function () {
  'use strict';

  console.log('═'.repeat(60));
  console.log('Debug Loader - Resource Loading Monitor');
  console.log('═'.repeat(60));

  // 拦截 fetch 请求
  const originalFetch = window.fetch;
  window.fetch = function (...args) {
    const url = args[0];
    if (url && (url.includes('undefined') || url === 'undefined')) {
      console.error('❌ Fetch called with undefined URL:', url);
      console.error('Stack:', new Error().stack);
      return Promise.reject(new Error('Undefined URL'));
    }
    console.log('📡 Fetch:', url);
    return originalFetch.apply(this, args);
  };

  // 拦截 XMLHttpRequest
  const originalXHROpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...args) {
    if (url && (url.includes('undefined') || url === 'undefined')) {
      console.error('❌ XHR called with undefined URL:', url);
      console.error('Stack:', new Error().stack);
    }
    console.log('📡 XHR:', method, url);
    return originalXHROpen.call(this, method, url, ...args);
  };

  // 拦截动态脚本加载
  const originalCreateElement = document.createElement;
  document.createElement = function (tagName, ...args) {
    const element = originalCreateElement.call(document, tagName, ...args);
    
    if (tagName.toLowerCase() === 'script') {
      const originalSetAttribute = element.setAttribute.bind(element);
      element.setAttribute = function (name, value) {
        if ((name === 'src' || name === 'href') && (value === 'undefined' || value.includes('undefined'))) {
          console.error('❌ Script src set to undefined:', value);
          console.error('Stack:', new Error().stack);
        }
        return originalSetAttribute(name, value);
      };
    }
    
    return element;
  };

  // 拦截 src 属性设置
  const scriptProto = HTMLScriptElement.prototype;
  const srcDescriptor = Object.getOwnPropertyDescriptor(scriptProto, 'src') || {
    get: function () { return this.getAttribute('src'); },
    set: function (value) { this.setAttribute('src', value); }
  };
  
  Object.defineProperty(scriptProto, 'src', {
    get: srcDescriptor.get,
    set: function (value) {
      if (value === 'undefined' || (typeof value === 'string' && value.includes('undefined'))) {
        console.error('❌ Script.src set to undefined:', value);
        console.error('Stack:', new Error().stack);
      }
      return srcDescriptor.set.call(this, value);
    }
  });

  // 监听资源加载错误
  window.addEventListener('error', function (e) {
    const target = e.target;
    if (target && (target.tagName === 'SCRIPT' || target.tagName === 'LINK' || target.tagName === 'IMG')) {
      const src = target.src || target.href;
      if (src && src.includes('undefined')) {
        console.error('❌ Resource failed to load:', src);
        console.error('Element:', target);
      }
    }
  }, true);

  console.log('✅ Debug loader installed');
  console.log('Monitoring for undefined URLs...');
})();
