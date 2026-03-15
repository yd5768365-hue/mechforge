/**
 * 包分析脚本
 * 分析项目大小和依赖
 */

const fs = require('fs');
const path = require('path');

// 配置
const config = {
  root: path.join(__dirname, '..'),
  exclude: ['node_modules', '.git', 'dist', 'build', '__pycache__', '.cache']
};

// 文件类型统计
const stats = {
  totalSize: 0,
  totalFiles: 0,
  byType: {},
  byDir: {}
};

// 获取文件大小（人类可读）
function formatSize(bytes) {
  const sizes = ['B', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
}

// 扫描目录
function scanDir(dir, baseDir = '') {
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const relativePath = path.join(baseDir, item);

    // 排除
    if (config.exclude.some(e => relativePath.includes(e))) continue;

    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      scanDir(fullPath, relativePath);
    } else {
      const ext = path.extname(item).toLowerCase() || 'no-ext';
      const size = stat.size;

      stats.totalSize += size;
      stats.totalFiles++;

      // 按类型统计
      if (!stats.byType[ext]) {
        stats.byType[ext] = { count: 0, size: 0 };
      }
      stats.byType[ext].count++;
      stats.byType[ext].size += size;

      // 按目录统计
      const dirName = path.dirname(relativePath);
      if (!stats.byDir[dirName]) {
        stats.byDir[dirName] = { count: 0, size: 0 };
      }
      stats.byDir[dirName].count++;
      stats.byDir[dirName].size += size;
    }
  }
}

// 生成报告
function generateReport() {
  console.log('\n📊 Bundle Analysis Report');
  console.log('═'.repeat(60));

  console.log('\n📁 Overview:');
  console.log(`  Total Files: ${stats.totalFiles}`);
  console.log(`  Total Size: ${formatSize(stats.totalSize)}`);

  console.log('\n📄 By File Type:');
  const sortedTypes = Object.entries(stats.byType)
    .sort((a, b) => b[1].size - a[1].size);

  for (const [ext, data] of sortedTypes.slice(0, 10)) {
    const percentage = ((data.size / stats.totalSize) * 100).toFixed(1);
    console.log(`  ${ext.padEnd(10)} ${String(data.count).padStart(4)} files  ${formatSize(data.size).padStart(10)}  ${percentage}%`);
  }

  console.log('\n📂 By Directory:');
  const sortedDirs = Object.entries(stats.byDir)
    .sort((a, b) => b[1].size - a[1].size);

  for (const [dir, data] of sortedDirs.slice(0, 10)) {
    const percentage = ((data.size / stats.totalSize) * 100).toFixed(1);
    console.log(`  ${dir.padEnd(20)} ${String(data.count).padStart(4)} files  ${formatSize(data.size).padStart(10)}  ${percentage}%`);
  }

  // 保存 JSON 报告
  const reportPath = path.join(config.root, 'bundle-analysis.json');
  fs.writeFileSync(reportPath, JSON.stringify(stats, null, 2));
  console.log(`\n💾 Report saved to: ${reportPath}`);
}

// 主函数
function main() {
  console.log('🔍 Analyzing project...');
  scanDir(config.root);
  generateReport();
}

main();
