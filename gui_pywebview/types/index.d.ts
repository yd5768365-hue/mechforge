/**
 * MechForge AI - TypeScript 类型定义
 * @version 1.0.0
 */

// ==================== 基础类型 ====================

declare type ElementId = string;
declare type Selector = string;
declare type EventType = string;
declare type ErrorType = 'NETWORK_ERROR' | 'API_ERROR' | 'VALIDATION_ERROR' | 'RUNTIME_ERROR' | 'INITIALIZATION_ERROR' | 'TIMEOUT_ERROR' | 'ABORT_ERROR' | 'UNKNOWN_ERROR';
declare type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';
declare type TabName = 'chat' | 'knowledge' | 'cae' | 'experience';

// ==================== DOM 工具 ====================

declare function $(id: ElementId): HTMLElement | null;
declare function $$(selector: Selector): NodeListOf<HTMLElement>;
declare function $one(selector: Selector): HTMLElement | null;

// ==================== 字符串工具 ====================

declare function escapeHtml(str: string | number | null | undefined): string;
declare function truncate(str: string, maxLen: number, suffix?: string): string;
declare function generateId(prefix?: string): string;
declare function toCamelCase(str: string): string;
declare function toKebabCase(str: string): string;

// ==================== 函数工具 ====================

declare function debounce<T extends (...args: any[]) => any>(fn: T, delay?: number): (...args: Parameters<T>) => void;
declare function throttle<T extends (...args: any[]) => any>(fn: T, limit?: number): (...args: Parameters<T>) => void;
declare function memoize<T extends (...args: any[]) => any>(fn: T): (...args: Parameters<T>) => ReturnType<T>;
declare function pipe<T>(...fns: Array<(arg: T) => T>): (value: T) => T;
declare function compose<T>(...fns: Array<(arg: T) => T>): (value: T) => T;

// ==================== 时间工具 ====================

declare function getTimestamp(): string;
declare function formatDateTime(date?: Date, format?: string): string;
declare function delay(ms: number): Promise<void>;

// ==================== 随机数工具 ====================

declare function random(min: number, max: number): number;
declare function randomInt(min: number, max: number): number;
declare function randomChoice<T>(arr: T[]): T;
declare function randomColor(): string;

// ==================== 对象工具 ====================

declare function deepClone<T>(obj: T): T;
declare function mergeObjects<T extends Record<string, any>>(...objects: T[]): T;
declare function pick<T extends Record<string, any>, K extends keyof T>(obj: T, keys: K[]): Pick<T, K>;
declare function omit<T extends Record<string, any>, K extends keyof T>(obj: T, keys: K[]): Omit<T, K>;
declare function toQueryString(params: Record<string, any>): string;

// ==================== DOM 操作 ====================

declare function appendChildren(parent: HTMLElement, children: HTMLElement[]): void;
declare function safeRemove(element: HTMLElement): boolean;
declare function onVisible(element: HTMLElement, callback: (el: HTMLElement) => void): IntersectionObserver | null;
declare function createElement<K extends keyof HTMLElementTagNameMap>(tag: K, attributes?: Record<string, any>, options?: { parent?: HTMLElement }): HTMLElementTagNameMap[K];

// ==================== 验证工具 ====================

declare function isEmpty(value: any): boolean;
declare function isNumber(value: any): boolean;
declare function isString(value: any): boolean;
declare function isFunction(value: any): boolean;
declare function isObject(value: any): boolean;

// ==================== 性能工具 ====================

declare function measurePerformance<T extends (...args: any[]) => any>(fn: T, label?: string): (...args: Parameters<T>) => ReturnType<T>;
declare function schedule(fn: () => void, delay?: number): void;

// ==================== 错误处理 ====================

interface ErrorInfo {
  type: ErrorType;
  message: string;
  severity: ErrorSeverity;
  timestamp: string;
  stack?: string;
  context?: Record<string, any>;
}

