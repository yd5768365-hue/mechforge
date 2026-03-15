/**
 * @fileoverview Code Quality Checker
 * @description 代码质量检查脚本
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');

// ==================== 配置 ====================

const CONFIG = {
  maxFileSize: 50 * 1024, // 50KB
  maxFunctionLength: 50,
  maxLinesPerFile: 500,
  maxComplexity: 10,
  requiredJSDoc: ['public', 'exported']
};

// ==================== 颜色输出 ====================

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// ==================== 检查器 ====================

class CodeQualityChecker {
  constructor() {
    this.issues = [];
    this.stats = {
      filesChecked: 0,
      totalLines: 0,
      functions: 0,
      classes: 0,
      comments: 0
    };
  }

  /**
   * 检查单个文件
   * @param {string} filePath - 文件路径
   * @param {string} content - 文件内容
   */
  checkFile(filePath, content) {
    this.stats.filesChecked++;
    const lines = content.split('\n');
    this.stats.totalLines += lines.length;

    const relativePath = path.relative(process.cwd(), filePath);

    // 检查文件大小
    const fileSize = Buffer.byteLength(content, 'utf8');
    if (fileSize > CONFIG.maxFileSize) {
      this.addIssue('warning', relativePath, 0, `File too large (${(fileSize / 1024).toFixed(2)}KB)`);
    }

    // 检查行数
    if (lines.length > CONFIG.maxLinesPerFile) {
      this.addIssue('warning', relativePath, 0, `File too long (${lines.length} lines)`);
    }

    // 检查每行
    let inFunction = false;
    let functionStartLine = 0;
    let braceCount = 0;
    let commentLines = 0;

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // 统计注释
      if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) {
        commentLines++;
        this.stats.comments++;
      }

      // 检查函数长度
      if (trimmed.match(/^(function|async function|const .* = .*function|const .* = async.*=>)/)) {
        inFunction = true;
        functionStartLine = lineNum;
        braceCount = 0;
        this.stats.functions++;
      }

      if (inFunction) {
        braceCount += (trimmed.match(/{/g) || []).length;
        braceCount -= (trimmed.match(/}/g) || []).length;

        if (braceCount === 0 && trimmed.includes('}')) {
          const functionLength = lineNum - functionStartLine + 1;
          if (functionLength > CONFIG.maxFunctionLength) {
            this.addIssue(
              'warning',
              relativePath,
              functionStartLine,
              `Function too long (${functionLength} lines)`
            );
          }
          inFunction = false;
        }
      }

      // 检查 console.log
      if (trimmed.match(/console\.(log|debug|info)\s*\(/)) {
        this.addIssue('info', relativePath, lineNum, 'Found console.log (remove in production)');
      }

      // 检查 TODO/FIXME
      if (trimmed.match(/\/\/\s*(TODO|FIXME|XXX|HACK)/i)) {
        this.addIssue('info', relativePath, lineNum, `Found ${trimmed.match(/TODO|FIXME|XXX|HACK/i)[0]}`);
      }

      // 检查长行
      if (line.length > 120) {
        this.addIssue('warning', relativePath, lineNum, `Line too long (${line.length} chars)`);
      }

      // 检查 trailing spaces
      if (line.match(/\s+$/)) {
        this.addIssue('error', relativePath, lineNum, 'Trailing whitespace');
      }

      // 检查 var 使用
      if (trimmed.match(/\bvar\s+/)) {
        this.addIssue('error', relativePath, lineNum, 'Use const or let instead of var');
      }

      // 检查 == 使用
      if (trimmed.match(/[^=!]==[^=]/) || trimmed.match(/!=[^=]/)) {
        this.addIssue('warning', relativePath, lineNum, 'Use === or !== instead');
      }
    });

    // 检查 JSDoc 覆盖率
    const jsdocRatio = commentLines / lines.length;
    if (jsdocRatio < 0.1 && lines.length > 50) {
      this.addIssue('info', relativePath, 0, `Low comment coverage (${(jsdocRatio * 100).toFixed(1)}%)`);
    }
  }

  /**
   * 添加问题
   * @param {string} severity - 严重程度
   * @param {string} file - 文件路径
   * @param {number} line - 行号
   * @param {string} message - 消息
   */
  addIssue(severity, file, line, message) {
    this.issues.push({ severity, file, line, message });
  }

  /**
   * 递归检查目录
   * @param {string} dir - 目录路径
   */
  checkDirectory(dir) {
    const files = fs.readdirSync(dir);

    files.forEach((file) => {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        if (!['node_modules', 'dist', 'build', '__pycache__', '.git'].includes(file)) {
          this.checkDirectory(fullPath);
        }
      } else if (file.endsWith('.js') && !file.endsWith('.min.js')) {
        const content = fs.readFileSync(fullPath, 'utf8');
        this.checkFile(fullPath, content);
      }
    });
  }

  /**
   * 生成报告
   */
  generateReport() {
    log('\n========== Code Quality Report ==========\n', 'cyan');

    // 统计
    const errors = this.issues.filter((i) => i.severity === 'error').length;
    const warnings = this.issues.filter((i) => i.severity === 'warning').length;
    const infos = this.issues.filter((i) => i.severity === 'info').length;

    log(`Files checked: ${this.stats.filesChecked}`, 'blue');
    log(`Total lines: ${this.stats.totalLines}`, 'blue');
    log(`Functions: ${this.stats.functions}`, 'blue');
    log(`Comment lines: ${this.stats.comments}`, 'blue');
    log(`\nIssues found:`, 'blue');
    log(`  Errors: ${errors}`, errors > 0 ? 'red' : 'green');
    log(`  Warnings: ${warnings}`, warnings > 0 ? 'yellow' : 'green');
    log(`  Info: ${infos}`, 'blue');

    // 按文件分组
    if (this.issues.length > 0) {
      log('\n---------- Issues ----------\n', 'magenta');

      const grouped = this.issues.reduce((acc, issue) => {
        if (!acc[issue.file]) acc[issue.file] = [];
        acc[issue.file].push(issue);
        return acc;
      }, {});

      Object.entries(grouped).forEach(([file, issues]) => {
        log(`\n${file}:`, 'cyan');
        issues.forEach((issue) => {
          const color = issue.severity === 'error' ? 'red' : issue.severity === 'warning' ? 'yellow' : 'blue';
          const line = issue.line > 0 ? `:${issue.line}` : '';
          log(`  ${issue.severity.toUpperCase()}${line}: ${issue.message}`, color);
        });
      });
    }

    // 评分
    const score = Math.max(0, 100 - errors * 5 - warnings * 2);
    const scoreColor = score >= 90 ? 'green' : score >= 70 ? 'yellow' : 'red';

    log(`\n========== Score: ${score}/100 ==========\n`, scoreColor);

    return { score, errors, warnings, infos };
  }
}

// ==================== 主程序 ====================

function main() {
  const checker = new CodeQualityChecker();

  log('Starting code quality check...', 'cyan');

  // 检查核心目录
  const dirsToCheck = ['core', 'app', 'services'];

  dirsToCheck.forEach((dir) => {
    const fullPath = path.join(process.cwd(), dir);
    if (fs.existsSync(fullPath)) {
      checker.checkDirectory(fullPath);
    }
  });

  const report = checker.generateReport();

  // 退出码
  process.exit(report.errors > 0 ? 1 : 0);
}

main();