interface AppError extends Error {
  type: ErrorType;
  severity: ErrorSeverity;
  timestamp: string;
  context: Record<string, any>;
  cause?: Error;
  toJSON(): ErrorInfo;
}

interface ErrorHandler {
  handleError(error: Error | string | object, type?: ErrorType, context?: Record<string, any>): ErrorInfo;
  onError(type: string, callback: (error: ErrorInfo) => void): () => void;
  getErrorHistory(type?: ErrorType, limit?: number): ErrorInfo[];
  clearHistory(): void;
  setSilentType(type: ErrorType, silent: boolean): void;
}

declare function withErrorHandling<T>(fn: () => Promise<T>, options?: {
  onError?: (error: ErrorInfo) => T;
  fallback?: T;
  retries?: number;
  retryDelay?: number;
  timeout?: number;
}): Promise<T>;

declare function createSafeAsync<T>(fn: () => Promise<T>, fallback?: T): () => Promise<T>;

// ==================== 事件管理 ====================

interface EventManager {
  on(element: HTMLElement, event: EventType, handler: (e: Event) => void, options?: { once?: boolean; passive?: boolean; capture?: boolean }): void;
  off(element: HTMLElement, event: EventType, handler: (e: Event) => void): void;
  once(element: HTMLElement, event: EventType, handler: (e: Event) => void, options?: { passive?: boolean; capture?: boolean }): void;
  delegate(container: HTMLElement, selector: string, event: EventType, handler: (e: Event, target: HTMLElement) => void): void;
  // cspell:ignore-line
  undelegate(container: HTMLElement, selector: string, event: EventType): void;
  emit(element: HTMLElement, eventName: string, detail?: any): void;
  cleanup(): void;
  observeRemoval(element: HTMLElement, callback: () => void): void;
  startAutoCleanup(): void;
  stopAutoCleanup(): void;
  getStats(): { totalListeners: number; eventCounts: Record<string, number>; trackedElements: number };
  destroy(): void;
}

// ==================== 性能监控 ====================

interface PerformanceMetrics {
  fps: Array<{ value: number; timestamp: number }>;
  frameTime: Array<{ value: number; timestamp: number }>;
  memory: Array<{ value: { used: number; total: number; limit: number; ratio: number }; timestamp: number }>;
  longTasks: Array<{ value: { duration: number; startTime: number; name: string }; timestamp: number }>;
  errors: Array<{ value: { message: string; stack?: string; context?: string }; timestamp: number }>;
}

interface PerformanceReport {
  fps: { average: number; min: number; max: number; history: Array<{ value: number; timestamp: number }> };
  memory: { usedMB: string; totalMB: string; limitMB: string; usagePercent: string } | null;
  longTasks: number;
  errors: number;
}

interface PerformanceMonitor {
  start(): void;
  stop(): void;
  recordError(error: Error, context?: string): void;
  getAverageFPS(): number;
  getMemoryStats(): { usedMB: string; totalMB: string; limitMB: string; usagePercent: string } | null;
  getReport(): PerformanceReport;
  logMetrics(): void;
  measure<T extends (...args: any[]) => any>(fn: T, name: string): (...args: Parameters<T>) => ReturnType<T>;
  mark(name: string): void;
  measureBetween(startMark: string, endMark: string, measureName: string): number;
  clear(): void;
  metrics: PerformanceMetrics;
}

// ==================== 模块加载 ====================

interface ModuleDefinition {
  path: string;
  required: boolean;
  lazy?: boolean;
  dependencies?: string[];
}

interface ModuleLoader {
  load(name: string, retryCount?: number): Promise<any>;
  preload(name: string): void;
  lazyLoad(name: string): Promise<any>;
  initCore(): Promise<void>;
  initLazy(): void;
  get(name: string): any;
  isLoaded(name: string): boolean;
  waitFor(name: string, timeout?: number): Promise<any>;
  registry: Record<string, ModuleDefinition>;
}

// ==================== 全局对象 ====================

declare const Utils: {
  $: typeof $;
  $$: typeof $$;
  $one: typeof $one;
  escapeHtml: typeof escapeHtml;
  truncate: typeof truncate;
  generateId: typeof generateId;
  toCamelCase: typeof toCamelCase;
  toKebabCase: typeof toKebabCase;
  debounce: typeof debounce;
  throttle: typeof throttle;
  memoize: typeof memoize;
  pipe: typeof pipe;
  compose: typeof compose;
  getTimestamp: typeof getTimestamp;
  formatDateTime: typeof formatDateTime;
  delay: typeof delay;
  random: typeof random;
  randomInt: typeof randomInt;
  randomChoice: typeof randomChoice;
  randomColor: typeof randomColor;
  deepClone: typeof deepClone;
  mergeObjects: typeof mergeObjects;
  pick: typeof pick;
  omit: typeof omit;
  toQueryString: typeof toQueryString;
  appendChildren: typeof appendChildren;
  safeRemove: typeof safeRemove;
  onVisible: typeof onVisible;
  createElement: typeof createElement;
  measurePerformance: typeof measurePerformance;
  schedule: typeof schedule;
  isEmpty: typeof isEmpty;
  isNumber: typeof isNumber;
  isString: typeof isString;
  isFunction: typeof isFunction;
  isObject: typeof isObject;
  RUNE_CHARS: string[];
  PARTICLE_COUNT: number;
  WHALE_SPEECH_MAX_LEN: number;
  RUNE_COUNT: number;
};

declare const ErrorHandler: ErrorHandler;
declare const ErrorTypes: Record<string, ErrorType>;
declare const ErrorSeverity: Record<string, ErrorSeverity>;
declare const AppError: new (type: ErrorType, message: string, context?: Record<string, any>, cause?: Error) => AppError;

declare const EventManager: EventManager;
declare const PerformanceMonitor: PerformanceMonitor;
declare const ModuleLoader: ModuleLoader;

// ==================== 测试框架 ====================

declare function describe(name: string, fn: () => void): void;
declare function it(name: string, fn: () => void | Promise<void>, timeout?: number): void;
declare namespace it {
  function skip(name: string, fn: () => void): void;
  function only(name: string, fn: () => void | Promise<void>, timeout?: number): void;
}
declare function beforeEach(fn: () => void | Promise<void>): void;
declare function afterEach(fn: () => void | Promise<void>): void;
declare function expect<T>(actual: T): {
  toBe(expected: T): void;
  toEqual(expected: T): void;
  toBeNull(): void;
  toBeUndefined(): void;
  toBeTruthy(): void;
  toBeFalsy(): void;
  toBeGreaterThan(expected: number): void;
  toBeGreaterThanOrEqual(expected: number): void;
  toBeLessThan(expected: number): void;
  toBeLessThanOrEqual(expected: number): void;
  toContain(expected: any): void;
  toMatch(pattern: RegExp): void;
  toThrow(expectedMessage?: string): void;
  toBeInstanceOf(expectedClass: new (...args: any[]) => any): void;
  toHaveLength(expected: number): void;
  toBeDefined(): void;
  toBeNaN(): void;
  not: {
    toBe(expected: T): void;
    toEqual(expected: T): void;
    toContain(expected: any): void;
    toMatch(pattern: RegExp): void;
  };
};

interface TestFramework {
  describe: typeof describe;
  it: typeof it;
  beforeEach: typeof beforeEach;
  afterEach: typeof afterEach;
  expect: typeof expect;
  run(): Promise<{ passed: number; failed: number; skipped: number; total: number; success: boolean }>;
  reset(): void;
}

declare const TestFramework: TestFramework;

// ==================== 应用状态 ====================

interface AppState {
  activeTab: TabName;
  booted: boolean;
  aiService: any;
  configService: any;
  initErrors: string[];
  initTime: number;
}

declare const AppState: AppState;
declare function getAppState(): AppState & { loadedModules: string[]; eventStats: any };
declare function getPerformanceReport(): PerformanceReport;
